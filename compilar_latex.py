#!/usr/bin/env python3
"""
Compilador de LaTeX para los reportes generados
Intenta compilar el archivo .tex a PDF usando pdflatex
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path


def encontrar_pdflatex():
    """Busca el ejecutable pdflatex en el sistema"""
    return shutil.which("pdflatex")


def compilar(tex_path, output_dir=None):
    """
    Compila un archivo .tex a PDF
    
    Args:
        tex_path: Ruta al archivo .tex
        output_dir: Directorio de salida (opcional)
    
    Returns:
        tuple: (éxito: bool, mensaje: str, pdf_path: str o None)
    """
    
    if not os.path.exists(tex_path):
        return False, f"Archivo no encontrado: {tex_path}", None
    
    pdflatex = encontrar_pdflatex()
    if not pdflatex:
        return False, "pdflatex no encontrado. Instale MiKTeX o TeX Live.", None
    
    # Directorio de trabajo
    tex_dir = os.path.dirname(os.path.abspath(tex_path))
    tex_name = os.path.basename(tex_path)
    
    if output_dir is None:
        output_dir = tex_dir
    
    os.makedirs(output_dir, exist_ok=True)
    
    print(f"Compilando: {tex_name}")
    print(f"Directorio: {tex_dir}")
    print(f"Usando: {pdflatex}")
    print()
    
    # Ejecutar pdflatex dos veces para referencias
    for i in range(2):
        print(f"  Paso {i+1}/2...")
        try:
            result = subprocess.run(
                [pdflatex, "-interaction=nonstopmode", "-output-directory", output_dir, tex_name],
                cwd=tex_dir,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            if result.returncode != 0:
                # Buscar errores en el log
                log_path = os.path.join(output_dir, tex_name.replace('.tex', '.log'))
                if os.path.exists(log_path):
                    with open(log_path, 'r', encoding='utf-8', errors='ignore') as f:
                        log_content = f.read()
                        # Extraer líneas con error
                        errores = [line for line in log_content.split('\n') if '!' in line][:5]
                        if errores:
                            return False, f"Errores de compilación:\n" + "\n".join(errores), None
                
                return False, f"Error de compilación (código {result.returncode})", None
                
        except subprocess.TimeoutExpired:
            return False, "Tiempo de espera agotado", None
        except Exception as e:
            return False, f"Error ejecutando pdflatex: {e}", None
    
    # Verificar que se generó el PDF
    pdf_name = tex_name.replace('.tex', '.pdf')
    pdf_path = os.path.join(output_dir, pdf_name)
    
    if os.path.exists(pdf_path):
        size_kb = os.path.getsize(pdf_path) / 1024
        return True, f"PDF generado exitosamente: {pdf_path} ({size_kb:.1f} KB)", pdf_path
    else:
        return False, "El PDF no se generó", None


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Compila archivos LaTeX a PDF')
    parser.add_argument('tex', nargs='?', help='Archivo .tex a compilar')
    parser.add_argument('-o', '--output', help='Directorio de salida')
    
    args = parser.parse_args()
    
    if args.tex:
        tex_path = args.tex
    else:
        # Buscar el último reporte generado
        resultados_dir = os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            '05_Resultados'
        )
        
        # Buscar archivos .tex recientes
        tex_files = list(Path(resultados_dir).glob('*_reporte.tex'))
        if not tex_files:
            print("[ERROR] No se encontró ningún archivo .tex")
            print("Uso: python compilar_latex.py <archivo.tex>")
            return 1
        
        # Tomar el más reciente
        tex_path = str(max(tex_files, key=lambda p: p.stat().st_mtime))
        print(f"Usando archivo más reciente: {os.path.basename(tex_path)}")
    
    exito, mensaje, pdf_path = compilar(tex_path, args.output)
    
    print()
    print("=" * 80)
    if exito:
        print("[OK] " + mensaje)
        print("=" * 80)
        return 0
    else:
        print("[ERROR] " + mensaje)
        print("=" * 80)
        
        if "no encontrado" in mensaje:
            print()
            print("Para compilar el LaTeX necesitas instalar un distribución TeX:")
            print()
            print("OPCIÓN 1 - MiKTeX (Windows - Recomendado):")
            print("  1. Descarga desde: https://miktex.org/download")
            print("  2. Instala la versión básica (~200 MB)")
            print("  3. Durante la instalación, selecciona 'Install missing packages on the fly'")
            print("  4. Reinicia tu terminal después de instalar")
            print()
            print("OPCIÓN 2 - TeX Live:")
            print("  1. Descarga desde: https://tug.org/texlive/")
            print("  2. Sigue las instrucciones de instalación")
            print()
            print("Después de instalar, verifica con: pdflatex --version")
        
        return 1


if __name__ == "__main__":
    sys.exit(main())
