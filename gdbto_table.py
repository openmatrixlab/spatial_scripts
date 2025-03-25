import os
import pandas as pd
from datetime import datetime


def gdb_tables_to_excel(gdb_path, output_excel=None, exclude_patterns=None):

    # Patrones de exclusión por defecto (capas de topología)
    if exclude_patterns is None:
        exclude_patterns = [
            '*topology*', '*Topology*', '*topo*', '*Topo*',  # Topología general
            '*_Dirty*', '*_dirty*',  # Áreas con errores topológicos
            '*_Err*', '*_err*',  # Errores
            '*_Fix*', '*_fix*',  # Correcciones
            '*_Rule*', '*_rule*',  # Reglas topológicas
            '*_Valid*', '*_valid*',  # Validación
            '*_Check*', '*_check*',  # Verificaciones
            '*_Correction*', '*_correction*'  # Correcciones
        ]

    # Importar geopandas
    try:
        import geopandas as gpd
        import fiona
        from fnmatch import fnmatch
    except ImportError:
        raise ImportError("Se requiere instalar geopandas y fiona: pip install geopandas fiona")

    # Validar que la GDB existe
    if not os.path.exists(gdb_path):
        raise ValueError(f"La geodatabase {gdb_path} no existe")

    # Crear nombre para el archivo Excel si no se proporciona
    if output_excel is None:
        gdb_name = os.path.basename(gdb_path).replace('.gdb', '')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = os.path.dirname(gdb_path)
        output_excel = os.path.join(output_dir, f"{gdb_name}_export_{timestamp}.xlsx")

    print(f"Procesando geodatabase: {gdb_path}")
    print(f"El archivo Excel se guardará en: {output_excel}")

    # Verificar disponibilidad de drivers de manera compatible con versiones anteriores
    print("Verificando drivers disponibles...")
    try:
        # Método compatible con versiones más recientes
        drivers = fiona.supported_drivers
        print(f"Se encontraron {len(drivers)} drivers compatibles")
    except AttributeError:
        # Alternativa para versiones antiguas de Fiona
        print("No se pudo obtener lista de drivers (versión antigua de Fiona)")
        drivers = {"FileGDB": "rw", "OpenFileGDB": "rw"}  # Asumir soporte básico

    # Verificar si hay soporte para GDB
    gdb_supported = False
    for driver_name in ["FileGDB", "OpenFileGDB"]:
        if driver_name in drivers:
            gdb_supported = True
            print(f"Soporte para geodatabases detectado: {driver_name}")

    if not gdb_supported:
        print("ADVERTENCIA: No se detectó soporte explícito para geodatabases de Esri")
        print("Se intentará abrir la geodatabase de todas formas...")

    # Listar capas disponibles
    try:
        print("\nIntentando listar capas de la geodatabase...")
        all_layers = fiona.listlayers(gdb_path)
        print(f"Se encontraron {len(all_layers)} capas en total")

        # Filtrar capas según los patrones a excluir
        layers = []
        excluded_layers = []

        for layer in all_layers:
            # Verificar si la capa coincide con algún patrón de exclusión
            should_exclude = False
            for pattern in exclude_patterns:
                if fnmatch(layer.lower(), pattern.lower()):
                    should_exclude = True
                    break

            if should_exclude:
                excluded_layers.append(layer)
            else:
                layers.append(layer)

        print(f"Se procesarán {len(layers)} capas (se excluyeron {len(excluded_layers)} capas de topología)")
        if excluded_layers:
            print("\nCapas excluidas:")
            for excluded in excluded_layers:
                print(f" - {excluded}")

        if len(layers) == 0:
            raise ValueError("No quedan capas para procesar después de aplicar los filtros")

    except Exception as e:
        print(f"Error al listar capas: {e}")
        raise ValueError("No se pudo acceder a la geodatabase. Verifica que el formato es compatible.")

    # Crear un escritor de Excel
    with pd.ExcelWriter(output_excel, engine='openpyxl') as writer:
        # Procesar cada capa
        for i, layer_name in enumerate(layers):
            try:
                print(f"Procesando capa {i + 1}/{len(layers)}: {layer_name}")

                # Crear un nombre válido para la hoja de Excel (máx 31 caracteres)
                sheet_name = str(layer_name).replace('/', '_')[:31]

                try:
                    # Leer la capa como GeoDataFrame
                    gdf = gpd.read_file(gdb_path, layer=layer_name)

                    # Convertir geometría a texto WKT para Excel si existe
                    if 'geometry' in gdf.columns:
                        # Convertir geometría a texto WKT
                        wkt_series = gdf['geometry'].apply(lambda geom: geom.wkt if geom else None)

                        # Eliminar la columna de geometría y añadir la versión WKT
                        df = pd.DataFrame(gdf.drop(columns=['geometry']))
                        df['geometry_wkt'] = wkt_series
                    else:
                        df = pd.DataFrame(gdf)

                    # Exportar a Excel
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f"  ✓ {len(df)} registros exportados a hoja '{sheet_name}'")

                except Exception as layer_err:
                    print(f"  ✗ Error al procesar capa {layer_name}: {layer_err}")

                    # Intentar alternativa: abrir como tabla sin geometría
                    try:
                        print(f"    Intentando abrir {layer_name} como tabla sin geometría...")
                        # Usar pandas directamente si es posible
                        with fiona.open(gdb_path, layer=layer_name) as src:
                            # Convertir a DataFrame
                            records = [record['properties'] for record in src]
                            df = pd.DataFrame.from_records(records)

                            # Exportar a Excel
                            df.to_excel(writer, sheet_name=sheet_name, index=False)
                            print(f"  ✓ {len(df)} registros exportados a hoja '{sheet_name}' (modo tabla)")
                    except Exception as table_err:
                        print(f"    ✗ También falló al abrir como tabla: {table_err}")

            except Exception as e:
                print(f"  ✗ Error general al procesar {layer_name}: {str(e)}")

    print(f"\n¡Proceso completado! Archivo Excel guardado en: {output_excel}")
    return output_excel


if __name__ == "__main__":
    print("=== Exportador de GDB a Excel (excluyendo capas de topología) ===")
    gdb_path = input("Ingresa la ruta completa a la geodatabase (.gdb): ")
    output_path = input(
        "Ingresa la ruta de salida del Excel (opcional, presiona Enter para usar la ubicación por defecto): ")

    # Solicitar patrones de exclusión personalizados (opcional)
    custom_exclusions = input("¿Quieres añadir patrones de exclusión adicionales? (s/n): ")
    exclude_patterns = None

    if custom_exclusions.lower() == 's':
        patterns = []
        print("Ingresa los patrones uno por uno (presiona Enter con un patrón vacío para terminar):")
        while True:
            pattern = input("Patrón (ej. '*topo*'): ")
            if not pattern:
                break
            patterns.append(pattern)

        if patterns:
            exclude_patterns = patterns

    if not output_path.strip():
        output_path = None

    try:
        gdb_tables_to_excel(gdb_path, output_path, exclude_patterns)
    except Exception as e:
        print(f"\nError: {str(e)}")

    input("\nPresiona Enter para salir...")