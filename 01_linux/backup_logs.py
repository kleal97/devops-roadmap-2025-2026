#!/usr/bin/env python3
import os
import tarfile
from datetime import datetime
from pathlib import Path
import glob

# === Configuración ===
SOURCE_DIR = Path("/var/log")                             # Carpeta a respaldar
DEST_DIR = Path.home() / "backups" / "logs"              # Dónde guardar backups
RETENTION = 7                                             # Cuántos archivos conservar

def ensure_dirs():
    DEST_DIR.mkdir(parents=True, exist_ok=True)

def make_backup():
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    archive_name = DEST_DIR / f"logs-{ts}.tar.gz"

    # Crear tar.gz
    with tarfile.open(archive_name, "w:gz") as tar:
        # Excluir archivos de gran tamaño poco útiles o sockets si molestan
        def is_excluded(tarinfo):
            # Evita sockets / pipes
            if not tarinfo.isfile() and not tarinfo.isdir():
                return None
            # Ejemplos de exclusión por nombre
            exclude_patterns = ["*.gz", "*.xz", "*.bz2", "*.zip"]
            from fnmatch import fnmatch
            for pat in exclude_patterns:
                if fnmatch(os.path.basename(tarinfo.name), pat):
                    return None
            return tarinfo

        print(f"[+] Creando backup: {archive_name}")
        tar.add(SOURCE_DIR, arcname=SOURCE_DIR.name, filter=is_excluded)

    return archive_name

def cleanup_old():
    backups = sorted(glob.glob(str(DEST_DIR / "logs-*.tar.gz")))
    if len(backups) <= RETENTION:
        print(f"[i] No hay backups para borrar (total={len(backups)}, retención={RETENTION})")
        return
    to_delete = backups[0:len(backups)-RETENTION]
    for f in to_delete:
        try:
            Path(f).unlink()
            print(f"[−] Eliminado backup antiguo: {f}")
        except Exception as e:
            print(f"[!] No pude borrar {f}: {e}")

def main():
    ensure_dirs()
    if not SOURCE_DIR.exists():
        print(f"[!] Fuente no encontrada: {SOURCE_DIR}")
        return 1
    archive = make_backup()
    print(f"[✓] Backup creado: {archive}")
    cleanup_old()
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
