import argparse
from src.medication import MedicationManager
from src.viacep_api import ViaCEPAPI

manager = MedicationManager()

parser = argparse.ArgumentParser(description="Gerenciador de medicamentos")
subparsers = parser.add_subparsers(dest="command")

# Comando: add
add_parser = subparsers.add_parser("add")
add_parser.add_argument("name")
add_parser.add_argument("time")

# Comando: list
list_parser = subparsers.add_parser("list")

# Comando: remove
remove_parser = subparsers.add_parser("remove")
remove_parser.add_argument("name")

# Comando: find-pharmacy (NOVO!)
pharmacy_parser = subparsers.add_parser("find-pharmacy")
pharmacy_parser.add_argument("cep", help="CEP para buscar farmácias próximas")

args = parser.parse_args()

if args.command == "add":
    manager.add_medication(args.name, args.time)
    print("✅ Medicamento adicionado com sucesso.")

elif args.command == "list":
    meds = manager.list_medications()
    if meds:
        print("\n💊 Medicamentos registrados:")
        for m in meds:
            print(f"   • {m['name']} às {m['time']}")
        print()
    else:
        print("⚠️  Nenhum medicamento registrado.")

elif args.command == "remove":
    manager.remove_medication(args.name)
    print("✅ Medicamento removido.")

elif args.command == "find-pharmacy":
    print(f"🔍 Buscando endereço para o CEP: {args.cep}...")
    address = ViaCEPAPI.search_address(args.cep)
    
    if address:
        formatted = ViaCEPAPI.format_address(address)
        print(formatted)
        print("\n💡 Dica: Procure por farmácias próximas a este endereço!")
    else:
        print("❌ CEP não encontrado. Verifique e tente novamente.")

else:
    parser.print_help()