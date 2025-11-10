import unittest
from unittest.mock import patch, MagicMock
from flask import Flask
from routes.login_doador import login_doador_bp
from routes.busca_cep import busca_cep_bp

class BuscaCepTestCase(unittest.TestCase):
    def setUp(self):
        app = Flask(__name__)
        app.secret_key = "test_secret"
        app.register_blueprint(busca_cep_bp)
        app.register_blueprint(login_doador_bp)
        self.client = app.test_client()
        self.app = app

    def test_api_localizacao_sem_endereco(self):
        response = self.client.get("/api/localizacao")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.get_json()["erro"], "Endereço não informado")

    @patch("routes.busca_cep.Nominatim.geocode")
    def test_api_localizacao_com_endereco_valido(self, mock_geocode):
        mock_location = MagicMock()
        mock_location.latitude = -23.5
        mock_location.longitude = -46.3
        mock_geocode.return_value = mock_location

        response = self.client.get("/api/localizacao?endereco=Rua A, Suzano")
        self.assertEqual(response.status_code, 200)
        self.assertIn("latitude", response.get_data(as_text=True))
        self.assertIn("longitude", response.get_data(as_text=True))

    @patch("routes.busca_cep.carregar_ongs", return_value=[
        {
            "CNPJ_ID": "123",
            "nome": "ONG X",
            "cep": "00000000",
            "descricao": "Teste"
        }
    ])
    @patch("routes.busca_cep.exibir_listas", return_value=[
        {"ID_ONG": "123", "ID_Lista": "L1", "status": True}
    ])
    @patch("routes.busca_cep.exibir_itens", return_value=[
        {"ID_Item": "I1", "categoria": "Alimento", "subcategoria": "Arroz"}
    ])
    @patch("routes.busca_cep.exibir_lista_itens", return_value=[
        {"ID_Item": "I1", "quantidade_necessaria": 5}
    ])
    def test_api_ong_detalhe_sucesso(self, mock_lista_itens, mock_itens, mock_listas, mock_ongs):
        response = self.client.get("/api/ong_detalhe/123")
        self.assertEqual(response.status_code, 200)
        self.assertIn("ONG X", response.get_data(as_text=True))
        self.assertIn("Alimento", response.get_data(as_text=True))

    @patch("routes.busca_cep.carregar_ongs", return_value=[])
    def test_api_ong_detalhe_nao_encontrada(self, mock_ongs):
        response = self.client.get("/api/ong_detalhe/999")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.get_json()["erro"], "ONG não encontrada")

if __name__ == "__main__":
    unittest.main()
