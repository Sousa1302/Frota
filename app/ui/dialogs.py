from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDoubleSpinBox, QMessageBox, QSpinBox
)

class AddVehicleDialog(QDialog):
    """
    Devolve um dict com:
    - tipo: "Veiculo" ou "CarroEletrico"
    - marca: str
    - modelo: str
    - ano: int
    - preco: float
    - bateria_kwh: float (se elétrico)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Veículo")
        self.resize(420, 250)

        layout = QVBoxLayout(self)

        # tipo
        row_tipo = QHBoxLayout()
        row_tipo.addWidget(QLabel("Tipo:"))
        self.cmb_tipo = QComboBox()
        self.cmb_tipo.addItems(["Veiculo", "CarroEletrico"])
        self.cmb_tipo.currentTextChanged.connect(self._toggle_bateria)
        row_tipo.addWidget(self.cmb_tipo)
        layout.addLayout(row_tipo)

        # marca
        row_marca = QHBoxLayout()
        row_marca.addWidget(QLabel("Marca:"))
        self.txt_marca = QLineEdit()
        self.txt_marca.setPlaceholderText("Ex: Toyota")
        row_marca.addWidget(self.txt_marca)
        layout.addLayout(row_marca)

        # modelo
        row_modelo = QHBoxLayout()
        row_modelo.addWidget(QLabel("Modelo:"))
        self.txt_modelo = QLineEdit()
        self.txt_modelo.setPlaceholderText("Ex: Yaris")
        row_modelo.addWidget(self.txt_modelo)
        layout.addLayout(row_modelo)

        # ano ✅
        row_ano = QHBoxLayout()
        row_ano.addWidget(QLabel("Ano:"))
        self.spn_ano = QSpinBox()
        self.spn_ano.setRange(1886, 2100)  # 1886 = 1º carro (histórico), 2100 para margem
        self.spn_ano.setValue(2015)
        row_ano.addWidget(self.spn_ano)
        layout.addLayout(row_ano)

        # preco
        row_preco = QHBoxLayout()
        row_preco.addWidget(QLabel("Preço (€):"))
        self.spn_preco = QDoubleSpinBox()
        self.spn_preco.setRange(0.0, 10_000_000.0)
        self.spn_preco.setDecimals(2)
        self.spn_preco.setValue(10000.00)
        row_preco.addWidget(self.spn_preco)
        layout.addLayout(row_preco)

        # bateria
        row_bat = QHBoxLayout()
        self.lbl_bat = QLabel("Bateria (kWh):")
        self.spn_bat = QDoubleSpinBox()
        self.spn_bat.setRange(0.0, 500.0)
        self.spn_bat.setDecimals(1)
        self.spn_bat.setValue(50.0)
        row_bat.addWidget(self.lbl_bat)
        row_bat.addWidget(self.spn_bat)
        layout.addLayout(row_bat)

        # botoes
        row_btn = QHBoxLayout()
        self.btn_ok = QPushButton("Adicionar")
        self.btn_cancel = QPushButton("Cancelar")
        self.btn_ok.clicked.connect(self._on_ok)
        self.btn_cancel.clicked.connect(self.reject)
        row_btn.addWidget(self.btn_ok)
        row_btn.addWidget(self.btn_cancel)
        layout.addLayout(row_btn)

        self._toggle_bateria(self.cmb_tipo.currentText())
        self.data = None

    def _toggle_bateria(self, tipo: str):
        is_eletrico = (tipo == "CarroEletrico")
        self.lbl_bat.setEnabled(is_eletrico)
        self.spn_bat.setEnabled(is_eletrico)

    def _on_ok(self):
        marca = self.txt_marca.text().strip()
        modelo = self.txt_modelo.text().strip()

        if not marca:
            QMessageBox.warning(self, "Erro", "A marca não pode estar vazia.")
            return
        if not modelo:
            QMessageBox.warning(self, "Erro", "O modelo não pode estar vazio.")
            return

        tipo = self.cmb_tipo.currentText()
        ano = int(self.spn_ano.value())
        preco = float(self.spn_preco.value())
        bateria = float(self.spn_bat.value())

        self.data = {
            "tipo": tipo,
            "marca": marca,
            "modelo": modelo,
            "ano": ano,
            "preco": preco,
            "bateria_kwh": bateria
        }
        self.accept()
