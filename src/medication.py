"""Regras de negócio e persistência dos lembretes de medicamentos."""

import json
import os
from pathlib import Path

#: Variável de ambiente usada para apontar outro arquivo de dados.
DATA_FILE_ENV = "MEDTIME_DATA_FILE"

#: Local padrão do arquivo de dados (no diretório do usuário, não no CWD).
DEFAULT_DATA_FILE = Path.home() / ".medtime" / "meds.json"

Medication = dict[str, str]


def resolve_data_file() -> Path:
    """Retorna o arquivo de dados em uso, respeitando ``MEDTIME_DATA_FILE``."""
    override = os.environ.get(DATA_FILE_ENV)
    return Path(override).expanduser() if override else DEFAULT_DATA_FILE


def normalize_time(value: str) -> str:
    """Valida um horário ``HH:MM`` e devolve a forma normalizada (``08:05``).

    Raises:
        ValueError: se o horário não estiver no formato ``HH:MM`` ou não existir.
    """
    try:
        hour_text, minute_text = str(value).split(":")
        hour, minute = int(hour_text), int(minute_text)
    except ValueError as exc:
        raise ValueError(f"Horário inválido: {value!r}. Use o formato HH:MM.") from exc

    if not (0 <= hour < 24 and 0 <= minute < 60):
        raise ValueError(f"Horário inválido: {value!r}. Use o formato HH:MM.")

    return f"{hour:02d}:{minute:02d}"


class MedicationManager:
    """Lê e grava os lembretes em um arquivo JSON."""

    def __init__(self, data_file: str | Path | None = None) -> None:
        self.data_file = Path(data_file) if data_file is not None else resolve_data_file()
        self.data_file.parent.mkdir(parents=True, exist_ok=True)
        if not self.data_file.exists():
            self._save([])

    def _load(self) -> list[Medication]:
        with self.data_file.open(encoding="utf-8") as file:
            return json.load(file)

    def _save(self, data: list[Medication]) -> None:
        with self.data_file.open("w", encoding="utf-8") as file:
            json.dump(data, file, indent=2, ensure_ascii=False)

    def add_medication(self, name: str, time: str, location: str | None = None) -> Medication:
        """Registra um medicamento e devolve o registro criado.

        Raises:
            ValueError: se o nome estiver vazio ou o horário for inválido.
        """
        clean_name = (name or "").strip()
        if not clean_name:
            raise ValueError("O nome do medicamento não pode ser vazio.")

        medication: Medication = {"name": clean_name, "time": normalize_time(time)}
        if location:
            medication["location"] = location

        data = self._load()
        data.append(medication)
        self._save(data)
        return medication

    def list_medications(self) -> list[Medication]:
        """Devolve os lembretes ordenados por horário."""
        return sorted(self._load(), key=lambda item: item["time"])

    def remove_medication(self, name: str) -> Medication:
        """Remove o primeiro lembrete com esse nome (sem diferenciar maiúsculas).

        Raises:
            ValueError: se nenhum medicamento com esse nome estiver registrado.
        """
        target = (name or "").strip().casefold()
        data = self._load()
        for index, medication in enumerate(data):
            if medication["name"].casefold() == target:
                removed = data.pop(index)
                self._save(data)
                return removed

        raise ValueError(f"Medicamento não encontrado: {name!r}")
