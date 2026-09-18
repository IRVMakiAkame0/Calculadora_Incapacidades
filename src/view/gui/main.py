"""Interfaz gráfica de la calculadora de incapacidades."""

import platform
import subprocess

from kivy.core.window import Window
from kivy.graphics import Color, Line, RoundedRectangle
from kivy.metrics import dp
from kivy.properties import ListProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.utils import get_color_from_hex

from kivymd.app import MDApp
from kivymd.uix.button import MDButton, MDButtonText
from kivymd.uix.dialog import (
    MDDialog,
    MDDialogButtonContainer,
    MDDialogHeadlineText,
    MDDialogSupportingText,
)
from kivymd.uix.label import MDLabel
from kivymd.uix.menu import MDDropdownMenu
from kivymd.uix.textfield import MDTextField, MDTextFieldHintText

from src.database.database import (
    crear_base_datos,
    guardar_caso,
    obtener_casos,
)
from src.model.incapacidad import (
    IncapacidadError,
    calcular_pago_incapacidad,
)


# ============================================================
# CONSTANTES DEL NEGOCIO
# ============================================================

TIPO_ENFERMEDAD_GENERAL = "Enfermedad general"
TIPO_MATERNIDAD = "Maternidad"
TIPO_RIESGO_LABORAL = "Riesgo laboral"

TIPOS_MOSTRADOS = {
    TIPO_ENFERMEDAD_GENERAL: "enfermedad_general",
    TIPO_MATERNIDAD: "maternidad",
    TIPO_RIESGO_LABORAL: "riesgo_laboral",
}

# ============================================================
# CONSTANTES DE TEMA
# ============================================================

TEMA_AUTOMATICO = "automatico"
TEMA_CLARO = "claro"
TEMA_OSCURO = "oscuro"

TEXTO_TEMA_AUTOMATICO = "Tema: Automático"
TEXTO_TEMA_CLARO = "Tema: Claro"
TEXTO_TEMA_OSCURO = "Tema: Oscuro"

# ============================================================
# CONSTANTES DE INTERFAZ
# ============================================================

TITULO_APLICACION = "Calculadora de Incapacidades"
SUBTITULO_APLICACION = (
    "Simulación clara y rápida del pago por incapacidad"
)

TEXTO_RESULTADO_INICIAL = (
    "Completa los datos para realizar la simulación."
)

TEXTO_HISTORIAL_VACIO = "Todavía no hay cálculos."

TEXTO_BOTON_CALCULAR = "Calcular pago"
TEXTO_BOTON_LIMPIAR = "Limpiar"
TEXTO_BOTON_ENTENDIDO = "Entendido"

TEXTO_TITULO_ERROR = "Revisa los datos"

VALOR_TIPO_INICIAL = TIPO_ENFERMEDAD_GENERAL

# ============================================================
# CONSTANTES DE DIMENSIONES
# ============================================================

ESPACIADO_PRINCIPAL = dp(12)
ESPACIADO_TARJETA = dp(10)
ESPACIADO_CONTENIDO = dp(16)
ESPACIADO_ENCABEZADO = dp(15)

PADDING_PRINCIPAL = dp(20)
PADDING_TARJETA = dp(20)
PADDING_RESULTADO = dp(18)

ALTURA_ENCABEZADO = dp(78)
ALTURA_TARJETA_FORMULARIO = dp(390)
ALTURA_TARJETA_RESULTADO = dp(120)
ALTURA_TARJETA_HISTORIAL = dp(210)
ALTURA_TARJETA_INFORMACION = dp(195)

ALTURA_CAMPO = dp(50)
ALTURA_BOTON = dp(48)


# ============================================================
# COLORES
# ============================================================

def color(hexadecimal: str) -> list[float]:
    """Convierte un color hexadecimal a RGBA."""
    return get_color_from_hex(hexadecimal)


