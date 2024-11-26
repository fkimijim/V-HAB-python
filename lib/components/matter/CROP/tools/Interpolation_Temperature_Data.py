import numpy as np

# Example data
afData = np.array([
    [0.0, 15.0],  # Start of the day
    [0.5, 20.0],  # Midday
    [1.0, 10.0]   # End of the day
])

fTime = 43200  # 12 hours in seconds (0.5 days)
temperature = Interpolation_Temperature_Data(afData, fTime)
print(f"Interpolated Temperature: {temperature} °C")
