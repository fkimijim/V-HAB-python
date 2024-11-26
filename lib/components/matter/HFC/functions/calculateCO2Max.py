import numpy as np
import matplotlib.pyplot as plt

# Calculate the max amount of CO2 at 1 atm and 298 K in BMIM Ac based on H2O content in the IL
xH2O = np.linspace(0, 1, 100)  # mol fraction
a = 11  # water effect coefficient
b = 18  # water effect coefficient
z = 1.84  # mol CO2 / dm^3 IL (pure component capacity)

fMolarityCO2 = z / (1 + b * np.exp(a * (xH2O - 1)))  # mol CO2 / dm^3 IL
fMolarityCO2 = fMolarityCO2 * 1000  # mol CO2 / m^3 IL

M = [0.19826, 0.17021]  # kg/mol

# Plot CO2 concentration vs. H2O mol fraction in IL
plt.figure(1)
plt.plot(xH2O, fMolarityCO2)
plt.xlabel('x_H₂O - mol fraction H₂O in IL')
plt.ylabel('y_CO₂ - concentration CO₂ in IL (mol CO₂/m³ IL)')
plt.show()

# Density values
afDensity = {
    1: np.array([1054.0, 1054.0, 1039.7, 1027.1]),  # [kg/m³]
    2: np.array([1103.5, 1097.2, 1084.7, 1072.9])   # [kg/m³]
}

# CO2 content data from Yokozeki & Shiflet (2008)
fMinTemp = 283.1  # [K]
fMaxTemp = 348.1  # [K]
afTemperatureData = np.array([283.1, 298.1, 323.1, 348.1])  # [K]
afTemperature = np.linspace(fMinTemp, fMaxTemp, 100)  # [K]

afPressureData = {
    1: 1000000 * np.array([
        [0.0102, 0.0502, 0.1002, 0.3997, 0.6994, 0,      0,      0,      0],
        [0.0101, 0.0502, 0.1003, 0.3999, 0.7002, 0.9996, 1.3001, 1.5001, 1.9994],
        [0.0104, 0.0504, 0.1004, 0.3995, 0.7003, 1.0001, 1.3002, 1.4995, 1.9993],
        [0.0104, 0.0505, 0.1000, 0.4002, 0.6994, 1.0003, 1.2994, 1.4997, 1.9993]
    ]),
    2: 1000000 * np.array([
        [0.0100, 0.0499, 0.1000, 0.3996, 0.6995, 0.9996, 1.2998, 1.4997, 1.9998]
    ])
}

afSolubilityData = {
    1: np.array([
        [0.192, 0.273, 0.307, 0.357, 0.394, 0, 0, 0, 0],
        [0.188, 0.252, 0.274, 0.324, 0.355, 0.381, 0.405, 0.420, 0.455],
        [0.108, 0.176, 0.204, 0.263, 0.292, 0.315, 0.334, 0.346, 0.373],
        [0.063, 0.129, 0.161, 0.226, 0.253, 0.272, 0.287, 0.294, 0.316]
    ]),
    2: np.array([
        [0.189, 0.246, 0.267, 0.313, 0.340, 0.362, 0.384, 0.398, 0.428]
    ])
}

z = {}
cafMolarityCO2 = {}

# Loop through IL types
for ii in range(1, 3):
    cafMolarityCO2[ii] = {}
    z[ii] = np.zeros_like(afSolubilityData[ii])
    for jj in range(len(afSolubilityData[ii])):
        cafMolarityCO2[ii][jj] = []
        for kk in range(len(afSolubilityData[ii][jj])):
            z[ii][jj][kk] = afSolubilityData[ii][jj][kk] / (1 - afSolubilityData[ii][jj][kk])
            molarity = z[ii][jj][kk] / (1 + b * np.exp(a * (xH2O - 1)))
            if molarity[0] != 0:
                cafMolarityCO2[ii][jj].append(molarity)

# Plot for BMIM Ac
plt.figure(2)
colors1 = np.array([[0, 0, 255], [150, 150, 250], [150, 30, 70], [255, 0, 0]]) / 255
for jj, temp_data in enumerate(afTemperatureData):
    for molarity in cafMolarityCO2[1][jj]:
        plt.plot(xH2O, molarity, color=colors1[jj])
plt.xlabel('x_H₂O - mol fraction H₂O in BMIM Ac')
plt.ylabel('y_CO₂ - max. mol CO₂ / mol BMIM Ac (mol CO₂/mol IL)')
plt.show()

# Plot for EMIM Ac
plt.figure(3)
colors2 = np.array([[0, 0, 250], [245, 245, 245], [230, 230, 230], [180, 180, 180],
                    [130, 130, 130], [90, 90, 90], [60, 60, 60], [30, 30, 30], [0, 0, 0]]) / 256
for jj in range(len(cafMolarityCO2[2])):
    for molarity in cafMolarityCO2[2][jj]:
        plt.plot(xH2O, molarity, color=colors2[jj])
plt.xlabel('x_H₂O - mol fraction H₂O in EMIM Ac')
plt.ylabel('y_CO₂ - max. mol CO₂ / mol EMIM Ac (mol CO₂/mol IL)')
plt.show()
