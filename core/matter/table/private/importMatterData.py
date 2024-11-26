import csv
import numpy as np

def import_matter_data(s_target):
    """
    Imports substance data from CSV files into a structured format.
    
    Parameters:
    s_target (str): 'MatterData' to import the main data file, or the name of a specific substance.
    
    Returns:
    dict: Structured data containing substance properties and related metadata.
    """
    ttx_import_matter = {}

    if s_target == 'MatterData':
        # Import MatterData.csv
        file_path = '+matter/+data/MatterData.csv'.replace('/', '\\')
        with open(file_path, 'r') as file:
            reader = csv.reader(file, delimiter=';')
            header_row = next(reader)
            column_names = [name for name in header_row if name.strip()]
            variable_names = [name for name in next(reader) if name.strip()]
            units = [name for name in next(reader) if name.strip()]

            raw_data = [row for row in reader if any(row)]

        # Initialize column metadata
        t_columns = {col: i for i, col in enumerate(column_names)}
        t_units = {col: units[i] for i, col in enumerate(column_names)}

        # Parse the raw data into structured format
        for row in raw_data:
            substance_name = row[0]
            if substance_name not in ttx_import_matter:
                ttx_import_matter[substance_name] = {
                    "sName": row[1],
                    "ttxPhases": {},
                    "tColumns": t_columns,
                    "tUnits": t_units,
                }

            # Parse phase-specific data
            phase_type = row[2].lower()
            if phase_type not in ttx_import_matter[substance_name]["ttxPhases"]:
                ttx_import_matter[substance_name]["ttxPhases"][phase_type] = {}

            for i, col_name in enumerate(column_names[3:], start=3):
                value = row[i]
                if value.strip():
                    try:
                        value = float(value)
                    except ValueError:
                        pass
                ttx_import_matter[substance_name]["ttxPhases"][phase_type][col_name] = value

    else:
        # Import specific substance files
        info_file_path = f'+matter/+data/+NIST/{s_target}_Information_File.csv'.replace('/', '\\')
        with open(info_file_path, 'r') as file:
            lines = file.readlines()
            column_names = lines[0].strip().split(';')
            variable_names = lines[1].strip().split(';')
            units = lines[2].strip().split(';')
            values = lines[3].strip().split(';')

        for i, col_name in enumerate(column_names):
            value = values[i]
            try:
                value = float(value)
            except ValueError:
                pass
            ttx_import_matter[variable_names[i]] = value
            ttx_import_matter[f"{variable_names[i]}_Unit"] = units[i]

        ttx_import_matter["bIndividualFile"] = True

        # Import isochoric and isobaric data
        for data_type in ["Isochoric", "Isobaric"]:
            header_file_path = f'+matter/+data/+NIST/{s_target}_{data_type}_HeaderFile.csv'.replace('/', '\\')
            data_file_path = f'+matter/+data/+NIST/{s_target}_{data_type}_DataFile.csv'.replace('/', '\\')

            with open(header_file_path, 'r') as file:
                headers = file.readlines()
                column_names = headers[0].strip().split(';')
                units = headers[1].strip().split(';')

            with open(data_file_path, 'r') as file:
                raw_data = np.loadtxt(file, delimiter=';', skiprows=0)

            ttx_import_matter[f"t{data_type}Data"] = {"tColumns": {}, "tUnits": {}, "Phases": {}}
            for i, col_name in enumerate(column_names):
                ttx_import_matter[f"t{data_type}Data"]["tColumns"][col_name] = i
                ttx_import_matter[f"t{data_type}Data"]["tUnits"][col_name] = units[i]

            # Organize data by phase
            phases = {"solid": 1, "liquid": 2, "gas": 3, "supercritical": 4}
            for phase_name, phase_id in phases.items():
                phase_data = raw_data[raw_data[:, ttx_import_matter[f"t{data_type}Data"]["tColumns"]["Phase"]] == phase_id]
                ttx_import_matter[f"t{data_type}Data"]["Phases"][phase_name] = phase_data

    return ttx_import_matter
