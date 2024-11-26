import math

def Calcite_Solubility(fCurrentTemp, fMolesCaCO3, fVolume):
    """
    Calculates the theoretical number of moles of CO3 and Ca produced 
    by the dissolution of CaCO3 in water, based on water temperature in K.

    Source:
    L. NIEL PLUMMER and EURYBIADES BUSENBERG: 
    "The solubilities of calcite, aragonite and vaterite in CO2-H2O solutions
    between 0 and 90°C, and an evaluation of the aqueous model for the system
    CaC03-CO2-H20", Geochimica et Cosmochimica Acta Vol. 46. pp. 1011-1040, 1981

    Parameters:
        fCurrentTemp (float): Current temperature in Kelvin.
        fMolesCaCO3 (float): Number of moles of CaCO3.
        fVolume (float): Volume of water in liters.

    Returns:
        float: Theoretical number of moles of dissolved CO3 and Ca.
    """
    # Calculate the log value for the equilibrium constant K_C
    flogK_C = (-171.9065 
               - (0.077993 * fCurrentTemp) 
               + (2839.319 / fCurrentTemp) 
               + (71.595 * math.log10(fCurrentTemp)))
    
    # Calculate the equilibrium constant K_C
    fK_C = 10 ** flogK_C

    # Concentration of calcite in the water volume in mol/L
    fConcentrationCaCO3 = fMolesCaCO3 / fVolume

    # Concentration of dissolved CO3 in the water volume in mol/L
    fConcentrationCO3 = math.sqrt(fK_C * fConcentrationCaCO3)

    # Number of moles of dissolved CO3 in mol
    fDissolvedMoles = fConcentrationCO3 * fVolume

    return fDissolvedMoles
