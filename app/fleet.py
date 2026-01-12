import csv
from pathlib import Path
from typing import List, Optional

from app.decorators import log_operacao
from app.models import Veiculo, CarroEletrico


def _safe_float(value: str, default: float = 0.0) -> float:
    try:
        return float(value)
    except Exception:
        return default


class Frota:
    HEADER = ["tipo", "criado_em", "marca", "modelo", "ano", "preco", "bateria_kwh"]

    def __init__(self, autosave_path: str = "data/frota_autosave.csv"):
        self.veiculos: List[Veiculo] = []
        self.autosave_path = Path(autosave_path)
        self.autosave_path.parent.mkdir(parents=True, exist_ok=True)

    # -------------------------
    # Persistência automática
    # -------------------------
    def carregar_autosave(self) -> None:
        if not self.autosave_path.exists():
            return

        try:
            with open(self.autosave_path, "r", newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                self.veiculos = [
                    CarroEletrico(
                        (r.get("marca") or "").strip(),
                        (r.get("modelo") or "").strip(),
                        int((r.get("ano") or "0").strip() or 0),
                        _safe_float((r.get("preco") or "0").strip(), 0.0),
                        criado_em=(r.get("criado_em") or "").strip() or "",
                        bateria_kwh=_safe_float((r.get("bateria_kwh") or "0").strip(), 0.0),
                    )

                if (r.get("tipo") or "").strip() == "CarroEletrico"
                else Veiculo(
                    (r.get("marca") or "").strip(),
                    (r.get("modelo") or "").strip(),
                    int((r.get("ano") or "0").strip() or 0),
                    _safe_float((r.get("preco") or "0").strip(), 0.0),
                    criado_em=(r.get("criado_em") or "").strip() or ""
                )
                for r in reader
            ]

        except Exception:
            self.veiculos = []

    def guardar_autosave(self) -> None:
        try:
            with open(self.autosave_path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.HEADER)
                writer.writerows(v.to_row() for v in self.veiculos)
        except Exception:
            pass

    # -----------
    # Validações 
    # -----------
    def validar_veiculo(self, v: Veiculo) -> None:
        if not v.marca or not v.marca.strip():
            raise ValueError("Marca vazia.")
        if not v.modelo or not v.modelo.strip():
            raise ValueError("Modelo vazio.")
        if v.preco < 0:
            raise ValueError("Preço não pode ser negativo.")
        if not (1886 <= v.ano <= 2100):
            raise ValueError("Ano inválido (1886–2100).")


        if hasattr(v, "bateria_kwh"):
            if abs(v.bateria_kwh) < 1e-9:
                v.bateria_kwh = 0.0
            if v.bateria_kwh < 0:
                raise ValueError("Bateria (kWh) não pode ser negativa.")

    
    @log_operacao
    def adicionar_veiculo(self, v):
        self.validar_veiculo(v)
        self.veiculos.append(v)
        self.guardar_autosave()


    @log_operacao
    def remover_por_indice(self, idx):
        if 0 <= idx < len(self.veiculos):
            self.veiculos.pop(idx)
            self.guardar_autosave()
            return True
        return False


    def obter(self, idx: int) -> Optional[Veiculo]:
        return self.veiculos[idx] if 0 <= idx < len(self.veiculos) else None

    # -------------------------
    # Pesquisa (list comprehension)
    # -------------------------
    def pesquisar_por_marca(self, marca: str) -> List[Veiculo]:
        m = marca.lower().strip()
        return [v for v in self.veiculos if v.marca.lower() == m]

    # -------------------------
    # Lambda (desconto/taxa)
    # -------------------------
    def _aplicar_percent_indices(self, percent: float, indices: List[int], fator_fn) -> None:
    
        fator = float(fator_fn(percent))
        for idx in indices:
            if 0 <= idx < len(self.veiculos):
                self.veiculos[idx].preco *= fator
        self.guardar_autosave()

    def aplicar_desconto_percent_indices(self, percent: float, indices: List[int]) -> None:
        self._aplicar_percent_indices(percent, indices, lambda p: 1.0 - (p / 100.0))

    def aplicar_taxa_percent_indices(self, percent: float, indices: List[int]) -> None:
        self._aplicar_percent_indices(percent, indices, lambda p: 1.0 + (p / 100.0))

    
    def aplicar_desconto_percent(self, percent: float) -> None:
        self._aplicar_percent_indices(percent, list(range(len(self.veiculos))), lambda p: 1.0 - (p / 100.0))

    def aplicar_taxa_percent(self, percent: float) -> None:
        self._aplicar_percent_indices(percent, list(range(len(self.veiculos))), lambda p: 1.0 + (p / 100.0))

    # -------------------------
    # Export
    # -------------------------
    def exportar_txt(self, path: str) -> None:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("\n".join(str(v) for v in self.veiculos) + ("\n" if self.veiculos else ""))
        except Exception:
            pass

    def exportar_csv(self, path: str) -> None:
        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(self.HEADER)
                writer.writerows(v.to_row() for v in self.veiculos)
        except Exception:
            pass
