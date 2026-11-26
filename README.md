# Auditor de Promociones (Python)

Mini proyecto en Python para **auditar promociones por volumen**, validar reglas tipo **Caja Bonificada** y analizar datos (ficticios) de pedidos usando **Pandas**.

El proyecto simula un escenario típico de fuerza de ventas: cada pedido trae una cantidad comprada (cajas/botellas) y una promoción capturada en campo. El auditor recalcula si la promoción *debería* haber aplicado según la regla de volumen, y marca cada registro como `OK`, `Error` o `Advertencia`.

## 📋 ¿Qué hace?

1. Carga un CSV con pedidos (`data/caja_bonificada_promociones.csv`).
2. Normaliza las cantidades: convierte cajas + botellas sueltas en **unidades normalizadas** (cajas equivalentes).
3. Calcula si la promoción **Caja Bonificada** debería aplicar (`caja_bonificada_esperado`) comparando las unidades normalizadas contra el umbral de la regla (`umbral_cajas`).
4. Valida cada registro y asigna un estatus:
   - **Error** — cantidades negativas/nulas o precio faltante.
   - **Advertencia** — precio distinto al esperado, o la Caja Bonificada capturada no coincide con la esperada.
   - **OK** — sin inconsistencias.
5. Calcula el importe de cada registro (`cajas × precio_unitario`).
6. Genera un resumen agrupado por estatus (registros e importe total por tipo).
7. Imprime un reporte en consola con el detalle auditado, el resumen y una conclusión narrativa.

## 🗂 Estructura del proyecto

```
auditor-promociones-python/
├── data/
│   └── caja_bonificada_promociones.csv   # Datos de pedidos (ficticios) a auditar
├── src/
│   └── auditor_promociones.py      # Lógica de carga, cálculo y auditoría
├── tests/
│   └── test_reglas.py              # Pruebas unitarias con pytest
└── requirements.txt                 # Dependencias del proyecto
```

## ⚙️ Requisitos

- Python 3.11+
- Dependencias listadas en `requirements.txt`:
  - `pandas`
  - `matplotlib`

## 🚀 Instalación

```bash
# Clonar el repositorio
git clone https://github.com/VicentePerezHdz/auditor-promociones-python.git
cd auditor-promociones-python

# Crear y activar un entorno virtual (opcional pero recomendado)
python -m venv venv
source venv/bin/activate        # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

## ▶️ Uso

Ejecuta el script principal desde la raíz del proyecto:

```bash
python src/auditor_promociones.py
```

Esto imprime en consola:

- **Registros auditados** — tabla con ruta, cliente, SKU, producto, unidades normalizadas, Caja Bonificada capturada vs. esperada, y estatus.
- **Resumen por estatus** — conteo de registros e importe total agrupado por `OK` / `Error` / `Advertencia`.
- **Conclusión** — resumen narrativo con el número de errores y advertencias detectados.

### Usar tus propios datos

El CSV debe incluir las siguientes columnas:

| Columna | Descripción |
|---|---|
| `ruta` | Ruta o zona de venta |
| `cliente` | Identificador o nombre del cliente |
| `sku` | Código del producto |
| `producto` | Nombre del producto |
| `cajas` | Cajas completas compradas |
| `botellas` | Botellas sueltas compradas |
| `botellas_por_caja` | Botellas que forman una caja completa |
| `precio_unitario` | Precio capturado en el pedido |
| `precio_esperado` | Precio de lista esperado |
| `umbral_cajas` | Umbral de cajas para activar la regla Caja Bonificada |
| `caja_bonificada_capturado` | Caja Bonificada capturada en campo (`SI`/`NO`) |

Puedes apuntar `cargar_datos()` a otra ruta pasando el parámetro `path`.

## 🧪 Pruebas

El proyecto incluye pruebas unitarias con `pytest` para las funciones de cálculo y validación (`calcular_unidades_normalizadas`, `promo_esperada`, `validar_registro`).

```bash
python -m pytest
```

## 📐 Reglas de negocio

- **Unidades normalizadas**: `cajas + (botellas / botellas_por_caja)`
- **Caja Bonificada esperada**: `SI` si `unidades_normalizadas >= umbral_cajas`, si no `NO`
- **Importe**: `cajas × precio_unitario` (cantidades negativas se ajustan a 0)

## 🛠 Tecnologías

- Python
- Pandas
- Pytest

## 👤 Autor

**Vicente de Jesús Pérez Hernández**
[github.com/VicentePerezHdz](https://github.com/VicentePerezHdz)
