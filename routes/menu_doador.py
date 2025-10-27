from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from dao.listas import exibir_listas, exibir_listas_por_ong
from dao.ong import listar_ongs, buscar_ong_por_id
from dao.itens import exibir_itens
from dao.itensLista import exibir_lista_itens
from dao.intencao_item import inserir_itens_intencao
from dao.intencao_de_doacao import inserir_intencao, listar_intencoes, verificar_intencao_existente
from dao.pedidos import listar_pedidos
from dao.feedback import buscar_feedbacks_por_lista
from datetime import date
import uuid

menu_doador_bp = Blueprint("menu_doador", __name__)

@menu_doador_bp.route("/MenuDoador", methods=["GET", "POST"])
def menu_doador():
    if "doador_logado" not in session:
        flash("⚠️ Nenhum doador logado. Faça login para continuar.")
        return redirect(url_for("login_doador.login_doador"))

    doador = session["doador_logado"]

    # 🔍 Filtro de busca
    busca = request.args.get("busca", "").strip().lower()

    # 🔍 Carregar dados base
    listas = exibir_listas()
    mapa_ongs = {o["CNPJ_ID"]: o for o in listar_ongs()}
    mapa_itens = {i["ID_Item"]: i for i in exibir_itens()}

    # 🔍 Aplicar filtro de busca
    if busca:
        listas = [
            l for l in listas
            if busca in l["titulo"].lower()
            or busca in l["descricao"].lower()
            or busca in mapa_ongs.get(l["ID_ONG"], {}).get("nome", "").lower()
            or busca in mapa_ongs.get(l["ID_ONG"], {}).get("cep", "").lower()
        ]

    # 🔔 Notificações
    intencoes = listar_intencoes()
    #print("DEBUG INTENCOES:", intencoes)
    todos_pedidos = listar_pedidos()
    pendentes = len([i for i in intencoes if i["status"] == "Pendente" and i["ID_Doador"] == doador["CPF_ID"]])
    aprovadas = len([i for i in intencoes if i["status"] == "Aprovado" and i["ID_Doador"] == doador["CPF_ID"]])
    meus_pedidos = [p for p in todos_pedidos if p.get("ID_Doador") == doador["CPF_ID"]]
    pedidos_andamento = len([p for p in meus_pedidos if p.get("status") in (0, 1, 2)])

    # 🔹 Modal de lista
    lista_modal = None
    ong_modal = None
    comentarios_lista = {}
    likes_lista = {}
    dislikes_lista = {}

    if "abrir_modal" in request.args:
        id_lista = request.args.get("abrir_modal")
        lista_modal = next((l for l in listas if str(l["ID_Lista"]) == str(id_lista)), None)
        if lista_modal:
            ong_modal = mapa_ongs.get(lista_modal["ID_ONG"])

             # 🔹 Carregar itens da lista
            lista_modal["itens"] = exibir_lista_itens(lista_modal["ID_Lista"])

            # 🔹 Buscar feedbacks da lista
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
                    "nome": fb.get("nome_doador", "Anônimo"),  # 👈 pega o nome do JOIN
                    "nota": fb.get("nota", 0),
                    "comentario": fb.get("comentario", ""),
                    "data": fb.get("data", "")
                })

    # 🔹 Ver detalhes da ONG
    ong_detalhe = None
    listas_ong_detalhe = []
    if "ver_ong" in request.args and lista_modal:
        ong_detalhe = buscar_ong_por_id(lista_modal["ID_ONG"])
        listas_ong_detalhe = exibir_listas_por_ong(lista_modal["ID_ONG"])
        for l in listas_ong_detalhe:
            l["itens"] = exibir_lista_itens(l["ID_Lista"])

    # 🔹 Criar intenção de doação
    mensagem_menu = None
    mensagem_modal = None
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
                    except:
                        pass

            if not itens_doacao:
                mensagem_modal = "⚠️ Selecione ao menos um item com quantidade válida."
            else:
                # 1. Verificar se já existe intenção pendente
                tem_intencao, msg_verificacao = verificar_intencao_existente(doador["CPF_ID"], lista_id)
                
                if tem_intencao:
                    mensagem_modal = "⚠️ Você já possui uma intenção de doação pendente para esta lista."
                else:
                    # 2. Gerar dados necessários
                    id_intencao = str(uuid.uuid4())[:8] # Gera um ID de 8 caracteres
                    ong_id = next((l["ID_ONG"] for l in listas if str(l["ID_Lista"]) == str(lista_id)), None)
                    
                    if not ong_id:
                        mensagem_modal = "❌ Erro: ONG da lista não encontrada."
                    else:
                        # 3. Chamar a função com todos os 6 argumentos
                        sucesso, msg = inserir_intencao(
                            id_intencao,
                            ong_id,
                            doador["CPF_ID"],
                            lista_id,
                            "Pendente", # Status inicial
                            date.today()
                        )
                        
                        if sucesso:
                            # Montar lista de dicionários no formato esperado
                            itens_lista = []
                            for item_id, qtd in itens_doacao.items():
                                itens_lista.append({
                                    "id_item": item_id,
                                    "quantidade_pretendida": qtd,
                                    "observacao": None
                                })

                            # Inserir todos de uma vez
                            inserir_itens_intencao(id_intencao, itens_lista)

                            mensagem_menu = "✅ Intenção registrada com sucesso!"
                            return redirect(url_for("menu_doador.menu_doador", mensagem_menu=mensagem_menu))

                        else:
                            mensagem_modal = f"❌ Erro ao registrar intenção: {msg}"

    return render_template("menuDoador.html",
        doador=doador,
        listas=listas,
        mapa_ongs=mapa_ongs,
        mapa_itens=mapa_itens,
        pendentes=pendentes,
        aprovadas=aprovadas,
        pedidos_andamento=pedidos_andamento,
        lista_modal=lista_modal,
        ong_modal=ong_modal,
        ong_detalhe=ong_detalhe,
        listas_ong_detalhe=listas_ong_detalhe,
        mensagem_menu=request.args.get("mensagem_menu"),
        mensagem_modal=mensagem_modal,
        busca=busca,
        comentarios_lista=comentarios_lista,
        likes_lista=likes_lista,
        dislikes_lista=dislikes_lista
    )
