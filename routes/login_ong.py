from flask import Blueprint, render_template, request, redirect, flash, session
from dao.ong import listar_ongs, cadastrar_ong, hash_senha
from Validadores import validar_email, validar_cnpj, validar_cep, validar_contato
from routes.administracao import consultar_cnpj_brasilapi
import bcrypt

login_ong_bp = Blueprint("login_ong", __name__)

# Verifica se a senha digitada corresponde ao hash salvo
def verificar_senha(senha_digitada, senha_hash):
    try:
        senha_hash = str(senha_hash).strip().replace("\n", "").replace(" ", "")
        return bcrypt.checkpw(senha_digitada.encode(), senha_hash.encode())
    except Exception:
        return False

# Login e cadastro de ONG
@login_ong_bp.route("/LoginONG", methods=["GET", "POST"])
def login_ong():
    if request.method == "POST":
        acao = request.form.get("acao")

        # Login
        if acao == "login":
            email = request.form.get("email", "").strip().lower()
            senha = request.form.get("senha", "")

            if not email or not senha:
                flash("Email e senha são obrigatórios.")
            elif not validar_email(email):
                flash("Email inválido.")
            else:
                ongs = listar_ongs()
                ong = next((u for u in ongs if u.get("email", "").strip().lower() == email), None)

                if ong and verificar_senha(senha, ong.get("senha", "")):
                    if ong.get("cargo") == 1:
                        flash("Login de administrador reconhecido.")
                        session["ong_logada"] = ong
                        return redirect("/Administracao")
                    elif not ong.get("status_conta"):
                        flash("Conta inativa. Aguarde liberação.")
                    elif ong.get("status_verificacao") != 1:
                        flash("ONG ainda não aprovada.")
                    else:
                        session["ong_logada"] = ong
                        flash(f"Bem-vindo(a), {ong.get('nome') or email}")
                        return redirect("/MenuONG")
                else:
                    flash("Credenciais inválidas ou conta não encontrada.")

            session["mostrar_cadastro"] = False

        # Cadastro
        elif acao == "cadastro":
            cnpj = request.form.get("cnpj", "").strip()
            nome = request.form.get("nome", "").strip()
            cep = request.form.get("cep", "").strip()
            contato = request.form.get("contato", "").strip()
            email = request.form.get("email", "").strip()
            senha = request.form.get("senha", "")
            descricao = request.form.get("descricao", "").strip()
            confirmar_senha = request.form.get("confirmar_senha", "")

            erros = []

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

            ongs_existentes = listar_ongs()
            email_normalizado = email.lower()
            if any(o.get("email", "").strip().lower() == email_normalizado for o in ongs_existentes):
                erros.append("Já existe uma ONG cadastrada com este e-mail.")

            sucesso_cnae, dados_cnpj = consultar_cnpj_brasilapi(cnpj)
            if not sucesso_cnae:
                erros.append("Não foi possível validar o CNPJ na Receita Federal.")
            elif not str(dados_cnpj.get("cnae_fiscal", "")).startswith(("94", "88")):
                erros.append("O CNPJ informado não pertence a uma organização associativa (CNAE fora da sessão 94 ou 88).")

            if erros:
                for erro in erros:
                    flash(erro)
                session["mostrar_cadastro"] = True
            else:
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

    mostrar_cadastro = session.pop("mostrar_cadastro", False)
    return render_template("loginONG.html", mostrar_cadastro=mostrar_cadastro)
