import numpy as np

def calculateWaterILEquilibrium(oLumen, oShell):
    """
    Calculate the equilibrium between water and the ionic liquid (IL).
    Specifically: water in the vapor phase and water in the liquid phase.
    
    Inputs:
        oLumen: gas phase in a Hollow Fiber Contactor
        oShell: liquid phase in a Hollow Fiber Contactor
    Outputs:
        fWaterEQPressure: equilibrium pressure of water in the gas phase [Pa]
        fWaterEQMolFractionGas: equilibrium molar fraction of water in the gas phase
    """
    fWaterEQPressure = 0
    fWaterEQMolFractionGas = 0

    fMinTemperature = 293.15  # [K]
    fMaxTemperature = 353.15  # [K]
    fPressure = oLumen['fPressure']  # [Pa]
    fTemperature = oShell['fTemperature']  # [K]

    if fTemperature <= fMinTemperature or fTemperature >= fMaxTemperature:
        print("Warning: IL temperature is out of range for IL-Water equilibrium calculations")

    arShellMolarRatios = (
        oShell['arPartialMass'] / oShell['oMT']['afMolarMass']
    ) / np.sum(oShell['arPartialMass'] / oShell['oMT']['afMolarMass'])
    rMolFractionWaterInIL = arShellMolarRatios[oShell['oMT']['tiN2I']['H2O']]

    # NIST Antoine parameters for water
    A = 4.6543
    B = 1435.264
    C = -64.848
    fSaturationPressureWater = (10 ** (A - B / (C + fTemperature))) * 100000

    # NRTL parameters from Roemich et al (2012) for [EMIM][Ac]
    fsmallG12 = 28939  # [J/mol]
    fsmallG21 = -25691  # [J/mol]
    fAlpha12 = 0.10243  # []
    R = 8.314  # [J/mol-K]

    # NRTL calculations
    fTao12 = fsmallG12 / (R * fTemperature)  # []
    fTao21 = fsmallG21 / (R * fTemperature)  # []
    fbigG12 = np.exp(-fAlpha12 * fTao12)  # []
    fbigG21 = np.exp(-fAlpha12 * fTao21)  # []

    fLnActivityCoefficient = (1 - rMolFractionWaterInIL) ** 2 * (
        (fTao21 * fbigG21 ** 2 / ((rMolFractionWaterInIL + (1 - rMolFractionWaterInIL)) * fbigG21) ** 2)
        + (fTao12 * fbigG12 ** 2 / (((1 - rMolFractionWaterInIL) + rMolFractionWaterInIL * fbigG12) ** 2))
    )

    rMolFractionWaterInGas = (
        np.exp(fLnActivityCoefficient) * rMolFractionWaterInIL * fSaturationPressureWater / fPressure
    )
    fWaterEQPressure = rMolFractionWaterInGas * fPressure  # [Pa]
    fWaterEQMolFractionGas = rMolFractionWaterInGas

    return fWaterEQPressure, fWaterEQMolFractionGas
