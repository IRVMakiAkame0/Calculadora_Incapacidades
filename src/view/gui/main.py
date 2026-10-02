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

TIPO_ENFERMEDAD_GENERAL = "Enfermedad General"
TIPO_MATERNIDAD = "Maternidad"
TIPO_RIESGO_LABORAL = "Riesgo Laboral"

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

TEXTO_RESULTADO_INICIAL = (
    "Completa los datos para realizar la simulación."
)

TEXTO_HISTORIAL_VACIO = "Todavía no hay cálculos."

TEXTO_BOTON_CALCULAR = "Calcular Pago"
TEXTO_BOTON_LIMPIAR = "Limpiar"
TEXTO_BOTON_ENTENDIDO = "Entendido"

TEXTO_TITULO_ERROR = "Revisa los datos"

VALOR_TIPO_INICIAL = None

# ============================================================
# CONSTANTES DE DIMENSIONES
# ============================================================

ESPACIADO_PRINCIPAL = dp(14)
ESPACIADO_TARJETA = dp(12)
ESPACIADO_CONTENIDO = dp(18)
ESPACIADO_ENCABEZADO = dp(15)

PADDING_PRINCIPAL = dp(32)
PADDING_TARJETA = dp(28)
PADDING_RESULTADO = dp(26)

ALTURA_ENCABEZADO = dp(68)
ALTURA_TARJETA_FORMULARIO = dp(450)
ALTURA_TARJETA_RESULTADO = dp(125)
ALTURA_TARJETA_HISTORIAL = dp(220)
ALTURA_TARJETA_INFORMACION = dp(230)

ALTURA_CAMPO = dp(54)
ALTURA_BOTON = dp(48)

# Alturas de las tarjetas desplegables
ALTURA_CABECERA_DESPLEGABLE = dp(72)
ALTURA_RESULTADO_EXPANDIDO = dp(170)
ALTURA_HISTORIAL_EXPANDIDO = dp(300)
ALTURA_INFORMACION_EXPANDIDA = dp(255)

