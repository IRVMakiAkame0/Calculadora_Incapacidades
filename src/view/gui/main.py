"""Interfaz gráfica profesional de la calculadora de incapacidades."""

import platform
import subprocess

from kivy.app import App
from kivy.core.window import Window
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.textinput import TextInput
from kivy.utils import get_color_from_hex

from src.model.incapacidad import (
    IncapacidadError,
    calcular_pago_incapacidad,
)

from src.database.database import (
    crear_base_datos, 
    guardar_caso,
    obtener_casos,
)


TIPOS_MOSTRADOS = {
    "Enfermedad general": "enfermedad_general",
    "Maternidad": "maternidad",
    "Riesgo laboral": "riesgo_laboral",
}


def color(hexadecimal: str) -> list[float]:
    """Convierte un color hexadecimal a RGBA."""

    return get_color_from_hex(hexadecimal)


PALETAS = {
    "claro": {
        "fondo": color("#F4F7FB"),
        "tarjeta": color("#FFFFFF"),
        "tarjeta_secundaria": color("#EEF4FF"),
        "texto": color("#14213D"),
        "texto_secundario": color("#000000"),
        "borde": color("#D7DFEA"),
        "campo": color("#F8FAFC"),
        "azul": color("#2563EB"),
        "azul_secundario": color("#3B82F6"),
        "azul_suave": color("#E8F0FF"),
        "blanco": color("#FFFFFF"),
        "error": color("#DC2626"),
    },
    "oscuro": {
        "fondo": color("#0F172A"),
        "tarjeta": color("#172033"),
        "tarjeta_secundaria": color("#1D2940"),
        "texto": color("#F8FAFC"),
        "texto_secundario": color("#FFFFFF"),
        "borde": color("#334155"),
        "campo": color("#111827"),
        "azul": color("#3B82F6"),
        "azul_secundario": color("#60A5FA"),
        "azul_suave": color("#172554"),
        "blanco": color("#FFFFFF"),
        "error": color("#F87171"),
    },
}


def detectar_tema_sistema() -> str:
    """Intenta detectar si el sistema utiliza tema claro u oscuro."""

    sistema = platform.system()

    if sistema == "Windows":
        try:
            import winreg

            ruta = (
                r"Software\Microsoft\Windows\CurrentVersion"
                r"\Themes\Personalize"
            )

            with winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                ruta,
            ) as clave:
                valor, _ = winreg.QueryValueEx(
                    clave,
                    "AppsUseLightTheme",
                )

            return "claro" if valor == 1 else "oscuro"

        except (OSError, ImportError):
            return "claro"

    if sistema == "Darwin":
        try:
            resultado = subprocess.run(
                [
                    "defaults",
                    "read",
                    "-g",
                    "AppleInterfaceStyle",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            if "Dark" in resultado.stdout:
                return "oscuro"

        except OSError:
            pass

        return "claro"

    if sistema == "Linux":
        try:
            resultado = subprocess.run(
                [
                    "gsettings",
                    "get",
                    "org.gnome.desktop.interface",
                    "color-scheme",
                ],
                capture_output=True,
                text=True,
                check=False,
            )

            if "dark" in resultado.stdout.lower():
                return "oscuro"

        except OSError:
            pass

    return "claro"


def formatear_cop(valor: float) -> str:
    """Formatea un número utilizando formato monetario colombiano."""

    formato = f"{valor:,.2f}"

    formato = (
        formato.replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"$ {formato}"


class Tarjeta(BoxLayout):
    """Contenedor con fondo y bordes redondeados."""

    color_fondo = ListProperty([1, 1, 1, 1])
    color_borde = ListProperty([0.8, 0.8, 0.8, 1])
    radio = NumericProperty(dp(18))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        with self.canvas.before:
            self._color_fondo = Color(*self.color_fondo)

            self._fondo = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.radio],
            )

            self._color_borde = Color(*self.color_borde)

            self._borde = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    self.radio,
                ),
                width=1,
            )

        self.bind(
            pos=self._actualizar_forma,
            size=self._actualizar_forma,
            color_fondo=self._actualizar_colores,
            color_borde=self._actualizar_colores,
        )

    def _actualizar_forma(self, *_args) -> None:
        self._fondo.pos = self.pos
        self._fondo.size = self.size

        self._borde.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            self.radio,
        )

    def _actualizar_colores(self, *_args) -> None:
        self._color_fondo.rgba = self.color_fondo
        self._color_borde.rgba = self.color_borde


