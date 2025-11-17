from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from dao.pedidos import listar_pedidos
from dao.itensPedido import exibir_pedidos_itens
from dao.listas import exibir_listas
from dao.itens import exibir_itens
from dao.ong import listar_ongs
from dao.intencao_de_doacao import listar_intencoes
from dao.feedback import buscar_feedbacks_por_doador   

pedidos_doador_bp = Blueprint("pedidos_doador", __name__)

STATUS_MAP = {
    0: "Em andamento",
    1: "Finalizado",
    2: "Cancelado"
}

@pedidos_doador_bp.route("/PedidosDoador", methods=["GET", "POST"])
def pedidos_doador():
    if "doador_logado" not in session:
        flash("Nenhum doador logado. Faça login para continuar.")
        return redirect(url_for("login_doador.login_doador"))

    id_doador = session["doador_logado"]["CPF_ID"]

    status_selecionado = request.form.get("status", "Todos")
    busca = request.form.get("busca", "").strip().lower()

    # Mapas auxiliares
    mapa_listas = {l["ID_Lista"]: l for l in exibir_listas()}
    mapa_itens = {i["ID_Item"]: i for i in exibir_itens()}
    mapa_ongs = {o["CNPJ_ID"]: o for o in listar_ongs()}
    mapa_intencoes = {i["ID_Intencao"]: i for i in listar_intencoes()}

    # Pedidos do doador
    todos_pedidos = listar_pedidos()
    meus_pedidos = [p for p in todos_pedidos if p.get("ID_Doador") == id_doador]

    # Injeta ID_Lista com base na intenção vinculada
    for pedido in meus_pedidos:
        intencao = mapa_intencoes.get(pedido.get("ID_Intencao"))
        if intencao:
            pedido["ID_Lista"] = intencao.get("ID_Lista")

    # Separar por status
    em_andamento = [p for p in meus_pedidos if p.get("status") == 0]
    finalizados = [p for p in meus_pedidos if p.get("status") == 1]
    cancelados = [p for p in meus_pedidos if p.get("status") == 2]

    # Filtro de busca
    def filtrar(lista):
        if not busca:
            return lista
        return [
            p for p in lista
            if busca in mapa_ongs.get(p.get("ID_ONG"), {}).get("nome", "").lower()
            or busca in mapa_listas.get(p.get("ID_Lista"), {}).get("titulo", "").lower()
        ]

    em_andamento, finalizados, cancelados = map(filtrar, [em_andamento, finalizados, cancelados])

    # Feedbacks já feitos pelo doador
    feedbacks = buscar_feedbacks_por_doador(id_doador) or []
    mapa_feedbacks = {fb["id_pedido"]: fb for fb in feedbacks if fb.get("id_pedido")}

    return render_template(
        "pedidosDoador.html",
        em_andamento=em_andamento,
        finalizados=finalizados,
        cancelados=cancelados,
        status_selecionado=status_selecionado,
        mapa_listas=mapa_listas,
        mapa_itens=mapa_itens,
        mapa_ongs=mapa_ongs,
        STATUS_MAP=STATUS_MAP,
        busca=busca,
        exibir_pedidos_itens=exibir_pedidos_itens,
        mapa_feedbacks=mapa_feedbacks
    )
