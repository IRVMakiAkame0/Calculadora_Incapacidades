# Calculadora de Incapacidades

Este proyecto contiene una calculadora para determinar de manera estimada el pago correspondiente a incapacidades laborales en Colombia, contemplando los tipos de incapacidad definidos en la lógica base del proyecto: enfermedad general, maternidad y riesgo laboral.

El proyecto inició con una lógica de negocio previamente desarrollada y suministrada por el docente. En esta etapa se continuó su desarrollo mediante la implementación de una interfaz gráfica, persistencia de datos y otras mejoras orientadas a convertirlo en una aplicación más completa y fácil de utilizar.

---

## Entradas

El cálculo se realiza mediante la función `calcular_pago_incapacidad`, que recibe los siguientes parámetros:

1. **`salario_mensual`** (`int` o `float`): salario mensual del empleado. Debe ser un valor numérico mayor a cero.

2. **`dias_incapacidad`** (`int` o `float`): número de días de incapacidad. Debe ser un valor numérico mayor a cero.

3. **`tipo_incapacidad`** (`str`): determina el porcentaje de reconocimiento económico que se utilizará para realizar el cálculo.

Los tipos contemplados por el proyecto son:

| Llave | Porcentaje | Fundamento legal |
|---|---:|---|
| `enfermedad_general` | 66.67% | Decreto 3135 de 1968 / Ley 776 de 2002 |
| `maternidad` | 100% | Art. 236 CST, modificado por la Ley 2114 de 2021 |
| `riesgo_laboral` | 100% | Ley 776 de 2002 |

Los tipos y porcentajes utilizados por la aplicación se encuentran definidos en la lógica del modelo.

---

## Validaciones

El programa realiza validaciones antes de efectuar el cálculo.

Entre las principales validaciones se encuentran:

- Tipo de incapacidad no reconocido.
- Salario menor o igual a cero.
- Días de incapacidad menores o iguales a cero.
- Ingreso de valores no numéricos.

La lógica del proyecto contempla excepciones propias para controlar diferentes entradas inválidas:

- `SalarioInvalido`
- `DiasIncapacidadInvalidos`
- `TipoIncapacidadInvalido`

En la interfaz gráfica estos errores son presentados mediante mensajes comprensibles para el usuario, evitando mostrar directamente errores técnicos de Python.

---

## Proceso de cálculo

Una vez validados los datos de entrada, el programa realiza el cálculo correspondiente.

De manera general, el proceso consiste en:

1. Consultar el porcentaje correspondiente al tipo de incapacidad.
2. Calcular el valor diario del salario.
3. Aplicar el porcentaje correspondiente.
4. Multiplicar el resultado por los días de incapacidad.

El valor diario se obtiene mediante:

```text
valor_dia = salario_mensual / 30
```

Posteriormente se calcula el pago:

```text
pago = valor_dia * porcentaje * dias_incapacidad
```

---

## Salida

El programa retorna un valor numérico que representa el monto estimado correspondiente al periodo de incapacidad ingresado.

En la interfaz gráfica el resultado se presenta de manera visual junto con información relacionada con el cálculo realizado.

---

## Alcance y limitaciones

La calculadora constituye una aproximación académica al cálculo de incapacidades y no pretende reemplazar una liquidación oficial realizada por una entidad competente.

Entre sus limitaciones se encuentran:

- No contempla todos los posibles escenarios administrativos de una incapacidad prolongada.
- El cálculo de enfermedad general utiliza el porcentaje establecido por la lógica del proyecto y no realiza una liquidación completa por diferentes tramos de días.
- No reproduce todas las reglas administrativas que pueden aplicar según EPS, ARL, empleador u otras entidades.
- Los resultados deben entenderse como una simulación académica basada en las reglas implementadas en el proyecto.

---

## Arquitectura del proyecto

El proyecto mantiene separada la lógica de negocio de las diferentes interfaces de usuario.

La estructura principal incluye:

```text
Calculadora_Incapacidades/
├── src/
│   ├── model/
│   │   └── incapacidad.py
│   ├── database/
│   │   └── database.py
│   └── view/
│       ├── console/
│       │   └── main.py
│       └── gui/
│           └── main.py
├── test/
│   └── test_incapacidad.py
├── requirements.txt
└── README.md
```

