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
        self.frota.carregar_autosave()

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

        # Barra de desconto/taxa
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
        self.table = QTableWidget(0, 8)
        header = self.table.horizontalHeader()

        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 220)
        self.table.setColumnWidth(7, 120)

        # Restantes colunas adaptáveis
        for col in range(2, 7):
            header.setSectionResizeMode(col, header.ResizeMode.Stretch)


        self.table.setHorizontalHeaderLabels(["ID", "Adicionado em", "Tipo", "Marca", "Modelo", "Ano", "Preço (€)", "Bateria (kWh)"])
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(self.table.SelectionMode.ExtendedSelection)
        self.table.setEditTriggers(self.table.EditTrigger.NoEditTriggers)
        layout.addWidget(self.table)

        # ligações
        self.btn_add.clicked.connect(self.on_add)
        self.btn_remove.clicked.connect(self.on_remove)
        self.btn_export_txt.clicked.connect(lambda: self.on_export("txt"))
        self.btn_export_csv.clicked.connect(lambda: self.on_export("csv"))
        self.btn_search.clicked.connect(self.on_search)
        self.btn_clear.clicked.connect(self.on_clear_filter)
        self.btn_discount.clicked.connect(lambda: self._apply_percent(self.frota.aplicar_desconto_percent_indices, self.spn_discount.value()))
        self.btn_tax.clicked.connect(lambda: self._apply_percent(self.frota.aplicar_taxa_percent_indices, self.spn_tax.value()))

        self.filtered_indices = None
        self.refresh_table()


    # Helpers
    def _info(self, msg: str):
        QMessageBox.information(self, "Info", msg)

    def _warn(self, msg: str):
        QMessageBox.warning(self, "Erro", msg)

    def _selected_real_indices(self):
        selected_rows = {idx.row() for idx in self.table.selectedIndexes()}
        out = []
        for line in selected_rows:
            it = self.table.item(line, 0)  
            if it is None:
                continue
            real_idx = it.data(Qt.ItemDataRole.UserRole)
            if isinstance(real_idx, int):
                out.append(real_idx)
        return sorted(set(out))


    def _apply_percent(self, function, percent: float):
        if not self.frota.veiculos:
            self._info("Inventário vazio.")
            return
        indices = self._selected_real_indices()
        if not indices:
            self._info("Seleciona pelo menos um veículo na tabela.")
            return
        function(float(percent), indices)  # callback of another function  
        self.refresh_table()

    
    # UI actions
    def refresh_table(self):
        indices = list(range(len(self.frota.veiculos))) if self.filtered_indices is None else self.filtered_indices
        self.table.setRowCount(0)

        for row, idx in enumerate(indices):
            v = self.frota.obter(idx)
            if v is None:
                continue

            self.table.insertRow(row)

            tipo = "CarroEletrico" if isinstance(v, CarroEletrico) else "Veiculo"
            bateria = f"{v.bateria_kwh:.1f}" if isinstance(v, CarroEletrico) else ""

            item_id = QTableWidgetItem(str(idx))
            item_id.setData(Qt.ItemDataRole.UserRole, idx)
            item_time = QTableWidgetItem(str(getattr(v, "criado_em", "")))

            items = [
                item_id,                               # 0 ID
                item_time,                             # 1 Adicionado em
                QTableWidgetItem(tipo),                # 2 Tipo
                QTableWidgetItem(v.marca),             # 3 Marca
                QTableWidgetItem(v.modelo),            # 4 Modelo
                QTableWidgetItem(str(v.ano)),          # 5 Ano
                QTableWidgetItem(f"{v.preco:.2f}"),    # 6 Preço
                QTableWidgetItem(bateria),             # 7 Bateria
            ]

            for col, it in enumerate(items):
                it.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                self.table.setItem(row, col, it)


    def on_add(self):
        dlg = AddVehicleDialog(self)
        if dlg.exec() != dlg.DialogCode.Accepted or not dlg.data:
            return

        d = dlg.data
        v = (
            CarroEletrico(
                d["marca"],
                d["modelo"],
                d["ano"],
                d["preco"],
                bateria_kwh=d["bateria_kwh"]  
            )
            if d["tipo"] == "CarroEletrico"
            else Veiculo(d["marca"], d["modelo"], d["ano"], d["preco"])
        )


        try:
            self.frota.adicionar_veiculo(v)
        except Exception as e:
            self._warn(str(e))
            return

        self.filtered_indices = None
        self.refresh_table()

    def on_remove(self):
        idxs = self._selected_real_indices()
        if not idxs:
            self._info("Seleciona uma linha para remover.")
            return

        # remover do maior para o menor para não baralhar índices
        for idx in sorted(idxs, reverse=True):
            self.frota.remover_por_indice(idx)

        self.filtered_indices = None
        self.refresh_table()

    def on_search(self):
        marca = self.txt_search.text().strip()
        if not marca:
            self._info("Escreve uma marca para pesquisar.")
            return

        m = marca.lower()
        self.filtered_indices = [i for i, v in enumerate(self.frota.veiculos) if v.marca.lower() == m]
        self.refresh_table()
        self._info(f"Foram encontrados {len(self.filtered_indices)} veículo(s).")

    def on_clear_filter(self):
        self.filtered_indices = None
        self.txt_search.clear()
        self.refresh_table()

    def on_export(self, kind: str):
        if not self.frota.veiculos:
            self._info("Inventário vazio.")
            return

        if kind == "txt":
            path, _ = QFileDialog.getSaveFileName(self, "Guardar TXT", "fleet_exportada.txt", "Text (*.txt)")
            if not path:
                return
            self.frota.exportar_txt(path)
            self._info("Inventário exportado para TXT.")
        else:
            path, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", "fleet_exportada.csv", "CSV (*.csv)")
            if not path:
                return
            self.frota.exportar_csv(path)
            self._info("Inventário exportado para CSV.")

    def closeEvent(self, event):
        try:
            self.frota.guardar_autosave()
        except Exception:
            pass
        event.accept()
