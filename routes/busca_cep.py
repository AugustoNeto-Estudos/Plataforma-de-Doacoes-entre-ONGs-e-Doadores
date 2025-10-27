from flask import Blueprint, render_template, request, flash, jsonify
from dao.cep import buscar_endereco, carregar_ongs, ongs_ordenadas_por_distancia
from dao.listas import exibir_listas
from dao.itensLista import exibir_lista_itens
from dao.itens import exibir_itens
from geopy.geocoders import Nominatim
import re

busca_cep_bp = Blueprint("busca_cep", __name__)

# 🔹 Rota principal: Busca por CEP ou palavra-chave
@busca_cep_bp.route("/BuscaCEP", methods=["GET", "POST"])
def busca_cep():
    resultados = []
    endereco = None
    termo = ""
    termo_lower = ""

    if request.method == "POST":
        termo = request.form.get("busca", "").strip()
        termo_lower = termo.lower()
        acao = request.form.get("acao")
        ongs = carregar_ongs()

        if acao == "listar_todas":
            resultados = ongs
        elif not termo:
            flash("Digite um CEP ou palavra-chave para buscar.")
        elif termo.isdigit() and len(termo) == 8:
            endereco = buscar_endereco(termo)
            if endereco:
                resultados = ongs_ordenadas_por_distancia(termo)
            else:
                flash("CEP inválido ou não encontrado.")
        else:
            resultados = [
                ong for ong in ongs
                if termo_lower in (ong.get("nome", "").lower())
                or termo_lower in (ong.get("descricao", "").lower())
                or termo_lower in (ong.get("bairro", "").lower())
                or termo_lower in (ong.get("cidade", "").lower())
            ]
    else:
        resultados = carregar_ongs()

    # 🔍 Enriquecer cada ONG com endereço completo via ViaCEP
    for ong in resultados:
        cep = re.sub(r'\D', '', ong.get("cep", ""))
        if cep and cep.isdigit() and len(cep) == 8:
            endereco_ong = buscar_endereco(cep)
            if endereco_ong:
                partes = [
                    endereco_ong.get("logradouro", ""),
                    endereco_ong.get("bairro", ""),
                    endereco_ong.get("cidade", ""),
                    "SP",  # Estado fixo
                    "Brasil"
                ]
                partes_validas = [p.strip() for p in partes if p and p.strip()]
                endereco_limpo = ', '.join(partes_validas)
                ong["endereco_completo"] = endereco_limpo

    return render_template(
        "buscaCEP.html",
        resultados=resultados,
        endereco=endereco,
        termo=termo
    )

# 🔹 Rota: Localização geográfica via endereço completo
@busca_cep_bp.route("/api/localizacao")
def api_localizacao():
    endereco = request.args.get("endereco", "")
    print(f"[LOG] Endereço recebido: {endereco}")
    if not endereco:
        print("[LOG] Nenhum endereço informado.")
        return jsonify({"erro": "Endereço não informado"}), 400

    # 🔹 Adiciona estado e país se estiverem ausentes
    if "SP" not in endereco and "São Paulo" not in endereco:
        endereco += ", SP"
    if "Brasil" not in endereco:
        endereco += ", Brasil"

    # 🔹 Limpeza profunda do endereço
    endereco_limpo = endereco
    endereco_limpo = re.sub(r',\s*,', ',', endereco_limpo)  # remove vírgulas duplicadas
    endereco_limpo = re.sub(r'\s+', ' ', endereco_limpo)    # remove espaços duplicados
    endereco_limpo = endereco_limpo.strip(", ").strip()

    print(f"[LOG] Endereço final para geolocalização: {endereco_limpo}")

    geolocator = Nominatim(user_agent="solidarihub")
    try:
        location = geolocator.geocode(endereco_limpo)
        print(f"[LOG] Resposta do Nominatim: {location}")
        if location:
            print(f"[LOG] Coordenadas encontradas: ({location.latitude}, {location.longitude})")
            return jsonify({
                "latitude": location.latitude,
                "longitude": location.longitude,
                "endereco": endereco_limpo
            })
        else:
            print("[LOG] Nominatim não encontrou localização.")
            return jsonify({"erro": f"Localização não encontrada para: {endereco_limpo}"}), 404
    except Exception as e:
        print(f"[LOG] Erro ao buscar localização: {str(e)}")
        return jsonify({"erro": f"Erro ao buscar localização: {str(e)}"}), 500

# 🔹 Rota: Detalhes da ONG para o modal
@busca_cep_bp.route("/api/ong_detalhe/<path:id>")
def api_ong_detalhe(id):
    ongs = carregar_ongs()
    listas = exibir_listas()
    itens = exibir_itens()

    ong = next((o for o in ongs if o["CNPJ_ID"] == id), None)
    if not ong:
        return jsonify({"erro": "ONG não encontrada"}), 404

    listas_ong = [l for l in listas if l["ID_ONG"] == id and l.get("status", True)]
    for l in listas_ong:
        l["itens"] = []
        for li in exibir_lista_itens(l["ID_Lista"]):
            item = next((i for i in itens if i["ID_Item"] == li["ID_Item"]), {})
            l["itens"].append({
                "ID_Item": item.get("ID_Item"),
                "categoria": item.get("categoria"),
                "subcategoria": item.get("subcategoria"),
                "quantidade_necessaria": li.get("quantidade_necessaria")
            })

    return jsonify({
        "nome": ong["nome"],
        "CNPJ_ID": ong["CNPJ_ID"],
        "cep": ong["cep"],
        "descricao": ong["descricao"],
        "listas": listas_ong
    })
