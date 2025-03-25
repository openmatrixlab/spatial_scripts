# Conversión de Geodatabases ESRI a CSV

Este repositorio contiene dos scripts en Python diseñados para extraer información tabular de una Geodatabase (.gdb) y exportarla a archivos CSV utilizando `arcpy`.

## Requisitos

- Python 3.x
- ArcGIS Desktop o ArcGIS Pro (para utilizar la librería `arcpy`)
- Librerías adicionales:
  - `pandas`
  - `os`
  - `sys`
  - `time`

## Scripts incluidos

### 1. `gdbto_table.py`

Convierte una tabla específica de una Geodatabase en un archivo CSV, permitiendo seleccionar campos específicos.

#### Características

- Exporta solo los campos indicados por el usuario.
- Permite convertir cualquier tabla contenida en una `.gdb`, ya sea una tabla independiente o una capa.
- Utiliza `arcpy` para crear una tabla temporal y `pandas` para generar el CSV.

#### Uso

```bash
python gdbto_table.py <ruta_gdb> <nombre_tabla> <campos> <ruta_salida_csv>

2. GdbtoCsv.py
Convierte automáticamente todas las Feature Classes dentro de una Geodatabase en archivos CSV individuales, exportando todos los campos.

Características

Recorre todas las capas vectoriales (Feature Classes) en la GDB.
Crea un CSV por cada capa, con su mismo nombre.
Exporta todos los campos alfanuméricos (excluye geometría).
Uso

python GdbtoCsv.py <ruta_gdb> <carpeta_salida>
Parámetros

<ruta_gdb>: Ruta absoluta a la geodatabase.
<carpeta_salida>: Carpeta donde se guardarán los archivos CSV generados.
Ejemplo

python GdbtoCsv.py "C:/datos/proyecto.gdb" "C:/salida/csvs/"
