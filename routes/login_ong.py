from flask import Blueprint, render_template, request, redirect, flash, session
from dao.ong import listar_ongs, cadastrar_ong, hash_senha
from Validadores import validar_email, validar_cnpj, validar_cep, validar_contato
import bcrypt
 
login_ong_bp = Blueprint("login_ong", __name__)
 
def verificar_senha(senha_digitada, senha_hash):
    try:
        senha_hash = str(senha_hash).strip().replace("\n", "").replace(" ", "")
        return bcrypt.checkpw(senha_digitada.encode(), senha_hash.encode())
    except Exception:
        return False
 
@login_ong_bp.route("/LoginONG", methods=["GET", "POST"])
def login_ong():
    if request.method == "POST":
        acao = request.form.get("acao")
 
        if acao == "login":
            email = request.form["email"]
            senha = request.form["senha"]
 
            if not email or not senha:
                flash("❌ Email e senha são obrigatórios.")
            elif not validar_email(email):
                flash("⚠️ Email inválido.")
            else:
                ongs = listar_ongs()
                ong = next((u for u in ongs if u.get("email", "").strip().lower() == email), None)
 
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
 
        elif acao == "cadastro":
            cnpj = request.form["cnpj"]
            nome = request.form["nome"]
            cep = request.form["cep"]
            contato = request.form["contato"]
            email = request.form["email"]
            senha = request.form["senha"]
            descricao = request.form["descricao"]
 
            erros = []
            if not cnpj or not nome or not email or not senha:
                erros.append("CNPJ, Nome, Email e Senha são obrigatórios.")
            if not validar_cnpj(cnpj):
                erros.append("CNPJ inválido.")
            if cep and not validar_cep(cep):
                erros.append("CEP inválido.")
            if contato and not validar_contato(contato):
                erros.append("Contato inválido.")
            if not validar_email(email):
                erros.append("Email inválido.")
 
            if erros:
                for erro in erros:
                    flash(f"❌ {erro}")
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
                if sucesso:
                    return redirect("/LoginONG")
 
    return render_template("loginONG.html")