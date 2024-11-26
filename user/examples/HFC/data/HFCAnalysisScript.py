import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Load Data Flags
doLoadData = True
doMarinate = False
doPlotData = True

# Function to load CO2 data
def importCO2file(filepath, start_row, end_row):
    data = pd.read_csv(filepath, skiprows=start_row-1, nrows=end_row-start_row+1, header=None)
    time_data = pd.to_datetime(data[0])
    co2_data = data[1].astype(float)
    return time_data, co2_data

# Weighted Mean Function
def weighted_mean(values, weights):
    return np.average(values, weights=weights)

# Bin Data Function
def bin_data(time_array, co2_array, error_array, common_time):
    co2_binned = []
    co2_error = []
    co2_count = []
    dt = common_time[1] - common_time[0]

    for i in range(len(common_time) - 1):
        indices = (time_array >= common_time[i]) & (time_array < common_time[i+1])
        if indices.any():
            weights = 1 / error_array[indices]**2
            co2_binned.append(np.average(co2_array[indices], weights=weights))
            co2_error.append(np.sqrt(np.sum((error_array[indices])**2)) / len(error_array[indices]))
            co2_count.append(len(indices))
        else:
            co2_binned.append(np.nan)
            co2_error.append(np.nan)
            co2_count.append(0)
    return np.array(co2_binned), np.array(co2_error), np.array(co2_count)

if doLoadData:
    print("Loading Data:")
    
    # Load Upstream and Downstream CO2 data
    UpTime_2, UpCO2_2 = importCO2file('data/April-04-2017-upstrm2.csv', 3, 1220)
    UpTime_1, UpCO2_1 = importCO2file('data/April-05-2017 - upstrm.csv', 3, 2060)
    DnTime_2, DnCO2_2 = importCO2file('data/April-04-2017-dwnstrm2.csv', 3, 1217)
    DnTime_1, DnCO2_1 = importCO2file('data/April-05-2017 - dwnstrm.csv', 3, 2098)
    
    # Combine data
    UpTime = pd.concat([UpTime_2, UpTime_1])
    UpCO2 = np.concatenate([UpCO2_2, UpCO2_1])
    DnTime = pd.concat([DnTime_2, DnTime_1])
    DnCO2 = np.concatenate([DnCO2_2, DnCO2_1])

    # Calculate Errors
    UpErr = np.full_like(UpCO2, 50)
    UpErr[UpCO2 >= 1667] = 0.03 * UpCO2[UpCO2 >= 1667]
    DnErr = np.full_like(DnCO2, 50)
    DnErr[DnCO2 >= 1667] = 0.03 * DnCO2[DnCO2 >= 1667]

    # Bin Data to Common Time
    Time_C = np.linspace(min(min(DnTime), min(UpTime)), max(max(DnTime), max(UpTime)), 1200)[:-1]
    UpCO2_C, UpCO2_E, UpCO2_n = bin_data(UpTime, UpCO2, UpErr, Time_C)
    DnCO2_C, DnCO2_E, DnCO2_n = bin_data(DnTime, DnCO2, DnErr, Time_C)

    # Remove Gaps
    valid_indices = (UpCO2_n > 0) & (DnCO2_n > 0)
    Time_C = Time_C[valid_indices]
    UpCO2_C, UpCO2_E, DnCO2_C, DnCO2_E = UpCO2_C[valid_indices], UpCO2_E[valid_indices], DnCO2_C[valid_indices], DnCO2_E[valid_indices]

    # Delta PPM and Errors
    PPM2T = 3200
    dPPM2T = 0
    Delta_C = PPM2T * (UpCO2_C - DnCO2_C) / UpCO2_C
    Delta_E = np.sqrt(((PPM2T * DnCO2_C / UpCO2_C**2)**2) * UpCO2_E**2 +
                      ((-PPM2T / UpCO2_C)**2) * DnCO2_E**2 +
                      ((1 - DnCO2_C / UpCO2_C)**2) * dPPM2T**2)

if doPlotData:
    print("Plotting Data:")
    
    plt.figure(figsize=(12, 8))
    
    # Plot Upstream and Downstream CO2
    plt.subplot(2, 1, 1)
    plt.plot(Time_C, UpCO2_C, label="Upstream CO2", color="blue")
    plt.plot(Time_C, DnCO2_C, label="Downstream CO2", color="red")
    plt.plot(Time_C, Delta_C, label="Delta CO2", color="green")
    plt.legend()
    plt.grid()
    plt.xlabel("Time")
    plt.ylabel("CO2 Concentration [PPM]")
    plt.title("CO2 Measurements Over Time")
    
    # Plot Gas Flow Trials
    plt.subplot(2, 1, 2)
    plt.errorbar([0.2, 0.3, 0.4, 0.5, 0.6], [1.1, 1.5, 1.7, 2.0, 2.3], yerr=[0.1, 0.1, 0.2, 0.2, 0.3], fmt='o', label="Experiment")
    plt.plot([0.2, 0.6], [1.0, 2.5], label="Model")
    plt.legend()
    plt.grid()
    plt.xlabel("Gas Flow Rate [SLPM]")
    plt.ylabel("CO2 Uptake [PPM]")
    plt.title("CO2 Uptake vs. Gas Flow Rate")
    
    plt.tight_layout()
    plt.show()
