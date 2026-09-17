# Instalasi

## Kebutuhan

- Python 3.12
- Git

Repository ini tidak memerlukan database, message broker, container runtime, atau web framework.

## Windows PowerShell

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Jika eksekusi script dibatasi, gunakan `.venv\Scripts\python.exe` secara langsung untuk setiap perintah tanpa mengaktifkan environment.

## Linux dan macOS Bash

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

Pastikan environment benar dengan `python --version`; hasilnya harus menunjukkan Python 3.12.x.
