import unittest
from unittest.mock import patch
from app import app
import bcrypt

class LoginDoadorTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch("routes.login_doador.validar_email", return_value=True)
    @patch("routes.login_doador.listar_doadores")
    @patch("routes.login_doador.doador_esta_ativo", return_value=True)
    @patch("routes.login_doador.verificar_senha", return_value=True)
    def test_login_sucesso_usuario_comum(self, mock_senha, mock_ativo, mock_listar, mock_validar_email):
        mock_listar.return_value = [{
            "email": "teste@exemplo.com",
            "senha": "hash123",
            "cargo": 0,
            "CPF_ID": "12345678900"
        }]

        response = self.app.post("/LoginDoador", data={
            "email": "teste@exemplo.com",
            "senha": "senha123"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("/MenuDoador", response.request.path)

    @patch("routes.login_doador.validar_email", return_value=True)
    @patch("routes.login_doador.listar_doadores")
    @patch("routes.login_doador.doador_esta_ativo", return_value=True)
    @patch("routes.login_doador.verificar_senha", return_value=True)
    def test_login_sucesso_admin(self, mock_senha, mock_ativo, mock_listar, mock_validar_email):
        mock_listar.return_value = [{
            "email": "admin@exemplo.com",
            "senha": "hash123",
            "cargo": 1,
            "CPF_ID": "00000000000"
        }]

        response = self.app.post("/LoginDoador", data={
            "email": "admin@exemplo.com",
            "senha": "admin123"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Acesso administrativo reconhecido.", response.get_data(as_text=True))
        self.assertIn("/Administracao", response.request.path)

    def test_login_campos_vazios(self):
        response = self.app.post("/LoginDoador", data={
            "email": "",
            "senha": ""
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Email e senha são obrigatórios.", response.get_data(as_text=True))

    @patch("routes.login_doador.validar_email", return_value=False)
    def test_login_email_invalido(self, mock_validar_email):
        response = self.app.post("/LoginDoador", data={
            "email": "email_invalido",
            "senha": "senha"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Email inválido.", response.get_data(as_text=True))

    @patch("routes.login_doador.validar_email", return_value=True)
    @patch("routes.login_doador.listar_doadores", return_value=[])
    def test_login_credenciais_invalidas(self, mock_listar, mock_validar_email):
        response = self.app.post("/LoginDoador", data={
            "email": "naoexiste@exemplo.com",
            "senha": "senhaerrada"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Credenciais inválidas.", response.get_data(as_text=True))

    @patch("routes.login_doador.validar_email", return_value=True)
    @patch("routes.login_doador.listar_doadores")
    @patch("routes.login_doador.doador_esta_ativo", return_value=False)
    @patch("routes.login_doador.verificar_senha", return_value=True)
    def test_login_conta_inativa(self, mock_senha, mock_ativo, mock_listar, mock_validar_email):
        mock_listar.return_value = [{
            "email": "inativo@exemplo.com",
            "senha": "hash123",
            "cargo": 0,
            "CPF_ID": "99999999999"
        }]

        response = self.app.post("/LoginDoador", data={
            "email": "inativo@exemplo.com",
            "senha": "senha123"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Conta inativa.", response.get_data(as_text=True))

if __name__ == "__main__":
    unittest.main()
