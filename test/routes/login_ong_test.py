import unittest
from unittest.mock import patch
from app import app
import bcrypt

class LoginOngTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    @patch("routes.login_ong.validar_email", return_value=True)
    @patch("routes.login_ong.listar_ongs")
    @patch("routes.login_ong.verificar_senha", return_value=True)
    def test_login_sucesso_admin(self, mock_senha, mock_listar, mock_validar_email):
        mock_listar.return_value = [{
            "email": "admin@ong.org",
            "senha": "hash123",
            "cargo": 1,
            "status_conta": True,
            "status_verificacao": 1
        }]

        response = self.app.post("/LoginONG", data={
            "acao": "login",
            "email": "admin@ong.org",
            "senha": "admin123"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Login de administrador reconhecido!", response.get_data(as_text=True))
        self.assertIn("/Administracao", response.request.path)

    @patch("routes.login_ong.validar_email", return_value=True)
    @patch("routes.login_ong.listar_ongs")
    @patch("routes.login_ong.verificar_senha", return_value=True)
    def test_login_sucesso_usuario_comum(self, mock_senha, mock_listar, mock_validar_email):
        mock_listar.return_value = [{
            "email": "ong@ong.org",
            "senha": "hash123",
            "cargo": 0,
            "status_conta": True,
            "status_verificacao": 1,
            "nome": "ONG Teste"
        }]

        response = self.app.post("/LoginONG", data={
            "acao": "login",
            "email": "ong@ong.org",
            "senha": "senha123"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Bem-vindo(a), ONG Teste", response.get_data(as_text=True))
        self.assertIn("/MenuONG", response.request.path)

    def test_login_campos_vazios(self):
        response = self.app.post("/LoginONG", data={
            "acao": "login",
            "email": "",
            "senha": ""
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Email e senha são obrigatórios.", response.get_data(as_text=True))

    @patch("routes.login_ong.validar_email", return_value=False)
    def test_login_email_invalido(self, mock_validar_email):
        response = self.app.post("/LoginONG", data={
            "acao": "login",
            "email": "email_invalido",
            "senha": "senha"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Email inválido.", response.get_data(as_text=True))

    @patch("routes.login_ong.validar_email", return_value=True)
    @patch("routes.login_ong.listar_ongs", return_value=[])
    def test_login_credenciais_invalidas(self, mock_listar, mock_validar_email):
        response = self.app.post("/LoginONG", data={
            "acao": "login",
            "email": "naoexiste@ong.org",
            "senha": "senhaerrada"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Credenciais inválidas ou conta não encontrada.", response.get_data(as_text=True))

    @patch("routes.login_ong.validar_cnpj", return_value=False)
    def test_cadastro_cnpj_invalido(self, mock_cnpj):
        response = self.app.post("/LoginONG", data={
            "acao": "cadastro",
            "cnpj": "00000000000000",
            "nome": "ONG Teste",
            "cep": "00000000",
            "contato": "11999999999",
            "email": "teste@ong.org",
            "senha": "123456",
            "confirmar_senha": "123456",
            "descricao": "Descrição"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("CNPJ inválido.", response.get_data(as_text=True))

    @patch("routes.login_ong.validar_cnpj", return_value=True)
    @patch("routes.login_ong.validar_email", return_value=True)
    @patch("routes.login_ong.validar_cep", return_value=True)
    @patch("routes.login_ong.validar_contato", return_value=True)
    @patch("routes.login_ong.cadastrar_ong", return_value=(True, "Cadastro realizado com sucesso"))
    @patch("routes.login_ong.hash_senha", return_value="hash123")
    def test_cadastro_sucesso(self, mock_hash, mock_cadastrar, mock_contato, mock_cep, mock_email, mock_cnpj):
        response = self.app.post("/LoginONG", data={
            "acao": "cadastro",
            "cnpj": "12345678000199",
            "nome": "ONG Teste",
            "cep": "08690000",
            "contato": "11999999999",
            "email": "teste@ong.org",
            "senha": "123456",
            "confirmar_senha": "123456",
            "descricao": "Descrição"
        }, follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Cadastro realizado com sucesso", response.get_data(as_text=True))

if __name__ == "__main__":
    unittest.main()
