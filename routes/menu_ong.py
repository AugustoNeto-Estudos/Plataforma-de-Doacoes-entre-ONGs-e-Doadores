from flask import Blueprint, render_template, session, redirect, flash, request
from dao.listas import inserir_lista
from dao.itensLista import inserir_lista_item
from dao.itens import exibir_itens
from dao.intencao_de_doacao import listar_intencoes
from dao.pedidos import listar_pedidos
import uuid

menu_ong_bp = Blueprint("menu_ong", __name__)

# Mapeamento reverso (string -> int)
STATUS_REVERSE = {
    "Pendente": 0,
    "Aprovado": 1,
    "Reprovado": 2,
    "Finalizado": 3
}

@menu_ong_bp.route("/MenuONG", methods=["GET", "POST"])
def menu_ong():
    ong = session.get("ong_logada")

    if not ong:
        flash("⚠️ Nenhuma ONG logada.")
        return redirect("/LoginONG")

    if not ong.get("status_conta", False):
        flash("🚫 Conta inativa. Aguarde liberação pela administração.")
        return redirect("/LoginONG")

    if ong.get("status_verificacao") != 1:
        flash("⏳ ONG ainda não aprovada.")
        return redirect("/LoginONG")

    if ong.get("cargo") == 1:
        flash("🔐 Acesso administrativo reconhecido.")
        return redirect("/Administracao")

    catalogo = exibir_itens() or []

    # Contagens para notificações
    todas_intencoes = listar_intencoes() or []
    minhas_intencoes = [i for i in todas_intencoes if i.get("ID_ONG") == ong.get("CNPJ_ID")]

    # 🔹 Converter status string -> int (se necessário)
    for i in minhas_intencoes:
        if isinstance(i.get("status"), str):
            i["status"] = STATUS_REVERSE.get(i["status"], -1)

    pendentes = [i for i in minhas_intencoes if i.get("status") == 0]
    aprovadas = [i for i in minhas_intencoes if i.get("status") == 1]

    todos_pedidos = listar_pedidos() or []
    meus_pedidos = [p for p in todos_pedidos if p.get("ID_ONG") == ong.get("CNPJ_ID")]
    pedidos_andamento = [p for p in meus_pedidos if p.get("status") == 0]

    # Criação rápida de lista
    if request.method == "POST" and request.form.get("acao") == "criar_lista_rapida":
        titulo = request.form.get("titulo")
        descricao = request.form.get("descricao")
        itens_selecionados = request.form.getlist("item_id")

        if not titulo or not itens_selecionados:
            flash("⚠️ Título e ao menos um item são obrigatórios.")
        else:
            id_lista = str(uuid.uuid4())[:8]
            sucesso, msg = inserir_lista(id_lista, titulo, ong.get("CNPJ_ID"), True, descricao)
            if sucesso:
                for item_id in itens_selecionados:
                    qtd = int(request.form.get(f"qtd_{item_id}", 1))
                    inserir_lista_item(id_lista, item_id, qtd)
                flash("✅ Lista criada com sucesso!")
                return redirect("/MenuONG")
            else:
                flash(msg)

    return render_template(
        "menuONG.html",
        ong=ong,
        catalogo=catalogo,
        num_pendentes=len(pendentes),
        num_aprovadas=len(aprovadas),
        num_pedidos=len(pedidos_andamento),
    )