PALETAS = {
    TEMA_CLARO: {
        "fondo": color("#E0F2FE"),
        "tarjeta": color("#FFFFFF"),
        "tarjeta_secundaria": color("#E0F2FE"),
        "texto": color("#1E3A8A"),
        "texto_secundario": color("#334155"),
        "borde": color("#CBD5E1"),
        "campo": color("#FFFFFF"),
        "azul": color("#2563EB"),
        "azul_secundario": color("#60A5FA"),
        "azul_suave": color("#E0F2FE"),
        "blanco": color("#FFFFFF"),
        "error": color("#EF766E"),
    },
    TEMA_OSCURO: {
        "fondo": color("#0F172A"),
        "tarjeta": color("#172033"),
        "tarjeta_secundaria": color("#1E3A8A"),
        "texto": color("#E0F2FE"),
        "texto_secundario": color("#FFFFFF"),
        "borde": color("#334155"),
        "campo": color("#111827"),
        "azul": color("#60A5FA"),
        "azul_secundario": color("#60A5FA"),
        "azul_suave": color("#1E3A8A"),
        "blanco": color("#FFFFFF"),
        "error": color("#EF766E"),
    },
}


# ============================================================
# FUNCIONES AUXILIARES
# ============================================================

def detectar_tema_sistema() -> str:
    """Detecta si el sistema utiliza tema claro u oscuro."""
    sistema_operativo = platform.system()

    if sistema_operativo == "Windows":
        return _detectar_tema_windows()

    if sistema_operativo == "Darwin":
        return _detectar_tema_macos()

    if sistema_operativo == "Linux":
        return _detectar_tema_linux()

    return TEMA_CLARO


def _detectar_tema_windows() -> str:
    """Detecta el tema configurado en Windows."""
    try:
        import winreg

        ruta_configuracion = (
            r"Software\Microsoft\Windows\CurrentVersion"
            r"\Themes\Personalize"
        )

        with winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            ruta_configuracion,
        ) as clave:

            valor_tema, _ = winreg.QueryValueEx(
                clave,
                "AppsUseLightTheme",
            )

        return (
            TEMA_CLARO
            if valor_tema == 1
            else TEMA_OSCURO
        )

    except (OSError, ImportError):
        return TEMA_CLARO


def _detectar_tema_macos() -> str:
    """Detecta el tema configurado en macOS."""
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
            return TEMA_OSCURO

    except OSError:
        pass

    return TEMA_CLARO


def _detectar_tema_linux() -> str:
    """Detecta el tema configurado en Linux."""
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
            return TEMA_OSCURO

    except OSError:
        pass

    return TEMA_CLARO


def formatear_cop(valor: float) -> str:
    """Formatea un número como moneda colombiana."""
    formato_moneda = f"{valor:,.2f}"

    formato_moneda = (
        formato_moneda
        .replace(",", "X")
        .replace(".", ",")
        .replace("X", ".")
    )

    return f"$ {formato_moneda}"


def configurar_texto_ajustable(etiqueta: MDLabel) -> None:
    """Configura una etiqueta para adaptar el texto a su tamaño."""
    etiqueta.bind(
        size=lambda instancia, tamano: setattr(
            instancia,
            "text_size",
            tamano,
        )
    )


# ============================================================
# COMPONENTES PERSONALIZADOS
# ============================================================

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
        """Actualiza la posición y tamaño de la tarjeta."""
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
        """Actualiza los colores de la tarjeta."""
        self._color_fondo.rgba = self.color_fondo
        self._color_borde.rgba = self.color_borde


class CampoTexto(MDTextField):
    """Campo de texto personalizado para la aplicación."""

    def __init__(self, hint_text="", **kwargs):
        super().__init__(
            MDTextFieldHintText(text=hint_text),
            **kwargs,
        )

        self.mode = "filled"


