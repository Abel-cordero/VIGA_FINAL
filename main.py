"""Entry point launching the beam design application."""

import logging
import os
import sys
import ctypes
from PyQt5.QtWidgets import QApplication, QMessageBox, QInputDialog
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from src.moment_app import MomentApp
from src.activation import check_activation, activate, machine_code


def main():
    """Start the Qt application."""
    logging.basicConfig(level=logging.ERROR)
    if os.name == "nt":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("VigApp060")
    app = QApplication(sys.argv)
    icon_path = os.path.join(
        os.path.dirname(__file__), "icon", "vigapp060.png")
    if os.path.exists(icon_path):
        pix = QPixmap(icon_path).scaled(
            256, 256, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        app.setWindowIcon(QIcon(pix))
    if not check_activation():
        code = machine_code()
        msg = f"Codigo de esta PC:\n{code}\n\nIngrese la clave:"
        key, ok = QInputDialog.getText(None, "Activar VIGAPP 060", msg)
        if not ok or not activate(key):
            QMessageBox.critical(
                None,
                "Licencia",
                (
                    "COMUNICARSE AL SIGUIENTE CORREO PARA SOLICTAR LA CLAVE DE "
                    "ACTIVACION: abelcorderotineo99@gmail.com  cel y wsp : "
                    "922148420"
                ),
            )
            return

    app.setStyle("Fusion")
    # Keep a reference to the main window so it isn't garbage collected
    window = MomentApp()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

