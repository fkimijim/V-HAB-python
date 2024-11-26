import os
import csv
import numpy as np


def importPlantParameters(*args):
    """
    Reads the PlantParameters.csv file and imports plant parameters. Optionally, imports specific plant parameters if a plant species is provided.
    
    Args:
        args: Optional, plant species name as a string.
        
    Returns:
        ttxImportPlantParameters: Dictionary of imported plant parameters.
    """
    # File path to the CSV file
    file_path = os.path.join('lib', '+components', '+matter', '+PlantModule', '+plantparameters', 'PlantParameters.csv')
    
    # Open the file and read the first line to determine the column names
    with open(file_path, 'r') as file:
        reader = csv.reader(file)
        csFirstRow = next(reader)
        csColumnNames = [col.strip() for col in csFirstRow if col.strip()]

        iNumberOfColumns = len(csColumnNames)

        # Read the second row (variable names)
        csSecondRow = next(reader)
        csVariableNames = [var.strip() for var in csSecondRow[:iNumberOfColumns] if var.strip()]

        # Read the third row (units)
        csThirdRow = next(reader)
        csUnits = [unit.strip() for unit in csThirdRow[:iNumberOfColumns] if unit.strip()]

        # Read all remaining rows
        data = list(reader)

    # Process raw data into numeric and string components
    csRawData = []
    for row in data:
        processed_row = [elem.strip() if elem.strip() else None for elem in row[:iNumberOfColumns]]
        csRawData.append(processed_row)

    # Extract column data
    afNumericData = np.full((len(csRawData), iNumberOfColumns), np.nan)
    for iColumn in range(1, iNumberOfColumns):  # Skip the first column (text)
        for iRow, value in enumerate(csRawData):
            try:
                afNumericData[iRow, iColumn] = float(value[iColumn].replace(',', '')) if value[iColumn] else np.nan
            except ValueError:
                afNumericData[iRow, iColumn] = np.nan

    csRawStringColumns = [row[0] for row in csRawData]

    # Initialize output dictionary
    ttxImportPlantParameters = {}

    # Create column and unit dictionaries
    tColumns = {name: idx for idx, name in enumerate(csColumnNames)}
    tUnits = {name: unit for name, unit in zip(csColumnNames, csUnits)}

    # Process substances
    for iRow, substance in enumerate(csRawStringColumns):
        if substance not in ttxImportPlantParameters:
            ttxImportPlantParameters[substance] = {}

            # Process properties for the substance
            for iCol, colName in enumerate(csColumnNames):
                if iCol >= len(csVariableNames):
                    continue
                ttxImportPlantParameters[substance][colName] = csRawData[iRow][iCol]

            # Add column and unit dictionaries
            ttxImportPlantParameters[substance]['tColumns'] = tColumns
            ttxImportPlantParameters[substance]['tUnits'] = tUnits

    # If a specific plant species is provided, filter the data
    if len(args) >= 1:
        sPlantSpecies = args[0]
        if sPlantSpecies in ttxImportPlantParameters:
            txPlantParameters = ttxImportPlantParameters[sPlantSpecies]

            # Import coefficient matrices for CQY
            cqy_path = os.path.join(
                'lib', '+components', '+matter', '+PlantModule', '+plantparameters', f'{sPlantSpecies}_Coefficient_Matrix_CQY.csv'
            )
            txPlantParameters['mfMatrix_CQY'] = np.loadtxt(cqy_path, delimiter=',')

            # Import coefficient matrices for T_A
            ta_path = os.path.join(
                'lib', '+components', '+matter', '+PlantModule', '+plantparameters', f'{sPlantSpecies}_Coefficient_Matrix_T_A.csv'
            )
            txPlantParameters['mfMatrix_T_A'] = np.loadtxt(ta_path, delimiter=',')

            # Additional calculations
            txPlantParameters['fAlpha'] = 0.0036  # Unit conversion factor

            # Fresh basis water factor for edible biomass
            wbf = float(txPlantParameters.get('fWBF', 0))
            txPlantParameters['fFBWF_Edible'] = wbf * (1 - wbf) ** -1 if wbf != 1 else float('inf')

            # Fresh basis water factor for inedible biomass
            txPlantParameters['fFBWF_Inedible'] = 9

            return txPlantParameters

    return ttxImportPlantParameters
