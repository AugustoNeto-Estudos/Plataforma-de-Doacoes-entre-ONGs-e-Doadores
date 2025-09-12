import streamlit as st
from psycopg2 import Error
from conexao import criar_conexao
import sys
import os

# Ajuste para importar funções do módulo dentro de /pages
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from item_BD import inserir_item, exibir_itens, consultar_item_id, atualizar_item, deletar_item

# ================== CONFIGURAÇÕES INICIAIS ==================
st.set_page_config(
    page_title="Gerenciamento de Itens - PostgreSQL",
    page_icon="📦",
    layout="centered"
)

st.title("📦 Painel de Gerenciamento de Itens")
st.write("Gerencie o catálogo de itens cadastrados no sistema.")

# ================== TESTAR CONEXÃO ==================
st.subheader("🔗 Testar Conexão com o Banco de Dados")
if st.button("🔄 Testar Conexão"):
    conexao = criar_conexao()
    if conexao:
        st.success("✅ Conexão estabelecida com sucesso!")
        conexao.close()
    else:
        st.error("❌ Não foi possível conectar ao banco.")

st.divider()

# ================== INSERIR ITEM ==================
st.subheader("🟢 Inserir Novo Item no Catálogo")
feedback_inserir = st.empty()

catalogo = ["Arroz", "Feijão", "Macarrão", "Cobertor", "Outros"]
with st.form(key="form_inserir"):
    escolha_catalogo = st.selectbox("Selecione o item do catálogo", catalogo)
    id_item = st.text_input("ID do Item")
    categoria = st.text_input("Categoria")
    subcategoria = st.text_input("Subcategoria (opcional)")
    descricao = None
    if escolha_catalogo == "Outros":
        descricao = st.text_area("Descreva o item")
    btn_inserir = st.form_submit_button("➕ Inserir Item")

if btn_inserir:
    if not id_item or not categoria:
        feedback_inserir.warning("⚠️ ID e Categoria são obrigatórios.")
    else:
        sucesso, msg = inserir_item(id_item, categoria, subcategoria if subcategoria else None)
        msg = str(msg)
        if sucesso:
            feedback_inserir.success(msg)
            if descricao:
                st.info(f"Descrição do item 'Outros': {descricao}")
        else:
            feedback_inserir.error(msg)

st.divider()

# ================== LISTAR ITENS ==================
st.subheader("📄 Listar Itens do Catálogo")
if st.button("📂 Exibir Itens"):
    itens = exibir_itens()
    if itens:
        st.success(f"✅ {len(itens)} itens encontrados!")
        st.table(itens)
    else:
        st.warning("⚠️ Nenhum item encontrado.")

st.divider()

# ================== CONSULTAR ITEM POR ID ==================
st.subheader("🔍 Consultar Item")
feedback_consulta = st.empty()
with st.form("form_consultar_item"):
    id_consulta = st.text_input("Digite o ID do Item para consultar")
    btn_consultar = st.form_submit_button("🔎 Consultar")

if btn_consultar:
    item = consultar_item_id(id_consulta)
    if item:
        feedback_consulta.success("✅ Item encontrado!")
        st.json(item)
    else:
        feedback_consulta.warning("⚠️ Nenhum item encontrado com esse ID.")

st.divider()

# ================== ATUALIZAR ITEM ==================
st.subheader("✏️ Atualizar Item")
feedback_atualizar = st.empty()
with st.form(key="form_atualizar"):
    id_update = st.text_input("ID do Item para atualizar")
    nova_categoria = st.text_input("Nova Categoria (opcional)")
    nova_subcategoria = st.text_input("Nova Subcategoria (opcional)")
    btn_atualizar = st.form_submit_button("🔄 Atualizar Item")

if btn_atualizar:
    sucesso, msg = atualizar_item(
        id_update,
        nova_categoria if nova_categoria else None,
        nova_subcategoria if nova_subcategoria else None
    )
    msg = str(msg)
    if sucesso:
        feedback_atualizar.success(msg)
    else:
        feedback_atualizar.error(msg)

st.divider()

# ================== DELETAR ITEM ==================
st.subheader("🗑️ Deletar Item")
feedback_deletar = st.empty()
with st.form(key="form_deletar"):
    id_delete = st.text_input("ID do Item para deletar")
    btn_deletar = st.form_submit_button("❌ Deletar Item")

if btn_deletar:
    sucesso, msg = deletar_item(id_delete)
    msg = str(msg)
    if sucesso:
        feedback_deletar.success(msg)
    else:
        feedback_deletar.error(msg)
