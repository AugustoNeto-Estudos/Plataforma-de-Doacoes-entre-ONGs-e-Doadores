from flask import Blueprint, render_template, redirect, url_for, flash, request
from dao.listas import exibir_listas
from dao.ong import buscar_ong_por_id
from dao.feedback import buscar_feedbacks_por_ong
import requests

perfil_ong_doador_bp = Blueprint("perfil_ong_doador", __name__)

@perfil_ong_doador_bp.route("/PerfilONGDoador/<path:cnpj>", methods=["GET", "POST"])
def perfil_ong_doador(cnpj):
    # Buscar ONG pelo CNPJ
    ong = buscar_ong_por_id(cnpj)
    if not ong:
        flash("⚠️ ONG não encontrada.")
        return redirect(url_for("menu_doador.menu_doador"))

    # Buscar listas da ONG
    listas = exibir_listas() or []
    listas_ong = [l for l in listas if l.get("ID_ONG") == ong.get("CNPJ_ID")]

    # Filtro de busca
    termo = request.args.get("busca", "").strip().lower()
    if termo:
        listas_ong = [
            l for l in listas_ong
            if termo in (l.get("titulo", "").lower() or "")
            or termo in (l.get("descricao", "").lower() or "")
        ]

    # Calcular nota média da ONG
    feedbacks = buscar_feedbacks_por_ong(ong.get("CNPJ_ID"))
    media_nota = round(sum(f["nota"] for f in feedbacks) / len(feedbacks), 1) if feedbacks else None

    # Consulta pública do CNPJ via BrasilAPI
    dados_cnpj = None
    if request.method == "POST":
        sucesso, resultado = consultar_cnpj_brasilapi(cnpj)
        if sucesso:
            dados_cnpj = resultado
            print("[DEBUG] Dados recebidos da BrasilAPI:", resultado)
            flash("✅ Dados públicos da ONG consultados com sucesso.")
        else:
            flash(f"❌ Falha ao consultar CNPJ: {resultado}")
            # Retorna dados mockados para não deixar modal vazio
            dados_cnpj = {
                "razao_social": "ONG Exemplo Solidária",
                "nome_fantasia": "Solidária Mock",
                "descricao_situacao_cadastral": "INEXISTENTE",
                "natureza_juridica": "Associação Privada",
                "data_inicio_atividade": "0000-00-00",
                "municipio": "Cidade Fictícia",
                "uf": "XX"
            }

    # Renderizar template com todos os dados
    return render_template(
        "perfilONGDoador.html",
        ong=ong,
        listas=listas_ong,
        media_nota=media_nota,
        dados_cnpj=dados_cnpj,
        busca=termo
    )

# Função auxiliar para consultar CNPJ via BrasilAPI
def consultar_cnpj_brasilapi(cnpj):
    cnpj = ''.join(filter(str.isdigit, cnpj))  # remove pontuação
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Erro {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"Erro na requisição: {str(e)}"
