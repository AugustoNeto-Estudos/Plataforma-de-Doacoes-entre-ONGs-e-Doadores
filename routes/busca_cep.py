import re
from flask import Blueprint, render_template, request, flash, jsonify, session
from geopy.geocoders import Nominatim

from dao.cep import buscar_endereco, carregar_ongs, ongs_ordenadas_por_distancia
from dao.listas import exibir_listas
from dao.itensLista import exibir_lista_itens
from dao.itens import exibir_itens

busca_cep_bp = Blueprint("busca_cep", __name__)

#Cache para armazenar o CEP
cep_cache = {}
def buscar_endereco_cache(cep):
    cep = re.sub(r"\D", "", cep)
    if len(cep) != 8:
        return None

    if cep in cep_cache:
        return cep_cache[cep]

    endereco = buscar_endereco(cep)
    if endereco:
        cep_cache[cep] = endereco
    return endereco

# Rota principal: busca por CEP ou palavra-chave
@busca_cep_bp.route("/BuscaCEP", methods=["GET", "POST"])
def busca_cep():
    if "doador_logado" not in session:
        return jsonify({"erro": "Acesso não autorizado"}), 401

    resultados, endereco = [], None
    termo = request.form.get("busca", "").strip() if request.method == "POST" else ""
    termo_lower = termo.lower()
    ongs = carregar_ongs()

        # Paginação
    page = int(request.args.get("page", 1))
    limit = 20
    start = (page - 1) * limit
    end = start + limit
    total_registros = len(ongs)

    # Aplica paginação
    ongs_paginadas = ongs[start:end]

    if request.method == "POST":
        acao = request.form.get("acao")

        if acao == "listar_todas":
            resultados = ongs_paginadas
        elif not termo:
            flash("Digite um CEP ou palavra-chave para buscar.")
        elif termo.isdigit() and len(termo) == 8:
            endereco = buscar_endereco(termo)
            resultados = (ongs_ordenadas_por_distancia(termo)[:limit]) if endereco else []
            if not endereco:
                flash("CEP inválido ou não encontrado.")
        else:
            resultados = [
                ong for ong in ongs_paginadas
                if termo_lower in ong.get("nome", "").lower()
                or termo_lower in ong.get("descricao", "").lower()
                or termo_lower in ong.get("bairro", "").lower()
                or termo_lower in ong.get("cidade", "").lower()
            ]
    else:
        resultados = ongs_paginadas

    # Enriquecer cada ONG com endereço completo
    for ong in resultados:
        cep = re.sub(r"\D", "", ong.get("cep", ""))
        if cep and len(cep) == 8:
            endereco_ong = buscar_endereco_cache(cep)
            if endereco_ong:
                partes = [
                    endereco_ong.get("logradouro", ""),
                    endereco_ong.get("bairro", ""),
                    endereco_ong.get("cidade", ""),
                    "SP",
                    "Brasil",
                ]
                partes_validas = [p.strip() for p in partes if p.strip()]
                ong["endereco_completo"] = ", ".join(partes_validas)
                ong["cep_limpo"] = cep

    return render_template(
        "buscaCEP.html",
        resultados=resultados,
        endereco=endereco,
        termo=termo,
        page=page,
        limit=limit,
        total_registros=total_registros
)

# Rota: localização geográfica via CEP ou texto
@busca_cep_bp.route("/api/localizacao")
def api_localizacao():
    if "doador_logado" not in session:
        return jsonify({"erro": "Acesso não autorizado"}), 401

    endereco = request.args.get("endereco", "")
    if not endereco:
        return jsonify({"erro": "Endereço não informado"}), 400

    geolocator = Nominatim(user_agent="solidarihub", timeout=10)

    # Tenta como CEP
    cep = re.sub(r"\D", "", endereco)
    if cep and len(cep) == 8:
        endereco_consulta = f"{cep}, Brasil"
        try:
            location = geolocator.geocode(endereco_consulta, country_codes="br")
            if location:
                return jsonify({
                    "latitude": location.latitude,
                    "longitude": location.longitude,
                    "endereco": endereco_consulta,
                })
        except Exception as e:
            return jsonify({"erro": f"Erro ao buscar localização via CEP: {str(e)}"}), 500

    # Fallback: endereço textual
    # Se não achou, tenta pelo endereço textual do Viacep
        endereco_viacep = buscar_endereco_cache(cep)
        if endereco_viacep and "erro" not in endereco_viacep:
            partes = [
                endereco_viacep.get("logradouro", ""),
                endereco_viacep.get("bairro", ""),
                endereco_viacep.get("localidade", ""),
                endereco_viacep.get("uf", ""),
                "Brasil",
            ]
            endereco_texto = ", ".join([p for p in partes if p.strip()])
            try:
                location = geolocator.geocode(endereco_texto, country_codes="br")
                if location:
                    return jsonify({
                        "latitude": location.latitude,
                        "longitude": location.longitude,
                        "endereco": endereco_texto,
                    })
            except Exception as e:
                return jsonify({"erro": f"Erro ao buscar localização via endereço: {str(e)}"}), 500

    #  Se não for CEP, tenta direto como texto
    endereco_texto = endereco if "Brasil" in endereco else f"{endereco}, Brasil"
    endereco_texto = re.sub(r"\s+", " ", endereco_texto).strip()

    try:
        location = geolocator.geocode(endereco_texto, country_codes="br")
        if location:
            return jsonify({
                "latitude": location.latitude,
                "longitude": location.longitude,
                "endereco": endereco_texto,
            })
        return jsonify({"erro": f"Localização não encontrada para: {endereco_texto}"}), 404
    except Exception as e:
        return jsonify({"erro": f"Erro ao buscar localização via texto: {str(e)}"}), 500

# Rota: detalhes da ONG para modal
@busca_cep_bp.route("/api/ong_detalhe/<path:id>")
def api_ong_detalhe(id):
    if "doador_logado" not in session:
        return jsonify({"erro": "Acesso não autorizado"}), 401

    ongs = carregar_ongs()
    listas = exibir_listas()
    itens = exibir_itens()

    ong = next((o for o in ongs if o["CNPJ_ID"] == id), None)
    if not ong:
        return jsonify({"erro": "ONG não encontrada"}), 404

    listas_ong = [l for l in listas if l["ID_ONG"] == id and l.get("status", True)]
    for lista in listas_ong:
        lista["itens"] = []
        for li in exibir_lista_itens(lista["ID_Lista"]):
            item = next((i for i in itens if i["ID_Item"] == li["ID_Item"]), {})
            lista["itens"].append({
                "ID_Item": item.get("ID_Item"),
                "categoria": item.get("categoria"),
                "subcategoria": item.get("subcategoria"),
                "quantidade_necessaria": li.get("quantidade_necessaria"),
            })

    return jsonify({
        "nome": ong["nome"],
        "CNPJ_ID": ong["CNPJ_ID"],
        "cep": ong["cep"],
        "descricao": ong["descricao"],
        "listas": listas_ong,
    })
