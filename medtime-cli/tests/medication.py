import pytest
from medication import MedicationManager

manager = MedicationManager()


def test_add_medication():
    manager.add_medication("Teste", "10:00")
    meds = manager.list_medications()
    assert any(m["name"] == "Teste" for m in meds)


def test_invalid_time():
    with pytest.raises(ValueError):
        manager.add_medication("Erro", "25:00")


def test_remove_nonexistent():
    with pytest.raises(ValueError):
        manager.remove_medication("NaoExiste")