"""Testes dos comandos do CLI."""

from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from src.main import main

ADDRESS = {
    "cep": "01310-100",
    "logradouro": "Avenida Paulista",
    "bairro": "Bela Vista",
    "localidade": "São Paulo",
    "uf": "SP",
}


def test_add_and_list(capsys: pytest.CaptureFixture[str], data_file: Path) -> None:
    assert main(["add", "Dipirona", "10:00"]) == 0
    capsys.readouterr()

    assert main(["list"]) == 0

    assert "10:00  Dipirona" in capsys.readouterr().out


def test_add_prints_confirmation(capsys: pytest.CaptureFixture[str], data_file: Path) -> None:
    main(["add", "Dipirona", "8:5"])

    assert "Medicamento adicionado: Dipirona às 08:05." in capsys.readouterr().out


def test_add_invalid_time_returns_error(
    capsys: pytest.CaptureFixture[str], data_file: Path
) -> None:
    assert main(["add", "Dipirona", "99:99"]) == 1
    assert "Horário inválido" in capsys.readouterr().err


def test_list_when_empty(capsys: pytest.CaptureFixture[str], data_file: Path) -> None:
    assert main(["list"]) == 0
    assert "Nenhum medicamento registrado." in capsys.readouterr().out


def test_remove(capsys: pytest.CaptureFixture[str], data_file: Path) -> None:
    main(["add", "Dipirona", "10:00"])
    capsys.readouterr()

    assert main(["remove", "Dipirona"]) == 0
    assert "Medicamento removido: Dipirona." in capsys.readouterr().out

    main(["list"])
    assert "Nenhum medicamento registrado." in capsys.readouterr().out


def test_remove_nonexistent_returns_error(
    capsys: pytest.CaptureFixture[str], data_file: Path
) -> None:
    assert main(["remove", "NaoExiste"]) == 1
    assert "não encontrado" in capsys.readouterr().err


def test_no_command_prints_help(capsys: pytest.CaptureFixture[str]) -> None:
    assert main([]) == 0
    assert "usage: medtime" in capsys.readouterr().out


@patch("src.main.ViaCEPAPI.search_address")
def test_cep_command(mock_search: MagicMock, capsys: pytest.CaptureFixture[str]) -> None:
    mock_search.return_value = ADDRESS

    assert main(["cep", "01310-100"]) == 0

    assert "Avenida Paulista" in capsys.readouterr().out
    mock_search.assert_called_once_with("01310-100")


@patch("src.main.ViaCEPAPI.search_address")
def test_cep_command_not_found(mock_search: MagicMock, capsys: pytest.CaptureFixture[str]) -> None:
    mock_search.return_value = None

    assert main(["cep", "00000-000"]) == 1
    assert "Endereço não encontrado." in capsys.readouterr().err


@patch("src.main.ViaCEPAPI.search_address")
def test_add_with_cep_saves_location(
    mock_search: MagicMock, capsys: pytest.CaptureFixture[str], data_file: Path
) -> None:
    mock_search.return_value = ADDRESS

    assert main(["add", "Insulina", "22:00", "--cep", "01310-100"]) == 0
    assert "Avenida Paulista, Bela Vista - São Paulo/SP" in capsys.readouterr().out

    main(["list"])
    assert "Avenida Paulista, Bela Vista - São Paulo/SP" in capsys.readouterr().out


@patch("src.main.ViaCEPAPI.search_address")
def test_add_with_unknown_cep_does_not_save(
    mock_search: MagicMock, capsys: pytest.CaptureFixture[str], data_file: Path
) -> None:
    mock_search.return_value = None

    assert main(["add", "Insulina", "22:00", "--cep", "99999-999"]) == 1
    assert "não foi salvo" in capsys.readouterr().err

    main(["list"])
    assert "Nenhum medicamento registrado." in capsys.readouterr().out


@patch("src.main.ViaCEPAPI.search_address")
def test_add_with_malformed_cep_does_not_call_the_api(
    mock_search: MagicMock, capsys: pytest.CaptureFixture[str], data_file: Path
) -> None:
    assert main(["add", "Insulina", "22:00", "--cep", "000"]) == 1
    assert "CEP inválido" in capsys.readouterr().err
    mock_search.assert_not_called()

    main(["list"])
    assert "Nenhum medicamento registrado." in capsys.readouterr().out


@patch("src.main.ViaCEPAPI.search_address")
def test_cep_command_with_malformed_cep(
    mock_search: MagicMock, capsys: pytest.CaptureFixture[str]
) -> None:
    """O CLI reporta o erro uma única vez, sem chamar a API."""
    assert main(["cep", "123"]) == 1

    captured = capsys.readouterr()
    assert "CEP inválido" in captured.err
    assert "Endereço não encontrado." not in captured.err
    mock_search.assert_not_called()
