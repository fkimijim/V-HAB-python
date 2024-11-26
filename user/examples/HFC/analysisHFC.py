import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Import COZIR data
def import_CO2file(filename, start_row, end_row):
    """
    Simulated data import function. Replace with actual file reading logic if needed.
    """
    data = pd.read_csv(filename, skiprows=start_row - 1, nrows=end_row - start_row + 1)
    times = pd.to_datetime(data.iloc[:, 0])  # Assume the first column is datetime
    co2_values = data.iloc[:, 1].astype(float)  # Assume the second column is CO2
    return times, co2_values

# Simulated filenames
upstream_file_2 = "April-04-2017-upstrm2.csv"
upstream_file_1 = "April-05-2017-upstrm.csv"
downstream_file_2 = "April-04-2017-dwnstrm2.csv"
downstream_file_1 = "April-05-2017-dwnstrm.csv"

# Import upstream and downstream CO2 data
UpTime_2, UpCO2_2 = import_CO2file(upstream_file_2, 3, 1220)
UpTime_1, UpCO2_1 = import_CO2file(upstream_file_1, 3, 2060)
DnTime_2, DnCO2_2 = import_CO2file(downstream_file_2, 3, 1217)
DnTime_1, DnCO2_1 = import_CO2file(downstream_file_1, 3, 2098)

# Combine data
UpTime = np.concatenate([UpTime_2, UpTime_1])
UpCO2 = np.concatenate([UpCO2_2, UpCO2_1])
DnTime = np.concatenate([DnTime_2, DnTime_1])
DnCO2 = np.concatenate([DnCO2_2, DnCO2_1])

# Initialize Common Time Array
Time_C = np.linspace(min(np.min(DnTime), np.min(UpTime)), max(np.max(DnTime), np.max(UpTime)), 600)
dt = Time_C[1] - Time_C[0]  # Bin Width

# Initialize Data Arrays to size of Common Time
UpCO2_C = np.full(len(Time_C), np.nan)
DnCO2_C = np.full(len(Time_C), np.nan)

for i in range(len(Time_C) - 1):
    # Find all indices for Upstream measurements with times in the bin
    iFindUp = np.where((Time_C[i] <= UpTime) & (UpTime <= Time_C[i + 1]))[0]
    # Average those measurements and assign to data array
    UpCO2_C[i] = np.mean(UpCO2[iFindUp]) if len(iFindUp) > 0 else np.nan

    # Find all indices for Downstream measurements with times in the bin
    iFindDn = np.where((Time_C[i] <= DnTime) & (DnTime <= Time_C[i + 1]))[0]
    # Average those measurements and assign to data array
    DnCO2_C[i] = np.mean(DnCO2[iFindDn]) if len(iFindDn) > 0 else np.nan

# Calculate Delta
Delta = UpCO2_C - DnCO2_C

# Event times for plotting
event_times = [
    datetime(2017, 4, 4, 13, 34, 0),
    datetime(2017, 4, 4, 14, 0, 0),
    datetime(2017, 4, 4, 14, 16, 0),
    datetime(2017, 4, 4, 14, 29, 0),
    datetime(2017, 4, 5, 10, 27, 0),
    datetime(2017, 4, 5, 11, 3, 0),
    datetime(2017, 4, 5, 11, 45, 0),
    datetime(2017, 4, 5, 12, 0, 0),
    datetime(2017, 4, 5, 12, 15, 0),
    datetime(2017, 4, 5, 12, 45, 0)
]
iEvents = [np.argmin(np.abs(Time_C - event)) for event in event_times]

# Plot All CO2 Data
print("Plotting Figures:")

PlotMax = 6000
PlotMin = -500

# Plot setup
plt.figure(figsize=(12, 8))
plt.title("COZIR Sensor Measurements for HFC Characterization - Gas Flow")
plt.axis("off")

# Plot Left Panel
a1 = plt.axes([0.1, 0.1, 0.4, 0.8])
a1.grid(True)
a1.plot(Time_C, UpCO2_C, 'b', label="Upstream")
a1.plot(Time_C, DnCO2_C, 'r', label="Downstream")
a1.plot(Time_C, Delta, 'g', label="Delta CO2")
for event in iEvents[:4]:
    a1.axvline(Time_C[event], linestyle="--", color="k")
a1.set_xlim([datetime(2017, 4, 4, 13, 0, 0), np.max(DnTime_2)])
a1.set_ylim([PlotMin, PlotMax])
a1.set_ylabel("CO2 Content [PPM]")
a1.legend()

# Plot Right Panel
a2 = plt.axes([0.5, 0.1, 0.4, 0.8])
a2.grid(True)
a2.plot(Time_C, UpCO2_C, 'b')
a2.plot(Time_C, DnCO2_C, 'r')
a2.plot(Time_C, Delta, 'g')
for event in iEvents[4:]:
    a2.axvline(Time_C[event], linestyle="--", color="k")
a2.set_xlim([np.min(DnTime_1), np.max(DnTime_1)])
a2.set_ylim([PlotMin, PlotMax])
a2.set_xlabel("Time")

plt.show()