### Modelo

`src/model/incapacidad.py`

Contiene la lógica de negocio relacionada con las incapacidades, incluyendo las validaciones y el cálculo correspondiente.

### Base de datos

`src/database/database.py`

Gestiona la persistencia de los casos mediante SQLite.

### Vista de consola

`src/view/console/main.py`

Permite utilizar las funcionalidades principales del programa directamente desde la terminal.

### Vista gráfica

`src/view/gui/main.py`

Contiene la interfaz gráfica de la aplicación desarrollada utilizando Kivy y KivyMD.

Tanto la interfaz gráfica como la interfaz de consola utilizan la lógica del modelo, evitando duplicar las reglas principales del cálculo.

---

## Interfaz gráfica

La aplicación cuenta con una interfaz gráfica desarrollada utilizando **Kivy** y **KivyMD**.

Entre sus funcionalidades se encuentran:

- Ingreso del salario mensual.
- Ingreso de los días de incapacidad.
- Selección del tipo de incapacidad.
- Cálculo del valor estimado.
- Presentación visual del resultado.
- Limpieza de los campos.
- Manejo amigable de errores.
- Historial de casos calculados.
- Persistencia de información.
- Tema claro.
- Tema oscuro.
- Tema automático.

La interfaz consume la lógica existente del proyecto y funciona como una nueva capa de presentación para facilitar la interacción del usuario.

---

## Persistencia de datos

La aplicación utiliza **SQLite** para almacenar los casos calculados.

Esto permite conservar información de los cálculos y posteriormente visualizar los casos registrados desde la aplicación.

Entre los datos asociados a los casos se encuentran:

- Tipo de incapacidad.
- Días de incapacidad.
- Salario utilizado.
- Pago calculado.

La persistencia permite que el historial no dependa únicamente de la sesión actual de ejecución.

---

## Requisitos

Se recomienda utilizar **Python 3.10 o superior**.

Las dependencias necesarias para ejecutar la aplicación se encuentran especificadas en:

```text
requirements.txt
```

Para instalarlas, desde la raíz del proyecto ejecutar:

```bash
python -m pip install -r requirements.txt
```

---

## Ejecutar la interfaz gráfica

Desde la carpeta raíz del proyecto ejecutar:

```bash
python -m src.view.gui.main
```

Esto iniciará la interfaz gráfica de la calculadora.

---

## Ejecutar la interfaz de consola

La versión de consola continúa disponible y utiliza la misma lógica principal del proyecto.

Para ejecutarla:

```bash
python -m src.view.console.main
```

---

## Ejecutar las pruebas

El proyecto cuenta con pruebas automatizadas para comprobar el funcionamiento de la lógica implementada.

Desde la raíz del proyecto ejecutar:

```bash
python -m pytest
```

Las pruebas permiten comprobar que las funcionalidades existentes continúan funcionando después de las modificaciones realizadas al proyecto.

---

## Integrantes y contribuciones

### Desarrollo base del proyecto

El desarrollo inicial de la lógica de la calculadora de incapacidades fue realizado por:

- Miguel Ángel Arango Cardona
- Juan Camilo García Castro

Esta lógica corresponde al proyecto base suministrado por el docente para continuar su desarrollo.

### Desarrollo de interfaz gráfica y aplicación

A partir del proyecto base suministrado, esta etapa fue desarrollada por:

| Nombre | GitHub |
|---|---|
| Isabella Ruiz Velasquez | [@IRVMakiAkame0](https://github.com/IRVMakiAkame0) |
| Andrés Rosas | [@andres-rosas](https://github.com/andres-rosas) |

Durante esta etapa se implementaron y mejoraron funcionalidades como:

- Desarrollo e integración de la interfaz gráfica.
- Uso de Kivy y KivyMD.
- Diseño visual de la aplicación.
- Implementación de temas claro, oscuro y automático.
- Integración de la lógica existente con la interfaz gráfica.
- Persistencia de información mediante SQLite.
- Historial de casos.
- Validaciones y manejo de errores desde la interfaz.
- Pruebas y ajustes de funcionamiento de la aplicación.

---
