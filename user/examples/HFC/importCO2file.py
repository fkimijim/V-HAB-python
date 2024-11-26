import numpy as np
import pandas as pd

def import_CO2_file(filename, start_row=3, end_row=None):
    """
    Import data from COSIR CO2 Sensor Data Files.

    Args:
        filename (str): Path to the CSV file.
        start_row (int): Row to start reading from (1-based index, default=3).
        end_row (int): Row to stop reading (1-based index, default=None for all rows).

    Returns:
        Time (pd.Series): Datetime objects for each timestamp in the file.
        CO2 (np.ndarray): CO2 content in PPM as a numpy array.
    """
    # Define the delimiter and column types
    delimiter = ','
    datetime_format = '%m/%d/%y %H:%M:%S.%f'

    # Use pandas to read the file with appropriate rows and columns
    data = pd.read_csv(filename, delimiter=delimiter, header=None, skiprows=start_row - 1, nrows=end_row - start_row + 1 if end_row else None)

    # Parse datetime column and clean CO2 data
    try:
        Time = pd.to_datetime(data[0], format=datetime_format, errors='coerce')
    except Exception as e:
        raise ValueError(f"Error parsing datetime column: {e}")

    # Convert CO2 column to numeric, coercing errors to NaN
    try:
        CO2 = pd.to_numeric(data[1], errors='coerce').to_numpy()
    except Exception as e:
        raise ValueError(f"Error converting CO2 data to numeric: {e}")

    return Time, CO2
