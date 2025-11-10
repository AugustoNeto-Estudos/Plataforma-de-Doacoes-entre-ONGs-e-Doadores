from flask import Blueprint, render_template, request, redirect, flash, session
from dao.ong import listar_ongs, cadastrar_ong, hash_senha
from Validadores import validar_email, validar_cnpj, validar_cep, validar_contato
import bcrypt

# Blueprint da rota de login/cadastro de ONG
login_ong_bp = Blueprint("login_ong", __name__)

# Função para verificar se a senha digitada bate com o hash salvo
def verificar_senha(senha_digitada, senha_hash):
    try:
        senha_hash = str(senha_hash).strip().replace("\n", "").replace(" ", "")
        return bcrypt.checkpw(senha_digitada.encode(), senha_hash.encode())
    except Exception:
        return False

# Rota principal para login e cadastro de ONG
@login_ong_bp.route("/LoginONG", methods=["GET", "POST"])
def login_ong():
    if request.method == "POST":
        acao = request.form.get("acao")  # Define se é login ou cadastro

        if acao == "login":
            email = request.form["email"]
            senha = request.form["senha"]

            # Valida campos obrigatórios
            if not email or not senha:
                flash("❌ Email e senha são obrigatórios.")
            elif not validar_email(email):
                flash("⚠️ Email inválido.")
            else:
                # Busca ONG pelo email
                ongs = listar_ongs()
                ong = next((u for u in ongs if u.get("email", "").strip().lower() == email), None)

                # Verifica senha e status da conta
                if ong and verificar_senha(senha, ong.get("senha", "")):
                    if ong.get("cargo") == 1:
                        flash("✅ Login de administrador reconhecido!")
                        session["ong_logada"] = ong
                        return redirect("/Administracao")
                    elif not ong.get("status_conta"):
                        flash("⚠️ Conta inativa. Aguarde liberação.")
                    elif ong.get("status_verificacao") != 1:
                        flash("⚠️ ONG ainda não aprovada.")
                    else:
                        session["ong_logada"] = ong
                        flash(f"✅ Bem-vindo(a), {ong.get('nome') or email}")
                        return redirect("/MenuONG")
                else:
                    flash("❌ Credenciais inválidas ou conta não encontrada.")

            # Após tentativa de login, volta para tela de login
            session["mostrar_cadastro"] = False

        elif acao == "cadastro":
            # Captura os dados do formulário
            cnpj = request.form["cnpj"]
            nome = request.form["nome"]
            cep = request.form["cep"]
            contato = request.form["contato"]
            email = request.form["email"]
            senha = request.form["senha"]
            descricao = request.form["descricao"]
            confirmar_senha = request.form["confirmar_senha"]

            erros = []

            # Valida campos obrigatórios e formatos
            if not cnpj or not nome or not email or not senha or not confirmar_senha:
                erros.append("CNPJ, Nome, Email e Senha são obrigatórios.")
            if not validar_cnpj(cnpj):
                erros.append("CNPJ inválido.")
            if cep and not validar_cep(cep):
                erros.append("CEP inválido.")
            if contato and not validar_contato(contato):
                erros.append("Contato inválido.")
            if not validar_email(email):
                erros.append("Email inválido.")
            if senha != confirmar_senha:
                erros.append("As senhas não coincidem.")

            if erros:
                # Exibe os erros e mantém tela de cadastro visível
                for erro in erros:
                    flash(f"❌ {erro}")
                session["mostrar_cadastro"] = True
            else:
                # Cadastra ONG e volta para tela de login
                senha_hash = hash_senha(senha)
                sucesso, msg = cadastrar_ong(
                    cnpj, nome, cep, contato, email, senha_hash,
                    status_verificacao=0,
                    status_conta=False,
                    descricao=descricao,
                    cargo=0
                )
                flash(msg)
                session["mostrar_cadastro"] = False
                if sucesso:
                    return redirect("/LoginONG")

    # Recupera flag para saber qual tela mostrar
    mostrar_cadastro = session.pop("mostrar_cadastro", False)
    return render_template("loginONG.html", mostrar_cadastro=mostrar_cadastro)
