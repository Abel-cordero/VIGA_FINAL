"""Simple hardware-locked activation handling with obfuscation."""

import base64
import hashlib
import os
import socket
import subprocess
import uuid

def _app_dir() -> str:
    """Return the application data folder."""
    if os.name == "nt":
        base = os.getenv(
            "LOCALAPPDATA",
            os.path.join(os.path.expanduser("~"), "AppData", "Local"),
        )
    else:
        base = os.getenv("XDG_DATA_HOME", os.path.expanduser("~/.local/share"))
    path = os.path.join(base, "vigapp060")
    os.makedirs(path, exist_ok=True)
    return path


APP_DIR = _app_dir()
# File storing the hardware fingerprint
KEY_FILE = os.path.join(APP_DIR, "key.dat")
COUNTER_FILE = os.path.join(APP_DIR, "counter.dat")
# Static license key prefix
LICENSE_PREFIX = "ABC"
LICENSE_SUFFIX = "-XYZ"

_SECRET = b"vigapp-key"


def _xor_bytes(data: bytes, key: bytes) -> bytes:
    """Return ``data`` XORed with ``key``."""
    return bytes(b ^ key[i % len(key)] for i, b in enumerate(data))


def _encrypt(val: str) -> str:
    """Return obfuscated representation of ``val``."""
    enc = _xor_bytes(val.encode(), _SECRET)
    return base64.urlsafe_b64encode(enc).decode()


def _decrypt(val: str) -> str:
    """Decode a value produced by :func:`_encrypt`."""
    try:
        dec = base64.urlsafe_b64decode(val.encode())
        return _xor_bytes(dec, _SECRET).decode()
    except Exception:
        return ""


def _disk_serial() -> str:
    """Return the first available disk serial number or an empty string."""
    try:
        if os.name == "nt":
            out = subprocess.check_output(
                ["wmic", "diskdrive", "get", "SerialNumber"],
                stderr=subprocess.DEVNULL,
                text=True,
            )
            lines = [l.strip() for l in out.splitlines() if l.strip()][1:]
            return lines[0] if lines else ""
        out = subprocess.check_output(
            ["lsblk", "-dn", "-o", "serial"],
            stderr=subprocess.DEVNULL,
            text=True,
        )
        lines = [l.strip() for l in out.splitlines() if l.strip()]
        return lines[0] if lines else ""
    except Exception:
        return ""


def _read_counter() -> int:
    """Return the current license counter."""
    if os.path.exists(COUNTER_FILE):
        try:
            data = open(COUNTER_FILE).read().strip()
            return int(_decrypt(data))
        except (ValueError, OSError):
            pass
    return 1


def _write_counter(val: int) -> None:
    """Persist the license counter."""
    with open(COUNTER_FILE, "w") as f:
        f.write(_encrypt(str(val)))


def machine_code() -> str:
    """Return the user-visible code for this machine."""
    return hardware_id()[:16]


def license_for(code: str, counter: int) -> str:
    """Return the license string for ``code`` and ``counter``."""
    raw = f"{code}:{counter}:{_SECRET.decode()}"
    digest = hashlib.sha256(raw.encode()).hexdigest()[:8].upper()
    return f"{LICENSE_PREFIX}{digest}{LICENSE_SUFFIX}"


def current_license() -> str:
    """Return the expected license for activation."""
    counter = _read_counter()
    return license_for(machine_code(), counter)

def hardware_id() -> str:
    """Return a stable identifier for the current machine."""
    mac = uuid.getnode()
    host = socket.gethostname()
    disk = _disk_serial()
    raw = f"{mac}-{host}-{disk}"
    return hashlib.sha256(raw.encode()).hexdigest()


def activate(key: str) -> bool:
    """Store the hardware hash if the provided key is correct."""
    if key != current_license():
        return False
    with open(KEY_FILE, "w") as f:
        f.write(_encrypt(hardware_id()))
    _write_counter(_read_counter() + 1)
    return True

def check_activation() -> bool:
    """Check that this machine matches the stored activation."""
    if not os.path.exists(KEY_FILE):
        return False
    with open(KEY_FILE) as f:
        stored = _decrypt(f.read().strip())
    return stored == hardware_id()
