# Conversión de Geodatabases de ESRI a CSV

Este repositorio contiene dos scripts en Python que permiten convertir datos contenidos en una Geodatabase (.gdb) de ESRI a archivos CSV. Ambos scripts están enfocados en facilitar la extracción y transformación de información geoespacial en formatos tabulares de uso común.

## Requisitos

- Python 3.7 o superior
- Paquetes:
  - `arcpy` (requiere instalación de ArcGIS)
  - `os`
  - `pandas`
  - `sys`
  - `time`

## Scripts

### 1. `gdbto_table.py`

Este script permite convertir una tabla específica dentro de una Geodatabase a un archivo CSV, permitiendo al usuario seleccionar campos específicos.

#### Características

- Permite indicar el path de la Geodatabase, el nombre de la tabla, los campos a exportar y la ruta de salida.
- Utiliza `arcpy` para realizar la conversión a tabla temporal y `pandas` para exportar a CSV.

#### Uso

```bash
python gdbto_table.py <path_gdb> <nombre_tabla> <campo1,campo2,...> <salida_csv>
