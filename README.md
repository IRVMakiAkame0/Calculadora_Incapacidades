# Calculadora de Incapacidades

Aplicación académica para estimar el pago correspondiente a incapacidades laborales en Colombia.

El proyecto inició a partir de una lógica de negocio suministrada por el docente y posteriormente fue ampliado mediante la aplicación de principios de **Clean Code**, el desarrollo de una interfaz gráfica, persistencia de datos y la generación de aplicaciones para **Windows y Android**.

La aplicación permite realizar cálculos de incapacidades desde una interfaz gráfica y conservar un historial de los casos realizados.

---

## 📋 Tabla de contenido

* [Descripción](#-descripción)
* [Funcionalidades](#-funcionalidades)
* [Tipos de incapacidad](#-tipos-de-incapacidad)
* [Proceso de cálculo](#-proceso-de-cálculo)
* [Validaciones](#-validaciones)
* [Arquitectura](#-arquitectura)
* [Tecnologías utilizadas](#-tecnologías-utilizadas)
* [Estructura del proyecto](#-estructura-del-proyecto)
* [Requisitos](#-requisitos)
* [Instalación](#-instalación)
* [Ejecución en consola](#-ejecución-en-consola)
* [Ejecución de la interfaz gráfica](#-ejecución-de-la-interfaz-gráfica)
* [Aplicación para Windows](#-aplicación-para-windows)
* [Aplicación para Android](#-aplicación-para-android)
* [Persistencia de datos](#-persistencia-de-datos)
* [Pruebas](#-pruebas)
* [Principios de Clean Code](#-principios-de-clean-code)
* [Alcance y limitaciones](#-alcance-y-limitaciones)
* [Integrantes](#-integrantes)

---

## 📌 Descripción

La **Calculadora de Incapacidades** es una aplicación desarrollada en Python que permite estimar el valor correspondiente a un período de incapacidad laboral.

El proyecto cuenta con:

* Interfaz gráfica desarrollada con Kivy y KivyMD.
* Interfaz de consola.
* Persistencia de información mediante SQLite.
* Historial de cálculos.
* Validación de datos.
* Manejo de excepciones.
* Temas claro, oscuro y automático.
* Aplicación ejecutable para Windows.
* Aplicación empaquetada para dispositivos Android.
* Pruebas automatizadas.
* Separación entre lógica de negocio, persistencia y presentación.

El objetivo académico del proyecto es aplicar principios de **Clean Code** y buenas prácticas de desarrollo de software en un proyecto funcional.

---

# 🚀 Funcionalidades

La aplicación permite:

* Ingresar el salario mensual del trabajador.
* Ingresar la cantidad de días de incapacidad.
* Seleccionar el tipo de incapacidad.
* Calcular el pago estimado.
* Mostrar el resultado de manera clara.
* Validar los datos ingresados.
* Mostrar mensajes comprensibles cuando ocurre un error.
* Guardar los cálculos realizados.
* Consultar el historial de casos.
* Utilizar la aplicación con tema claro.
* Utilizar la aplicación con tema oscuro.
* Utilizar el tema automático según la configuración del sistema.
* Ejecutar la aplicación desde Python.
* Ejecutar la aplicación como programa de Windows.
* Utilizar la aplicación desde un dispositivo Android mediante el APK.

---

# 🏥 Tipos de incapacidad

El proyecto contempla los siguientes tipos:

| Tipo               | Porcentaje utilizado |
| ------------------ | -------------------: |
| Enfermedad general |               66.67% |
| Maternidad         |                 100% |
| Riesgo laboral     |                 100% |

Los porcentajes y reglas utilizados corresponden a la lógica académica implementada en el proyecto.

> **Nota:** Los resultados son una simulación académica y no sustituyen una liquidación oficial realizada por una entidad competente.

---

# 🧮 Proceso de cálculo

Una vez validados los datos, el programa realiza el cálculo en varias etapas:

1. Identifica el tipo de incapacidad.
2. Obtiene el porcentaje de reconocimiento correspondiente.
3. Calcula el valor diario del salario.
4. Calcula el pago correspondiente a los días de incapacidad.

El valor diario se obtiene mediante:

```text
valor_dia = salario_mensual / 30
```

Posteriormente:

```text
pago = valor_dia × porcentaje_reconocimiento × dias_incapacidad
```

### Ejemplo

Para un salario mensual de:

```text
$2.500.000
```

y una incapacidad de:

```text
5 días
```

el programa utiliza el tipo de incapacidad seleccionado para determinar el porcentaje correspondiente y calcular el valor estimado.

---

# ✅ Validaciones

Antes de realizar el cálculo, el programa verifica que la información ingresada sea válida.

Entre las principales validaciones se encuentran:

* Salario menor o igual a cero.
* Días de incapacidad menores o iguales a cero.
* Tipo de incapacidad inexistente.
* Valores no numéricos.
* Datos incompletos.

El proyecto utiliza excepciones específicas para representar diferentes errores de entrada.

Esto permite separar la validación de la lógica principal y mostrar mensajes comprensibles al usuario.

---

# 🏗️ Arquitectura

El proyecto utiliza una estructura separada por responsabilidades.

La lógica principal se encuentra en el modelo, mientras que las diferentes interfaces funcionan como capas de presentación.

```text
                    ┌─────────────────────┐
                    │      Usuario        │
                    └──────────┬──────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                 │
       ┌──────▼──────┐                   ┌──────▼──────┐
       │   Consola   │                   │     GUI     │
       │   (View)    │                   │   Kivy/KivyMD│
       └──────┬──────┘                   └──────┬──────┘
              │                                 │
              └────────────────┬────────────────┘
                               │
                       ┌───────▼────────┐
                       │     Modelo     │
                       │   Incapacidad  │
                       └───────┬────────┘
                               │
                 ┌─────────────┴─────────────┐
                 │                           │
          ┌──────▼──────┐             ┌──────▼──────┐
          │ Validaciones│             │   Cálculo   │
          └─────────────┘             └─────────────┘
                               │
                       ┌───────▼────────┐
                       │    SQLite      │
                       │   Persistencia │
                       └────────────────┘
```

La separación de responsabilidades permite modificar la interfaz sin tener que duplicar la lógica de cálculo.

---

# 📁 Estructura del proyecto

```text
Calculadora_Incapacidades/
│
├── .github/
│   └── workflows/
│       └── build-windows.yml
│
├── doc/
│
├── src/
│   ├── database/
│   │   ├── __init__.py
│   │   └── database.py
│   │
│   ├── model/
│   │   └── incapacidad.py
│   │
│   └── view/
│       ├── console/
│       │   └── main.py
│       │
│       └── gui/
│           └── main.py
│
├── test/
│   └── test_incapacidad.py
│
├── .gitignore
├── buildozer.spec
├── main.py
├── requirements.txt
└── README.md
```

### `src/model/`

Contiene la lógica de negocio de la aplicación.

Aquí se encuentran las funciones relacionadas con:

* cálculo de incapacidades;
* validación de datos;
* tipos de incapacidad;
* excepciones.

### `src/database/`

Contiene la lógica encargada de la persistencia de los datos mediante SQLite.

Permite:

* crear la base de datos;
* guardar casos;
* consultar el historial.

### `src/view/console/`

Contiene la interfaz de consola.

Permite ejecutar la calculadora desde una terminal.

### `src/view/gui/`

Contiene la interfaz gráfica desarrollada con Kivy y KivyMD.

Incluye:

* formulario de cálculo;
* selección del tipo de incapacidad;
* resultados;
* historial;
* temas claro y oscuro;
* validaciones visuales.

### `test/`

Contiene las pruebas automatizadas de la lógica de negocio.

### `.github/workflows/`

Contiene la configuración de GitHub Actions utilizada para automatizar la generación de la aplicación para Windows.

---

# 🛠️ Tecnologías utilizadas

| Tecnología         | Uso                                           |
| ------------------ | --------------------------------------------- |
| Python             | Lenguaje principal                            |
| Kivy               | Desarrollo de la interfaz gráfica             |
| KivyMD             | Componentes y diseño de la interfaz           |
| SQLite             | Persistencia de datos                         |
| Pytest             | Pruebas automatizadas                         |
| PyInstaller        | Generación del ejecutable de Windows          |
| Buildozer          | Empaquetado de la aplicación Android          |
| Python-for-Android | Construcción del paquete Android              |
| Git                | Control de versiones                          |
| GitHub             | Repositorio y colaboración                    |
| GitHub Actions     | Automatización de la compilación para Windows |

---

# 💻 Requisitos

Para ejecutar el proyecto desde código fuente se necesita:

* Python 3.12 recomendado.
* Git.
* Las dependencias especificadas en `requirements.txt`.

Las dependencias principales del proyecto son:

```text
Kivy
KivyMD
Pytest
```

La configuración utilizada para Android define además las dependencias necesarias para Buildozer y Python-for-Android.

---

# 📥 Instalación

Clonar el repositorio:

```bash
git clone https://github.com/IRVMakiAkame0/Calculadora_Incapacidades.git
```

Entrar al proyecto:

```bash
cd Calculadora_Incapacidades
```

Crear un entorno virtual:

### Windows

```bash
python -m venv .venv
```

Activar el entorno:

```bash
.venv\Scripts\activate
```

Actualizar pip:

```bash
python -m pip install --upgrade pip
```

Instalar las dependencias:

```bash
python -m pip install -r requirements.txt
```

---

# 🖥️ Ejecución en consola

Desde la raíz del proyecto:

```bash
python -m src.view.console.main
```

La versión de consola utiliza la misma lógica de negocio que la aplicación gráfica.

Esto permite comprobar que la lógica está separada de la interfaz.

---

# 🖼️ Ejecución de la interfaz gráfica

Desde la raíz del proyecto:

```bash
python -m src.view.gui.main
```

La interfaz gráfica permite realizar los cálculos de forma visual y consultar el historial de casos almacenados.

---

# 🪟 Aplicación para Windows

El proyecto incluye una configuración de **GitHub Actions** para generar automáticamente la aplicación de Windows.

El workflow utiliza:

* Windows como sistema de compilación.
* Python 3.12.
* PyInstaller.
* Las dependencias del proyecto.
* Las pruebas unitarias antes de generar el ejecutable.

El workflow se encuentra en:

```text
.github/workflows/build-windows.yml
```

El ejecutable se genera utilizando PyInstaller.

El proceso utiliza:

```bash
python -m PyInstaller \
    --noconfirm \
    --clean \
    --onedir \
    --windowed \
    --name CalculadoraIncapacidades \
    --paths . \
    src/view/gui/main.py
```

El resultado se genera dentro de:

```text
dist/CalculadoraIncapacidades/
```

El workflow de GitHub Actions publica esta carpeta como un artefacto denominado:

```text
CalculadoraIncapacidades-Windows
```

De esta manera, el programa puede utilizarse en Windows sin necesidad de ejecutar directamente el código fuente de Python.

---

# 📱 Aplicación para Android

El proyecto también fue preparado para generar una aplicación para dispositivos Android utilizando **Buildozer** y **Python-for-Android**.

La configuración se encuentra en:

```text
buildozer.spec
```

Actualmente la configuración establece:

```text
title = Calculadora de Incapacidades
package.name = calculadoraincapacidades
package.domain = com.calculadoraincapacidades
```

La aplicación está configurada para ejecutarse en orientación vertical:

```text
orientation = portrait
```

También se definen las arquitecturas Android:

```text
arm64-v8a
armeabi-v7a
```

La configuración de Android utiliza:

```text
android.api = 33
android.minapi = 24
```

## Generar el APK

La generación del APK se realiza mediante Buildozer.

En un entorno compatible con Buildozer, ejecutar:

```bash
buildozer android debug
```

El archivo generado se encontrará en:

```text
bin/
```

El APK generado puede transferirse posteriormente a un dispositivo Android para realizar las pruebas de funcionamiento.

## Configuración del APK

El proyecto utiliza las siguientes dependencias para la aplicación Android:

```text
python3
kivy==2.3.1
kivymd==2.0.0
filetype
materialyoucolor
asynckivy
asyncgui
```

Estas dependencias se encuentran configuradas directamente en `buildozer.spec`.

---

# 💾 Persistencia de datos

La aplicación utiliza **SQLite** para almacenar los casos calculados.

El historial permite conservar información incluso después de cerrar y volver a abrir la aplicación.

Entre los datos almacenados se encuentran:

* Tipo de incapacidad.
* Días de incapacidad.
* Salario utilizado.
* Pago calculado.

La persistencia se encuentra separada de la lógica de negocio y es gestionada por:

```text
src/database/database.py
```

Los archivos de base de datos generados localmente no deben formar parte del repositorio.

---

# 🧪 Pruebas

El proyecto cuenta con pruebas automatizadas para comprobar la lógica de cálculo.

Para ejecutar las pruebas:

```bash
python -m pytest
```

También pueden ejecutarse utilizando `unittest`:

```bash
python -m unittest discover -s test -v
```

Las pruebas permiten comprobar que los cambios realizados en la interfaz o en otras partes del proyecto no afecten la lógica principal.

Además, el proceso automatizado de construcción para Windows ejecuta las pruebas antes de generar el ejecutable.

---

# 🧹 Principios de Clean Code

Durante el desarrollo se aplicaron diferentes principios relacionados con Clean Code.

### Nombres significativos

Se utilizan nombres que permiten comprender la responsabilidad de variables, funciones y clases.

Ejemplos:

```python
salario_mensual
dias_incapacidad
tipo_incapacidad
porcentaje_reconocimiento
```

En lugar de nombres ambiguos como:

```python
x
y
dato
valor
```

### Responsabilidad única

Las diferentes partes del proyecto tienen responsabilidades separadas:

```text
Modelo       → lógica de negocio
Base de datos → persistencia
Vista         → interacción con el usuario
Pruebas      → verificación del comportamiento
```

### Separación de responsabilidades

La interfaz gráfica no contiene directamente las reglas principales del cálculo.

La lógica se encuentra centralizada en el modelo para evitar duplicación.

### Manejo de excepciones

Se utilizan excepciones específicas para representar errores relacionados con los datos ingresados.

Esto permite diferenciar los distintos tipos de errores y proporcionar mensajes adecuados al usuario.

### Evitar duplicación

Las interfaces de consola y gráfica utilizan la misma lógica de negocio.

Esto evita implementar dos veces las mismas reglas de cálculo.

### Funciones y métodos enfocados

Las funciones buscan realizar una responsabilidad concreta y evitar mezclar diferentes niveles de lógica.

### Código mantenible

La estructura modular facilita realizar cambios en una parte del proyecto sin afectar innecesariamente las demás.

---

# ⚠️ Alcance y limitaciones

Esta aplicación fue desarrollada con fines académicos.

Los resultados corresponden a una **simulación basada en las reglas implementadas en el proyecto**.

La aplicación no pretende reemplazar una liquidación oficial realizada por una EPS, ARL, empleador u otra entidad competente.

Entre las principales limitaciones se encuentran:

* No se contemplan todos los escenarios administrativos posibles.
* No se implementan todas las reglas que pueden intervenir en una liquidación real.
* El cálculo corresponde a la lógica académica definida para el proyecto.
* Los porcentajes y reglas implementados no deben interpretarse como asesoría legal o laboral.
* El resultado debe utilizarse como una estimación.

---

# 👥 Integrantes

## Desarrollo base

La lógica inicial del proyecto fue desarrollada por:

* Miguel Ángel Arango Cardona
* Juan Camilo García Castro

Esta lógica corresponde al proyecto base suministrado por el docente.

## Desarrollo y ampliación

La etapa de ampliación del proyecto fue desarrollada por:

| Integrante              | GitHub                                             |
| ----------------------- | -------------------------------------------------- |
| Isabella Ruiz Velasquez | [@IRVMakiAkame0](https://github.com/IRVMakiAkame0) |
| Andrés Rosas            | [@andres-rosas](https://github.com/andres-rosas)   |

Durante esta etapa se trabajó en:

* Aplicación de principios de Clean Code.
* Desarrollo de la interfaz gráfica.
* Integración de Kivy y KivyMD.
* Diseño visual.
* Temas claro, oscuro y automático.
* Persistencia mediante SQLite.
* Historial de casos.
* Validaciones.
* Manejo de errores.
* Pruebas.
* Generación de la aplicación para Windows.
* Preparación y generación de la aplicación Android.
* Configuración de procesos de compilación.

---

# 📄 Licencia

Este proyecto fue desarrollado con fines académicos para la aplicación de principios de Clean Code y buenas prácticas de desarrollo de software.
