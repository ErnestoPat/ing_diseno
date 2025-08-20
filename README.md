# Calculadora de Diseño Estructural en Acero

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Una herramienta modular de análisis y diseño para elementos de acero estructural, desarrollada en Python. Este proyecto aplica los principios de normativas de ingeniería y buenas prácticas de arquitectura de software para crear una plataforma de cálculo robusta y escalable.

## Descripción General

Este programa realiza el análisis y diseño de una viga de acero simplemente apoyada, sometida a cargas puntuales y distribuidas. Calcula las solicitaciones de diseño (momento y cortante últimos), verifica la resistencia del perfil seleccionado según la normativa AISC 360-22 y determina los requisitos de arriostramiento lateral y torsional. Finalmente, genera una memoria de cálculo profesional en formato PDF.

El proyecto está diseñado con una arquitectura de tres capas (`core`, `analysis`, `design`) que permite una gran flexibilidad, como usar las combinaciones de carga de las NTC de México con las especificaciones de diseño del AISC de Estados Unidos.

## Características Principales

- **Análisis Estructural:** Calcula diagramas de momento y cortante para vigas con cargas múltiples.
- **Combinaciones de Carga:** Implementa factores y combinaciones de normativas como:
  - ASCE 7 (para AISC 360-22)
  - NTC para Criterios y Acciones 2023 (Ciudad de México)
- **Base de Datos de Perfiles:** Carga perfiles de acero y sus propiedades directamente desde la base de datos oficial del AISC v15.0 en formato Excel.
- **Diseño a Flexión y Cortante:** Verifica la resistencia del perfil seleccionado (`φMn`, `φVn`) contra las solicitaciones (`Mu`, `Vu`) según el AISC 360-22 (LRFD).
- **Cálculo de Arriostramiento:** Determina la resistencia y rigidez requeridas para el arriostramiento lateral y torsional de vigas, así como para columnas.
- **Arquitectura Modular:** El código está desacoplado en tres capas principales, permitiendo intercambiar normativas de acciones y diseño de forma independiente.
- **Reporte Profesional:** Genera una memoria de cálculo detallada en formato PDF con todos los datos de entrada, resultados y verificaciones.

## Estructura del Proyecto

El software sigue una arquitectura de tres capas para asegurar la modularidad y escalabilidad:

SuperCalculadora_Ingenieriera/
|
|-- core/           # Herramientas base (unidades, materiales, perfiles)
|-- analysis/       # Lógica de análisis (modelo, cargas, combinaciones, solver)
|-- design/         # Lógica de diseño por material (acero, concreto, etc.)
|   |-- acero/
|
|-- reporting/      # Módulo para generar reportes en PDF.
|-- database/       # Archivos de bases de datos externas (ej. AISC).
|-- tests/          # (Futuro) Pruebas automatizadas para validar los cálculos.
|
|-- run.py          # Punto de entrada principal para ejecutar el programa.
|-- requirements.txt # Lista de dependencias del proyecto.

## Instalación y Puesta en Marcha

Sigue estos pasos para ejecutar el proyecto en tu máquina local.

### Prerrequisitos
- [Python](https://www.python.org/downloads/) (versión 3.9 o superior)
- [Git](https://git-scm.com/downloads/)

### Pasos

1.  **Clona el repositorio:**
    ```bash
    git clone [https://github.com/ErnestoPat/ing_diseno.git](https://github.com/ErnestoPat/ing_diseno.git)
    cd ing_diseno
    ```

2.  **Crea y activa un entorno virtual:**
    ```bash
    # Crear el entorno
    python -m venv .venv

    # Activar en Windows (PowerShell)
    .\.venv\Scripts\Activate.ps1

    # Activar en macOS/Linux
    source .venv/bin/activate
    ```

3.  **Instala las dependencias:**
    El archivo `requirements.txt` contiene todas las librerías necesarias.
    ```bash
    pip install -r requirements.txt
    ```

## Cómo Usar

1.  **Ajusta los parámetros:** Abre el archivo `run.py` y modifica los datos de entrada en la función `programa_principal()` según tus necesidades (datos del proyecto, propiedades de la viga, cargas, etc.).

2.  **Ejecuta el programa:**
    Asegúrate de que tu entorno virtual esté activado y ejecuta el siguiente comando en la terminal desde la carpeta raíz del proyecto:
    ```bash
    python run.py
    ```

3.  **Revisa los resultados:**
    * Verás el resumen de los cálculos impreso en la consola.
    * Una memoria de cálculo completa en PDF se habrá generado automáticamente en la carpeta `reporting/output/`.

## Hoja de Ruta (Futuras Mejoras)

- [ ] **Implementar el análisis completo de Pandeo Lateral-Torsional (LTB)** en `design/acero/beam_checker.py`.
- [ ] **Crear un módulo de diseño de arriostramientos** que proponga secciones de acero para cumplir los requisitos.
- [ ] **Desarrollar un módulo de diseño de vigas** que seleccione el perfil más ligero para unas solicitaciones dadas.
- [ ] **Añadir una interfaz gráfica de usuario (GUI)** en la carpeta `gui/` para una interacción más amigable.
- [ ] **Implementar pruebas automatizadas** en la carpeta `tests/` para garantizar la precisión de los cálculos.

## Licencia

Este proyecto está bajo la **Licencia MIT**. Consulta el archivo `LICENSE` para más detalles.

## Descargo de Responsabilidad

Esta es una herramienta de software con fines educativos y de desarrollo. Los resultados deben ser verificados por un ingeniero profesional calificado antes de su uso en cualquier aplicación real, de acuerdo con las normativas locales y las buenas prácticas de la ingeniería.