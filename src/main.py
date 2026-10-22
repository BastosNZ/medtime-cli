"""Interface de linha de comando do MedTime."""

import argparse
import sys

from src.medication import MedicationManager, resolve_data_file
from src.viacep_api import ViaCEPAPI


def build_parser() -> argparse.ArgumentParser:
    """Monta o parser de argumentos do CLI."""
    parser = argparse.ArgumentParser(
        prog="medtime",
        description="Gerenciador de lembretes de medicamentos.",
    )
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add", help="registra um medicamento")
    add_parser.add_argument("name", help="nome do medicamento")
    add_parser.add_argument("time", help="horário no formato HH:MM")
    add_parser.add_argument(
        "--cep",
        help="CEP da farmácia; o endereço é consultado na ViaCEP e salvo no lembrete",
    )

    subparsers.add_parser("list", help="lista os medicamentos registrados")

    remove_parser = subparsers.add_parser("remove", help="remove um medicamento")
    remove_parser.add_argument("name", help="nome do medicamento")

    cep_parser = subparsers.add_parser("cep", help="consulta um endereço pelo CEP")
    cep_parser.add_argument("cep", help="CEP no formato XXXXX-XXX ou XXXXXXXX")

    return parser


def _lookup_cep(cep: str) -> dict[str, str] | None:
    """Consulta o CEP na ViaCEP, validando o formato antes da chamada.

    Raises:
        ValueError: se o CEP for malformado (tratado por ``main``).
    """
    ViaCEPAPI.clean_cep(cep)
    return ViaCEPAPI.search_address(cep)


def _run_cep(cep: str) -> int:
    address = _lookup_cep(cep)
    if address is None:
        print("Endereço não encontrado.", file=sys.stderr)
        return 1
    print(ViaCEPAPI.format_address(address))
    return 0


def _run_add(manager: MedicationManager, name: str, time: str, cep: str | None) -> int:
    location = None
    if cep:
        address = _lookup_cep(cep)
        if address is None:
            print("Endereço não encontrado; o medicamento não foi salvo.", file=sys.stderr)
            return 1
        location = ViaCEPAPI.short_address(address)

    medication = manager.add_medication(name, time, location=location)
    print(f"Medicamento adicionado: {medication['name']} às {medication['time']}.")
    if location:
        print(f"Farmácia: {location}")
    return 0


def _run_list(manager: MedicationManager) -> int:
    medications = manager.list_medications()
    if not medications:
        print("Nenhum medicamento registrado.")
        return 0

    for medication in medications:
        line = f"{medication['time']}  {medication['name']}"
        if medication.get("location"):
            line += f"  ({medication['location']})"
        print(line)
    return 0


def main(argv: list[str] | None = None) -> int:
    """Executa o CLI e devolve o código de saída."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    try:
        if args.command == "cep":
            return _run_cep(args.cep)

        manager = MedicationManager()
        if args.command == "add":
            return _run_add(manager, args.name, args.time, args.cep)
        if args.command == "list":
            return _run_list(manager)
        if args.command == "remove":
            removed = manager.remove_medication(args.name)
            print(f"Medicamento removido: {removed['name']}.")
            return 0
    except ValueError as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Erro ao acessar {resolve_data_file()}: {exc}", file=sys.stderr)
        return 1

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
