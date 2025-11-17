from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from dao.intencao_de_doacao import listar_intencoes, atualizar_status
from dao.intencao_item import listar_itens_intencao, atualizar_item_intencao
from dao.listas import exibir_listas
from dao.itens import exibir_itens
from dao.doador import listar_doadores

intencoes_ong_bp = Blueprint("intencoes_ong", __name__)

STATUS_MAP = {
    0: "Pendente",
    1: "Aprovado",
    2: "Reprovado",
    3: "Finalizado"
}

STATUS_REVERSE = {v: k for k, v in STATUS_MAP.items()}

# Tela principal de intenções recebidas pela ONG
@intencoes_ong_bp.route("/IntencoesONG", methods=["GET", "POST"])
def intencoes_ong():
    ong = session.get("ong_logada")
    if not ong:
        flash("Nenhuma ONG logada. Faça login para continuar.")
        return redirect(url_for("login_ong.login_ong"))

    status_selecionado = request.form.get("status", "Todos")
    busca = request.form.get("busca", "").strip().lower()

    mapa_listas = {l["ID_Lista"]: l for l in exibir_listas()}
    mapa_itens = {i["ID_Item"]: i for i in exibir_itens()}
    mapa_doadores = {d["CPF_ID"]: d for d in listar_doadores()}

    todas_intencoes = listar_intencoes()
    intencoes_ong = [i for i in todas_intencoes if i.get("ID_ONG") == ong.get("CNPJ_ID")]

    for i in intencoes_ong:
        if isinstance(i["status"], str):
            i["status"] = STATUS_REVERSE.get(i["status"], -1)

    def filtrar(lista):
        if not busca:
            return lista
        return [
            i for i in lista
            if busca in mapa_doadores.get(i["ID_Doador"], {}).get("nome", "").lower()
            or busca in mapa_listas.get(i["ID_Lista"], {}).get("titulo", "").lower()
        ]

    pendentes   = filtrar([i for i in intencoes_ong if i["status"] == 0])
    aprovadas   = filtrar([i for i in intencoes_ong if i["status"] == 1])
    reprovadas  = filtrar([i for i in intencoes_ong if i["status"] == 2])
    finalizadas = filtrar([i for i in intencoes_ong if i["status"] == 3])

    return render_template("intencoesONG.html",
        pendentes=pendentes,
        aprovadas=aprovadas,
        reprovadas=reprovadas,
        finalizadas=finalizadas,
        status_selecionado=status_selecionado,
        mapa_listas=mapa_listas,
        mapa_itens=mapa_itens,
        mapa_doadores=mapa_doadores,
        STATUS_MAP=STATUS_MAP,
        busca=busca,
        listar_itens_intencao=listar_itens_intencao
    )

# Aprovar intenção e adicionar observações
@intencoes_ong_bp.route("/AprovarIntencao/<id>", methods=["POST"])
def aprovar_intencao(id):
    itens = listar_itens_intencao(id)
    for item in itens:
        obs = request.form.get(f"obs_{item['ID_Item']}")
        atualizar_item_intencao(id, item["ID_Item"], nova_observacao=obs)
    sucesso, msg = atualizar_status(id, "Aprovado")
    flash("Intenção aprovada." if sucesso else msg, "success")
    return redirect(url_for("intencoes_ong.intencoes_ong"))

# Recusar intenção
@intencoes_ong_bp.route("/RecusarIntencao/<id>")
def recusar_intencao(id):
    atualizar_status(id, "Reprovado")
    flash("Intenção recusada.", "success")
    return redirect(url_for("intencoes_ong.intencoes_ong"))

# Reverter intenção para pendente
@intencoes_ong_bp.route("/ReverterIntencao/<id>")
def reverter_intencao(id):
    atualizar_status(id, "Pendente")
    flash("Intenção revertida para pendente.", "warning")
    return redirect(url_for("intencoes_ong.intencoes_ong"))
