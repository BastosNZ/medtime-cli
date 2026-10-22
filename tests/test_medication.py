"""Testes do armazenamento e da validação dos lembretes."""

import json
from pathlib import Path

import pytest

from src.medication import (
    DATA_FILE_ENV,
    MedicationManager,
    normalize_time,
    resolve_data_file,
)


def test_add_medication(manager: MedicationManager) -> None:
    manager.add_medication("Dipirona", "10:00")

    medications = manager.list_medications()

    assert medications == [{"name": "Dipirona", "time": "10:00"}]


def test_add_medication_returns_record(manager: MedicationManager) -> None:
    created = manager.add_medication("Ibuprofeno", "7:5")

    assert created == {"name": "Ibuprofeno", "time": "07:05"}


def test_add_medication_with_location(manager: MedicationManager) -> None:
    created = manager.add_medication("Insulina", "22:00", location="Bela Vista - São Paulo/SP")

    assert created["location"] == "Bela Vista - São Paulo/SP"
    assert manager.list_medications()[0]["location"] == "Bela Vista - São Paulo/SP"


def test_add_medication_strips_name(manager: MedicationManager) -> None:
    created = manager.add_medication("  Losartana  ", "08:00")

    assert created["name"] == "Losartana"


@pytest.mark.parametrize("name", ["", "   "])
def test_add_medication_rejects_empty_name(manager: MedicationManager, name: str) -> None:
    with pytest.raises(ValueError, match="não pode ser vazio"):
        manager.add_medication(name, "08:00")

    assert manager.list_medications() == []


@pytest.mark.parametrize(
    "time",
    ["25:00", "12:60", "-1:00", "10", "10:00:00", "abc", "", "ab:cd", "10:"],
)
def test_add_medication_rejects_invalid_time(manager: MedicationManager, time: str) -> None:
    with pytest.raises(ValueError, match="Horário inválido"):
        manager.add_medication("Erro", time)

    assert manager.list_medications() == []


@pytest.mark.parametrize(
    ("raw", "expected"),
    [("00:00", "00:00"), ("23:59", "23:59"), ("8:5", "08:05"), ("07:00", "07:00")],
)
def test_normalize_time(raw: str, expected: str) -> None:
    assert normalize_time(raw) == expected


def test_list_medications_sorted_by_time(manager: MedicationManager) -> None:
    manager.add_medication("Noite", "22:00")
    manager.add_medication("Manhã", "06:30")
    manager.add_medication("Tarde", "14:00")

    assert [m["name"] for m in manager.list_medications()] == ["Manhã", "Tarde", "Noite"]


def test_list_medications_empty(manager: MedicationManager) -> None:
    assert manager.list_medications() == []


def test_remove_medication(manager: MedicationManager) -> None:
    manager.add_medication("Dipirona", "10:00")
    manager.add_medication("Paracetamol", "12:00")

    removed = manager.remove_medication("Dipirona")

    assert removed["name"] == "Dipirona"
    assert [m["name"] for m in manager.list_medications()] == ["Paracetamol"]


def test_remove_medication_is_case_insensitive(manager: MedicationManager) -> None:
    manager.add_medication("Dipirona", "10:00")

    manager.remove_medication("dipirona")

    assert manager.list_medications() == []


def test_remove_nonexistent(manager: MedicationManager) -> None:
    manager.add_medication("Dipirona", "10:00")

    with pytest.raises(ValueError, match="não encontrado"):
        manager.remove_medication("NaoExiste")

    assert len(manager.list_medications()) == 1


def test_remove_only_removes_one_duplicate(manager: MedicationManager) -> None:
    manager.add_medication("Dipirona", "10:00")
    manager.add_medication("Dipirona", "18:00")

    manager.remove_medication("Dipirona")

    assert [m["time"] for m in manager.list_medications()] == ["18:00"]


def test_data_is_persisted_between_instances(data_file: Path) -> None:
    MedicationManager(data_file).add_medication("Dipirona", "10:00")

    assert MedicationManager(data_file).list_medications()[0]["name"] == "Dipirona"


def test_data_file_is_valid_json(manager: MedicationManager, data_file: Path) -> None:
    manager.add_medication("Dipirona", "10:00")

    assert json.loads(data_file.read_text(encoding="utf-8")) == [
        {"name": "Dipirona", "time": "10:00"}
    ]


def test_creates_data_file_and_parent_directory(tmp_path: Path) -> None:
    target = tmp_path / "sub" / "dir" / "meds.json"

    MedicationManager(target)

    assert target.exists()
    assert json.loads(target.read_text(encoding="utf-8")) == []


def test_resolve_data_file_uses_env_var(data_file: Path) -> None:
    assert resolve_data_file() == data_file


def test_resolve_data_file_default_is_outside_cwd(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv(DATA_FILE_ENV, raising=False)

    assert resolve_data_file().is_absolute()


def test_manager_without_argument_follows_env_var(data_file: Path) -> None:
    MedicationManager().add_medication("Dipirona", "10:00")

    assert data_file.exists()
    assert json.loads(data_file.read_text(encoding="utf-8"))[0]["name"] == "Dipirona"
