from dataclasses import dataclass


@dataclass
class Veiculo:
    marca: str
    modelo: str
    ano: int
    preco: float

    def __str__(self) -> str:
        return f"Veiculo | {self.marca} {self.modelo} ({self.ano}) | {self.preco:.2f}€"

    def to_row(self) -> list:
        # tipo, marca, modelo, ano, preco, bateria_kwh
        return ["Veiculo", self.marca, self.modelo, str(self.ano), f"{self.preco:.2f}", ""]


@dataclass
class CarroEletrico(Veiculo):
    bateria_kwh: float = 0.0

    # ✅ exemplo de lambda (curta e clara)
    autonomia_km = lambda self: self.bateria_kwh * 5.0

    def __str__(self) -> str:
        return (
            f"CarroEletrico | {self.marca} {self.modelo} ({self.ano}) | {self.preco:.2f}€ | "
            f"{self.bateria_kwh:.1f} kWh | Autonomia: {self.autonomia_km():.0f} km"
        )

    def to_row(self) -> list:
        return ["CarroEletrico", self.marca, self.modelo, str(self.ano), f"{self.preco:.2f}", f"{self.bateria_kwh:.1f}"]
