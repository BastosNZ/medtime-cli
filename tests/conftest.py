"""Fixtures compartilhadas pelos testes."""

from pathlib import Path

import pytest

from src.medication import DATA_FILE_ENV, MedicationManager


@pytest.fixture
def data_file(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Aponta o arquivo de dados para um diretório temporário e isolado."""
    path = tmp_path / "meds.json"
    monkeypatch.setenv(DATA_FILE_ENV, str(path))
    return path


@pytest.fixture
def manager(data_file: Path) -> MedicationManager:
    """Um ``MedicationManager`` novo, gravando apenas no ``tmp_path``."""
    return MedicationManager(data_file)
