import os
from osgeo import ogr
import pandas as pd
from multiprocessing import Pool

# Ruta base donde están las carpetas y geodatabases
base_path = ""


# Función para procesar una sola geodatabase
def procesar_gdb(gdb_path):
    resultados = []
    driver = ogr.GetDriverByName("OpenFileGDB")
    data_source = driver.Open(gdb_path, 0)

    if not data_source:
        print(f"No se pudo abrir la geodatabase: {gdb_path}")
        return resultados

    # Iterar sobre las capas de la geodatabase
    for i in range(data_source.GetLayerCount()):
        try:
            layer = data_source.GetLayerByIndex(i)
            layer_name = layer.GetName()
            num_features = layer.GetFeatureCount()  # Número de objetos en la capa
            layer_definition = layer.GetLayerDefn()

            # Obtener los atributos y tipos
            for j in range(layer_definition.GetFieldCount()):
                field = layer_definition.GetFieldDefn(j)
                field_name = field.GetName()
                field_type = field.GetFieldTypeName(field.GetType())

                # Agregar a la lista de resultados
                resultados.append({
                    "GDB": os.path.basename(gdb_path),
                    "Ruta": gdb_path,
                    "Capa": layer_name,
                    "Num_Objetos": num_features,
                    "Campo": field_name,
                    "Tipo": field_type
                })

            print(f"Procesada capa {i + 1}/{data_source.GetLayerCount()} de {os.path.basename(gdb_path)}")
        except Exception as e:
            print(f"Error procesando la capa {i} en {gdb_path}: {e}")

    print(f"Procesada GDB: {os.path.basename(gdb_path)}")
    return resultados


# Función principal para recorrer la carpeta base y subcarpetas
def buscar_geodatabases():
    gdb_paths = []

    # Recorrer todas las carpetas y buscar archivos .gdb
    for root, dirs, files in os.walk(base_path):
        for dir_name in dirs:
            if dir_name.endswith(".gdb"):
                gdb_path = os.path.join(root, dir_name)
                gdb_paths.append(gdb_path)

    return gdb_paths


# Procesar GDBs en paralelo
def procesar_todas_gdbs(gdb_paths):
    all_results = []

    with Pool(processes=4) as pool:  # Ajusta el número de procesos según tu CPU
        results = pool.map(procesar_gdb, gdb_paths)
        for r in results:
            all_results.extend(r)

    return all_results


# Guardar los resultados en un archivo CSV
def guardar_resultados(resultados):
    if resultados:
        df = pd.DataFrame(resultados)
        output_path = os.path.join(os.getcwd(), "atributos_gdbs.csv")
        df.to_csv(output_path, index=False)
        print(f"Proceso completado. Resultados guardados en: {output_path}")
    else:
        print("No se encontraron GDBs para procesar o no se generaron resultados.")


# Función principal
def main():
    print("Buscando geodatabases...")
    gdb_paths = buscar_geodatabases()

    if not gdb_paths:
        print("No se encontraron geodatabases en la ruta especificada.")
        return

    print(f"Se encontraron {len(gdb_paths)} geodatabases. Procesando...")
    resultados = procesar_todas_gdbs(gdb_paths)

    guardar_resultados(resultados)


# Ejecutar el script
if __name__ == "__main__":
    main()