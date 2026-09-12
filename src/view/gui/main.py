"""Interfaz gráfica de la calculadora de incapacidades usando Kivy."""

from kivy.app import App
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput

from src.model.incapacidad import (
    IncapacidadError,
    calcular_pago_incapacidad,
)


TIPOS_MOSTRADOS = {
    "Enfermedad general": "enfermedad_general",
    "Maternidad": "maternidad",
    "Riesgo laboral": "riesgo_laboral",
}


class CalculadoraIncapacidadGUI(BoxLayout):
    """Interfaz principal de la calculadora de incapacidades."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.padding = dp(20)
        self.spacing = dp(12)

        self.historial: list[str] = []

        self.crear_titulo()
        self.crear_formulario()
        self.crear_botones()
        self.crear_resultado()
        self.crear_historial()

    def crear_titulo(self) -> None:
        """Crea el título principal de la aplicación."""

        titulo = Label(
            text="Calculadora de Incapacidades",
            font_size="26sp",
            bold=True,
            size_hint_y=None,
            height=dp(55),
        )

        self.add_widget(titulo)

    def crear_formulario(self) -> None:
        """Crea los campos necesarios para realizar el cálculo."""

        self.add_widget(
            Label(
                text="Salario mensual (COP)",
                size_hint_y=None,
                height=dp(30),
            )
        )

        self.entrada_salario = TextInput(
            hint_text="Ejemplo: 2500000",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(45),
        )

        self.add_widget(self.entrada_salario)

        self.add_widget(
            Label(
                text="Días de incapacidad",
                size_hint_y=None,
                height=dp(30),
            )
        )

        self.entrada_dias = TextInput(
            hint_text="Ejemplo: 5",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(45),
        )

        self.add_widget(self.entrada_dias)

        self.add_widget(
            Label(
                text="Tipo de incapacidad",
                size_hint_y=None,
                height=dp(30),
            )
        )

        self.selector_tipo = Spinner(
            text="Enfermedad general",
            values=tuple(TIPOS_MOSTRADOS.keys()),
            size_hint_y=None,
            height=dp(45),
        )

        self.add_widget(self.selector_tipo)

    def crear_botones(self) -> None:
        """Crea los botones principales de la interfaz."""

        contenedor_botones = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50),
        )

        boton_calcular = Button(
            text="Calcular",
            font_size="17sp",
        )
        boton_calcular.bind(on_release=self.calcular)

        boton_limpiar = Button(
            text="Limpiar",
            font_size="17sp",
        )
        boton_limpiar.bind(on_release=self.limpiar)

        contenedor_botones.add_widget(boton_calcular)
        contenedor_botones.add_widget(boton_limpiar)

        self.add_widget(contenedor_botones)

    def crear_resultado(self) -> None:
        """Crea el área donde se muestra el resultado."""

        self.resultado = Label(
            text="Ingrese los datos para realizar el cálculo.",
            font_size="18sp",
            size_hint_y=None,
            height=dp(70),
        )

        self.add_widget(self.resultado)

    def crear_historial(self) -> None:
        """Crea el área del historial de cálculos."""

        self.add_widget(
            Label(
                text="Historial de cálculos",
                bold=True,
                font_size="18sp",
                size_hint_y=None,
                height=dp(35),
            )
        )

        scroll = ScrollView()

        self.texto_historial = Label(
            text="Todavía no hay cálculos.",
            size_hint_y=None,
            halign="left",
            valign="top",
        )

        self.texto_historial.bind(
            width=lambda instancia, ancho: setattr(
                instancia,
                "text_size",
                (ancho, None),
            )
        )

        self.texto_historial.bind(
            texture_size=lambda instancia, tamano: setattr(
                instancia,
                "height",
                tamano[1],
            )
        )

        scroll.add_widget(self.texto_historial)
        self.add_widget(scroll)

    def calcular(self, _boton: Button) -> None:
        """Obtiene los datos, realiza el cálculo y muestra el resultado."""

        try:
            salario = self.convertir_numero(
                texto=self.entrada_salario.text,
                campo="salario",
            )

            dias = self.convertir_numero(
                texto=self.entrada_dias.text,
                campo="días de incapacidad",
            )

            tipo_mostrado = self.selector_tipo.text
            tipo_incapacidad = TIPOS_MOSTRADOS[tipo_mostrado]

            pago = calcular_pago_incapacidad(
                salario_mensual=salario,
                dias_incapacidad=dias,
                tipo_incapacidad=tipo_incapacidad,
            )

            self.resultado.text = (
                f"Valor a pagar:\n"
                f"${pago:,.2f} COP"
            )

            self.agregar_al_historial(
                salario=salario,
                dias=dias,
                tipo=tipo_mostrado,
                pago=pago,
            )

        except ValueError as error:
            self.mostrar_error(str(error))

        except IncapacidadError as error:
            self.mostrar_error(str(error))

    def convertir_numero(self, texto: str, campo: str) -> float:
        """Convierte un campo de texto a número."""

        if not texto.strip():
            raise ValueError(
                f"Debe ingresar un valor para {campo}."
            )

        try:
            return float(texto)
        except ValueError as error:
            raise ValueError(
                f"El valor ingresado para {campo} debe ser numérico."
            ) from error

    def agregar_al_historial(
        self,
        salario: float,
        dias: float,
        tipo: str,
        pago: float,
    ) -> None:
        """Agrega un cálculo exitoso al historial de la sesión."""

        registro = (
            f"{tipo} | "
            f"{dias:g} días | "
            f"Salario: ${salario:,.2f} | "
            f"Pago: ${pago:,.2f}"
        )

        self.historial.append(registro)

        self.texto_historial.text = "\n\n".join(
            f"{indice}. {elemento}"
            for indice, elemento in enumerate(
                self.historial,
                start=1,
            )
        )

    def limpiar(self, _boton: Button) -> None:
        """Limpia los datos del formulario."""

        self.entrada_salario.text = ""
        self.entrada_dias.text = ""
        self.selector_tipo.text = "Enfermedad general"

        self.resultado.text = (
            "Ingrese los datos para realizar el cálculo."
        )

        self.entrada_salario.focus = True

    def mostrar_error(self, mensaje: str) -> None:
        """Muestra un mensaje de error amigable mediante un popup."""

        contenido = BoxLayout(
            orientation="vertical",
            padding=dp(15),
            spacing=dp(10),
        )

        mensaje_error = mensaje.replace("Error: ", "")

        etiqueta = Label(
            text=mensaje_error,
            halign="center",
            valign="middle",
        )

        etiqueta.bind(
            size=lambda instancia, tamano: setattr(
                instancia,
                "text_size",
                tamano,
            )
        )

        boton_cerrar = Button(
            text="Entendido",
            size_hint_y=None,
            height=dp(45),
        )

        contenido.add_widget(etiqueta)
        contenido.add_widget(boton_cerrar)

        popup = Popup(
            title="Dato inválido",
            content=contenido,
            size_hint=(0.85, 0.45),
            auto_dismiss=False,
        )

        boton_cerrar.bind(
            on_release=popup.dismiss
        )

        popup.open()


class CalculadoraIncapacidadesApp(App):
    """Aplicación Kivy de la calculadora de incapacidades."""

    title = "Calculadora de Incapacidades"

    def build(self) -> CalculadoraIncapacidadGUI:
        return CalculadoraIncapacidadGUI()


if __name__ == "__main__":
    CalculadoraIncapacidadesApp().run()