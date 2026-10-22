"""Integração com a API ViaCEP para buscar endereços.

ViaCEP: https://viacep.com.br
"""

import sys

import requests

Address = dict[str, str]


class ViaCEPAPI:
    """Cliente para consumir a API ViaCEP."""

    BASE_URL = "https://viacep.com.br/ws"
    TIMEOUT = 5

    @staticmethod
    def clean_cep(cep: str) -> str:
        """Remove separadores do CEP e valida o formato.

        Raises:
            ValueError: se o CEP não tiver exatamente 8 dígitos.
        """
        digits = str(cep).replace("-", "").replace(".", "").strip()
        if len(digits) != 8 or not digits.isdigit():
            raise ValueError(f"CEP inválido: {cep!r}. Informe 8 dígitos (ex.: 01310-100).")
        return digits

    @staticmethod
    def search_address(cep: str) -> Address | None:
        """Busca o endereço de um CEP.

        Args:
            cep: CEP no formato ``XXXXX-XXX`` ou ``XXXXXXXX``.

        Returns:
            Dicionário com os dados do endereço, ou ``None`` se o CEP for
            inválido, não existir ou a consulta falhar.

        Exemplo de retorno::

            {
                "cep": "01310-100",
                "logradouro": "Avenida Paulista",
                "bairro": "Bela Vista",
                "localidade": "São Paulo",
                "uf": "SP",
            }
        """
        try:
            digits = ViaCEPAPI.clean_cep(cep)
            url = f"{ViaCEPAPI.BASE_URL}/{digits}/json/"
            response = requests.get(url, timeout=ViaCEPAPI.TIMEOUT)
            response.raise_for_status()
            data = response.json()
        except requests.exceptions.RequestException as exc:
            print(f"Erro ao consultar a ViaCEP: {exc}", file=sys.stderr)
            return None
        except ValueError as exc:
            # CEP malformado ou resposta que não é um JSON válido.
            print(f"Erro: {exc}", file=sys.stderr)
            return None

        # A ViaCEP responde 200 com {"erro": true} quando o CEP não existe.
        if data.get("erro"):
            return None

        return data

    @staticmethod
    def format_address(address_data: Address) -> str:
        """Formata os dados do endereço para exibição no terminal."""
        return (
            "Endereço encontrado:\n"
            f"  CEP:     {address_data.get('cep', 'N/A')}\n"
            f"  Rua:     {address_data.get('logradouro', 'N/A')}\n"
            f"  Bairro:  {address_data.get('bairro', 'N/A')}\n"
            f"  Cidade:  {address_data.get('localidade', 'N/A')}\n"
            f"  Estado:  {address_data.get('uf', 'N/A')}"
        )

    @staticmethod
    def short_address(address_data: Address) -> str:
        """Resume o endereço em uma linha (``Rua, Bairro - Cidade/UF``)."""
        parts = [
            address_data.get("logradouro", ""),
            address_data.get("bairro", ""),
        ]
        line = ", ".join(part for part in parts if part)
        city = address_data.get("localidade", "")
        uf = address_data.get("uf", "")
        if city:
            line = f"{line} - {city}/{uf}" if line else f"{city}/{uf}"
        return line
