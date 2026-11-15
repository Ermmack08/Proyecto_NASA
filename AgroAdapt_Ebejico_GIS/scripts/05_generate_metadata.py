"""Genera un inventario simple de los productos procesados para compartir con el equipo."""
import sys
from pathlib import Path
# Permite ejecutar este script desde la raíz con: python scripts/NOMBRE.py
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import json
from datetime import datetime, timezone
from config import PROCESSED_DIR, GEOGRAPHIC_DIR, OUTPUTS_DIR

def main():
    records = []
    for folder in (PROCESSED_DIR, GEOGRAPHIC_DIR):
        if not folder.exists():
            continue
        for path in folder.rglob("*"):
            if path.is_file():
                records.append({
                    "file": path.relative_to(OUTPUTS_DIR.parent).as_posix(),
                    "name": path.name,
                    "bytes": path.stat().st_size,
                    "modified": datetime.fromtimestamp(
                        path.stat().st_mtime, timezone.utc
                    ).isoformat(),
                })
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)
    target = OUTPUTS_DIR / "data_inventory.json"
    target.write_text(json.dumps(records, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Inventario creado: {target}")

if __name__ == "__main__":
    main()
