import os
import subprocess
from pathlib import Path


def create_private_and_public_keys() -> None:
    """
    Генерирует закрытый и открытый ключи в директории certs, если их нет
    """
    path = Path(__file__).resolve().parent / "certs"
    if not len(os.listdir(path)) == 0:
        return
    subprocess.run(
        ["openssl", "genrsa", "-out", path / "private.pem", "2048"]
    )
    subprocess.run(
        [
            "openssl",
            "rsa",
            "-in",
            path / "private.pem",
            "-outform",
            "PEM",
            "-pubout",
            "-out",
            path / "public.pem",
        ]
    )


if __name__ == "__main__":
    create_private_and_public_keys()
