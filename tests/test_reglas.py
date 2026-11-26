import pandas as pd
from src.auditor_promociones import calcular_unidades_normalizadas, promo_esperada, validar_registro


def test_normaliza_cajas_y_botellas():
    row = pd.Series({"cajas": 8, "botellas": 12, "botellas_por_caja": 12})
    assert calcular_unidades_normalizadas(row) == 9


def test_promocion_esperada_si():
    row = pd.Series({"unidades_normalizadas": 10, "umbral_cajas": 10})
    assert promo_esperada(row) == "SI"


def test_precio_faltante_devuelve_error():
    row = pd.Series({
        "cajas": 1,
        "botellas": 0,
        "precio_unitario": None,
        "precio_esperado": 10,
        "caja_bonificada_capturado": "NO",
        "caja_bonificada_esperado": "NO",
    })
    assert validar_registro(row).startswith("Error")
