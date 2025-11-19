from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from dao.intencao_de_doacao import listar_intencoes, atualizar_status
from dao.intencao_item import listar_itens_intencao
from dao.listas import exibir_listas
from dao.itens import exibir_itens
from dao.ong import listar_ongs
from dao.pedidos import inserir_pedido
from dao.itensPedido import inserir_pedido_item
from datetime import date
import uuid

intencoes_doador_bp = Blueprint("intencoes_doador", __name__)

STATUS_MAP = {
    0: "Pendente",
    1: "Aprovado",
    2: "Reprovado",
    3: "Finalizado"
}

STATUS_REVERSE = {v: k for k, v in STATUS_MAP.items()}

# Tela principal de intenções feitas pelo doador
@intencoes_doador_bp.route("/IntencoesDoador", methods=["GET", "POST"])
def intencoes_doador():
    if "doador_logado" not in session:
        flash("Nenhum doador logado. Faça login para continuar.")
        return redirect(url_for("login_doador.login_doador"))

    status_selecionado = request.form.get("status", "Todos")
    busca = request.form.get("busca", "").strip().lower()

    mapa_listas = {l["ID_Lista"]: l for l in exibir_listas()}
    mapa_itens = {i["ID_Item"]: i for i in exibir_itens()}
    mapa_ongs = {o["CNPJ_ID"]: o for o in listar_ongs()}

    todas_intencoes = listar_intencoes()
    cpf_doador = session["doador_logado"]["CPF_ID"]
    minhas_intencoes = [i for i in todas_intencoes if i.get("ID_Doador") == cpf_doador]

    for i in minhas_intencoes:
        if isinstance(i["status"], str):
            i["status"] = STATUS_REVERSE.get(i["status"], -1)

    def filtrar(lista):
        if not busca:
            return lista
        return [
            i for i in lista
            if busca in mapa_ongs.get(i["ID_ONG"], {}).get("nome", "").lower()
            or busca in mapa_listas.get(i["ID_Lista"], {}).get("titulo", "").lower()
        ]

    pendentes   = filtrar([i for i in minhas_intencoes if i["status"] == 0])
    aprovadas   = filtrar([i for i in minhas_intencoes if i["status"] == 1])
    reprovadas  = filtrar([i for i in minhas_intencoes if i["status"] == 2])
    finalizadas = filtrar([i for i in minhas_intencoes if i["status"] == 3])

    return render_template("intencoesDoador.html",
        pendentes=pendentes,
        aprovadas=aprovadas,
        reprovadas=reprovadas,
        finalizadas=finalizadas,
        status_selecionado=status_selecionado,
        mapa_listas=mapa_listas,
        mapa_itens=mapa_itens,
        mapa_ongs=mapa_ongs,
        STATUS_MAP=STATUS_MAP,
        busca=busca,
        listar_itens_intencao=listar_itens_intencao
    )

# Confirmar intenção aprovada e gerar pedido
@intencoes_doador_bp.route("/ConfirmarPedido/<id_intencao>", methods=["POST"])
def confirmar_pedido(id_intencao):
    intencao = next((i for i in listar_intencoes() if i["ID_Intencao"] == id_intencao), None)
    if not intencao:
        flash("Intenção não encontrada.", "warning")
        return redirect(url_for("intencoes_doador.intencoes_doador"))

    itens_intencao = listar_itens_intencao(id_intencao)
    id_pedido = str(uuid.uuid4())[:8]

    sucesso, msg = inserir_pedido(
        id_pedido,
        intencao["ID_ONG"],
        intencao["ID_Doador"],
        intencao["ID_Intencao"],
        0,
        date.today()
    )

    if sucesso:
        for item in itens_intencao:
            inserir_pedido_item(
                id_pedido,
                item["ID_Item"],
                item["quantidade_pretendida"],
                item.get("observacao")
            )
        atualizar_status(id_intencao, "Finalizado")
        flash("Pedido criado com sucesso.", "success")
    else:
        flash(f"Erro ao criar pedido: {msg}", "error")

    return redirect(url_for("intencoes_doador.intencoes_doador"))

# Reprovar intenção aprovada
@intencoes_doador_bp.route("/ReprovarIntencao/<id_intencao>", methods=["POST"])
def reprovar_intencao(id_intencao):
    intencao = next((i for i in listar_intencoes() if i["ID_Intencao"] == id_intencao), None)
    if not intencao:
        flash("Intenção não encontrada.", "warning")
        return redirect(url_for("intencoes_doador.intencoes_doador"))

    atualizar_status(id_intencao, "Reprovado")
    flash("Intenção reprovada. A ONG será notificada.", "error")
    return redirect(url_for("intencoes_doador.intencoes_doador"))
