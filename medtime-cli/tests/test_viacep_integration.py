"""
Testes de integração da API ViaCEP.
"""

import pytest
import requests
from unittest.mock import patch, MagicMock
from src.viacep_api import ViaCEPAPI


class TestViaCEPAPI:
    """Testes para a integração com ViaCEP"""
    
    @patch('src.viacep_api.requests.get')
    def test_search_address_success(self, mock_get):
        """Testa busca de endereço com sucesso"""
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "cep": "01310-100",
            "logradouro": "Avenida Paulista",
            "bairro": "Bela Vista",
            "localidade": "São Paulo",
            "uf": "SP"
        }
        mock_get.return_value = mock_response
        
        resultado = ViaCEPAPI.search_address("01310-100")
        
        assert resultado is not None
        assert resultado["cep"] == "01310-100"
        assert resultado["logradouro"] == "Avenida Paulista"
        assert resultado["localidade"] == "São Paulo"
        assert mock_get.called
    
    @patch('src.viacep_api.requests.get')
    def test_search_address_not_found(self, mock_get):
        """Testa CEP não encontrado"""
        mock_response = MagicMock()
        mock_response.json.return_value = {"erro": True}
        mock_get.return_value = mock_response
        
        resultado = ViaCEPAPI.search_address("00000-000")
        
        assert resultado is None
    
    @patch('src.viacep_api.requests.get')
    def test_search_address_connection_error(self, mock_get):
        """Testa erro de conexão"""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection error")
        
        resultado = ViaCEPAPI.search_address("01310-100")
        
        assert resultado is None
    
    def test_search_address_invalid_cep(self):
        """Testa CEP inválido"""
        resultado = ViaCEPAPI.search_address("123")
        
        assert resultado is None
    
    def test_format_address(self):
        """Testa formatação do endereço"""
        address_data = {
            "cep": "01310-100",
            "logradouro": "Avenida Paulista",
            "bairro": "Bela Vista",
            "localidade": "São Paulo",
            "uf": "SP"
        }
        
        formatted = ViaCEPAPI.format_address(address_data)
        
        assert "01310-100" in formatted
        assert "Avenida Paulista" in formatted
        assert "São Paulo" in formatted
        assert "SP" in formatted