class CampoTexto(TextInput):
    """Campo de texto con apariencia moderna."""

    color_fondo = ListProperty([1, 1, 1, 1])
    color_borde = ListProperty([0.8, 0.8, 0.8, 1])
    radio = NumericProperty(dp(12))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_active = ""
        self.background_color = [0, 0, 0, 0]

        self.padding = [dp(14), dp(13)]
        self.font_size = "16sp"

        with self.canvas.before:
            self._color_fondo = Color(*self.color_fondo)

            self._fondo = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.radio],
            )

            self._color_borde = Color(*self.color_borde)

            self._borde = Line(
                rounded_rectangle=(
                    self.x,
                    self.y,
                    self.width,
                    self.height,
                    self.radio,
                ),
                width=1,
            )

        self.bind(
            pos=self._actualizar_forma,
            size=self._actualizar_forma,
            color_fondo=self._actualizar_colores,
            color_borde=self._actualizar_colores,
        )

    def _actualizar_forma(self, *_args) -> None:
        self._fondo.pos = self.pos
        self._fondo.size = self.size

        self._borde.rounded_rectangle = (
            self.x,
            self.y,
            self.width,
            self.height,
            self.radio,
        )

    def _actualizar_colores(self, *_args) -> None:
        self._color_fondo.rgba = self.color_fondo
        self._color_borde.rgba = self.color_borde


class BotonRedondeado(Button):
    """Botón con fondo redondeado."""

    color_fondo = ListProperty([0.15, 0.39, 0.92, 1])
    radio = NumericProperty(dp(12))

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.background_normal = ""
        self.background_down = ""
        self.background_color = [0, 0, 0, 0]

        with self.canvas.before:
            self._color_fondo = Color(*self.color_fondo)

            self._fondo = RoundedRectangle(
                pos=self.pos,
                size=self.size,
                radius=[self.radio],
            )

        self.bind(
            pos=self._actualizar_forma,
            size=self._actualizar_forma,
            color_fondo=self._actualizar_color,
        )

    def _actualizar_forma(self, *_args) -> None:
        self._fondo.pos = self.pos
        self._fondo.size = self.size

    def _actualizar_color(self, *_args) -> None:
        self._color_fondo.rgba = self.color_fondo


