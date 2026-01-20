from dataclasses import dataclass, field
from datetime import datetime


def now_str() -> str:
    # Ex: 2026-01-12 14:23:10
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@dataclass
class Veiculo:
    marca: str
    modelo: str
    ano: int
    preco: float
    criado_em: str = field(default_factory=now_str)

    def __post_init__(self):
        if not self.criado_em:
            self.criado_em = now_str()

    def __str__(self) -> str:
        return f"Veiculo | {self.marca} {self.modelo} ({self.ano}) | {self.preco:.2f}€"

    def to_row(self) -> list:
        # tipo, criado_em, marca, modelo, ano, preco, bateria_kwh
        return ["Veiculo", self.criado_em, self.marca, self.modelo, str(self.ano), f"{self.preco:.2f}", ""]


@dataclass
class CarroEletrico(Veiculo):
    bateria_kwh: float = 0.0

    def __str__(self) -> str:
        return (
            f"CarroEletrico | {self.marca} {self.modelo} ({self.ano}) | {self.preco:.2f}€ | "
            f"{self.bateria_kwh:.1f} kWh"
        )

    def to_row(self) -> list:
        return ["CarroEletrico", self.criado_em, self.marca, self.modelo, str(self.ano), f"{self.preco:.2f}", f"{self.bateria_kwh:.1f}"]
