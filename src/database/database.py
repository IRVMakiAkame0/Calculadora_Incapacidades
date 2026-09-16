"""Gestión de la base de datos de la calculadora de incapacidades."""

import sqlite3
from datetime import datetime
from pathlib import Path


RUTA_PROYECTO = Path(__file__).resolve().parents[2]
RUTA_BASE_DATOS = RUTA_PROYECTO / "incapacidades.db"


def obtener_conexion() -> sqlite3.Connection:
    """Crea una conexión con la base de datos."""

    conexion = sqlite3.connect(RUTA_BASE_DATOS)
    conexion.row_factory = sqlite3.Row

    return conexion


def crear_base_datos() -> None:
    """Crea la tabla de casos si todavía no existe."""

    with obtener_conexion() as conexion:
        conexion.execute(
            """
            CREATE TABLE IF NOT EXISTS casos_incapacidad (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                tipo_incapacidad TEXT NOT NULL,
                salario REAL NOT NULL,
                dias INTEGER NOT NULL,
                pago REAL NOT NULL
            )
            """
        )


def guardar_caso(
    tipo_incapacidad: str,
    salario: float,
    dias: int,
    pago: float,
) -> int:
    """Guarda un caso y retorna el ID generado."""

    fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    with obtener_conexion() as conexion:
        cursor = conexion.execute(
            """
            INSERT INTO casos_incapacidad (
                fecha,
                tipo_incapacidad,
                salario,
                dias,
                pago
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                fecha,
                tipo_incapacidad,
                salario,
                dias,
                pago,
            ),
        )

        return cursor.lastrowid


def obtener_casos() -> list[sqlite3.Row]:
    """Obtiene todos los casos guardados."""

    with obtener_conexion() as conexion:
        cursor = conexion.execute(
            """
            SELECT
                id,
                fecha,
                tipo_incapacidad,
                salario,
                dias,
                pago
            FROM casos_incapacidad
            ORDER BY id DESC
            """
        )

        return cursor.fetchall()


def buscar_casos(texto: str) -> list[sqlite3.Row]:
    """Busca casos por ID, fecha o tipo de incapacidad."""

    busqueda = f"%{texto.strip()}%"

    with obtener_conexion() as conexion:
        cursor = conexion.execute(
            """
            SELECT
                id,
                fecha,
                tipo_incapacidad,
                salario,
                dias,
                pago
            FROM casos_incapacidad
            WHERE CAST(id AS TEXT) LIKE ?
               OR fecha LIKE ?
               OR tipo_incapacidad LIKE ?
            ORDER BY id DESC
            """,
            (
                busqueda,
                busqueda,
                busqueda,
            ),
        )

        return cursor.fetchall()


def eliminar_caso(id_caso: int) -> None:
    """Elimina un caso según su ID."""

    with obtener_conexion() as conexion:
        conexion.execute(
            """
            DELETE FROM casos_incapacidad
            WHERE id = ?
            """,
            (id_caso,),
        )