TEXTO_EXPANDIR = "+"
TEXTO_CONTRAER = "-"
TEXTO_NUEVO_RESULTADO = "Nuevo Resultado"

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
    """Configura una etiqueta para adaptar texto y altura."""

    etiqueta.bind(
        width=lambda instancia, ancho: setattr(
            instancia,
            "text_size",
            (ancho, None),
        )
    )

    etiqueta.bind(
        texture_size=lambda instancia, tamano: setattr(
            instancia,
            "height",
            tamano[1] + dp(10),
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
        
        self.radius = [
            dp(12),
            dp(12),
            dp(12),
            dp(12),
        ]
        
class CampoSalario(CampoTexto):
    """Campo de salario con separadores de miles."""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._formateando = False
        self.bind(text=self._formatear_salario)

    def _formatear_salario(self, _instancia, texto: str) -> None:
        """Agrega separadores de miles mientras se escribe."""
        if self._formateando:
            return

        numeros = texto.replace(".", "").strip()

        if not numeros:
            return

        if not numeros.isdigit():
            return

        texto_formateado = f"{int(numeros):,}".replace(",", ".")

        if texto != texto_formateado:
            self._formateando = True
            self.text = texto_formateado
            self.cursor = (len(self.text), 0)
            self._formateando = False


class BotonRedondeado(MDButton):
    """Botón personalizado compatible con KivyMD 2.0.0."""

    def __init__(
        self,
        text="",
        style="filled",
        **kwargs,
    ):
        self.texto_boton = MDButtonText(
            text=text,
            halign="center",
            font_size = "18sp",
        )

        super().__init__(
            self.texto_boton,
            style=style,
            **kwargs,
        )

        # Centra siempre el texto dentro del botón
        self.bind(
            size=self._centrar_texto,
            pos=self._centrar_texto,
        )

    def actualizar_texto(self, texto: str) -> None:
        """Actualiza el texto visible del botón."""
        self.texto_boton.text = texto

    def _centrar_texto(self, *_args) -> None:
        """Mantiene el texto centrado dentro del botón."""
        self.texto_boton.pos_hint = {
            "center_x": 0.5,
            "center_y": 0.5,
        }
        
class BotonDesplegable(MDLabel):
    """Control para expandir o contraer una sección."""

    def __init__(self, text="+", **kwargs):
        super().__init__(
            text=text,
            bold=True,
            font_size="30sp",
            halign="center",
            valign="middle",
            size_hint=(None, None),
            width=dp(56),
            height=dp(56),
            **kwargs,
        )
        
        self.register_event_type("on_release")

        self.text_size = self.size
        self.bind(size=self._actualizar_texto)

    def _actualizar_texto(self, *_args) -> None:
        """Mantiene centrado el símbolo del control."""
        self.text_size = self.size

    def on_touch_down(self, touch):
        """Detecta cuando el usuario pulsa el control."""
        if self.collide_point(*touch.pos):
            self.dispatch("on_release")
            return True

        return super().on_touch_down(touch)

    def actualizar_texto(self, texto: str) -> None:
        """Cambia el símbolo mostrado."""
        self.text = texto

    def on_release(self) -> None:
        """Evento ejecutado al pulsar el control."""

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
        self.menu_tema = None
        self.dialogo_error = None
        self.tipo_seleccionado = VALOR_TIPO_INICIAL
        self.botones_tipo = {}

        self.crear_encabezado()
        self.crear_contenido()
        self.aplicar_tema()
        self.cargar_historial()
        
        # Detectar cambios en el tamaño de la ventana
        Window.bind(size = self.actualizar_diseno_responsive)
        
        # Aplica la distribución correcta al iniciar
        self.actualizar_diseno_responsive()
        
        
    def actualizar_diseno_responsive(self, *_args) -> None:
        """Adapta la interfaz para computador, tablet y celular."""

        ancho = Window.width
        modo_movil = ancho < dp(600)

        if modo_movil:
            # Márgenes más pequeños para aprovechar el celular.
            self.padding = [
                dp(12),
                dp(10),
                dp(12),
                dp(10),
            ]

            # Encabezado.
            self.encabezado.height = dp(95)
            self.encabezado.orientation = "vertical"
            self.encabezado.spacing = dp(6)

            self.titulo_principal.font_size = "21sp"
            self.titulo_principal.halign = "left"
            
            self.titulo_resultado.font_size = "16sp"
            self.titulo_historial.font_size = "16sp"
            self.titulo_informacion.font_size = "16sp"
            
            # En celular liberamos espacio para los títulos
            self.aviso_nuevo_resultado.width = 0
            self.aviso_nuevo_resultado.opacity = 0

            self.boton_resultado.width = dp(32)
            self.boton_informacion.width = dp(32)

            # Más margen interno para que el texto no toque los bordes
            self.tarjeta_resultado.padding = [
                dp(16), dp(14), dp(10), dp(8)
            ]

            self.tarjeta_historial.padding = [
                dp(20), dp(14), dp(14), dp(16)
            ]

            self.tarjeta_informacion.padding = [
                dp(20), dp(14), dp(14), dp(14)
            ]
            
            self.textos_encabezado.size_hint_y = None
            self.textos_encabezado.height = dp(48)
            
            self.boton_tema.size_hint = (None, None)
            self.boton_tema.width = dp(180)
            self.boton_tema.height = ALTURA_BOTON
            
            self.boton_tema.pos_hint = {
                "center_x": 0.5
            }

            # Tipos de incapacidad:
            # mantienen su tamaño y se desplazan horizontalmente.
            self.contenedor_opciones_tipo.padding = [
                dp(4), 0, dp(4), 0
            ]
            
            self.tarjeta_formulario.height = dp(520)

            # Acciones una debajo de la otra.
            self.contenedor_botones_accion.orientation = "vertical"
            self.contenedor_botones_accion.height = dp(108)
            
            self.tarjeta_historial.height = dp(300)
            
            self.tarjeta_resultado.height = ALTURA_RESULTADO_EXPANDIDO
            self.contenido_resultado.height = dp(60)

        else:
            # Computador/tablet
            
            # Restaurar distribución de computador
            self.aviso_nuevo_resultado.width = dp(120)
            self.aviso_nuevo_resultado.opacity = 1

            self.boton_resultado.width = dp(56)
            self.boton_informacion.width = dp(56)

            self.tarjeta_resultado.padding = [
                dp(24), dp(14), dp(18), dp(16)
            ]

            self.tarjeta_historial.padding = [
                dp(24), dp(14), dp(18), dp(16)
            ]

            self.tarjeta_informacion.padding = [
                dp(30), dp(14), dp(24), dp(14)
            ]
            
            self.padding = PADDING_PRINCIPAL

            self.encabezado.height = ALTURA_ENCABEZADO
            self.encabezado.orientation = "horizontal"
            self.encabezado.spacing = ESPACIADO_ENCABEZADO

            self.titulo_principal.font_size = "26sp"
            self.titulo_resultado.font_size = "18sp"
            self.titulo_historial.font_size = "18sp"
            self.titulo_informacion.font_size = "18sp"
            
            self.textos_encabezado.size_hint_y = 1
            
            self.boton_tema.size_hint = (None, 1)
            self.boton_tema.width = dp(180)
            self.boton_tema.pos_hint = {}
            
            self.tarjeta_formulario.height = ALTURA_TARJETA_FORMULARIO

            self.contenedor_botones_accion.orientation = "horizontal"
            self.contenedor_botones_accion.height = dp(50)
            
    def cambiar_estado_tarjeta(
        self,
        tarjeta,
        contenido,
        boton,
    ):
        """Expande o contrae una tarjeta."""

        esta_expandida = getattr(
            tarjeta,
            "esta_expandida",
            True
        )

        if esta_expandida:
            # CONTRAER

            tarjeta.esta_expandida = False

            contenido.opacity = 0
            contenido.disabled = True
            contenido.height = 0

            tarjeta.height = ALTURA_CABECERA_DESPLEGABLE

            boton.actualizar_texto(
                TEXTO_EXPANDIR
            )

            if tarjeta is self.tarjeta_resultado:

                contenido.height = self.contenido_resultado.height

                tarjeta.height = (
                    self.contenido_resultado.height + dp(60)
                )


        else:
            # EXPANDIR

            tarjeta.esta_expandida = True

            contenido.opacity = 1
            contenido.disabled = False


            if tarjeta is self.tarjeta_resultado:

                contenido.height = dp(65)
                tarjeta.height = ALTURA_RESULTADO_EXPANDIDO


            elif tarjeta is self.tarjeta_historial:

                contenido.height = dp(210)
                tarjeta.height = ALTURA_HISTORIAL_EXPANDIDO

                # obliga a refrescar el historial
                self.cargar_historial()


            elif tarjeta is self.tarjeta_informacion:

                contenido.height = dp(180)
                tarjeta.height = ALTURA_INFORMACION_EXPANDIDA


            boton.actualizar_texto(
                TEXTO_CONTRAER
            )
    
    def alternar_informacion(self, *_args) -> None:
        """Expande o contrae la tarjeta de información."""

        esta_expandida = getattr(
            self.tarjeta_informacion,
            "esta_expandida",
            True,
        )

        if esta_expandida:
            # CONTRAER
            self.tarjeta_informacion.esta_expandida = False

            self.contenido_informacion.opacity = 0
            self.contenido_informacion.disabled = True
            self.contenido_informacion.height = 0

            self.tarjeta_informacion.height = (
                ALTURA_CABECERA_DESPLEGABLE
            )

            self.boton_informacion.actualizar_texto(
                TEXTO_EXPANDIR
            )

        else:
            # EXPANDIR
            self.tarjeta_informacion.esta_expandida = True

            self.contenido_informacion.opacity = 1
            self.contenido_informacion.disabled = False
            self.contenido_informacion.height =dp(180)

            self.tarjeta_informacion.height = (
                ALTURA_INFORMACION_EXPANDIDA
            )

            self.boton_informacion.actualizar_texto(
                TEXTO_CONTRAER
            )

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
            text = texto,
            **kwargs,
        )

        if secundario:
            self.labels_secundarios.append(etiqueta)
        else:
            self.labels_principales.append(etiqueta)

        return etiqueta

    def crear_encabezado(self) -> None:
        """Crea el encabezado principal."""
        self.encabezado = BoxLayout(
            orientation = "horizontal",
            spacing = ESPACIADO_ENCABEZADO,
            size_hint_y = None,
            height = ALTURA_ENCABEZADO,
        )

        textos_encabezado = BoxLayout(
            orientation = "vertical",
        )
        
        self.textos_encabezado = textos_encabezado

        titulo = self.crear_label(
            TITULO_APLICACION,
            bold = True,
            font_size = "26sp",
            halign = "left",
            valign = "middle",
        )
        
        self.titulo_principal = titulo

        configurar_texto_ajustable(titulo)

        textos_encabezado.add_widget(titulo)

        self.boton_tema = BotonRedondeado(
            text = TEXTO_TEMA_AUTOMATICO,
            style = "outlined",
            size_hint_x = None,
            width = dp(180),
        )

        self.boton_tema.bind(
            on_release = self.abrir_menu_tema
        )

        self.encabezado.add_widget(textos_encabezado)
        self.encabezado.add_widget(self.boton_tema)

        self.add_widget(self.encabezado)

    def crear_contenido(self) -> None:
        """Crea el contenido desplazable y adaptable de la aplicación."""

        self.scroll = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
        )

        self.contenido = BoxLayout(
            orientation="vertical",
            spacing=dp(24),
            padding=[0, dp(8), 0, dp(20)],
            size_hint_y=None,
        )

        self.contenido.bind(
            minimum_height=self.contenido.setter("height")
        )

        self.crear_tarjeta_formulario(self.contenido)
        self.crear_tarjeta_resultado(self.contenido)
        self.crear_tarjeta_historial(self.contenido)
        self.crear_tarjeta_informacion(self.contenido)

        self.scroll.add_widget(self.contenido)
        self.add_widget(self.scroll)

    def crear_tarjeta_formulario(
        self,
        contenido: BoxLayout,
    ) -> None:
        """Crea la tarjeta principal del formulario."""
        tarjeta = Tarjeta(
            orientation = "vertical",
            spacing = dp(12),
            padding = [dp(20), dp(14), dp(20), dp(18)],
            size_hint_y = None,
            height = ALTURA_TARJETA_FORMULARIO,
        )

        self.tarjetas.append(tarjeta)
        
        self.tarjeta_formulario = tarjeta

        tarjeta.add_widget(
            self.crear_label(
                "Ingresa los Datos de la Incapacidad",
                bold = True,
                font_size = "18sp",
                size_hint_y = None,
                height = dp(40),
                halign = "center",
                valign = "middle"
            )
        )


        tarjeta.add_widget(
            self.crear_label(
                "Tipo de Incapacidad",
                bold = True,
                font_size = "18sp",
                size_hint_y = None,
                height = dp(35),
                halign = "left",
            )
        )

        scroll_tipos = ScrollView(
            do_scroll_x=True,
            do_scroll_y=False,
            size_hint_y=None,
            height=dp(56),
            bar_width = dp(3),
        )

        self.contenedor_opciones_tipo = BoxLayout(
            orientation="horizontal",
            spacing=dp(12),
            padding=[dp(4), 0, dp(4), 0],
            size_hint=(None, None),
            height=ALTURA_BOTON,
        )

        self.contenedor_opciones_tipo.bind(
            minimum_width = self.contenedor_opciones_tipo.setter("width")
        )

        for tipo in TIPOS_MOSTRADOS:
            boton = BotonRedondeado(
                text=tipo,
                style="outlined",
                size_hint=(None, None),
                width=dp(150),
                height=ALTURA_BOTON,
            )

            boton.bind(
                on_release = lambda _boton, tipo = tipo: (
                    self.seleccionar_tipo(tipo)
                )
            )

            self.botones_tipo[tipo] = boton
            self.contenedor_opciones_tipo.add_widget(boton)

        scroll_tipos.add_widget(self.contenedor_opciones_tipo)
        tarjeta.add_widget(scroll_tipos)

        tarjeta.add_widget(
            self.crear_label(
                "Salario Mensual (COP)",
                bold = True,
                font_size = "15sp",
                size_hint_y = None,
                height = dp(28),
                halign = "left",
            )
        )

        self.entrada_salario = CampoSalario(
            hint_text = "Ejemplo: 2.500.000",
            multiline = False,
            size_hint_y = None,
            height = ALTURA_CAMPO,
        )

        self.campos.append(self.entrada_salario)
        tarjeta.add_widget(self.entrada_salario)

        tarjeta.add_widget(
            self.crear_label(
                "Días de Incapacidad",
                bold = True,
                font_size="15sp",
                size_hint_y = None,
                height = dp(28),
                halign = "left",
            )
        )

        self.entrada_dias = CampoTexto(
            hint_text = "Ejemplo: 5",
            multiline = False,
            input_filter = "int",
            size_hint_y = None,
            height = ALTURA_CAMPO,
        )

        self.campos.append(self.entrada_dias)
        tarjeta.add_widget(self.entrada_dias)

        botones = BoxLayout(
            orientation = "horizontal",
            spacing = dp(10),
            size_hint_y = None,
            height = dp(50),
        )
        
        self.contenedor_botones_accion = botones

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
        """Crea la tarjeta desplegable del resultado."""

        self.tarjeta_resultado = Tarjeta(
            orientation="vertical",
            spacing=dp(2),
            padding=[dp(24), dp(4), dp(18), dp(4)],
            size_hint_y=None,
            height=ALTURA_RESULTADO_EXPANDIDO,
        )

        # Estado inicial
        self.tarjeta_resultado.esta_expandida = True
        
        self.tarjeta_resultado.altura_original = ALTURA_RESULTADO_EXPANDIDO

        self.tarjetas.append(self.tarjeta_resultado)

        # ====================================================
        # CABECERA
        # ====================================================

        cabecera = BoxLayout(
            orientation="horizontal",
            spacing=dp(6),
            size_hint_y=None,
            height=dp(40),
        )

        self.titulo_resultado = self.crear_label(
            "Resultado Estimado",
            bold=True,
            secundario=True,
            font_size="18sp",
            halign="left",
            valign="middle",
        )

        self.aviso_nuevo_resultado = self.crear_label(
            "",
            secundario=True,
            bold=True,
            font_size="13sp",
            halign="right",
            valign="middle",
            size_hint_x=None,
            width=dp(90),
        )

        configurar_texto_ajustable(
            self.aviso_nuevo_resultado
        )

        self.boton_resultado = BotonDesplegable(
            text=TEXTO_CONTRAER,
        )

        cabecera.add_widget(
            self.titulo_resultado
        )

        cabecera.add_widget(
            self.aviso_nuevo_resultado
        )

        cabecera.add_widget(
            self.boton_resultado
        )

        # ====================================================
        # CONTENIDO
        # ====================================================

        self.contenido_resultado = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
        )

        self.resultado = self.crear_label(
            TEXTO_RESULTADO_INICIAL,
            bold=True,
            font_size="18sp",
            halign="left",
            valign="middle",
        )

        configurar_texto_ajustable(
            self.resultado
        )
        
        self.resultado.bind(
            texture_size=self.actualizar_altura_resultado
        )

        self.contenido_resultado.add_widget(
            self.resultado
        )

        # ====================================================
        # BOTÓN
        # ====================================================

        self.boton_resultado.bind(
            on_release=lambda *_: (
                self.cambiar_estado_tarjeta(
                    self.tarjeta_resultado,
                    self.contenido_resultado,
                    self.boton_resultado,
                )
            )
        )

        self.tarjeta_resultado.add_widget(
            cabecera
        )

        self.tarjeta_resultado.add_widget(
            self.contenido_resultado
        )

        contenido.add_widget(
            self.tarjeta_resultado
        )

    
    def crear_tarjeta_historial(
        self,
        contenido: BoxLayout,
    ) -> None:
        """Crea la tarjeta fija del historial."""

        self.tarjeta_historial = Tarjeta(
            orientation="vertical",
            spacing=dp(5),
            padding=[dp(24), dp(8), dp(18), dp(8)],
            size_hint_y=None,
            height=dp(300),
        )

        # Estado inicial
        self.tarjeta_historial.esta_expandida = True
        
        self.tarjeta_historial.altura_original = ALTURA_HISTORIAL_EXPANDIDO

        self.tarjetas.append(
            self.tarjeta_historial
        )

        # ====================================================
        # CABECERA
        # ====================================================

        cabecera = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(50),
        )

        self.titulo_historial = self.crear_label(
            "Historial de Cálculos",
            bold=True,
            font_size="18sp",
            halign="left",
            valign="middle",
        )

        configurar_texto_ajustable(
            self.titulo_historial
        )

        cabecera.add_widget(
            self.titulo_historial
        )



        # ====================================================
        # CONTENIDO
        # ====================================================

        self.contenido_historial = BoxLayout(
            orientation="vertical",
            spacing=dp(5),
            size_hint_y=None,
            height=dp(220),
        )

        descripcion = self.crear_label(
            "Últimos cálculos realizados",
            secundario=True,
            font_size="13sp",
            size_hint_y=None,
            height=dp(35),
            halign="left",
            valign="middle",
        )

        configurar_texto_ajustable(
            descripcion
        )

        self.scroll_historial = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
            bar_width=dp(8),
        )
        
        self.scroll_historial.size_hint_y = None
        self.scroll_historial.height = dp(180)

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
                max(
                    tamano[1] + dp(10),
                    dp(40),
                ),
            )
        )

        self.scroll_historial.add_widget(
            self.texto_historial
        )

        self.contenido_historial.add_widget(
            descripcion
        )

        self.contenido_historial.add_widget(
            self.scroll_historial
        )

        self.tarjeta_historial.add_widget(
            cabecera
        )

        self.tarjeta_historial.add_widget(
            self.contenido_historial
        )

        contenido.add_widget(
            self.tarjeta_historial
        )
    

    def crear_tarjeta_informacion(
        self,
        contenido: BoxLayout,
    ) -> None:
        """Crea la tarjeta informativa desplegable."""

        self.tarjeta_informacion = Tarjeta(
            orientation="vertical",
            spacing=dp(8),
            padding=[dp(24), dp(10), dp(18), dp(12)],
            size_hint_y=None,
            height=ALTURA_INFORMACION_EXPANDIDA,
        )

        # Estado inicial
        self.tarjeta_informacion.esta_expandida = True
        
        self.tarjeta_informacion.altura_original = ALTURA_INFORMACION_EXPANDIDA

        self.tarjetas.append(
            self.tarjeta_informacion
        )

        # ====================================================
        # CABECERA
        # ====================================================

        cabecera = BoxLayout(
            orientation="horizontal",
            spacing=dp(8),
            size_hint_y=None,
            height=dp(50),
        )

        self.titulo_informacion = self.crear_label(
            "¿Cómo Funciona Esta Herramienta?",
            bold=True,
            font_size="18sp",
            halign="left",
            valign="middle",
        )

        configurar_texto_ajustable(
            self.titulo_informacion
        )

        self.boton_informacion = BotonDesplegable(
            text=TEXTO_CONTRAER,
        )

        cabecera.add_widget(
            self.titulo_informacion
        )

        cabecera.add_widget(
            self.boton_informacion
        )

        # ====================================================
        # CONTENIDO
        # ====================================================

        self.contenido_informacion = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(180),
        )

        self.scroll_informacion = ScrollView(
            do_scroll_x=False,
            do_scroll_y=True,
        )

        self.lista_informacion = BoxLayout(
            orientation="vertical",
            spacing=dp(10),
            size_hint_y=None,
            padding=[dp(4), dp(4), dp(4), dp(8)],
        )

        self.lista_informacion.bind(
            minimum_height=self.lista_informacion.setter("height")
        )

        textos_informacion = [
            (
                "• [b]Enfermedad general:[/b] "
                "Reconocimiento del 66,67%."
            ),
            (
                "• [b]Maternidad:[/b] "
                "Reconocimiento del 100%."
            ),
            (
                "• [b]Riesgo laboral:[/b] "
                "Reconocimiento del 100%."
            ),
        ]

        for texto in textos_informacion:

            etiqueta = self.crear_label(
                texto,
                secundario=True,
                markup=True,
                font_size="14sp",
                size_hint_y=None,
                halign="left",
                valign="top",
            )

            etiqueta.bind(
                width=lambda instancia, ancho: setattr(
                    instancia,
                    "text_size",
                    (ancho, None),
                )
            )

            etiqueta.bind(
                texture_size=lambda instancia, tamano: setattr(
                    instancia,
                    "height",
                    tamano[1] + dp(10),
                )
            )

            self.lista_informacion.add_widget(etiqueta)

        nota = self.crear_label(
            "Los valores corresponden a las reglas "
            "definidas en el proyecto.",
            secundario=True,
            font_size="12sp",
            size_hint_y=None,
            halign="left",
            valign="top",
        )

        nota.bind(
            width=lambda instancia, ancho: setattr(
                instancia,
                "text_size",
                (ancho, None),
            )
        )

        nota.bind(
            texture_size=lambda instancia, tamano: setattr(
                instancia,
                "height",
                tamano[1] + dp(10),
            )
        )

        self.lista_informacion.add_widget(nota)

        self.scroll_informacion.add_widget(
            self.lista_informacion
        )

        self.contenido_informacion.add_widget(
            self.scroll_informacion
        )

        # ====================================================
        # BOTÓN
        # ====================================================

        self.boton_informacion.bind(
            on_release=self.alternar_informacion
        )

        self.tarjeta_informacion.add_widget(
            cabecera
        )

        self.tarjeta_informacion.add_widget(
            self.contenido_informacion
        )

        contenido.add_widget(
            self.tarjeta_informacion
        )

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
            caller = self.boton_tema,
            items = elementos_menu,
            width = dp(170),
            position = "auto",
        )

        self.menu_tema.open()

    def seleccionar_tipo(self, tipo: str) -> None:
        """Selecciona un tipo de incapacidad."""
        self.tipo_seleccionado = tipo

        self.actualizar_botones_tipo()
        
    def actualizar_botones_tipo(self) -> None:
        """Actualiza el estilo visual de los tipos de incapacidad."""
        tema_actual = self.obtener_tema_actual()
        paleta = PALETAS[tema_actual]

        for tipo, boton in self.botones_tipo.items():
            if tipo == self.tipo_seleccionado:
                boton.style = "filled"
                boton.md_bg_color = paleta["azul"]
                boton.texto_boton.theme_text_color = "Custom"
                boton.texto_boton.text_color = paleta["blanco"]
            else:
                boton.style = "outlined"
                boton.md_bg_color = paleta["tarjeta"]
                boton.texto_boton.theme_text_color = "Custom"
                boton.texto_boton.text_color = paleta["azul_secundario"]

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
        
        for boton in (
            self.boton_resultado,
            self.boton_informacion,
        ):
            boton.theme_text_color = "Custom"
            boton.text_color = paleta["azul_secundario"]
        
        self.actualizar_botones_tipo()

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

        tipo_mostrado = self.tipo_seleccionado
        if tipo_mostrado is None:
            raise ValueError(
                "Debes Seleccionar un Tipo de Incapacidad"
            )
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
        """Muestra y destaca el resultado de un nuevo cálculo."""

        self.resultado.text = (
            f"Pago Estimado:\n"
            f"{formatear_cop(pago)} COP\n"
            f"{tipo_incapacidad} | {dias} días | "
            f"Caso {id_caso}"
        )
        
        self.aviso_nuevo_resultado.text = TEXTO_NUEVO_RESULTADO

        self.contenido_resultado.opacity = 1
        self.contenido_resultado.disabled = False
        
        self.tarjeta_resultado.esta_expandida = True

        self.boton_resultado.actualizar_texto(
            TEXTO_CONTRAER
        )
        
    def actualizar_altura_resultado(self, instancia, tamano):
        """Ajusta la tarjeta de resultado según el texto."""

        altura_texto = tamano[1]

        nueva_altura_contenido = altura_texto + dp(15)

        self.contenido_resultado.height = nueva_altura_contenido

        self.tarjeta_resultado.height = (
            nueva_altura_contenido + dp(60)
        )
        self.tarjeta_resultado.height = max(
            self.tarjeta_resultado.height,
            ALTURA_RESULTADO_EXPANDIDO
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
            texto_limpio = texto.replace(".", "")
            return float(texto_limpio)

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
            f"Caso {caso['id']} | "
            f"{caso['tipo_incapacidad']} | "
            f"{caso['dias']} días\n"
            f"Salario: {formatear_cop(caso['salario'])} | "
            f"Pago: {formatear_cop(caso['pago'])}"
        )

    # ========================================================
    # FORMULARIO Y ERRORES
    # ========================================================

    def limpiar(self, _boton: MDButton) -> None:
        """Restablece el formulario y el resultado"""
        self.entrada_salario.text = ""
        self.entrada_dias.text = ""

        self.tipo_seleccionado = VALOR_TIPO_INICIAL
        self.actualizar_botones_tipo()
        

        self.resultado.text = TEXTO_RESULTADO_INICIAL
        self.aviso_nuevo_resultado.text = ""
        
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