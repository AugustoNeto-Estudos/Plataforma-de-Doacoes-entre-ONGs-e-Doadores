from flask import Blueprint, render_template, session, redirect, flash, request
from dao.listas import exibir_listas, inserir_lista, deletar_lista, atualizar_status_lista, atualizar_descricao_lista
from dao.itensLista import exibir_lista_itens, inserir_lista_item, atualizar_quantidade_item
from dao.itens import exibir_itens
import uuid

gerenciar_listas_ong_bp = Blueprint("gerenciar_listas_ong", __name__)

@gerenciar_listas_ong_bp.route("/GerenciarListasONG", methods=["GET", "POST"])
def gerenciar_listas_ong():
    # Sessão e validações
    ong = session.get("ong_logada")
    if not ong:
        flash("⚠️ Nenhuma ONG logada.")
        return redirect("/LoginONG")
    if not ong.get("status_conta", False):
        flash("🚫 Conta inativa.")
        return redirect("/LoginONG")
    if ong.get("status_verificacao") != 1:
        flash("⏳ ONG ainda não aprovada.")
        return redirect("/LoginONG")

    # Dados base
    listas = exibir_listas() or []
    catalogo = exibir_itens() or []
    mapa_itens = {i["ID_Item"]: f"{i['categoria']} - {i['subcategoria'] or 'Sem subcategoria'}" for i in catalogo}
    listas_ong = [l for l in listas if l.get("ID_ONG") == ong.get("CNPJ_ID")]

    # Ações de formulário (POST)
    if request.method == "POST":
        acao = request.form.get("acao")
        id_lista = request.form.get("id_lista")

        if acao == "excluir_lista":
            sucesso, msg = deletar_lista(id_lista)

        elif acao == "finalizar_lista":
            sucesso, msg = atualizar_status_lista(id_lista, False)

        elif acao == "reativar_lista":
            sucesso, msg = atualizar_status_lista(id_lista, True)

        elif acao == "atualizar_descricao":
            nova_desc = request.form.get("nova_descricao", "").strip()
            if not id_lista:
                sucesso, msg = False, "❌ Lista inválida."
            elif not nova_desc:
                sucesso, msg = False, "⚠️ Informe a nova descrição."
            else:
                sucesso, msg = atualizar_descricao_lista(id_lista, nova_desc)

        elif acao == "atualizar_quantidade":
            id_item = request.form.get("id_item")
            try:
                nova_qtd = int(request.form.get("nova_qtd", 1))
            except ValueError:
                nova_qtd = 1
            if not id_lista or not id_item:
                sucesso, msg = False, "❌ Lista ou item inválido."
            else:
                sucesso, msg = atualizar_quantidade_item(id_lista, id_item, max(nova_qtd, 1))

        elif acao == "adicionar_item":
            id_item = request.form.get("id_item")
            try:
                qtd = int(request.form.get("quantidade", 1))
            except ValueError:
                qtd = 1
            if not id_lista or not id_item:
                sucesso, msg = False, "❌ Lista ou item inválido."
            else:
                sucesso, msg = inserir_lista_item(id_lista, id_item, max(qtd, 1))

        elif acao == "criar_lista":
            titulo = request.form.get("titulo", "").strip()
            descricao = request.form.get("descricao", "").strip()
            itens = request.form.getlist("item_id")  # vindo do multiselect (Choices.js)
            if not titulo:
                sucesso, msg = False, "⚠️ O título da lista é obrigatório."
            elif not itens:
                sucesso, msg = False, "⚠️ Selecione ao menos um item."
            else:
                novo_id = str(uuid.uuid4())[:8]
                sucesso, msg = inserir_lista(novo_id, titulo, ong.get("CNPJ_ID"), True, descricao)
                if sucesso:
                    # Quantidade padrão 1; se quiser etapa 2 com quantidades, o HTML deve enviar qtd_{id_item}
                    for item_id in itens:
                        try:
                            qtd = int(request.form.get(f"qtd_{item_id}", 1))
                        except ValueError:
                            qtd = 1
                        inserir_lista_item(novo_id, item_id, max(qtd, 1))
                else:
                    # manter msg retornada
                    pass
        else:
            sucesso, msg = False, "❌ Ação desconhecida."

        flash(msg)
        return redirect("/GerenciarListasONG")

    # Itens por lista
    for lista in listas_ong:
        lista["itens"] = exibir_lista_itens(lista["ID_Lista"])

    # Filtros (GET)
    busca = request.args.get("busca", "").lower()
    filtro = request.args.get("filtro_status", "")

    if busca:
        listas_ong = [
            l for l in listas_ong
            if (busca in l.get("titulo", "").lower()) or (busca in l.get("descricao", "").lower())
        ]

    if filtro == "ativa":
        listas_ong = [l for l in listas_ong if l.get("status", True)]
    elif filtro == "finalizada":
        listas_ong = [l for l in listas_ong if not l.get("status", True)]

    return render_template(
        "gerenciarListasONG.html",
        ong=ong,
        listas=listas_ong,
        mapa_itens=mapa_itens,
        catalogo=catalogo
    )
