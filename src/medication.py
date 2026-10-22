import json
import os

DATA_FILE = "data/meds.json"

class MedicationManager:
    def __init__(self):
        os.makedirs("data", exist_ok=True)
        if not os.path.exists(DATA_FILE):
            with open(DATA_FILE, "w") as f:
                json.dump([], f)

    def _load(self):
        with open(DATA_FILE, "r") as f:
            return json.load(f)

    def _save(self, data):
        with open(DATA_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def add_medication(self, name, time):
        if not self._valid_time(time):
            raise ValueError("Horário inválido")

        data = self._load()
        data.append({"name": name, "time": time})
        self._save(data)

    def list_medications(self):
        return self._load()

    def remove_medication(self, name):
        data = self._load()
        new_data = [m for m in data if m["name"] != name]
        if len(data) == len(new_data):
            raise ValueError("Medicamento não encontrado")
        self._save(new_data)

    def _valid_time(self, time):
        try:
            h, m = map(int, time.split(":"))
            return 0 <= h < 24 and 0 <= m < 60
        except:
            return False
