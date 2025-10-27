from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from dao.pedidos import listar_pedidos, atualizar_status_pedido
from dao.itensPedido import exibir_pedidos_itens
from dao.listas import exibir_listas
from dao.itens import exibir_itens
from dao.ong import listar_ongs
from dao.doador import listar_doadores
from dao.intencao_de_doacao import listar_intencoes

pedidos_ong_bp = Blueprint("pedidos_ong", __name__)

STATUS_MAP = {
    0: "Em andamento",
    1: "Finalizado",
    2: "Cancelado"
}

@pedidos_ong_bp.route("/PedidosONG", methods=["GET", "POST"])
def pedidos_ong():
    if "ong_logada" not in session:
        flash("⚠️ Nenhuma ONG logada. Faça login para continuar.", "warning")
        return redirect(url_for("login_ong.login_ong"))

    status_selecionado = request.form.get("status", "Todos")
    busca = request.form.get("busca", "").strip().lower()

    mapa_listas = {l["ID_Lista"]: l for l in exibir_listas()}
    mapa_itens = {i["ID_Item"]: i for i in exibir_itens()}
    mapa_ongs = {o["CNPJ_ID"]: o for o in listar_ongs()}
    mapa_doadores = {d["CPF_ID"]: d for d in listar_doadores()}
    mapa_intencoes = {i["ID_Intencao"]: i for i in listar_intencoes()}

    todos_pedidos = listar_pedidos()
    meus_pedidos = [p for p in todos_pedidos if p.get("ID_ONG") == session["ong_logada"]["CNPJ_ID"]]

    # 🔗 Injeta ID_Lista via intenção
    for p in meus_pedidos:
        intencao = mapa_intencoes.get(p.get("ID_Intencao"))
        if intencao:
            p["ID_Lista"] = intencao.get("ID_Lista")

    em_andamento = [p for p in meus_pedidos if p.get("status") == 0]
    finalizados = [p for p in meus_pedidos if p.get("status") == 1]
    cancelados = [p for p in meus_pedidos if p.get("status") == 2]

    def filtrar(lista):
        if not busca:
            return lista
        return [
            p for p in lista
            if busca in mapa_doadores.get(p.get("ID_Doador"), {}).get("nome", "").lower()
            or busca in mapa_listas.get(p.get("ID_Lista"), {}).get("titulo", "").lower()
        ]

    em_andamento, finalizados, cancelados = map(filtrar, [em_andamento, finalizados, cancelados])

    return render_template("pedidosONG.html",
        em_andamento=em_andamento,
        finalizados=finalizados,
        cancelados=cancelados,
        status_selecionado=status_selecionado,
        mapa_listas=mapa_listas,
        mapa_itens=mapa_itens,
        mapa_doadores=mapa_doadores,
        STATUS_MAP=STATUS_MAP,
        busca=busca,
        exibir_pedidos_itens=exibir_pedidos_itens
    )

@pedidos_ong_bp.route("/FinalizarPedido/<id>")
def finalizar_pedido(id):
    sucesso, msg = atualizar_status_pedido(id, 1)
    flash("✅ Pedido finalizado com sucesso!", "success") if sucesso  else flash(msg, "error")
    return redirect(url_for("pedidos_ong.pedidos_ong"))

@pedidos_ong_bp.route("/CancelarPedido/<id>")
def cancelar_pedido(id):
    sucesso, msg = atualizar_status_pedido(id, 2)
    flash("✅ Pedido cancelado com sucesso.", "success") if sucesso  else flash(msg, "error")
    return redirect(url_for("pedidos_ong.pedidos_ong"))
