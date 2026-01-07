from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QDoubleSpinBox, QMessageBox
)

class AddVehicleDialog(QDialog):
    """
    Devolve um dict com:
    - tipo: "Veiculo" ou "CarroEletrico"
    - marca: str
    - preco: float
    - bateria_kwh: float (se elétrico)
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Adicionar Veículo")
        self.resize(360, 180)

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
        if not marca:
            QMessageBox.warning(self, "Erro", "A marca não pode estar vazia.")
            return

        tipo = self.cmb_tipo.currentText()
        preco = float(self.spn_preco.value())
        bateria = float(self.spn_bat.value())

        self.data = {
            "tipo": tipo,
            "marca": marca,
            "preco": preco,
            "bateria_kwh": bateria
        }
        self.accept()
