# Clasificador de Cuentas

Este proyecto es un clasificador de cuentas que, dado un nombre de cuenta como entrada, devuelve la cuenta asociada. La aplicación utiliza dos métodos para obtener la información:

- **Lookups en Base de Datos:**  
  Se realiza una búsqueda en una base de datos preconfigurada. Si la cuenta existe, se devuelve el resultado correspondiente.

- **Inferencia con Inteligencia Artificial:**  
  En caso de no encontrar la cuenta en la base de datos, el sistema utiliza un modelo de lenguaje (LLM) basado en modelos de Llama para inferir y devolver la cuenta asociada.

---

## Características

- **Búsqueda Eficiente:**  
  Realiza consultas a una base de datos para obtener resultados rápidos mediante lookups.

- **Inteligencia Artificial para Casos No Resueltos:**  
  Si la cuenta no se encuentra en la base de datos, el sistema recurre a un motor de inferencia basado en Llama para deducir la respuesta.

- **Pruebas Automatizadas:**  
  Se incluyen tests que permiten validar el correcto funcionamiento de cada módulo y la aplicación en su conjunto.

---

## Estructura del Proyecto

```
app/
├── app.py                # Aplicación principal para probar modulos
├── client.py             # Configuraciones de la DB y del motor de inferencias (vector DB, host, modelo)
├── commands.py           # Permite ejecutar comandos sobre la DB (ver comandos abajo)
├── load_rag.ipynb        # Notebook con pruebas y formas de cargar el RAG
├── database/             # Módulo con funciones para la interacción y conexión con la base de datos
│   └── ...             
├── inference/            # Módulo con funciones para la interacción y conexión con el motor de inferencias
│   └── ...
├── tests/                # Carpeta con tests y logs de ejecución de pruebas
│   └── ...
├── rag_files/            # Carpeta con las distintas formas de cargar informacion al RAG
│   └── ...             
├── accounts/             # Carpeta con los archivos que se cargan en la DB Relacional
│   └── ...       
├── ui/                   # Módulo de interfaz para demo
│   └── ... 
```

## Instalación

1. **Crear y activar un entorno virtual:**
   
```bash
   conda create --name llama-env python=3.10.16

   conda activate llama-env
```

2. **Instalar las dependencias:**
```bash
   pip install -r requirements.txt
```

## Configuración

- **client.py:**  
  Aquí se definen las configuraciones para conectarse a la base de datos y al motor de inferencias. Puedes ajustar parámetros como la URL de la base de datos, el host y el modelo de Llama que se utilizará.

- **database e inference:**  
  Estos módulos contienen las funciones necesarias para interactuar con la base de datos y el motor de inferencias respectivamente.

---

## Comandos

Para ejecutar los comandos se utiliza

```bash
python commands.py
```
Se admiten las siguientes flags:

- **--load_db**: Carga la DB con las cuentas del archivo ./accounts/accounts.csv
- **--truncate**: Vacia las tablas de la DB.


## Uso

Para ejecutar la aplicación principal, utiliza el siguiente comando:
```bash
python app.py
```


La aplicación recibirá como input el nombre de una cuenta y devolverá la cuenta asociada, utilizando primero la base de datos para la búsqueda y, si es necesario, el motor de inferencias.

Para activar la interfaz web de demo ejecutar
```bash
python -m ui.app
```

---

## Pruebas

Los tests se encuentran en la carpeta `tests/`. Para ejecutar los tests con pytest, desde el directorio raíz del proyecto ejecuta:

```bash
pytest app/tests
```

Esto ejecutará todos los tests y mostrará los logs de ejecución.

---
