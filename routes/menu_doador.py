from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from dao.listas import exibir_listas, exibir_listas_por_ong
from dao.ong import listar_ongs, buscar_ong_por_id
from dao.itens import exibir_itens
from dao.itensLista import exibir_lista_itens
from dao.intencao_item import inserir_itens_intencao
from dao.intencao_de_doacao import inserir_intencao, listar_intencoes
from dao.pedidos import listar_pedidos
from dao.feedback import buscar_feedbacks_por_lista
from datetime import date
import uuid

menu_doador_bp = Blueprint("menu_doador", __name__)

@menu_doador_bp.route("/MenuDoador", methods=["GET", "POST"])
def menu_doador():
    if "doador_logado" not in session:
        flash("Nenhum doador logado. Faça login para continuar.")
        return redirect(url_for("login_doador.login_doador"))

    doador = session["doador_logado"]

    # Filtro de busca
    busca = request.args.get("busca", "").strip().lower()

    # Dados base
    listas = exibir_listas()
    mapa_ongs = {o["CNPJ_ID"]: o for o in listar_ongs()}
    mapa_itens = {i["ID_Item"]: i for i in exibir_itens()}

    todas_listas = exibir_listas()
    total_registros = len(todas_listas)

    page = int(request.args.get("page", 1))
    limit = 50
    start = (page - 1) * limit
    end = start + limit

    listas = todas_listas[start:end]

    mapa_ongs = {o["CNPJ_ID"]: o for o in listar_ongs()}  
    ongs_paginadas = listar_ongs()[start:end]             
    
    # Aplicar filtro de busca

    if busca:
        listas = [
            l for l in listas
            if busca in l["titulo"].lower()
            or busca in l["descricao"].lower()
            or busca in mapa_ongs.get(l["ID_ONG"], {}).get("nome", "").lower()
            or busca in mapa_ongs.get(l["ID_ONG"], {}).get("cep", "").lower()
        ]

    # Notificações
    intencoes = listar_intencoes()
    todos_pedidos = listar_pedidos()
    pendentes = len([i for i in intencoes if i["status"] == "Pendente" and i["ID_Doador"] == doador["CPF_ID"]])
    aprovadas = len([i for i in intencoes if i["status"] == "Aprovado" and i["ID_Doador"] == doador["CPF_ID"]])
    meus_pedidos = [p for p in todos_pedidos if p.get("ID_Doador") == doador["CPF_ID"]]
    pedidos_andamento = len([p for p in meus_pedidos if p.get("status") in (0, 2)])
    pedidos_finalizados = len([p for p in meus_pedidos if p.get("status")])

    # Modal de lista
    lista_modal, ong_modal = None, None
    comentarios_lista, likes_lista, dislikes_lista = {}, {}, {}

    if "abrir_modal" in request.args:
        id_lista = request.args.get("abrir_modal")
        lista_modal = next((l for l in todas_listas if str(l["ID_Lista"]) == str(id_lista)), None)
        if lista_modal:
            ong_modal = mapa_ongs.get(lista_modal["ID_ONG"])
            lista_modal["itens"] = exibir_lista_itens(lista_modal["ID_Lista"])

            feedbacks = buscar_feedbacks_por_lista(lista_modal["ID_Lista"])
            comentarios_lista[lista_modal["ID_Lista"]] = []
            likes_lista[lista_modal["ID_Lista"]] = 0
            dislikes_lista[lista_modal["ID_Lista"]] = 0

            for fb in feedbacks:
                if fb["reacao"]:
                    likes_lista[lista_modal["ID_Lista"]] += 1
                else:
                    dislikes_lista[lista_modal["ID_Lista"]] += 1

                comentarios_lista[lista_modal["ID_Lista"]].append({
                    "nome": fb.get("nome_doador", "Anônimo"),
                    "nota": fb.get("nota", 0),
                    "comentario": fb.get("comentario", ""),
                    "data": fb.get("data", "")
                })

    # Detalhes da ONG
    ong_detalhe, listas_ong_detalhe = None, []
    if "ver_ong" in request.args and lista_modal:
        ong_detalhe = buscar_ong_por_id(lista_modal["ID_ONG"])
        listas_ong_detalhe = exibir_listas_por_ong(lista_modal["ID_ONG"])
        for l in listas_ong_detalhe:
            l["itens"] = exibir_lista_itens(l["ID_Lista"])

    # Criar intenção de doação
    mensagem_menu, mensagem_modal = None, None
    if request.method == "POST":
        lista_id = request.form.get("lista_id")
        acao = request.form.get("acao")

        if acao == "confirmar_intencao":
            itens_doacao = {}
            for key, value in request.form.items():
                if key.startswith("qtd_") and value.strip():
                    try:
                        qtd = int(value)
                        if qtd > 0:
                            item_id = key.replace("qtd_", "")
                            itens_doacao[item_id] = qtd
                    except ValueError:
                        pass

            if not itens_doacao:
                mensagem_modal = "Selecione ao menos um item com quantidade válida."
            else:
                intencoes_existentes = [
                    i for i in listar_intencoes()
                    if i["ID_Doador"] == doador["CPF_ID"]
                    and i["ID_Lista"] == lista_id
                    and i["status"] in ("Pendente", "Aprovado", 0, 1)
                ]

                if intencoes_existentes:
                    mensagem_modal = "Você já possui uma intenção ativa para esta lista."
                else:
                    id_intencao = str(uuid.uuid4())[:8]
                    ong_id = next((l["ID_ONG"] for l in todas_listas if str(l["ID_Lista"]) == str(lista_id)), None)

                    if not ong_id:
                        mensagem_modal = "Erro: ONG da lista não encontrada."
                    else:
                        sucesso, msg = inserir_intencao(
                            id_intencao,
                            ong_id,
                            doador["CPF_ID"],
                            lista_id,
                            "Pendente",
                            date.today()
                        )

                        if sucesso:
                            itens_lista = [
                                {"id_item": item_id, "quantidade_pretendida": qtd, "observacao": None}
                                for item_id, qtd in itens_doacao.items()
                            ]
                            inserir_itens_intencao(id_intencao, itens_lista)
                            mensagem_menu = "Intenção registrada com sucesso."
                            return redirect(url_for("menu_doador.menu_doador", mensagem_menu=mensagem_menu))
                        else:
                            mensagem_modal = f"Erro ao registrar intenção: {msg}"

    return render_template("menuDoador.html",
        doador=doador,
        listas=listas,
        mapa_ongs=mapa_ongs,
        mapa_itens=mapa_itens,
        pendentes=pendentes,
        aprovadas=aprovadas,
        pedidos_andamento=pedidos_andamento,
        pedidos_finalizados=pedidos_finalizados,
        lista_modal=lista_modal,
        ong_modal=ong_modal,
        ong_detalhe=ong_detalhe,
        listas_ong_detalhe=listas_ong_detalhe,
        mensagem_menu=request.args.get("mensagem_menu"),
        mensagem_modal=mensagem_modal,
        busca=busca,
        comentarios_lista=comentarios_lista,
        likes_lista=likes_lista,
        dislikes_lista=dislikes_lista,
        page=page,
        total_registros=total_registros,
        limit=limit
    )
