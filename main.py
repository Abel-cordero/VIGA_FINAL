"""Entry point launching the beam design application."""

import logging
import os
import sys
import ctypes
import hashlib
import subprocess
from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from src.moment_app import MomentApp


SECRET_KEY = "mi_clave_secreta"


def obtener_serial() -> str:
    """Return disk serial using wmic (Windows only)."""
    try:
        out = subprocess.check_output(
            ["wmic", "diskdrive", "get", "SerialNumber"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        return lines[1] if len(lines) > 1 else ""
    except Exception:
        return ""


def calcular_clave(serial: str) -> str:
    """Return SHA256 hash of serial concatenated with SECRET_KEY."""
    data = (serial + SECRET_KEY).encode()
    return hashlib.sha256(data).hexdigest()


def verificar_activacion() -> bool:
    """Prompt for an activation key and validate it."""
    serial = obtener_serial()
    if not serial:
        print("No se pudo obtener el serial del disco.")
        return False
    print(f"ID unico: {serial}")
    clave = input("Ingrese la clave de activacion: ").strip()
    return clave == calcular_clave(serial)


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
    if not verificar_activacion():
        print(
            "COMUNICARSE AL SIGUIENTE CORREO PARA SOLICTAR LA CLAVE DE "
            "ACTIVACION: abelcorderotineo99@gmail.com  cel y wsp : 922148420"
        )
        return

    app.setStyle("Fusion")
    # Keep a reference to the main window so it isn't garbage collected
    window = MomentApp()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()

