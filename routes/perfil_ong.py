from flask import Blueprint, render_template, session, redirect, flash, request
from dao.listas import exibir_listas
from dao.feedback import buscar_feedbacks_por_ong

perfil_ong_bp = Blueprint("perfil_ong", __name__)

@perfil_ong_bp.route("/PerfilONG")
def perfil_ong():
    ong = session.get("ong_logada")

    if not ong:
        flash("Nenhuma ONG logada.")
        return redirect("/LoginONG")

    if not ong.get("status_conta", False):
        flash("Conta inativa. Aguarde liberação.")
        return redirect("/LoginONG")

    if ong.get("status_verificacao") != 1:
        flash("ONG ainda não aprovada.")
        return redirect("/LoginONG")

    listas = exibir_listas() or []
    listas_ong = [l for l in listas if l.get("ID_ONG") == ong.get("CNPJ_ID")]

    # Filtro de busca
    termo = request.args.get("busca", "").strip().lower()
    if termo:
        listas_ong = [
            l for l in listas_ong
            if termo in l.get("titulo", "").lower()
            or termo in l.get("descricao", "").lower()
        ]

    # Calcular nota média da ONG
    feedbacks = buscar_feedbacks_por_ong(ong.get("CNPJ_ID"))
    media_nota = round(sum(f["nota"] for f in feedbacks) / len(feedbacks), 1) if feedbacks else None

    return render_template(
        "perfilONG.html",
        ong=ong,
        listas=listas_ong,
        media_nota=media_nota,
        busca=termo
    )
