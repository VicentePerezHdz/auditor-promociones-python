from __future__ import annotations

import sys
# Fuerza UTF-8 en la salida del terminal (necesario en Windows para mostrar tildes y ñ)
sys.stdout.reconfigure(encoding="utf-8")

# pandas es la librería principal para manipular tablas de datos (DataFrames)
from pathlib import Path
import pandas as pd

# Ruta automática al CSV: sube dos niveles desde este archivo y busca la carpeta "data"
DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "caja_bonificada_promociones.csv"


def cargar_datos(path: Path = DATA_PATH) -> pd.DataFrame:
    """Lee el archivo CSV y normaliza columnas numéricas."""
    # Carga el CSV como una tabla (DataFrame)
    df = pd.read_csv(path)

    # Lista de columnas que deben ser números; el CSV puede traerlas como texto
    numeric_cols = [
        "cajas",
        "botellas",
        "botellas_por_caja",
        "precio_unitario",
        "precio_esperado",
        "umbral_cajas",
    ]
    for col in numeric_cols:
        # errors="coerce" convierte valores no numéricos a NaN en vez de lanzar error
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def calcular_unidades_normalizadas(row: pd.Series) -> float:
    # Si algún campo clave es nulo, no se puede calcular: devolvemos 0
    if pd.isna(row["cajas"]) or pd.isna(row["botellas"]) or pd.isna(row["botellas_por_caja"]):
        return 0.0
    # Evitamos división entre cero
    if row["botellas_por_caja"] == 0:
        return 0.0
    # Fórmula: cajas completas + fracción de cajas que forman las botellas sueltas
    return row["cajas"] + (row["botellas"] / row["botellas_por_caja"])


def promo_esperada(row: pd.Series) -> str:
    # Si el cliente compró suficiente volumen, la promoción Caja Bonificada debería aplicar
    return "SI" if row["unidades_normalizadas"] >= row["umbral_cajas"] else "NO"


def validar_registro(row: pd.Series) -> str:
    errores: list[str] = []
    advertencias: list[str] = []

    # Error crítico: cantidades negativas o nulas hacen inválido el registro
    if pd.isna(row["cajas"]) or pd.isna(row["botellas"]) or row["cajas"] < 0 or row["botellas"] < 0:
        errores.append("cantidad inválida")

    # Error crítico: sin precio no se puede calcular el importe
    if pd.isna(row["precio_unitario"]):
        errores.append("precio faltante")

    # Advertencia: el precio capturado difiere del precio de lista
    if not pd.isna(row["precio_unitario"]) and row["precio_unitario"] != row["precio_esperado"]:
        advertencias.append("precio distinto al esperado")

    # Advertencia: lo que se capturó en campo Caja Bonificada no coincide con la regla calculada
    if row["caja_bonificada_capturado"] != row["caja_bonificada_esperado"]:
        advertencias.append("caja bonificada no coincide")

    # Errores tienen prioridad; si existen, se reportan junto con las advertencias
    if errores:
        return "Error: " + " | ".join(errores + advertencias)
    if advertencias:
        return "Advertencia: " + " | ".join(advertencias)
    return "OK"


def auditar(df: pd.DataFrame) -> pd.DataFrame:
    resultado = df.copy()  # Trabajamos sobre una copia para no modificar el DataFrame original

    # Paso 1: calcular unidades normalizadas fila por fila (axis=1 = por columna → recorre filas)
    resultado["unidades_normalizadas"] = resultado.apply(calcular_unidades_normalizadas, axis=1)

    # Paso 2: determinar si la promo debería aplicar según la regla de volumen
    resultado["caja_bonificada_esperado"] = resultado.apply(promo_esperada, axis=1)

    # Paso 3: ejecutar todas las validaciones y asignar un estatus por registro
    resultado["estatus"] = resultado.apply(validar_registro, axis=1)

    # Paso 4: calcular el importe (cajas × precio); clip evita negativos, fillna evita errores con NaN
    resultado["importe"] = (
        resultado["cajas"].clip(lower=0).fillna(0)
        * resultado["precio_unitario"].fillna(0)
    )
    return resultado


def resumen_por_estatus(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df
        # Extrae la primera palabra del estatus ("OK", "Error", "Advertencia") como categoría
        .assign(tipo=df["estatus"].str.split(":").str[0])
        # Agrupa y cuenta registros + suma importe por categoría
        .groupby("tipo", as_index=False)
        .agg(registros=("sku", "count"), importe=("importe", "sum"))
        .sort_values("registros", ascending=False)
    )


def main() -> None:
    # --- Flujo principal del programa ---

    # 1. Cargar datos desde el CSV
    datos = cargar_datos()

    # 2. Auditar: enriquece el DataFrame con columnas calculadas y estatus
    auditados = auditar(datos)

    # 3. Generar el resumen agrupado por tipo de estatus
    resumen = resumen_por_estatus(auditados)

    # Columnas relevantes para mostrar al usuario (ocultamos campos intermedios)
    columnas = [
        "ruta",
        "cliente",
        "sku",
        "producto",
        "unidades_normalizadas",
        "caja_bonificada_capturado",
        "caja_bonificada_esperado",
        "estatus",
    ]

    print("\nRegistros auditados")
    print(auditados[columnas])

    print("\nResumen por estatus")
    print(resumen)

    # Filtros para contar errores y advertencias en la conclusión narrativa
    errores = auditados[auditados["estatus"].str.startswith("Error")]
    advertencias = auditados[auditados["estatus"].str.startswith("Advertencia")]

    print("\nConclusión:")
    print(
        f"Se detectaron {len(errores)} errores y {len(advertencias)} advertencias. "
        "La operación puede continuar, pero conviene corregir precios faltantes "
        "y revisar promociones Caja Bonificada que no coinciden antes de publicar el reporte."
    )


# Solo se ejecuta si corres el archivo directamente (no cuando se importa como módulo)
if __name__ == "__main__":
    main()
