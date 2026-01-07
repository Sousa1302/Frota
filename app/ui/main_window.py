from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QTableWidget, QTableWidgetItem, QLineEdit, QLabel, QMessageBox,
    QFileDialog, QDoubleSpinBox
)
from PyQt6.QtCore import Qt

from app.fleet import Frota
from app.models import Veiculo, CarroEletrico
from app.ui.dialogs import AddVehicleDialog


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Gestão de Frotas (PyQt6)")
        self.resize(900, 520)

        self.frota = Frota()

        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)

        # Barra de ações
        bar = QHBoxLayout()

        self.btn_add = QPushButton("Adicionar")
        self.btn_remove = QPushButton("Remover Selecionado")
        self.btn_export_txt = QPushButton("Exportar TXT")
        self.btn_export_csv = QPushButton("Exportar CSV")

        bar.addWidget(self.btn_add)
        bar.addWidget(self.btn_remove)
        bar.addWidget(self.btn_export_txt)
        bar.addWidget(self.btn_export_csv)

        bar.addSpacing(16)

        bar.addWidget(QLabel("Pesquisar marca:"))
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("Ex: Toyota")
        self.btn_search = QPushButton("Pesquisar")
        self.btn_clear = QPushButton("Limpar filtro")

        bar.addWidget(self.txt_search)
        bar.addWidget(self.btn_search)
        bar.addWidget(self.btn_clear)

        layout.addLayout(bar)

        # Barra de desconto/taxa (lambda)
        bar2 = QHBoxLayout()
        bar2.addWidget(QLabel("Desconto (%):"))
        self.spn_discount = QDoubleSpinBox()
        self.spn_discount.setRange(0.0, 99.0)
        self.spn_discount.setDecimals(1)
        self.spn_discount.setValue(10.0)
        self.btn_discount = QPushButton("Aplicar Desconto")

        bar2.addSpacing(12)
        bar2.addWidget(QLabel("Taxa (%):"))
        self.spn_tax = QDoubleSpinBox()
        self.spn_tax.setRange(0.0, 500.0)
        self.spn_tax.setDecimals(1)
        self.spn_tax.setValue(23.0)
        self.btn_tax = QPushButton("Aplicar Taxa")

        bar2.addWidget(self.spn_discount)
        bar2.addWidget(self.btn_discount)
        bar2.addSpacing(16)
        bar2.addWidget(self.spn_tax)
        bar2.addWidget(self.btn_tax)

        layout.addLayout(bar2)

        # Tabela
        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["#", "Tipo", "Marca", "Preço (€)", "Bateria (kWh)"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # ligações
        self.btn_add.clicked.connect(self.on_add)
        self.btn_remove.clicked.connect(self.on_remove)
        self.btn_export_txt.clicked.connect(self.on_export_txt)
        self.btn_export_csv.clicked.connect(self.on_export_csv)
        self.btn_search.clicked.connect(self.on_search)
        self.btn_clear.clicked.connect(self.on_clear_filter)
        self.btn_discount.clicked.connect(self.on_discount)
        self.btn_tax.clicked.connect(self.on_tax)

        # estado de filtro
        self.filtered_indices = None  # None = sem filtro
        self.refresh_table()

    def refresh_table(self):
        # decide lista mostrada
        if self.filtered_indices is None:
            indices = list(range(len(self.frota.veiculos)))
        else:
            indices = self.filtered_indices

        self.table.setRowCount(0)

        for row, idx in enumerate(indices):
            v = self.frota.obter(idx)
            if v is None:
                continue

            self.table.insertRow(row)

            tipo = "CarroEletrico" if isinstance(v, CarroEletrico) else "Veiculo"
            bateria = f"{v.bateria_kwh:.1f}" if isinstance(v, CarroEletrico) else ""

            items = [
                QTableWidgetItem(str(idx)),
                QTableWidgetItem(tipo),
                QTableWidgetItem(v.marca),
                QTableWidgetItem(f"{v.preco:.2f}"),
                QTableWidgetItem(bateria),
            ]

            for col, it in enumerate(items):
                it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, it)

    def on_add(self):
        dlg = AddVehicleDialog(self)
        if dlg.exec() == dlg.DialogCode.Accepted and dlg.data:
            d = dlg.data
            if d["tipo"] == "CarroEletrico":
                v = CarroEletrico(d["marca"], d["preco"], d["bateria_kwh"])
            else:
                v = Veiculo(d["marca"], d["preco"])

            self.frota.adicionar_veiculo(v)
            self.filtered_indices = None
            self.refresh_table()

    def _selected_real_index(self):
        row = self.table.currentRow()
        if row < 0:
            return None
        idx_item = self.table.item(row, 0)
        if not idx_item:
            return None
        return int(idx_item.text())

    def on_remove(self):
        idx = self._selected_real_index()
        if idx is None:
            QMessageBox.information(self, "Info", "Seleciona uma linha para remover.")
            return

        ok = self.frota.remover_por_indice(idx)
        if not ok:
            QMessageBox.warning(self, "Erro", "Não foi possível remover (índice inválido).")
            return

        self.filtered_indices = None
        self.refresh_table()

    def on_search(self):
        marca = self.txt_search.text().strip()
        if not marca:
            QMessageBox.information(self, "Info", "Escreve uma marca para pesquisar.")
            return

        # usamos o método que internamente faz list comprehension
        encontrados = self.frota.pesquisar_por_marca(marca)

        # converter objetos encontrados para índices reais (para a tabela)
        # (fazemos assim para remover/exportar continuar certo)
        self.filtered_indices = [i for i, v in enumerate(self.frota.veiculos) if v in encontrados]
        self.refresh_table()

        QMessageBox.information(self, "Resultado", f"Foram encontrados {len(encontrados)} veículo(s).")

    def on_clear_filter(self):
        self.filtered_indices = None
        self.txt_search.clear()
        self.refresh_table()

    def on_discount(self):
        if not self.frota.veiculos:
            QMessageBox.information(self, "Info", "Inventário vazio.")
            return
        percent = float(self.spn_discount.value())
        self.frota.aplicar_desconto_percent(percent)  # lambda dentro
        self.refresh_table()

    def on_tax(self):
        if not self.frota.veiculos:
            QMessageBox.information(self, "Info", "Inventário vazio.")
            return
        percent = float(self.spn_tax.value())
        self.frota.aplicar_taxa_percent(percent)  # lambda dentro
        self.refresh_table()

    def on_export_txt(self):
        if not self.frota.veiculos:
            QMessageBox.information(self, "Info", "Inventário vazio.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Guardar TXT", "fleet_exportada.txt", "Text (*.txt)")
        if not path:
            return
        self.frota.exportar_txt(path)
        QMessageBox.information(self, "OK", "Inventário exportado para TXT.")

    def on_export_csv(self):
        if not self.frota.veiculos:
            QMessageBox.information(self, "Info", "Inventário vazio.")
            return
        path, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", "fleet_exportada.csv", "CSV (*.csv)")
        if not path:
            return
        self.frota.exportar_csv(path)
        QMessageBox.information(self, "OK", "Inventário exportado para CSV.")
