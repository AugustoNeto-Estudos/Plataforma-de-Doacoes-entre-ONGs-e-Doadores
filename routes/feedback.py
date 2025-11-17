from flask import Blueprint, request, redirect, url_for, flash, session, render_template
from dao.feedback import (
    criar_feedback, listar_feedbacks,
    buscar_feedbacks_por_doador
)

feedback_bp = Blueprint("feedback", __name__)

# Página para listar feedbacks (admin/debug)
@feedback_bp.route("/Feedbacks")
def feedbacks():
    feedbacks = listar_feedbacks()
    return render_template("administracao.html", feedbacks=feedbacks)

# Criar novo feedback (via modal em PedidosDoador)
@feedback_bp.route("/Feedback/Novo", methods=["POST"])
def novo_feedback():
    if "doador_logado" not in session:
        flash("É necessário estar logado como doador para avaliar.", "warning")
        return redirect(url_for("login_doador.login_doador"))

    id_ong = request.form.get("id_ong")
    id_doador = session["doador_logado"]["CPF_ID"]
    id_pedido = request.form.get("id_pedido")
    id_lista = request.form.get("id_lista")
    nota = request.form.get("nota")
    reacao = request.form.get("reacao")
    comentario = request.form.get("comentario")

    # Verifica se já existe feedback para este pedido
    feedbacks_existentes = buscar_feedbacks_por_doador(id_doador)
    if any(fb.get("id_pedido") == id_pedido for fb in feedbacks_existentes):
        flash("Você já avaliou este pedido.", "warning")
        return redirect(url_for("pedidos_doador.pedidos_doador"))

    try:
        nota = int(nota)
        reacao = (reacao == "true")
    except (ValueError, TypeError):
        flash("Dados inválidos na avaliação.", "error")
        return redirect(url_for("pedidos_doador.pedidos_doador"))

    sucesso = criar_feedback(id_ong, id_doador, id_pedido, id_lista, nota, reacao, comentario)

    if sucesso:
        flash("Avaliação registrada com sucesso.", "success")
    else:
        flash("Erro ao registrar avaliação.", "error")

    return redirect(url_for("pedidos_doador.pedidos_doador"))
