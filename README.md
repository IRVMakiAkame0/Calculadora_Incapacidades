# Calculadora de Incapacidades

Este proyecto contiene una calculadora sencilla para determinar el pago correspondiente a incapacidades laborales en Colombia, contemplando los distintos tipos reconocidos por la legislación laboral: enfermedad general, maternidad y riesgo laboral.

## Entradas (Inputs)

El programa recibe la información a través de la función `calcular_pago_incapacidad`, la cual toma los siguientes parámetros:

1. **`salario_mensual`** (`int` o `float`): El salario mensual del empleado. Debe ser un valor numérico mayor a cero.
2. **`dias_incapacidad`** (`int` o `float`): El número de días que el empleado estará incapacitado. Debe ser un valor numérico mayor a cero.
3. **`tipo_incapacidad`** (`str`, opcional): Llave que determina el porcentaje de reconocimiento económico a aplicar. Por defecto es `"enfermedad_general"`. Los valores válidos están definidos en el diccionario `TIPOS_INCAPACIDAD`:

   | Llave                | Porcentaje | Fundamento legal |
   |-----------------------|-----------|-------------------|
   | `enfermedad_general`  | 66.67%    | Decreto 3135 de 1968 / Ley 776 de 2002 |
   | `maternidad`          | 100%      | Art. 236 CST, modificado por la Ley 2114 de 2021 |
   | `riesgo_laboral`      | 100%      | Ley 776 de 2002 (a cargo de la ARL) |

   Para agregar un nuevo tipo de incapacidad, basta con añadir una llave nueva a `TIPOS_INCAPACIDAD` en `incapacidad.py`; no es necesario modificar la lógica de cálculo.

### Validaciones

El programa realiza validaciones sobre los datos de entrada y, si fallan, lanza una excepción propia en lugar de una genérica:

- **`tipo_incapacidad` no reconocido** (no existe como llave en `TIPOS_INCAPACIDAD`) → `TipoIncapacidadInvalido`.
- **`salario_mensual` menor o igual a cero** → `SalarioInvalido`.
- **`dias_incapacidad` menor o igual a cero** → `DiasIncapacidadInvalidos`.
- **`salario_mensual` o `dias_incapacidad` no numéricos** (ej. texto) → `TypeError`.

Estas tres excepciones propias (`SalarioInvalido`, `DiasIncapacidadInvalidos`, `TipoIncapacidadInvalido`) están definidas en `incapacidad.py` y heredan directamente de `Exception`, no de `ValueError`.

## Proceso (Process)

Una vez validados los datos de entrada, el programa realiza los siguientes cálculos matemáticos de manera interna:

1. **Búsqueda del porcentaje:** Consulta el porcentaje de reconocimiento correspondiente al `tipo_incapacidad` recibido en el diccionario `TIPOS_INCAPACIDAD`.
2. **Cálculo del valor diario:** Divide el `salario_mensual` entre 30 (días estándar del mes laboral) para obtener cuánto gana el empleado en un día.
   > `valor_dia = salario_mensual / 30`
3. **Cálculo del pago por incapacidad:** Multiplica el valor de un día de trabajo por el porcentaje de reconocimiento y luego lo multiplica por el número de días de incapacidad.
   > `pago = valor_dia * porcentaje * dias_incapacidad`

## Salida (Outputs)

El programa retorna (devuelve) un valor de tipo `float` (número con decimales) que representa el monto total en dinero que el empleado debe recibir por el periodo de incapacidad reportado.

## Alcance y Limitaciones

Aunque la función ya distingue entre enfermedad general, maternidad y riesgo laboral, sigue siendo una aproximación simplificada frente a la norma real:

- **No valida un tope de días:** la función no limita ni ajusta el cálculo para incapacidades muy prolongadas (por ejemplo, más de 720 días). En la práctica, pasado el día 540 continuo de una incapacidad por enfermedad general, el pago deja de regirse por el esquema normal de EPS y pasa a trámites especiales de rehabilitación y calificación de pérdida de capacidad laboral. Si se ingresa un número de días superior a ese umbral, el programa igual retorna un resultado numérico, pero dicho resultado no representa necesariamente un valor jurídicamente válido y debería revisarse manualmente.
- **No calcula por tramos:** para `enfermedad_general`, la ley real varía el porcentaje según el tramo de días (66.67% del día 1 al 90, 50% del día 91 al 180). La función aplica un único porcentaje fijo a la totalidad de los días ingresados.
- **No reproduce reglas adicionales de `riesgo_laboral`:** por ejemplo, no contempla que los dos primeros días de una incapacidad por enfermedad general corren por cuenta del empleador, ni otras condiciones administrativas propias de la ARL o la EPS.

