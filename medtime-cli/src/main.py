import argparse
from src.medication import MedicationManager

manager = MedicationManager()

parser = argparse.ArgumentParser(description="Gerenciador de medicamentos")
subparsers = parser.add_subparsers(dest="command")

add_parser = subparsers.add_parser("add")
add_parser.add_argument("name")
add_parser.add_argument("time")

list_parser = subparsers.add_parser("list")

remove_parser = subparsers.add_parser("remove")
remove_parser.add_argument("name")

args = parser.parse_args()

if args.command == "add":
    manager.add_medication(args.name, args.time)
    print("Medicamento adicionado com sucesso.")

elif args.command == "list":
    meds = manager.list_medications()
    for m in meds:
        print(f"{m['name']} - {m['time']}")

elif args.command == "remove":
    manager.remove_medication(args.name)
    print("Medicamento removido.")

else:
    parser.print_help()
