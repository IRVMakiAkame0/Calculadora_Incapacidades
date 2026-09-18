"""
Casos de prueba para el cálculo de pago por incapacidad.

Los casos están organizados en tres grupos:

- Casos normales: situaciones de uso cotidiano.
- Casos extraordinarios: datos válidos que representan límites
  o situaciones poco frecuentes.
- Casos de error: datos inválidos que deben ser rechazados.

Ejecutar con:

    python -m unittest test_incapacidad.py -v
"""

import unittest

from src.model.incapacidad import (
    DiasIncapacidadInvalidos,
    SalarioInvalido,
    TipoIncapacidadInvalido,
    ValorNoNumerico,
    calcular_pago_incapacidad,
)


class TestCasosNormales(unittest.TestCase):
    """Pruebas para situaciones normales de cálculo."""

    def test_salario_alto_con_incapacidad_de_5_dias(self):
        """Calcula correctamente una incapacidad estándar de 5 días."""
        pago = calcular_pago_incapacidad(
            salario_mensual=5_300_000,
            dias_incapacidad=5,
        )

        self.assertAlmostEqual(
            pago,
            588_918.3333333333,
            places=5,
        )

    def test_salario_medio_con_incapacidad_de_10_dias(self):
        """Calcula correctamente una incapacidad de 10 días."""
        pago = calcular_pago_incapacidad(
            salario_mensual=2_500_000,
            dias_incapacidad=10,
        )

        self.assertAlmostEqual(
            pago,
            555_583.3333333333,
            places=5,
        )

    def test_salario_minimo_con_incapacidad_de_3_dias(self):
        """Calcula correctamente una incapacidad corta de 3 días."""
        pago = calcular_pago_incapacidad(
            salario_mensual=1_750_905,
            dias_incapacidad=3,
        )

        self.assertAlmostEqual(
            pago,
            116_732.83635,
            places=5,
        )


class TestCasosExtraordinarios(unittest.TestCase):
    """Pruebas para situaciones válidas poco frecuentes o extremas."""

    def test_incapacidad_minima_de_un_dia(self):
        """Calcula correctamente una incapacidad de un solo día."""
        pago = calcular_pago_incapacidad(
            salario_mensual=1_750_905,
            dias_incapacidad=1,
        )

        self.assertAlmostEqual(
            pago,
            38_910.94545,
            places=5,
        )

    def test_incapacidad_prolongada_de_180_dias(self):
        """Calcula correctamente una incapacidad prolongada de 180 días."""
        pago = calcular_pago_incapacidad(
            salario_mensual=15_000_000,
            dias_incapacidad=180,
        )

        self.assertAlmostEqual(
            pago,
            60_003_000,
            places=5,
        )

    def test_salario_decimal_con_incapacidad_de_45_dias(self):
        """Calcula correctamente usando un salario con decimales."""
        pago = calcular_pago_incapacidad(
            salario_mensual=987_654.32,
            dias_incapacidad=45,
        )

        self.assertAlmostEqual(
            pago,
            987_703.702716,
            places=5,
        )

    def test_incapacidad_laboral_de_720_dias(self):
        """Calcula correctamente 720 días con reconocimiento del 100 %."""
        pago = calcular_pago_incapacidad(
            salario_mensual=3_000_000,
            dias_incapacidad=720,
            tipo_incapacidad="riesgo_laboral",
        )

        self.assertAlmostEqual(
            pago,
            72_000_000,
            places=5,
        )

    def test_incapacidad_de_900_dias_por_enfermedad_general(self):
        """Calcula correctamente una incapacidad superior a 720 días."""
        pago = calcular_pago_incapacidad(
            salario_mensual=2_200_000,
            dias_incapacidad=900,
            tipo_incapacidad="enfermedad_general",
        )

        self.assertAlmostEqual(
            pago,
            44_002_200,
            places=5,
        )


class TestCasosDeError(unittest.TestCase):
    """Pruebas para datos inválidos."""

    def test_rechaza_salario_negativo(self):
        """Rechaza un salario mensual negativo."""
        with self.assertRaises(SalarioInvalido):
            calcular_pago_incapacidad(
                salario_mensual=-1_000_000,
                dias_incapacidad=5,
            )

    def test_rechaza_salario_igual_a_cero(self):
        """Rechaza un salario mensual igual a cero."""
        with self.assertRaises(SalarioInvalido):
            calcular_pago_incapacidad(
                salario_mensual=0,
                dias_incapacidad=10,
            )

    def test_rechaza_dias_de_incapacidad_negativos(self):
        """Rechaza una cantidad negativa de días de incapacidad."""
        with self.assertRaises(DiasIncapacidadInvalidos):
            calcular_pago_incapacidad(
                salario_mensual=1_200_000,
                dias_incapacidad=-3,
            )

    def test_rechaza_salario_no_numerico(self):
        """Rechaza un salario que no sea numérico."""
        with self.assertRaises(ValorNoNumerico):
            calcular_pago_incapacidad(
                salario_mensual="N/A",
                dias_incapacidad=5,
            )

    def test_rechaza_tipo_de_incapacidad_no_reconocido(self):
        """Rechaza un tipo de incapacidad que no está registrado."""
        with self.assertRaises(TipoIncapacidadInvalido):
            calcular_pago_incapacidad(
                salario_mensual=1_500_000,
                dias_incapacidad=10,
                tipo_incapacidad="desempleo",
            )

    def test_rechaza_dias_de_incapacidad_no_numericos(self):
        """Rechaza días de incapacidad que no sean numéricos."""
        with self.assertRaises(ValorNoNumerico):
            calcular_pago_incapacidad(
                salario_mensual=1_500_000,
                dias_incapacidad="diez",
            )


if __name__ == "__main__":
    unittest.main()