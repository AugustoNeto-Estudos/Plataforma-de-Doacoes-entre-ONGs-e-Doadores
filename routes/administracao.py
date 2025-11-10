from flask import Blueprint, render_template, request, redirect, flash, session
from dao.ong import listar_ongs, atualizar_status_ong, atualizar_status_verificacao_ong, excluir_ong
from dao.doador import listar_doadores, atualizar_status_doador, excluir_doador
from dao.itens import exibir_itens, inserir_item, deletar_item, atualizar_item
import requests
import uuid

admin_bp = Blueprint("admin", __name__)

def consultar_cnpj_brasilapi(cnpj):
    cnpj = ''.join(filter(str.isdigit, cnpj))  # remove pontos, barras e traços
    url = f"https://brasilapi.com.br/api/cnpj/v1/{cnpj}"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return True, response.json()
        else:
            return False, f"Erro {response.status_code}: {response.text}"
    except Exception as e:
        return False, f"Erro na requisição: {str(e)}"

@admin_bp.route("/Administracao", methods=["GET", "POST"])
def painel_admin():
    usuario = session.get("doador_logado") or session.get("ong_logada")
    if not usuario or usuario.get("cargo") != 1:
        flash("🚫 Acesso restrito. Esta página é exclusiva para administradores.")
        return redirect("/")

    # Ações de formulário
    if request.method == "POST":
        acao = request.form.get("acao")
        id = request.form.get("id")

        if acao == "aprovar_ong":
            sucesso, msg = atualizar_status_verificacao_ong(id, 1)
        elif acao == "pendente_ong":
            sucesso, msg = atualizar_status_verificacao_ong(id, 0)
        elif acao == "consultar_cnpj":
            sucesso, resultado = consultar_cnpj_brasilapi(id)
            if sucesso:
                dados_cnpj = resultado
                flash("✅ Dados públicos da ONG consultados com sucesso.")
            else:
                flash(f"❌ Falha ao consultar CNPJ: {resultado}")
                # Retorna dados mockados para não deixar modal vazio
                dados_cnpj = {
                    "razao_social": "ONG Exemplo Solidária",
                    "nome_fantasia": "Solidária Mock",
                    "descricao_situacao_cadastral": "INEXISTENTE",
                    "natureza_juridica": "Associação Privada",
                    "data_inicio_atividade": "0000-00-00",
                    "municipio": "Cidade Fictícia",
                    "uf": "XX"
                }

            # Renderiza a página com o modal aberto
            ongs = listar_ongs()
            doadores = listar_doadores()
            itens = exibir_itens()
            return render_template(
                "administracao.html",
                ongs=ongs,
                doadores=doadores,
                itens=itens,
                dados_cnpj=dados_cnpj,
                abrir_modal=True   # flag para o JS abrir modal
            )

        elif acao == "recusar_ong":
            sucesso, msg = atualizar_status_verificacao_ong(id, 2)
        elif acao == "ativar_ong":
            sucesso, msg = atualizar_status_ong(id, True)
        elif acao == "desativar_ong":
            sucesso, msg = atualizar_status_ong(id, False)
        elif acao == "excluir_ong":
            sucesso, msg = excluir_ong(id)
        elif acao == "ativar_doador":
            sucesso, msg = atualizar_status_doador(id, True)
        elif acao == "desativar_doador":
            sucesso, msg = atualizar_status_doador(id, False)
        elif acao == "excluir_doador":
            sucesso, msg = excluir_doador(id)
        elif acao == "atualizar_item":
            nova_cat = request.form.get("nova_categoria")
            nova_sub = request.form.get("nova_subcategoria")
            sucesso, msg = atualizar_item(id, nova_cat, nova_sub)
        elif acao == "excluir_item":
            sucesso, msg = deletar_item(id)
        elif acao == "inserir_item":
            categoria = request.form.get("categoria")
            subcategoria = request.form.get("subcategoria")
            if not categoria:
                flash("⚠️ A categoria é obrigatória.")
                return redirect("/Administracao")
            id_item = str(uuid.uuid4())[:8]
            sucesso, msg = inserir_item(id_item, categoria.strip(), subcategoria.strip() or None)
        else:
            sucesso, msg = False, "❌ Ação desconhecida."

        # Para todas as ações normais, mantém flash + redirect
        flash(msg)
        return redirect("/Administracao")

    # Dados para exibição (GET)
    ongs = listar_ongs()
    doadores = listar_doadores()
    itens = exibir_itens()

    # --- Filtros e busca (GET) ---
    busca_ong = request.args.get("busca_ong", "").lower()
    filtro_ong = request.args.get("filtro_ong", "")
    busca_doador = request.args.get("busca_doador", "").lower()
    filtro_doador = request.args.get("filtro_doador", "")

    if busca_ong:
        ongs = [o for o in ongs if busca_ong in o["nome"].lower() or busca_ong in o["email"].lower()]
    if filtro_ong == "ativa":
        ongs = [o for o in ongs if o["status_conta"]]
    elif filtro_ong == "inativa":
        ongs = [o for o in ongs if not o["status_conta"]]
    elif filtro_ong == "pendente":
        ongs = [o for o in ongs if o["status_verificacao"] == 0]
    elif filtro_ong == "aprovada":
        ongs = [o for o in ongs if o["status_verificacao"] == 1]
    elif filtro_ong == "recusada":
        ongs = [o for o in ongs if o["status_verificacao"] == 2]

    if busca_doador:
        doadores = [d for d in doadores if busca_doador in d["nome"].lower() or busca_doador in d["email"].lower()]
    if filtro_doador == "ativa":
        doadores = [d for d in doadores if d["status_conta"]]
    elif filtro_doador == "inativa":
        doadores = [d for d in doadores if not d["status_conta"]]

    return render_template("administracao.html", ongs=ongs, doadores=doadores, itens=itens)
