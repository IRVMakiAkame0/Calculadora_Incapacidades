"""Gestión de la base de datos de la calculadora de incapacidades."""

import sqlite3
from datetime import datetime
from pathlib import Path


# ============================================================
# CONFIGURACIÓN
# ============================================================

DIRECTORIO_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_BASE_DE_DATOS = DIRECTORIO_PROYECTO / "incapacidades.db"

NOMBRE_TABLA = "casos_incapacidad"
FORMATO_FECHA = "%Y-%m-%d %H:%M:%S"


CONSULTA_OBTENER_CASOS = f"""
    SELECT
        id,
        fecha,
        tipo_incapacidad,
        salario,
        dias,
        pago
    FROM {NOMBRE_TABLA}
    ORDER BY id DESC
"""


# ============================================================
# CONEXIÓN
# ============================================================

def obtener_conexion() -> sqlite3.Connection:
    """Crea y configura una conexión con la base de datos."""
    conexion = sqlite3.connect(RUTA_BASE_DE_DATOS)
    conexion.row_factory = sqlite3.Row

    return conexion


# ============================================================
# CREACIÓN DE LA BASE DE DATOS
# ============================================================

def crear_base_datos() -> None:
    """Crea la tabla de casos si todavía no existe."""
    with obtener_conexion() as conexion:
        conexion.execute(
            f"""
            CREATE TABLE IF NOT EXISTS {NOMBRE_TABLA} (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                tipo_incapacidad TEXT NOT NULL,
                salario REAL NOT NULL,
                dias INTEGER NOT NULL,
                pago REAL NOT NULL
            )
            """
        )


# ============================================================
# GUARDAR CASOS
# ============================================================

def guardar_caso(
    tipo_incapacidad: str,
    salario: float,
    dias: int,
    pago: float,
) -> int:
    """Guarda un caso y retorna el ID generado."""
    fecha_actual = datetime.now().strftime(FORMATO_FECHA)

    with obtener_conexion() as conexion:
        resultado = conexion.execute(
            f"""
            INSERT INTO {NOMBRE_TABLA} (
                fecha,
                tipo_incapacidad,
                salario,
                dias,
                pago
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                fecha_actual,
                tipo_incapacidad,
                salario,
                dias,
                pago,
            ),
        )

        return resultado.lastrowid


# ============================================================
# CONSULTAR CASOS
# ============================================================

def obtener_casos() -> list[sqlite3.Row]:
    """Obtiene todos los casos guardados, del más reciente al más antiguo."""
    with obtener_conexion() as conexion:
        resultado = conexion.execute(
            CONSULTA_OBTENER_CASOS
        )

        return resultado.fetchall()


def buscar_casos(texto_busqueda: str) -> list[sqlite3.Row]:
    """Busca casos por ID, fecha o tipo de incapacidad."""
    texto_busqueda = f"%{texto_busqueda.strip()}%"

    with obtener_conexion() as conexion:
        resultado = conexion.execute(
            f"""
            SELECT
                id,
                fecha,
                tipo_incapacidad,
                salario,
                dias,
                pago
            FROM {NOMBRE_TABLA}
            WHERE CAST(id AS TEXT) LIKE ?
               OR fecha LIKE ?
               OR tipo_incapacidad LIKE ?
            ORDER BY id DESC
            """,
            (
                texto_busqueda,
                texto_busqueda,
                texto_busqueda,
            ),
        )

        return resultado.fetchall()


# ============================================================
# ELIMINAR CASOS
# ============================================================

def eliminar_caso(id_caso: int) -> None:
    """Elimina un caso según su ID."""
    with obtener_conexion() as conexion:
        conexion.execute(
            f"""
            DELETE FROM {NOMBRE_TABLA}
            WHERE id = ?
            """,
            (id_caso,),
        )