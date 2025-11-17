from flask import Flask
from routes.home import home_bp
from routes.login_doador import login_doador_bp
from routes.login_ong import login_ong_bp
from routes.recuperar_senha import recuperar_senha_bp, configurar_mail
from routes.administracao import admin_bp
from routes.busca_cep import busca_cep_bp
from routes.menu_doador import menu_doador_bp
from routes.menu_ong import menu_ong_bp
from routes.perfil_ong import perfil_ong_bp
from routes.perfil_ong_doador import perfil_ong_doador_bp
from routes.gerenciar_listas_ong import gerenciar_listas_ong_bp
from routes.intencoes_doador import intencoes_doador_bp
from routes.intencoes_ong import intencoes_ong_bp
from routes.pedidos_doador import pedidos_doador_bp
from routes.pedidos_ONG import pedidos_ong_bp
from routes.feedback import feedback_bp
from routes.termos import termos_bp

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"

mail = configurar_mail(app)
app.extensions['mail'] = mail

# Registro dos blueprints
app.register_blueprint(home_bp)
app.register_blueprint(login_doador_bp)
app.register_blueprint(login_ong_bp)
app.register_blueprint(recuperar_senha_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(busca_cep_bp)
app.register_blueprint(menu_doador_bp)
app.register_blueprint(menu_ong_bp)
app.register_blueprint(termos_bp)
app.register_blueprint(perfil_ong_bp)
app.register_blueprint(perfil_ong_doador_bp)
app.register_blueprint(gerenciar_listas_ong_bp)
app.register_blueprint(intencoes_doador_bp)
app.register_blueprint(intencoes_ong_bp)
app.register_blueprint(pedidos_doador_bp)
app.register_blueprint(pedidos_ong_bp)
app.register_blueprint(feedback_bp)

if __name__ == "__main__":
    app.run(debug=True)
