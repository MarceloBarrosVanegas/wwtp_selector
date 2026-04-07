#!/usr/bin/env python3
"""
Script para inicializar la base de datos con datos del Excel.
Ejecutar: python init-db.py
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from app.database import engine
from app.models import Base
from import_data import import_from_json

if __name__ == "__main__":
    print("Inicializando base de datos...")
    
    # Crear tablas
    print("Creando tablas...")
    Base.metadata.create_all(bind=engine)
    
    # Importar datos
    print("Importando datos del Excel...")
    json_path = os.path.join(os.path.dirname(__file__), 'data_export.json')
    
    if os.path.exists(json_path):
        import_from_json(json_path)
        print("\nBase de datos inicializada correctamente!")
        print("\nPuedes iniciar la aplicación con:")
        print("  docker-compose up")
        print("\nO localmente:")
        print("  Backend: cd backend && uvicorn app.main:app --reload")
        print("  Frontend: cd frontend && npm run dev")
    else:
        print(f"\nERROR: No se encontró el archivo {json_path}")
        print("Ejecuta primero el script de exportación desde el Excel.")
