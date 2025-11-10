from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from itsdangerous import URLSafeTimedSerializer
from flask_mail import Mail, Message
from dao.conexao import criar_conexao
from psycopg2 import Error
import bcrypt
import time

recuperar_senha_bp = Blueprint('recuperar_senha', __name__, template_folder='../templates')

# Configuração do Mailtrap (coloque isso no seu app principal)
def configurar_mail(app):
    app.config['MAIL_SERVER'] = 'sandbox.smtp.mailtrap.io'
    app.config['MAIL_PORT'] = 587  # ou 2525 se 587 estiver bloqueada
    app.config['MAIL_USERNAME'] = '7afed2773a79b8'
    app.config['MAIL_PASSWORD'] = 'f75a12199e8159'
    app.config['MAIL_USE_TLS'] = True  # Criptografia pro e-mail
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_DEFAULT_SENDER'] = 'suporte@solidarihub.com'
    return Mail(app)

# Serializer para tokens
def gerar_token(email):
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    return serializer.dumps(email, salt='redefinir-senha')

def verificar_token(token, max_age=3600):
    serializer = URLSafeTimedSerializer(current_app.secret_key)
    try:
        return serializer.loads(token, salt='redefinir-senha', max_age=max_age)
    except Exception:
        return None

# Envio de e-mail via Mailtrap
def enviar_email_redefinicao(destinatario, link):
    mail = current_app.extensions.get('mail')
    assunto = "Redefinição de Senha - SolidariHub"
    corpo_html = f"""
    <html>
    <body>
      <h2>Redefinição de Senha</h2>
      <p>Recebemos uma solicitação para redefinir sua senha.</p>
      <p><a href="{link}">Clique aqui para redefinir sua senha</a></p>
      <p>Se você não solicitou isso, ignore este e-mail.</p>
    </body>
    </html>
    """
    msg = Message(subject=assunto, recipients=[destinatario], html=corpo_html)
    try:
        mail.send(msg)
        print("E-mail enviado com sucesso via Mailtrap!")
    except Exception as e:
        print("Erro ao enviar e-mail:", str(e))

# Função auxiliar para criptografar senha
def hash_senha(senha):
    return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode("utf-8").strip()

# Atualiza a senha no banco para ONG ou Doador
def atualizar_senha_usuario(email, nova_senha):
    senha_criptografada = hash_senha(nova_senha)
    conexao = criar_conexao()
    if not conexao:
        return False, "❌ Falha ao conectar ao banco."

    try:
        with conexao.cursor() as cursor:
            # Verifica se é ONG
            cursor.execute('SELECT "CNPJ_ID" FROM public."ong" WHERE email = %s', (email.strip().lower(),))
            resultado_ong = cursor.fetchone()

            if resultado_ong:
                cursor.execute('UPDATE public."ong" SET senha = %s WHERE email = %s', (senha_criptografada, email.strip().lower()))
                conexao.commit()
                return True, "✅ Senha da ONG atualizada com sucesso!"

            # Verifica se é Doador
            cursor.execute('SELECT "CPF_ID" FROM public."doador" WHERE email = %s', (email.strip().lower(),))
            resultado_doador = cursor.fetchone()

            if resultado_doador:
                cursor.execute('UPDATE public."doador" SET senha = %s WHERE email = %s', (senha_criptografada, email.strip().lower()))
                conexao.commit()
                return True, "✅ Senha do doador atualizada com sucesso!"

            return False, "⚠️ Usuário não encontrado."

    except Error as erro:
        return False, f"❌ Erro ao atualizar senha: {str(erro).strip()[:200]}"

    finally:
        conexao.close()

@recuperar_senha_bp.route('/recuperar_senha', methods=['GET', 'POST'])
def recuperar_senha():
    if request.method == 'POST':
        email = request.form['email']
        token = gerar_token(email)
        link = url_for('recuperar_senha.redefinir_senha', token=token, _external=True)
        enviar_email_redefinicao(email, link)
        flash('Um e-mail foi enviado com instruções para redefinir sua senha.')  ## Tem que no html e css colocar um objt para receber isto e renderizar ai aparece a msg pro user
        return redirect(url_for('recuperar_senha.recuperar_senha'))
 
    return render_template('recuperarSenha.html')

@recuperar_senha_bp.route('/redefinir_senha/<token>', methods=['GET', 'POST'])
def redefinir_senha(token):
    email = verificar_token(token)
    if not email:
        flash('Token inválido ou expirado.')
        return redirect(url_for('recuperar_senha.recuperar_senha'))

    if request.method == 'POST':
        nova_senha = request.form['senha']
        confirmar_senha = request.form['confirmar_senha']

        if not nova_senha or not confirmar_senha:
            flash("❌ Preencha todos os campos.")
            return redirect(url_for('recuperar_senha.redefinir_senha', token=token))

        if nova_senha != confirmar_senha:
            flash("❌ As senhas não coincidem.")
            return redirect(url_for('recuperar_senha.redefinir_senha', token=token))

        sucesso, mensagem = atualizar_senha_usuario(email, nova_senha)
        flash(mensagem)
        return redirect(url_for('home.index'))


    return render_template('redefinir_senha.html', token=token)