class BotonRedondeado(MDButton):
    """Botón personalizado compatible con KivyMD 2.0.0."""

    def __init__(
        self,
        text="",
        style="filled",
        **kwargs,
    ):
        self.texto_boton = MDButtonText(text=text)

        super().__init__(
            self.texto_boton,
            style=style,
            **kwargs,
        )

    def actualizar_texto(self, texto: str) -> None:
        """Actualiza el texto visible del botón."""
        self.texto_boton.text = texto


# ============================================================
# INTERFAZ PRINCIPAL
# ============================================================

class CalculadoraIncapacidadGUI(BoxLayout):
    """Interfaz principal de la calculadora de incapacidades."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.orientation = "vertical"
        self.padding = PADDING_PRINCIPAL
        self.spacing = ESPACIADO_PRINCIPAL

        self.tarjetas: list[Tarjeta] = []
        self.labels_principales: list[MDLabel] = []
        self.labels_secundarios: list[MDLabel] = []
        self.campos: list[CampoTexto] = []

        self.modo_tema = TEMA_AUTOMATICO
        self.menu_tipo = None
        self.menu_tema = None
        self.dialogo_error = None

        self.crear_encabezado()
        self.crear_contenido()
        self.aplicar_tema()
        self.cargar_historial()

    # ========================================================
    # CREACIÓN DE ELEMENTOS
    # ========================================================

    def crear_label(
        self,
        texto: str,
        secundario: bool = False,
        **kwargs,
    ) -> MDLabel:
        """Crea una etiqueta y la registra para aplicar temas."""
        etiqueta = MDLabel(
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
            spacing=ESPACIADO_ENCABEZADO,
            size_hint_y=None,
            height=ALTURA_ENCABEZADO,
        )

        textos_encabezado = BoxLayout(
            orientation="vertical",
        )

        titulo = self.crear_label(
            TITULO_APLICACION,
            bold=True,
            font_size="26sp",
            halign="left",
            valign="middle",
        )

        configurar_texto_ajustable(titulo)

        subtitulo = self.crear_label(
            SUBTITULO_APLICACION,
            secundario=True,
            font_size="13sp",
            halign="left",
            valign="middle",
        )

        configurar_texto_ajustable(subtitulo)

        textos_encabezado.add_widget(titulo)
        textos_encabezado.add_widget(subtitulo)

        self.boton_tema = BotonRedondeado(
            text=TEXTO_TEMA_AUTOMATICO,
            style="outlined",
            size_hint_x=None,
            width=dp(180),
        )

        self.boton_tema.bind(
            on_release=self.abrir_menu_tema
        )

        encabezado.add_widget(textos_encabezado)
        encabezado.add_widget(self.boton_tema)

        self.add_widget(encabezado)

    def crear_contenido(self) -> None:
        """Crea el contenido desplazable de la aplicación."""
        scroll = ScrollView(
            do_scroll_x=False,
        )

        contenido = BoxLayout(
            orientation="vertical",
            spacing=ESPACIADO_CONTENIDO,
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
            spacing=ESPACIADO_TARJETA,
            padding=PADDING_TARJETA,
            size_hint_y=None,
            height=ALTURA_TARJETA_FORMULARIO,
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

        self.boton_tipo = BotonRedondeado(
            text=VALOR_TIPO_INICIAL,
            style="outlined",
            size_hint_y=None,
            height=ALTURA_BOTON,
        )

        self.boton_tipo.bind(
            on_release=self.abrir_menu_tipo
        )

        tarjeta.add_widget(self.boton_tipo)

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
            height=ALTURA_CAMPO,
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
            input_filter="int",
            size_hint_y=None,
            height=ALTURA_CAMPO,
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
            text=TEXTO_BOTON_CALCULAR,
            style="filled",
        )

        self.boton_calcular.bind(
            on_release=self.calcular
        )

        self.boton_limpiar = BotonRedondeado(
            text=TEXTO_BOTON_LIMPIAR,
            style="outlined",
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
            padding=PADDING_RESULTADO,
            size_hint_y=None,
            height=ALTURA_TARJETA_RESULTADO,
        )

        self.tarjetas.append(self.tarjeta_resultado)

        titulo_resultado = self.crear_label(
            "Resultado estimado",
            secundario=True,
            font_size="13sp",
            size_hint_y=None,
            height=dp(25),
            halign="left",
        )

        self.resultado = self.crear_label(
            TEXTO_RESULTADO_INICIAL,
            bold=True,
            font_size="22sp",
            size_hint_y=None,
            height=dp(55),
            halign="left",
            valign="middle",
        )

        configurar_texto_ajustable(self.resultado)

        self.tarjeta_resultado.add_widget(titulo_resultado)
        self.tarjeta_resultado.add_widget(self.resultado)

        contenido.add_widget(self.tarjeta_resultado)

    def crear_tarjeta_historial(
        self,
        contenido: BoxLayout,
    ) -> None:
        """Crea la tarjeta donde se muestra el historial."""
        tarjeta = Tarjeta(
            orientation="vertical",
            spacing=dp(8),
            padding=PADDING_RESULTADO,
            size_hint_y=None,
            height=ALTURA_TARJETA_HISTORIAL,
        )

        self.tarjetas.append(tarjeta)

        tarjeta.add_widget(
            self.crear_label(
                "Historial de cálculos",
                bold=True,
                font_size="18sp",
                size_hint_y=None,
                height=dp(35),
                halign="left",
            )
        )

        tarjeta.add_widget(
            self.crear_label(
                "Los cálculos guardados aparecerán aquí.",
                secundario=True,
                font_size="13sp",
                size_hint_y=None,
                height=dp(24),
                halign="left",
            )
        )

        scroll = ScrollView()

        self.texto_historial = self.crear_label(
            TEXTO_HISTORIAL_VACIO,
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
        """Crea la tarjeta informativa."""
        tarjeta = Tarjeta(
            orientation="vertical",
            spacing=dp(6),
            padding=PADDING_RESULTADO,
            size_hint_y=None,
            height=ALTURA_TARJETA_INFORMACION,
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

        textos_informacion = [
            "• Enfermedad general: reconocimiento del 66,67%.",
            "• Maternidad: reconocimiento del 100%.",
            "• Riesgo laboral: reconocimiento del 100%.",
        ]

        for texto in textos_informacion:
            tarjeta.add_widget(
                self.crear_label(
                    texto,
                    secundario=True,
                    font_size="14sp",
                    size_hint_y=None,
                    height=dp(30),
                    halign="left",
                )
            )

        tarjeta.add_widget(
            self.crear_label(
                "Los valores corresponden a las reglas "
                "definidas en el proyecto.",
                secundario=True,
                font_size="12sp",
                size_hint_y=None,
                height=dp(35),
                halign="left",
            )
        )

        contenido.add_widget(tarjeta)

    # ========================================================
    # MENÚS
    # ========================================================

    def abrir_menu_tema(self, *_args) -> None:
        """Abre el menú de selección de tema."""
        opciones_tema = [
            TEXTO_TEMA_AUTOMATICO,
            TEXTO_TEMA_CLARO,
            TEXTO_TEMA_OSCURO,
        ]

        elementos_menu = [
            {
                "text": opcion,
                "on_release": lambda opcion=opcion: (
                    self.cambiar_tema(opcion)
                ),
            }
            for opcion in opciones_tema
        ]

        self.menu_tema = MDDropdownMenu(
            caller=self.boton_tema,
            items=elementos_menu,
        )

        self.menu_tema.open()

    def abrir_menu_tipo(self, *_args) -> None:
        """Abre el menú para seleccionar el tipo de incapacidad."""
        opciones_tipo = tuple(TIPOS_MOSTRADOS.keys())

        elementos_menu = [
            {
                "text": opcion,
                "on_release": lambda opcion=opcion: (
                    self.seleccionar_tipo(opcion)
                ),
            }
            for opcion in opciones_tipo
        ]

        self.menu_tipo = MDDropdownMenu(
            caller=self.boton_tipo,
            items=elementos_menu,
        )

        self.menu_tipo.open()

    def seleccionar_tipo(self, tipo: str) -> None:
        """Selecciona un tipo de incapacidad."""
        self.boton_tipo.actualizar_texto(tipo)

        if self.menu_tipo:
            self.menu_tipo.dismiss()

    # ========================================================
    # TEMA
    # ========================================================

    def cambiar_tema(self, texto: str) -> None:
        """Cambia el tema visual seleccionado."""
        temas_disponibles = {
            TEXTO_TEMA_CLARO: TEMA_CLARO,
            TEXTO_TEMA_OSCURO: TEMA_OSCURO,
            TEXTO_TEMA_AUTOMATICO: TEMA_AUTOMATICO,
        }

        self.modo_tema = temas_disponibles.get(
            texto,
            TEMA_AUTOMATICO,
        )

        self.boton_tema.actualizar_texto(texto)

        if self.menu_tema:
            self.menu_tema.dismiss()

        self.aplicar_tema()

    def obtener_tema_actual(self) -> str:
        """Obtiene el tema que debe utilizar la interfaz."""
        if self.modo_tema == TEMA_AUTOMATICO:
            return detectar_tema_sistema()

        return self.modo_tema

    def aplicar_tema(self) -> None:
        """Aplica los colores correspondientes al tema actual."""
        tema_actual = self.obtener_tema_actual()
        paleta = PALETAS[tema_actual]

        Window.clearcolor = paleta["fondo"]

        for tarjeta in self.tarjetas:
            tarjeta.color_fondo = paleta["tarjeta"]
            tarjeta.color_borde = paleta["borde"]

        self.tarjeta_resultado.color_fondo = paleta["azul_suave"]

        for etiqueta in self.labels_principales:
            etiqueta.theme_text_color = "Custom"
            etiqueta.text_color = paleta["texto"]

        for etiqueta in self.labels_secundarios:
            etiqueta.theme_text_color = "Custom"
            etiqueta.text_color = paleta["texto_secundario"]

        self.resultado.theme_text_color = "Custom"
        self.resultado.text_color = paleta["azul_secundario"]

        for campo in self.campos:
            campo.text_color = paleta["texto"]
            campo.line_color_normal = paleta["borde"]
            campo.line_color_focus = paleta["azul"]

        self.boton_calcular.md_bg_color = paleta["azul"]
        self.boton_limpiar.md_bg_color = (
            paleta["tarjeta_secundaria"]
        )

    # ========================================================
    # CÁLCULO
    # ========================================================

    def calcular(self, _boton: MDButton) -> None:
        """Obtiene los datos, calcula y guarda el resultado."""
        try:
            datos = self.obtener_datos_formulario()
            pago = self.calcular_pago(datos)

            self.guardar_resultado(
                datos=datos,
                pago=pago,
            )

        except (ValueError, IncapacidadError) as error:
            self.mostrar_error(str(error))

    def obtener_datos_formulario(self) -> dict:
        """Obtiene y valida los datos ingresados en el formulario."""
        salario = self.convertir_numero(
            texto=self.entrada_salario.text,
            campo="salario",
        )

        dias = self.convertir_dias(
            self.entrada_dias.text
        )

        tipo_mostrado = self.boton_tipo.texto_boton.text
        tipo_incapacidad = TIPOS_MOSTRADOS[tipo_mostrado]

        return {
            "salario": salario,
            "dias": dias,
            "tipo_mostrado": tipo_mostrado,
            "tipo_incapacidad": tipo_incapacidad,
        }

    def calcular_pago(self, datos: dict) -> float:
        """Calcula el pago correspondiente a los datos recibidos."""
        return calcular_pago_incapacidad(
            salario_mensual=datos["salario"],
            dias_incapacidad=datos["dias"],
            tipo_incapacidad=datos["tipo_incapacidad"],
        )

    def guardar_resultado(
        self,
        datos: dict,
        pago: float,
    ) -> None:
        """Guarda el cálculo y actualiza la interfaz."""
        id_caso = guardar_caso(
            tipo_incapacidad=datos["tipo_mostrado"],
            salario=datos["salario"],
            dias=datos["dias"],
            pago=pago,
        )

        self.mostrar_resultado(
            tipo_incapacidad=datos["tipo_mostrado"],
            dias=datos["dias"],
            pago=pago,
            id_caso=id_caso,
        )

        self.cargar_historial()

    def mostrar_resultado(
        self,
        tipo_incapacidad: str,
        dias: int,
        pago: float,
        id_caso: int,
    ) -> None:
        """Muestra el resultado del cálculo."""
        self.resultado.text = (
            f"{formatear_cop(pago)} COP\n"
            f"{tipo_incapacidad} | {dias} días | "
            f"Caso #{id_caso}"
        )

    def convertir_numero(
        self,
        texto: str,
        campo: str,
    ) -> float:
        """Convierte un campo de texto a número decimal."""
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

    def convertir_dias(self, texto: str) -> int:
        """Convierte el campo de días a un número entero."""
        if not texto.strip():
            raise ValueError(
                "Debes ingresar un valor para días de incapacidad."
            )

        try:
            return int(texto)

        except ValueError as error:
            raise ValueError(
                "Los días de incapacidad deben ser un número entero."
            ) from error

    # ========================================================
    # HISTORIAL
    # ========================================================

    def cargar_historial(self) -> None:
        """Carga en pantalla los casos guardados."""
        casos = obtener_casos()

        if not casos:
            self.texto_historial.text = TEXTO_HISTORIAL_VACIO
            return

        registros = [
            self.formatear_caso_historial(caso)
            for caso in casos
        ]

        self.texto_historial.text = "\n\n".join(registros)

    def formatear_caso_historial(self, caso: dict) -> str:
        """Convierte un caso almacenado en texto."""
        return (
            f"Caso #{caso['id']} | "
            f"{caso['tipo_incapacidad']} | "
            f"{caso['dias']} días\n"
            f"Salario: {formatear_cop(caso['salario'])} | "
            f"Pago: {formatear_cop(caso['pago'])}"
        )

    # ========================================================
    # FORMULARIO Y ERRORES
    # ========================================================

    def limpiar(self, _boton: MDButton) -> None:
        """Limpia los campos del formulario."""
        self.entrada_salario.text = ""
        self.entrada_dias.text = ""

        self.boton_tipo.actualizar_texto(
            VALOR_TIPO_INICIAL
        )

        self.resultado.text = TEXTO_RESULTADO_INICIAL
        self.entrada_salario.focus = True

    def mostrar_error(self, mensaje: str) -> None:
        """Muestra un mensaje de error mediante MDDialog."""
        mensaje_error = mensaje.replace("Error: ", "")

        boton_entendido = BotonRedondeado(
            text=TEXTO_BOTON_ENTENDIDO,
            style="text",
        )

        self.dialogo_error = MDDialog(
            MDDialogHeadlineText(
                text=TEXTO_TITULO_ERROR,
            ),
            MDDialogSupportingText(
                text=mensaje_error,
            ),
            MDDialogButtonContainer(
                boton_entendido,
            ),
        )

        boton_entendido.bind(
            on_release=lambda *_args: (
                self.dialogo_error.dismiss()
            )
        )

        self.dialogo_error.open()


# ============================================================
# APLICACIÓN
# ============================================================

class CalculadoraIncapacidadesApp(MDApp):
    """Aplicación gráfica de la calculadora."""

    title = TITULO_APLICACION

    def build(self) -> CalculadoraIncapacidadGUI:
        """Inicializa la base de datos y construye la interfaz."""
        crear_base_datos()

        self.theme_cls.primary_palette = "Blue"
        self.theme_cls.theme_style = "Light"

        return CalculadoraIncapacidadGUI()


if __name__ == "__main__":
    CalculadoraIncapacidadesApp().run()