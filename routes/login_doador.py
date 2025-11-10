from flask import Blueprint, render_template, request, redirect, flash, session
from dao.doador import listar_doadores, cadastrar_doador, doador_esta_ativo, hash_senha
from Validadores import validar_email, validar_cpf, validar_contato
import bcrypt
import time

# Blueprint da rota de login/cadastro de doador
login_doador_bp = Blueprint("login_doador", __name__)

# Função para verificar se a senha digitada bate com o hash salvo
def verificar_senha(senha_digitada, senha_hash):
    try:
        senha_hash = str(senha_hash).strip().replace("\n", "").replace(" ", "")
        return bcrypt.checkpw(senha_digitada.encode(), senha_hash.encode())
    except Exception:
        return False

# Rota de login do doador
@login_doador_bp.route("/LoginDoador", methods=["GET", "POST"])
def login_doador():
    if request.method == "POST":
        email = request.form["email"]
        senha = request.form["senha"]

        # Valida campos obrigatórios
        if not email or not senha:
            flash("❌ Email e senha são obrigatórios.")
        elif not validar_email(email):
            flash("⚠️ Email inválido.")
        else:
            # Busca doador pelo email
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

        # Após tentativa de login, volta para tela de login
        session["mostrar_cadastro"] = False

    # Recupera flag para saber qual tela mostrar
    mostrar_cadastro = session.pop("mostrar_cadastro", False)
    return render_template("loginDoador.html", mostrar_cadastro=mostrar_cadastro)

# Rota de cadastro do doador
@login_doador_bp.route("/CadastroDoador", methods=["GET", "POST"])
def cadastro_doador():
    if request.method == "POST":
        # Captura os dados do formulário
        cpf = request.form["cpf"]
        nome = request.form["nome"]
        email = request.form["email"]
        contato = request.form["contato"]
        senha = request.form["senha"]
        confirmar_senha = request.form["confirmar_senha"]

        erros = []

        # Valida campos obrigatórios e formatos
        if not cpf or not nome or not email or not senha or not confirmar_senha:
            erros.append("Todos os campos obrigatórios devem ser preenchidos.")
        if not validar_cpf(cpf):
            erros.append("CPF inválido.")
        if not validar_email(email):
            erros.append("Email inválido.")
        if contato and not validar_contato(contato):
            erros.append("Contato inválido.")
        if senha != confirmar_senha:
            erros.append("As senhas não coincidem.")

        if erros:
            # Exibe os erros e mantém tela de cadastro visível
            for erro in erros:
                flash(f"❌ {erro}")
            session["mostrar_cadastro"] = True
        else:
            # Cadastra doador e volta para tela de login
            senha_hash = hash_senha(senha)
            sucesso, msg = cadastrar_doador(
                cpf, nome, email, contato, senha_hash,
                status_conta=True, cargo=0  # 0 = usuário comum
            )
            flash(msg)
            session["mostrar_cadastro"] = False
            if sucesso:
                return redirect("/LoginDoador")

    # Recupera flag para saber qual tela mostrar
    mostrar_cadastro = session.pop("mostrar_cadastro", False)
    return render_template("loginDoador.html", mostrar_cadastro=mostrar_cadastro)