Arquitectura de carpetas

El proyecto sigue una separación simple entre lógica de negocio (modelo) e interfaz de usuario (vista):
```bash
Calculadora_Incapacidades/
├── README.md
├── doc/
│   ├── casos_prueba_incapacidad.xlsx # Casos de prueba documentados (normales, extraordinarios, error)
│   ├── Entrevista1.ogg # Entrevista con experto del tema
│   └── Entrevista2.ogg # Continuación de la entrevista
├── src/
│   ├── __init__.py
│   ├── model/
│   │   ├── __init__.py
│   │   └── incapacidad.py              # Lógica de cálculo: calcular_pago_incapacidad, TIPOS_INCAPACIDAD y excepciones propias
│   └── view/
│       └── console_view.py             # Interfaz de consola interactiva
└── test/
    ├── __init__.py
    └── test_incapacidad.py             # Pruebas unitarias del módulo de cálculo
```
src/model/incapacidad.py: contiene toda la lógica de negocio (validaciones, TIPOS_INCAPACIDAD y la función calcular_pago_incapacidad), sin ninguna dependencia de la interfaz de usuario.
src/view/console_view.py: capa de presentación que consume el modelo y gestiona la interacción por consola (menú, entradas del usuario, mensajes de error).
test/test_incapacidad.py: pruebas unitarias que validan el módulo incapacidad.py de forma aislada.

## Ejecución (Ejecutar el programa)

El proyecto cuenta con una interfaz de consola interactiva (`console_view`) que permite a los usuarios calcular el pago por incapacidad de forma guiada.

Para ejecutar el programa, debes abrir una terminal o consola, ubicarte en el directorio raíz del proyecto (donde se encuentra este archivo `README.md`) y ejecutar el siguiente comando:

```bash
python -m src.view.console_view
```

Al ejecutarlo, verás un menú interactivo que te pedirá ingresar el salario, los días de incapacidad y seleccionar el tipo de incapacidad para luego mostrar el monto total a pagar.

Pruebas (Tests)

El proyecto incluye, dentro de la carpeta test/, un archivo test_incapacidad.py que se puede ejecutar para verificar el correcto funcionamiento del programa frente a diversos casos normales, extraordinarios y de error (incluyendo los tres tipos de incapacidad y las tres excepciones propias).

Para ejecutar las pruebas unitarias, ubícate en el directorio raíz del proyecto (donde está este README.md) y ejecuta:

```bash
python -m unittest test.test_incapacidad -v
```

También puedes ejecutar todas las pruebas del proyecto (útil si en el futuro se agregan más archivos de prueba a la carpeta test/) con:

```bash
python -m unittest discover -s test -v
```

## Interfaz gráfica con Kivy

El proyecto cuenta con una interfaz gráfica desarrollada utilizando Kivy.

La interfaz permite:

- Ingresar el salario mensual.
- Ingresar los días de incapacidad.
- Seleccionar el tipo de incapacidad.
- Calcular el pago correspondiente.
- Limpiar los campos del formulario.
- Mostrar mensajes de error amigables.
- Consultar un historial de los cálculos realizados durante la sesión.

La interfaz gráfica utiliza la misma lógica de negocio que la versión de consola mediante la función `calcular_pago_incapacidad()`.

De esta manera, la lógica del cálculo no se encuentra duplicada entre las diferentes interfaces.

### Tipos de incapacidad disponibles

- Enfermedad general.
- Maternidad.
- Riesgo laboral.

## Requisitos

Se recomienda utilizar Python 3.10 o superior.

Las dependencias del proyecto se encuentran en:

`requirements.txt`

Para instalarlas:

`python -m pip install -r requirements.txt`

## Ejecutar la interfaz gráfica

Desde la raíz del proyecto ejecutar:

`python -m src.view.gui.main`

Esto iniciará la interfaz gráfica desarrollada con Kivy.

## Ejecutar la interfaz de consola

Desde la raíz del proyecto ejecutar:

`python -m src.view.console.main`

La versión de consola continúa disponible y utiliza la misma lógica de negocio que la interfaz gráfica.

## Ejecutar las pruebas unitarias

Desde la raíz del proyecto ejecutar:

`python -m unittest discover -s test -v`

Las pruebas unitarias verifican el funcionamiento de la lógica de cálculo de incapacidades.

La incorporación de la interfaz gráfica no modifica la lógica del modelo, por lo que las pruebas existentes deben continuar funcionando correctamente.

## Arquitectura

El proyecto separa la lógica de negocio de las interfaces de usuario.

La estructura principal es:

Calculadora_Incapacidades/

- src/
  - model/
    - incapacidad.py
  - view/
    - console/
      - __init__.py
      - main.py
    - gui/
      - __init__.py
      - main.py
- test/
  - test_incapacidad.py
- requirements.txt
- README.md

### Modelo

`src/model/incapacidad.py`

Contiene las reglas de negocio y el cálculo del pago de las incapacidades.

### Vista de consola

`src/view/console/main.py`

Permite utilizar el programa desde la terminal.

### Vista gráfica

`src/view/gui/main.py`

Implementa la interfaz gráfica utilizando Kivy.

Tanto la interfaz de consola como la interfaz gráfica utilizan el mismo modelo.

## Manejo de errores

La aplicación controla errores como:

- Salario inválido.
- Días de incapacidad inválidos.
- Tipo de incapacidad inválido.
- Valores no numéricos.

En la interfaz gráfica estos errores se muestran mediante mensajes amigables para el usuario y no mediante errores técnicos de Python.

## Funcionalidad adicional

Como funcionalidad adicional de la interfaz gráfica se implementó un historial de cálculos durante la sesión.

Cada cálculo exitoso registra:

- Tipo de incapacidad.
- Días de incapacidad.
- Salario utilizado.
- Pago calculado.

## Interfaz gráfica

El proyecto cuenta con una interfaz gráfica desarrollada con Kivy y KivyMD, que permite utilizar la calculadora de incapacidades de una forma visual e intuitiva.

La interfaz permite:

- Ingresar el salario mensual.
- Ingresar los días de incapacidad.
- Seleccionar el tipo de incapacidad.
- Calcular el valor estimado de la incapacidad.
- Limpiar los datos ingresados.
- Visualizar los resultados obtenidos.
- Consultar el historial de cálculos realizados.
- Utilizar temas claro, oscuro y automático.

## Persistencia de datos

La aplicación utiliza SQLite para almacenar los casos calculados.

Los cálculos realizados desde la interfaz gráfica pueden conservarse y posteriormente visualizarse en el historial de la aplicación.

## Ejecución de la interfaz gráfica

Desde la carpeta principal del proyecto:

`python -m src.view.gui.main`

---

## Interfaz gráfica y aplicación

Como continuación del proyecto base suministrado por el docente, se desarrolló una interfaz gráfica para facilitar el uso de la calculadora de incapacidades.

Esta etapa incorpora:

- Interfaz gráfica desarrollada con Kivy y KivyMD.
- Integración de la lógica de cálculo existente con la interfaz gráfica.
- Temas visuales claro, oscuro y automático.
- Persistencia de los cálculos mediante SQLite.
- Historial de casos calculados.
- Validación de los datos ingresados.
- Ejecución tanto mediante interfaz gráfica como por consola.

### Desarrollo de esta etapa

- Isabella Ruiz
- Andrés Rosas

Los autores del desarrollo inicial y de la lógica base del proyecto se conservan en los créditos originales de este repositorio.

## Instalación de dependencias

Desde la carpeta principal del proyecto:

`python -m pip install -r requirements.txt`

---


## Integrantes y contribuciones

### Desarrollo base del proyecto
El desarrollo inicial de la lógica de la calculadora de incapacidades fue realizado por:

- Miguel Ángel Arango Cardona
- Juan Camilo García Castro

### Desarrollo de interfaz gráfica y aplicación
A partir del proyecto base suministrado por el docente, esta etapa fue desarrollada por:

| Nombre | Github |
|---|---|
| Isabella Ruiz Velasquez | [@IRVMakiAkame0](https://github.com/IRVMakiAkame0). |
| Andrés Rosas | [@andres-rosas](https://github.com/andres-rosas). |

En esta etapa se implementaron y mejoraron funcionalidades como:

- Interfaz gráfica con Kivy y KivyMD.
- Diseño visual y temas de la aplicación.
- Persistencia de datos mediante SQLite.
- Historial de cálculos.
- Integración de la lógica existente con la interfaz gráfica.
- Pruebas y ajustes de funcionamiento de la aplicación.