#!/usr/bin/env python3
from pathlib import Path
import sys
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from config import ENVIRONMENTAL_INDICATORS_FILE
from modules.environmental_data import load_environmental_indicators, validate_environmental_indicators, summarize_data_readiness
from modules.agronomic_readiness import build_readiness_report

def main():
    env_path = ENVIRONMENTAL_INDICATORS_FILE
    df = load_environmental_indicators(env_path)
    errors = validate_environmental_indicators(df)
    if errors:
        print("ERRORES:")
        for e in errors: print("-",e)
        raise SystemExit(1)
    print("CONTRATO AMBIENTAL VALIDADO")
    print("Estado:", summarize_data_readiness(df)["status"])
    print("Registros ambientales recibidos:", len(df))
    output = ROOT/"data/processed/environmental_readiness.csv"
    report = build_readiness_report(env_path,output)
    print("Informe:",output)
    print(report.to_string(index=False))
    print("\nNo se generaron puntuaciones de aptitud: faltan datos ambientales y validación agronómica.")

if __name__=="__main__":
    main()
