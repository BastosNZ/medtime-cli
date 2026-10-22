# MedTime

Aplicação de linha de comando para registrar, listar e remover lembretes de
medicamentos, ajudando a não esquecer os horários corretos.

Projeto acadêmico — Engenharia de Software, UniCEUB.

## Requisitos

- Python 3.11 ou superior

## Instalação

```bash
git clone https://github.com/BastosNZ/medtime-cli.git
cd medtime-cli
python -m venv .venv
# Linux/macOS
source .venv/bin/activate
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

pip install -r requirements.txt
```

## Uso

Todos os comandos são executados a partir da raiz do repositório:

```bash
python -m src.main --help
```

### Registrar um medicamento

```bash
$ python -m src.main add Dipirona 8:05
Medicamento adicionado: Dipirona às 08:05.
```

O horário é validado e normalizado para o formato `HH:MM`.

### Listar os medicamentos

A listagem sai ordenada por horário:

```bash
$ python -m src.main list
08:05  Dipirona
22:00  Losartana
```

### Remover um medicamento

A busca pelo nome não diferencia maiúsculas de minúsculas:

```bash
$ python -m src.main remove losartana
Medicamento removido: Losartana.
```

### Consultar um endereço pelo CEP

Integração com a API pública [ViaCEP](https://viacep.com.br) (requer internet):

```bash
$ python -m src.main cep 01310-100
Endereço encontrado:
  CEP:     01310-100
  Rua:     Avenida Paulista
  Bairro:  Bela Vista
  Cidade:  São Paulo
  Estado:  SP
```

O CEP também pode ser informado ao registrar um medicamento, para guardar junto
o endereço da farmácia onde ele é comprado:

```bash
$ python -m src.main add Insulina 07:00 --cep 70070-120
Medicamento adicionado: Insulina às 07:00.
Farmácia: Quadra SBS Quadra 2, Asa Sul - Brasília/DF
```

## Onde os dados ficam salvos

Os lembretes são gravados em um arquivo JSON no diretório do usuário:

- Linux/macOS: `~/.medtime/meds.json`
- Windows: `C:\Users\<usuário>\.medtime\meds.json`

Para usar outro arquivo (útil em testes ou para manter os dados junto do
projeto), defina a variável de ambiente `MEDTIME_DATA_FILE`:

```bash
MEDTIME_DATA_FILE=./meds.json python -m src.main list
```

## Estrutura do projeto

```
.
├── .github/workflows/ci.yml   # pipeline de lint + testes
├── pyproject.toml             # configuração do ruff e do pytest
├── requirements.txt
├── src/
│   ├── main.py                # CLI (argparse)
│   ├── medication.py          # regras de negócio e persistência
│   └── viacep_api.py          # cliente da API ViaCEP
└── tests/
    ├── conftest.py            # fixtures (arquivo de dados isolado)
    ├── test_main.py
    ├── test_medication.py
    └── test_viacep_api.py
```

## Testes

```bash
pytest
```

Os testes são isolados: cada um grava em um arquivo temporário (`tmp_path`) e as
chamadas à ViaCEP são sempre feitas com mock, sem acessar a rede.

## Lint e formatação

```bash
ruff check .
ruff format --check .
```

## CI

O workflow em `.github/workflows/ci.yml` roda `ruff check`, `ruff format --check`
e `pytest` em cada push na `main` e em cada pull request, nas versões 3.11, 3.12
e 3.13 do Python.

## Versão

1.0.0