class CalculadoraIncapacidadGUI(BoxLayout):
    """Interfaz principal de la calculadora de incapacidades."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.padding = dp(20)
        self.spacing = dp(12)

        self.historial: list[str] = []

        self.tarjetas: list[Tarjeta] = []
        self.labels_principales: list[Label] = []
        self.labels_secundarios: list[Label] = []
        self.campos: list[CampoTexto] = []

        self.modo_tema = "automatico"

        self.crear_encabezado()
        self.crear_contenido()

        self.aplicar_tema()
        self.cargar_historial()

    def crear_label(
        self,
        texto: str,
        secundario: bool = False,
        **kwargs,
    ) -> Label:
        """Crea una etiqueta registrada para el sistema de temas."""

        etiqueta = Label(
            text=texto,
            **kwargs,
        )

        if secundario:
            self.labels_secundarios.append(etiqueta)
        else:
            self.labels_principales.append(etiqueta)

        return etiqueta

    def crear_encabezado(self) -> None:
        """Crea el encabezado principal."""

        encabezado = BoxLayout(
            orientation="horizontal",
            spacing=dp(15),
            size_hint_y=None,
            height=dp(78),
        )

        textos = BoxLayout(
            orientation="vertical",
            spacing=0,
        )

        titulo = self.crear_label(
            "Calculadora de Incapacidades",
            bold=True,
            font_size="26sp",
            halign="left",
            valign="middle",
        )

        titulo.bind(
            size=lambda instancia, tamano: setattr(
                instancia,
                "text_size",
                tamano,
            )
        )

        subtitulo = self.crear_label(
            "Simulación clara y rápida del pago por incapacidad",
            secundario=True,
            font_size="13sp",
            halign="left",
            valign="middle",
        )

        subtitulo.bind(
            size=lambda instancia, tamano: setattr(
                instancia,
                "text_size",
                tamano,
            )
        )

        textos.add_widget(titulo)
        textos.add_widget(subtitulo)

        self.selector_tema = Spinner(
            text="Tema: Automático",
            values=(
                "Tema: Automático",
                "Tema: Claro",
                "Tema: Oscuro",
            ),
            size_hint_x=None,
            width=dp(170),
            size_hint_y=None,
            height=dp(44),
            font_size="14sp",
        )

        self.selector_tema.bind(
            text=self.cambiar_tema
        )

        encabezado.add_widget(textos)
        encabezado.add_widget(self.selector_tema)

        self.add_widget(encabezado)

    def crear_contenido(self) -> None:
        """Crea el contenido desplazable de la aplicación."""

        scroll = ScrollView(
            do_scroll_x=False,
        )

        contenido = BoxLayout(
            orientation="vertical",
            spacing=dp(16),
            padding=[0, dp(8), 0, dp(20)],
            size_hint_y=None,
        )

        contenido.bind(
            minimum_height=contenido.setter("height")
        )

        self.crear_tarjeta_formulario(contenido)
        self.crear_tarjeta_resultado(contenido)
        self.crear_tarjeta_historial(contenido)
        self.crear_tarjeta_informacion(contenido)

        scroll.add_widget(contenido)
        self.add_widget(scroll)

    def crear_tarjeta_formulario(
        self,
        contenido: BoxLayout,
    ) -> None:
        """Crea la tarjeta principal del formulario."""

        tarjeta = Tarjeta(
            orientation="vertical",
            spacing=dp(10),
            padding=dp(20),
            size_hint_y=None,
            height=dp(385),
        )

        self.tarjetas.append(tarjeta)

        tarjeta.add_widget(
            self.crear_label(
                "Simular pago",
                bold=True,
                font_size="20sp",
                size_hint_y=None,
                height=dp(35),
                halign="left",
            )
        )

        tarjeta.add_widget(
            self.crear_label(
                "Ingresa los datos de la incapacidad.",
                secundario=True,
                font_size="13sp",
                size_hint_y=None,
                height=dp(25),
                halign="left",
            )
        )

        tarjeta.add_widget(
            self.crear_label(
                "Tipo de incapacidad",
                font_size="15sp",
                size_hint_y=None,
                height=dp(28),
                halign="left",
            )
        )

        self.selector_tipo = Spinner(
            text="Enfermedad general",
            values=tuple(TIPOS_MOSTRADOS.keys()),
            size_hint_y=None,
            height=dp(48),
            font_size="16sp",
        )

        tarjeta.add_widget(self.selector_tipo)

        tarjeta.add_widget(
            self.crear_label(
                "Salario mensual (COP)",
                font_size="15sp",
                size_hint_y=None,
                height=dp(28),
                halign="left",
            )
        )

        self.entrada_salario = CampoTexto(
            hint_text="Ejemplo: 2500000",
            multiline=False,
            input_filter="int",
            size_hint_y=None,
            height=dp(50),
        )

        self.campos.append(self.entrada_salario)
        tarjeta.add_widget(self.entrada_salario)

        tarjeta.add_widget(
            self.crear_label(
                "Días de incapacidad",
                font_size="15sp",
                size_hint_y=None,
                height=dp(28),
                halign="left",
            )
        )

        self.entrada_dias = CampoTexto(
            hint_text="Ejemplo: 5",
            multiline=False,
            input_filter="float",
            size_hint_y=None,
            height=dp(50),
        )

        self.campos.append(self.entrada_dias)
        tarjeta.add_widget(self.entrada_dias)

        botones = BoxLayout(
            orientation="horizontal",
            spacing=dp(10),
            size_hint_y=None,
            height=dp(50),
        )

        self.boton_calcular = BotonRedondeado(
            text="Calcular pago",
            bold=True,
            font_size="16sp",
        )

        self.boton_calcular.bind(
            on_release=self.calcular
        )

        self.boton_limpiar = BotonRedondeado(
            text="Limpiar",
            font_size="16sp",
        )

        self.boton_limpiar.bind(
            on_release=self.limpiar
        )

        botones.add_widget(self.boton_calcular)
        botones.add_widget(self.boton_limpiar)

        tarjeta.add_widget(botones)

        contenido.add_widget(tarjeta)

    def crear_tarjeta_resultado(
        self,
        contenido: BoxLayout,
    ) -> None:
        """Crea la tarjeta donde se muestra el resultado."""

        self.tarjeta_resultado = Tarjeta(
            orientation="vertical",
            spacing=dp(5),
            padding=dp(18),
            size_hint_y=None,
            height=dp(120),
        )

        self.tarjetas.append(self.tarjeta_resultado)

        resultado_titulo = self.crear_label(
            "Resultado estimado",
            secundario=True,
            font_size="13sp",
            size_hint_y=None,
            height=dp(25),
            halign="left",
        )

        self.resultado = self.crear_label(
            "Completa los datos para realizar la simulación.",
            bold=True,
            font_size="22sp",
            size_hint_y=None,
            height=dp(55),
            halign="left",
            valign="middle",
        )

        self.resultado.bind(
            size=lambda instancia, tamano: setattr(
                instancia,
                "text_size",
                tamano,
            )
        )

        self.tarjeta_resultado.add_widget(resultado_titulo)
        self.tarjeta_resultado.add_widget(self.resultado)

        contenido.add_widget(self.tarjeta_resultado)

    def crear_tarjeta_historial(
        self,
        contenido: BoxLayout,
    ) -> None:
        """Crea la tarjeta del historial."""

        tarjeta = Tarjeta(
            orientation="vertical",
            spacing=dp(8),
            padding=dp(18),
            size_hint_y=None,
            height=dp(210),
        )

        self.tarjetas.append(tarjeta)

        tarjeta.add_widget(
            self.crear_label(
                "Historial de la sesión",
                bold=True,
                font_size="18sp",
                size_hint_y=None,
                height=dp(35),
                halign="left",
            )
        )

        tarjeta.add_widget(
            self.crear_label(
                "Los cálculos exitosos aparecerán aquí.",
                secundario=True,
                font_size="13sp",
                size_hint_y=None,
                height=dp(24),
                halign="left",
            )
        )

        scroll = ScrollView()

        self.texto_historial = self.crear_label(
            "Todavía no hay cálculos.",
            secundario=True,
            size_hint_y=None,
            halign="left",
            valign="top",
            font_size="14sp",
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
        tarjeta.add_widget(scroll)

        contenido.add_widget(tarjeta)

    def crear_tarjeta_informacion(
        self,
        contenido: BoxLayout,
    ) -> None:
        """Muestra información sobre los cálculos disponibles."""

        tarjeta = Tarjeta(
            orientation="vertical",
            spacing=dp(6),
            padding=dp(18),
            size_hint_y=None,
            height=dp(195),
        )

        self.tarjetas.append(tarjeta)

        tarjeta.add_widget(
            self.crear_label(
                "¿Cómo funciona esta herramienta?",
                bold=True,
                font_size="18sp",
                size_hint_y=None,
                height=dp(35),
                halign="left",
            )
        )

        textos = [
            "• Enfermedad general: reconocimiento del 66,67%.",
            "• Maternidad: reconocimiento del 100%.",
            "• Riesgo laboral: reconocimiento del 100%.",
        ]

        for texto in textos:
            etiqueta = self.crear_label(
                texto,
                secundario=True,
                font_size="14sp",
                size_hint_y=None,
                height=dp(30),
                halign="left",
            )

            tarjeta.add_widget(etiqueta)

        tarjeta.add_widget(
            self.crear_label(
                "Los valores corresponden a las reglas definidas "
                "en el proyecto.",
                secundario=True,
                font_size="12sp",
                size_hint_y=None,
                height=dp(35),
                halign="left",
            )
        )

        contenido.add_widget(tarjeta)

    def cambiar_tema(
        self,
        _spinner: Spinner,
        texto: str,
    ) -> None:
        """Cambia el tema visual elegido por el usuario."""

        if texto == "Tema: Claro":
            self.modo_tema = "claro"

        elif texto == "Tema: Oscuro":
            self.modo_tema = "oscuro"

        else:
            self.modo_tema = "automatico"

        self.aplicar_tema()

    def obtener_tema_actual(self) -> str:
        """Retorna el tema que debe mostrarse."""

        if self.modo_tema == "automatico":
            return detectar_tema_sistema()

        return self.modo_tema

    def aplicar_tema(self) -> None:
        """Aplica los colores correspondientes al tema actual."""

        tema = self.obtener_tema_actual()
        paleta = PALETAS[tema]

        Window.clearcolor = paleta["fondo"]

        for tarjeta in self.tarjetas:
            tarjeta.color_fondo = paleta["tarjeta"]
            tarjeta.color_borde = paleta["borde"]

        self.tarjeta_resultado.color_fondo = paleta["azul_suave"]

        for etiqueta in self.labels_principales:
            etiqueta.color = paleta["texto"]

        for etiqueta in self.labels_secundarios:
            etiqueta.color = paleta["texto_secundario"]

        self.resultado.color = paleta["azul_secundario"]

        for campo in self.campos:
            campo.color_fondo = paleta["campo"]
            campo.color_borde = paleta["borde"]
            campo.foreground_color = paleta["texto"]
            campo.hint_text_color = paleta["texto_secundario"]
            campo.cursor_color = paleta["azul"]

        self.selector_tipo.background_normal = ""
        self.selector_tipo.background_color = paleta["campo"]
        self.selector_tipo.color = paleta["texto"]

        self.selector_tema.background_normal = ""
        self.selector_tema.background_color = paleta["tarjeta"]
        self.selector_tema.color = paleta["texto"]

        self.boton_calcular.color_fondo = paleta["azul"]
        self.boton_calcular.color = paleta["blanco"]

        self.boton_limpiar.color_fondo = paleta["tarjeta_secundaria"]
        self.boton_limpiar.color = paleta["texto"]

    def calcular(self, _boton: Button) -> None:
        """Obtiene los datos, calcula y muestra el resultado."""

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

            id_caso = guardar_caso(
                tipo_incapacidad=tipo_mostrado,
                salario=salario,
                dias=int(dias),
                pago=pago,
            )

            self.resultado.text = (
                f"{formatear_cop(pago)} COP\n"
                f"{tipo_mostrado} | {dias:g} días | Caso #{id_caso}"
            )
            
        except (ValueError, IncapacidadError) as error:
            self.mostrar_error(str(error))

    def convertir_numero(
        self,
        texto: str,
        campo: str,
    ) -> float:
        """Convierte un campo de texto a número."""

        if not texto.strip():
            raise ValueError(
                f"Debes ingresar un valor para {campo}."
            )

        try:
            return float(texto)

        except ValueError as error:
            raise ValueError(
                f"El valor de {campo} debe ser numérico."
            ) from error
            
    def cargar_historial(self) -> None:
        """Carga en pantalla los casos guardados en la base de datos"""
        casos = obtener_casos()
        
        if not casos:
            self.texto_historial.text = "Todavia no hay calculos"
            return
        
        registros = []
        
        for caso in casos:
            registro = (
                f"Caso #{caso['id']} | {caso['tipo_incapacidad']} | "
                f"{caso['dias']:g} dias\n"
                f"Salario: {formatear_cop(caso['salario'])} | "
                f"Pago: {formatear_cop(caso['pago'])}"
            )
            
            registros.append(registro)
        
        self.texto_historial.text = "\n\n".join(registros)
            

    def agregar_al_historial(
        self,
        salario: float,
        dias: float,
        tipo: str,
        pago: float,
    ) -> None:
        """Agrega un cálculo exitoso al historial."""

        registro = (
            f"{tipo} · {dias:g} días\n"
            f"Salario: {formatear_cop(salario)} · "
            f"Pago: {formatear_cop(pago)}"
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
        """Limpia los campos del formulario."""

        self.entrada_salario.text = ""
        self.entrada_dias.text = ""
        self.selector_tipo.text = "Enfermedad general"

        self.resultado.text = (
            "Completa los datos para realizar la simulación."
        )

        self.entrada_salario.focus = True

    def mostrar_error(self, mensaje: str) -> None:
        """Muestra un mensaje de error amigable."""

        paleta = PALETAS[self.obtener_tema_actual()]

        contenido = Tarjeta(
            orientation="vertical",
            spacing=dp(15),
            padding=dp(20),
            color_fondo=paleta["tarjeta"],
            color_borde=paleta["borde"],
        )

        mensaje_error = mensaje.replace("Error: ", "")

        etiqueta = Label(
            text=mensaje_error,
            color=paleta["texto"],
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

        boton_cerrar = BotonRedondeado(
            text="Entendido",
            color_fondo=paleta["azul"],
            color=paleta["blanco"],
            size_hint_y=None,
            height=dp(46),
        )

        contenido.add_widget(etiqueta)
        contenido.add_widget(boton_cerrar)

        popup = Popup(
            title="Revisa los datos",
            content=contenido,
            size_hint=(0.85, 0.45),
            auto_dismiss=False,
        )

        boton_cerrar.bind(
            on_release=popup.dismiss
        )

        popup.open()


class CalculadoraIncapacidadesApp(App):
    """Aplicación gráfica de la calculadora."""

    title = "Calculadora de Incapacidades"

    def build(self) -> CalculadoraIncapacidadGUI:
        crear_base_datos()
        return CalculadoraIncapacidadGUI()
    


if __name__ == "__main__":
    CalculadoraIncapacidadesApp().run()