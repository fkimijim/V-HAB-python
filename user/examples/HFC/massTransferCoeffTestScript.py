# Import necessary libraries
import numpy as np

# Constants and input parameters
fFiberOD = 7.7E-4  # [m]
fFiberID = 4.51E-4  # [m]
fFiberL = 0.295  # [m]
fFiberCount = 11
fContactArea = 4.6E-3  # [m^2] effective inner membrane area
fPorosity = 0.3
fPackingFactor = 0.04

# Pick data points at 30% water content in IL
fDynamicVisc = 38  # cP
fILDensity = 1030  # kg/m^3
fKinematicVisc = fDynamicVisc / fILDensity * 1E-3  # [m^2/s]

fGasFlowRate = 20 / 1E6 / 60  # [m^3/s]
fCO2InletConc = 0.15  # ratio
fTemperature = 300  # [K]
fPressure = 101325  # [Pa]
R = 8.314  # [J/mol/K]

# Display the calculated variables
print(f"Fiber Outer Diameter (fFiberOD): {fFiberOD} m")
print(f"Fiber Inner Diameter (fFiberID): {fFiberID} m")
print(f"Fiber Length (fFiberL): {fFiberL} m")
print(f"Fiber Count (fFiberCount): {fFiberCount}")
print(f"Contact Area (fContactArea): {fContactArea} m^2")
print(f"Porosity (fPorosity): {fPorosity}")
print(f"Packing Factor (fPackingFactor): {fPackingFactor}")
print(f"Dynamic Viscosity (fDynamicVisc): {fDynamicVisc} cP")
print(f"IL Density (fILDensity): {fILDensity} kg/m^3")
print(f"Kinematic Viscosity (fKinematicVisc): {fKinematicVisc} m^2/s")
print(f"Gas Flow Rate (fGasFlowRate): {fGasFlowRate} m^3/s")
print(f"CO2 Inlet Concentration (fCO2InletConc): {fCO2InletConc}")
print(f"Temperature (fTemperature): {fTemperature} K")
print(f"Pressure (fPressure): {fPressure} Pa")
print(f"Universal Gas Constant (R): {R} J/mol/K")
