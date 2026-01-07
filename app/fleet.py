import csv
from typing import List, Optional
from app.decorators import log_operacao
from app.models import Veiculo

class Frota:
    def __init__(self):
        self.veiculos: List[Veiculo] = []

    @log_operacao
    def adicionar_veiculo(self, v: Veiculo) -> None:
        self.veiculos.append(v)

    @log_operacao
    def remover_por_indice(self, idx: int) -> bool:
        if 0 <= idx < len(self.veiculos):
            self.veiculos.pop(idx)
            return True
        return False

    # ✅ Compreensão de listas (filtro por marca numa linha)
    def pesquisar_por_marca(self, marca: str) -> List[Veiculo]:
        return [v for v in self.veiculos if v.marca.lower() == marca.lower()]

    # ✅ Lambda (desconto ou taxa)
    def aplicar_desconto_percent(self, percent: float) -> None:
        """
        percent=10 aplica 10% desconto
        """
        fator = 1.0 - (percent / 100.0)
        desconto = lambda preco: preco * fator  # ✅ lambda exigida
        for v in self.veiculos:
            v.preco = float(desconto(v.preco))

    def aplicar_taxa_percent(self, percent: float) -> None:
        fator = 1.0 + (percent / 100.0)
        taxa = lambda preco: preco * fator
        for v in self.veiculos:
            v.preco = float(taxa(v.preco))

    # ✅ Escrita em ficheiro (TXT ou CSV)
    def exportar_txt(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            for v in self.veiculos:
                f.write(str(v) + "\n")

    def exportar_csv(self, path: str) -> None:
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["tipo", "marca", "modelo", "ano", "preco", "bateria_kwh"])
            for v in self.veiculos:
                writer.writerow(v.to_row())

    def obter(self, idx: int) -> Optional[Veiculo]:
        if 0 <= idx < len(self.veiculos):
            return self.veiculos[idx]
        return None
