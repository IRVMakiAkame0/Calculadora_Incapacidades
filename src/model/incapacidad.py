"""
Módulo de cálculo de pago por incapacidad laboral en Colombia.

Fórmula:
    valor_dia = salario_mensual / DIAS_MES
    pago = valor_dia * porcentaje_reconocimiento * dias_incapacidad

El porcentaje de reconocimiento depende del tipo de incapacidad.
"""

from collections.abc import Iterable
from typing import Final


DIAS_MES: Final = 30

TIPOS_INCAPACIDAD: Final[dict[str, float]] = {
    "enfermedad_general": 0.6667,
    "maternidad": 1.0,
    "riesgo_laboral": 1.0,
}


class IncapacidadError(Exception):
    """Excepción base para los errores de la calculadora."""


class ValorNoNumerico(IncapacidadError, TypeError):
    """Indica que un campo que debía ser numérico no lo es."""

    def __init__(
        self,
        nombre_campo: str,
        valor: object,
    ) -> None:
        mensaje = (
            f"Error: '{nombre_campo}' debe ser un valor numérico "
            f"(recibido: {valor}). Por favor ingrese un número."
        )

        super().__init__(mensaje)


class SalarioInvalido(IncapacidadError):
    """Indica que el salario mensual no es válido."""

    def __init__(self, salario_mensual: float) -> None:
        mensaje = (
            "Error: el salario debe ser un valor positivo mayor "
            f"a cero (recibido: {salario_mensual}). "
            "Por favor asigne un salario válido."
        )

        super().__init__(mensaje)


class DiasIncapacidadInvalidos(IncapacidadError):
    """Indica que la cantidad de días de incapacidad no es válida."""

    def __init__(self, dias_incapacidad: float) -> None:
        mensaje = (
            "Error: los días de incapacidad deben ser un valor "
            f"positivo mayor a cero (recibido: {dias_incapacidad}). "
            "Debe reportar al menos 1 día de incapacidad."
        )

        super().__init__(mensaje)


class TipoIncapacidadInvalido(IncapacidadError):
    """Indica que el tipo de incapacidad no está registrado."""

    def __init__(
        self,
        tipo_incapacidad: str,
        tipos_validos: Iterable[str],
    ) -> None:
        tipos_disponibles = ", ".join(tipos_validos)

        mensaje = (
            f"Error: '{tipo_incapacidad}' no es un tipo de "
            "incapacidad válido. "
            f"Use uno de: {tipos_disponibles}"
        )

        super().__init__(mensaje)


def _validar_numerico(
    valor: int | float,
    nombre_campo: str,
) -> None:
    """Valida que un valor sea numérico."""
    if not isinstance(valor, (int, float)):
        raise ValorNoNumerico(
            nombre_campo=nombre_campo,
            valor=valor,
        )


def validar_salario(salario_mensual: float) -> None:
    """
    Valida el salario mensual.

    El salario debe ser numérico y estrictamente mayor que cero.

    Raises:
        ValorNoNumerico: Si el salario no es numérico.
        SalarioInvalido: Si el salario es cero o negativo.
    """
    _validar_numerico(
        valor=salario_mensual,
        nombre_campo="salario_mensual",
    )

    if salario_mensual <= 0:
        raise SalarioInvalido(salario_mensual)


def validar_dias_incapacidad(
    dias_incapacidad: float,
) -> None:
    """
    Valida la cantidad de días de incapacidad.

    Los días deben ser numéricos y estrictamente mayores que cero.

    Raises:
        ValorNoNumerico: Si los días no son numéricos.
        DiasIncapacidadInvalidos: Si los días son cero o negativos.
    """
    _validar_numerico(
        valor=dias_incapacidad,
        nombre_campo="dias_incapacidad",
    )

    if dias_incapacidad <= 0:
        raise DiasIncapacidadInvalidos(dias_incapacidad)


def validar_entradas(
    salario_mensual: float,
    dias_incapacidad: float,
) -> None:
    """
    Valida todos los datos necesarios para realizar el cálculo.
    """
    validar_salario(salario_mensual)
    validar_dias_incapacidad(dias_incapacidad)


def obtener_porcentaje_reconocimiento(
    tipo_incapacidad: str,
) -> float:
    """
    Obtiene el porcentaje de reconocimiento según el tipo.

    Raises:
        TipoIncapacidadInvalido: Si el tipo no está registrado.

    Returns:
        Porcentaje de reconocimiento económico.
    """
    if tipo_incapacidad not in TIPOS_INCAPACIDAD:
        raise TipoIncapacidadInvalido(
            tipo_incapacidad=tipo_incapacidad,
            tipos_validos=TIPOS_INCAPACIDAD.keys(),
        )

    return TIPOS_INCAPACIDAD[tipo_incapacidad]


def calcular_valor_dia(salario_mensual: float) -> float:
    """Calcula el valor correspondiente a un día de salario."""
    return salario_mensual / DIAS_MES


def calcular_pago(
    valor_dia: float,
    porcentaje_reconocimiento: float,
    dias_incapacidad: float,
) -> float:
    """Calcula el pago total de la incapacidad."""
    return (
        valor_dia
        * porcentaje_reconocimiento
        * dias_incapacidad
    )


def calcular_pago_incapacidad(
    salario_mensual: float,
    dias_incapacidad: float,
    tipo_incapacidad: str = "enfermedad_general",
) -> float:
    """
    Calcula el pago correspondiente a una incapacidad.

    Args:
        salario_mensual: Salario mensual del empleado.
        dias_incapacidad: Cantidad de días de incapacidad.
        tipo_incapacidad: Tipo registrado de incapacidad.

    Returns:
        Valor total a pagar por la incapacidad.

    Raises:
        ValorNoNumerico: Si el salario o los días no son numéricos.
        SalarioInvalido: Si el salario es cero o negativo.
        DiasIncapacidadInvalidos: Si los días son cero o negativos.
        TipoIncapacidadInvalido: Si el tipo no está registrado.
    """
    validar_entradas(
        salario_mensual=salario_mensual,
        dias_incapacidad=dias_incapacidad,
    )

    porcentaje_reconocimiento = (
        obtener_porcentaje_reconocimiento(
            tipo_incapacidad=tipo_incapacidad,
        )
    )

    valor_dia = calcular_valor_dia(
        salario_mensual=salario_mensual,
    )

    return calcular_pago(
        valor_dia=valor_dia,
        porcentaje_reconocimiento=porcentaje_reconocimiento,
        dias_incapacidad=dias_incapacidad,
    )