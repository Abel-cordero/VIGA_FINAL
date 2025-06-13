import sys
import os

from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QLineEdit,
    QPushButton,
    QSpinBox,
    QLabel,
    QMessageBox,
)

# Ensure the "src" package is importable when executing this script directly
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.activation import license_for


class LicenseGenerator(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Generador de Licencia")
        layout = QVBoxLayout(self)

        self.code_edit = QLineEdit()
        self.code_edit.setPlaceholderText("ID de equipo")
        layout.addWidget(self.code_edit)

        counter_row = QHBoxLayout()
        counter_row.addWidget(QLabel("Contador:"))
        self.counter = QSpinBox()
        self.counter.setMinimum(1)
        self.counter.setMaximum(9999)
        counter_row.addWidget(self.counter)
        layout.addLayout(counter_row)

        self.license_edit = QLineEdit()
        self.license_edit.setReadOnly(True)
        layout.addWidget(self.license_edit)

        btn_row = QHBoxLayout()
        gen_btn = QPushButton("Generar")
        copy_btn = QPushButton("Copiar")
        btn_row.addWidget(gen_btn)
        btn_row.addWidget(copy_btn)
        layout.addLayout(btn_row)

        gen_btn.clicked.connect(self.generate)
        copy_btn.clicked.connect(self.copy)

    def generate(self):
        code = self.code_edit.text().strip()
        if not code:
            QMessageBox.warning(self, "Error", "Ingrese el ID")
            return
        lic = license_for(code, self.counter.value())
        self.license_edit.setText(lic)

    def copy(self):
        QApplication.clipboard().setText(self.license_edit.text())


def main():
    app = QApplication(sys.argv)
    win = LicenseGenerator()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
