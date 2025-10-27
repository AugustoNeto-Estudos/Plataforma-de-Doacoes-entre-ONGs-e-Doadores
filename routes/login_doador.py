from flask import Blueprint, render_template, request, redirect, flash, session
from dao.doador import listar_doadores, cadastrar_doador, doador_esta_ativo, hash_senha
from Validadores import validar_email, validar_cpf, validar_contato
import bcrypt
import time
 
login_doador_bp = Blueprint("login_doador", __name__)
 
def verificar_senha(senha_digitada, senha_hash):
    try:
        senha_hash = str(senha_hash).strip().replace("\n", "").replace(" ", "")
        return bcrypt.checkpw(senha_digitada.encode(), senha_hash.encode())
    except Exception:
        return False
 
@login_doador_bp.route("/LoginDoador", methods=["GET", "POST"])
def login_doador():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]
 
        if not email or not senha:
            flash("❌ Email e senha são obrigatórios.")
        elif not validar_email(email):
            flash("⚠️ Email inválido.")
        else:
            doadores = listar_doadores()
            for doador in doadores:
                if doador["email"] == email and verificar_senha(senha, doador["senha"]):
                    if not doador_esta_ativo(email):
                        flash("⚠️ Conta inativa.")
                        break
 
                    session["doador_logado"] = doador
                    flash("✅ Login realizado com sucesso!")
 
                    if doador.get("cargo") == 1:
                        flash("🔐 Acesso administrativo reconhecido.")
                        return redirect("/Administracao")
 
                    time.sleep(2)
                    return redirect("/MenuDoador")
 
            else:
                flash("❌ Credenciais inválidas.")
 
    return render_template("loginDoador.html")
 
@login_doador_bp.route("/CadastroDoador", methods=["GET", "POST"])
def cadastro_doador():
    if request.method == "POST":
        cpf = request.form["cpf"]
        nome = request.form["nome"]
        email = request.form["email"]
        contato = request.form["contato"]
        senha = request.form["senha"]
 
        erros = []
        if not cpf or not nome or not email or not senha:
            erros.append("Todos os campos obrigatórios devem ser preenchidos.")
        if not validar_cpf(cpf):
            erros.append("CPF inválido.")
        if not validar_email(email):
            erros.append("Email inválido.")
        if contato and not validar_contato(contato):
            erros.append("Contato inválido.")
 
        if erros:
            for erro in erros:
                flash(f"❌ {erro}")
        else:
            senha_hash = hash_senha(senha)
            sucesso, msg = cadastrar_doador(cpf, nome, email, contato, senha_hash, status_conta=True, cargo=0) # 0 user comum, 1 User adm
            flash(msg)
            if sucesso:
                return redirect("/LoginDoador")
 
    return render_template("loginDoador.html")