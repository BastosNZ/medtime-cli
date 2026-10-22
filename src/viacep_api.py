"""
Integração com a API ViaCEP para buscar informações de endereços.
ViaCEP: https://viacep.com.br
"""

import requests
from typing import Optional, Dict


class ViaCEPAPI:
    """Cliente para consumir a API ViaCEP"""
    
    BASE_URL = "https://viacep.com.br/ws"
    TIMEOUT = 5
    
    @staticmethod
    def search_address(cep: str) -> Optional[Dict]:
        """
        Busca informações de endereço pelo CEP.
        
        Args:
            cep: CEP no formato XXXXX-XXX ou XXXXXXXX
            
        Returns:
            Dict com endereço ou None se não encontrado/erro
            
        Exemplo:
            {
                'cep': '01310-100',
                'logradouro': 'Avenida Paulista',
                'bairro': 'Bela Vista',
                'localidade': 'São Paulo',
                'uf': 'SP'
            }
        """
        try:
            # Limpar CEP (remover hífens)
            cep_limpo = cep.replace("-", "").strip()
            
            # Validar tamanho
            if len(cep_limpo) != 8 or not cep_limpo.isdigit():
                raise ValueError("CEP deve conter 8 dígitos")
            
            # Fazer requisição
            url = f"{ViaCEPAPI.BASE_URL}/{cep_limpo}/json/"
            response = requests.get(url, timeout=ViaCEPAPI.TIMEOUT)
            response.raise_for_status()
            
            data = response.json()
            
            # Verificar se é um erro (CEP não encontrado)
            if "erro" in data:
                return None
            
            return data
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Erro ao consultar ViaCEP: {e}")
            return None
        except ValueError as e:
            print(f"❌ {e}")
            return None
    
    @staticmethod
    def format_address(address_data: Dict) -> str:
        """
        Formata os dados do endereço para exibição.
        
        Args:
            address_data: Dict com dados do endereço
            
        Returns:
            String formatada
        """
        return (
            f"📍 Endereço encontrado:\n"
            f"   CEP: {address_data.get('cep', 'N/A')}\n"
            f"   Rua: {address_data.get('logradouro', 'N/A')}\n"
            f"   Bairro: {address_data.get('bairro', 'N/A')}\n"
            f"   Cidade: {address_data.get('localidade', 'N/A')}\n"
            f"   Estado: {address_data.get('uf', 'N/A')}"
        )
