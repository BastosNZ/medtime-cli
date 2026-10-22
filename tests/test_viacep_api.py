"""Testes da integração com a API ViaCEP (sempre com mock, nunca rede real)."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from src.viacep_api import ViaCEPAPI

ADDRESS = {
    "cep": "01310-100",
    "logradouro": "Avenida Paulista",
    "bairro": "Bela Vista",
    "localidade": "São Paulo",
    "uf": "SP",
}


def _mock_response(payload: dict) -> MagicMock:
    response = MagicMock()
    response.json.return_value = payload
    return response


class TestSearchAddress:
    """Testes de ``ViaCEPAPI.search_address``."""

    @patch("src.viacep_api.requests.get")
    def test_success(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(ADDRESS)

        result = ViaCEPAPI.search_address("01310-100")

        assert result == ADDRESS
        mock_get.assert_called_once_with(
            "https://viacep.com.br/ws/01310100/json/",
            timeout=ViaCEPAPI.TIMEOUT,
        )

    @patch("src.viacep_api.requests.get")
    def test_accepts_cep_without_separator(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response(ADDRESS)

        assert ViaCEPAPI.search_address("01310100") == ADDRESS

    @patch("src.viacep_api.requests.get")
    def test_not_found(self, mock_get: MagicMock) -> None:
        mock_get.return_value = _mock_response({"erro": "true"})

        assert ViaCEPAPI.search_address("99999-999") is None

    @patch("src.viacep_api.requests.get")
    def test_connection_error(self, mock_get: MagicMock) -> None:
        mock_get.side_effect = requests.exceptions.ConnectionError("sem rede")

        assert ViaCEPAPI.search_address("01310-100") is None

    @patch("src.viacep_api.requests.get")
    def test_timeout(self, mock_get: MagicMock) -> None:
        mock_get.side_effect = requests.exceptions.Timeout("tempo esgotado")

        assert ViaCEPAPI.search_address("01310-100") is None

    @patch("src.viacep_api.requests.get")
    def test_http_error(self, mock_get: MagicMock) -> None:
        response = MagicMock()
        response.raise_for_status.side_effect = requests.exceptions.HTTPError("500")
        mock_get.return_value = response

        assert ViaCEPAPI.search_address("01310-100") is None

    @patch("src.viacep_api.requests.get")
    def test_invalid_json(self, mock_get: MagicMock) -> None:
        response = MagicMock()
        response.json.side_effect = ValueError("resposta não é JSON")
        mock_get.return_value = response

        assert ViaCEPAPI.search_address("01310-100") is None

    @patch("src.viacep_api.requests.get")
    def test_unexpected_error_is_not_swallowed(self, mock_get: MagicMock) -> None:
        """Erros não previstos devem aparecer, não virar ``None`` silencioso."""
        mock_get.side_effect = TypeError("erro de programação")

        with pytest.raises(TypeError):
            ViaCEPAPI.search_address("01310-100")

    @pytest.mark.parametrize("cep", ["123", "", "0131010a", "013101000", "CEP"])
    @patch("src.viacep_api.requests.get")
    def test_invalid_cep_does_not_call_the_api(self, mock_get: MagicMock, cep: str) -> None:
        assert ViaCEPAPI.search_address(cep) is None
        mock_get.assert_not_called()


class TestCleanCep:
    """Testes de ``ViaCEPAPI.clean_cep``."""

    @pytest.mark.parametrize(
        ("raw", "expected"),
        [("01310-100", "01310100"), ("01310100", "01310100"), (" 01310-100 ", "01310100")],
    )
    def test_cleans_valid_cep(self, raw: str, expected: str) -> None:
        assert ViaCEPAPI.clean_cep(raw) == expected

    def test_rejects_invalid_cep(self) -> None:
        with pytest.raises(ValueError, match="CEP inválido"):
            ViaCEPAPI.clean_cep("123")


class TestFormatting:
    """Testes das funções de exibição."""

    def test_format_address(self) -> None:
        formatted = ViaCEPAPI.format_address(ADDRESS)

        assert "01310-100" in formatted
        assert "Avenida Paulista" in formatted
        assert "Bela Vista" in formatted
        assert "São Paulo" in formatted
        assert "SP" in formatted

    def test_format_address_with_missing_fields(self) -> None:
        assert "N/A" in ViaCEPAPI.format_address({})

    def test_short_address(self) -> None:
        assert ViaCEPAPI.short_address(ADDRESS) == ("Avenida Paulista, Bela Vista - São Paulo/SP")

    def test_short_address_without_street(self) -> None:
        assert ViaCEPAPI.short_address({"localidade": "Brasília", "uf": "DF"}) == "Brasília/DF"
