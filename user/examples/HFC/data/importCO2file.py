import pandas as pd
import numpy as np
from datetime import datetime

def importCO2file(filename, start_row=3, end_row=None):
    """
    IMPORTCO2FILE: Import data from COZIR CO2 Sensor Data Files.
    Args:
        filename (str): Path to the CSV file.
        start_row (int): Row to start reading from (1-based index).
        end_row (int): Row to stop reading (1-based index, inclusive). Use None to read till the end.
    Returns:
        Time (pd.Series): Datetime column representing time.
        CO2 (np.ndarray): CO2 content in PPM as a NumPy array.
    Example:
        Time, CO2 = importCO2file('March-04-2017 - Upstream.csv', 3, 606)
    """
    # Define column names based on the structure of the CSV file
    column_names = ['Time', 'CO2', 'Other']

    # Read the CSV file
    # Skip rows before start_row, limit rows to (end_row - start_row + 1) if end_row is defined
    skip_rows = start_row - 1
    nrows = end_row - start_row + 1 if end_row else None

    # Load data using pandas
    data = pd.read_csv(
        filename,
        skiprows=skip_rows,
        nrows=nrows,
        usecols=[0, 1],  # Assuming 'Time' and 'CO2' are in the first two columns
        names=column_names[:2],  # Only 'Time' and 'CO2' are relevant
        parse_dates=['Time'],  # Parse 'Time' column as datetime
        date_parser=lambda x: pd.to_datetime(x, format='%m/%d/%y %H:%M:%S.%f'),
        dtype={'CO2': str}  # Read CO2 as string to handle potential issues
    )

    # Extract 'Time' and process 'CO2'
    Time = data['Time']
    CO2 = pd.to_numeric(data['CO2'], errors='coerce').to_numpy()  # Convert CO2 to numeric, replace invalid entries with NaN

    return Time, CO2

# Example usage:
# Time, CO2 = importCO2file('March-04-2017 - Upstream.csv', start_row=3, end_row=606)
