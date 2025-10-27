from flask import Blueprint, render_template, redirect, url_for, flash
from dao.listas import exibir_listas
from dao.ong import buscar_ong_por_id
from dao.feedback import buscar_feedbacks_por_ong

perfil_ong_doador_bp = Blueprint("perfil_ong_doador", __name__)

@perfil_ong_doador_bp.route("/PerfilONGDoador/<path:cnpj>")
def perfil_ong_doador(cnpj):
    # Buscar ONG pelo CNPJ
    ong = buscar_ong_por_id(cnpj)
    if not ong:
        flash("⚠️ ONG não encontrada.")
        return redirect(url_for("menu_doador.menu_doador"))

    # Buscar listas da ONG
    listas = exibir_listas() or []
    listas_ong = [l for l in listas if l.get("ID_ONG") == ong.get("CNPJ_ID")]

    # Calcular nota média da ONG
    feedbacks = buscar_feedbacks_por_ong(ong.get("CNPJ_ID"))
    if feedbacks:
        media_nota = round(sum(f["nota"] for f in feedbacks) / len(feedbacks), 1)
    else:
        media_nota = None

    return render_template("perfilONGDoador.html", ong=ong, listas=listas_ong, media_nota=media_nota)
