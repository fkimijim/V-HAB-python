import math

def CO2_Outgassing(fCurrentTemp, fPartialPressureCO2):
    """
    Calculates the theoretical CO2 gas concentration in the gas phase 
    above a solution at ambient pressure and the dimensionless Henry solubility.

    Source:
    R. Sander: Compilation of Henry's law constants (version 4.0) for
    water as solvent (2015), pp. 4399-4402, pp. 4488

    Parameters:
        fCurrentTemp (float): Current temperature in Kelvin.
        fPartialPressureCO2 (float): Partial pressure of CO2 in Pa.

    Returns:
        tuple: 
            - fCO2_gas_concentration (float): CO2 gas concentration in the gas phase in mol/L.
            - fH_cc_CO2 (float): Dimensionless Henry solubility.
    """
    # Reference Henry constant for CO2 at 298.15 K in [mol/(m3*Pa)]
    fH_cp_CO2_reference = 3.3e-4

    # Enthalpy factor influenced by the enthalpy of dissolution of CO2
    fEnthalpyFactor_CO2 = 2400

    # Calculate current temperature-dependent Henry constant in [mol/(m3*Pa)]
    fH_cp_CO2 = fH_cp_CO2_reference * math.exp(
        fEnthalpyFactor_CO2 * ((1 / fCurrentTemp) - (1 / 298.15))
    )

    # Calculate the solubility concentration of CO2 in the solution in mol/L
    fSolubilityCO2 = 0.001 * fPartialPressureCO2 * fH_cp_CO2

    # Gas constant in J/(mol*K)
    fR = 8.314

    # Calculate the dimensionless Henry solubility
    fH_cc_CO2 = (fR * fCurrentTemp) * fH_cp_CO2

    # Calculate the gas concentration above the solution in mol/L
    fCO2_gas_concentration = fSolubilityCO2 / fH_cc_CO2

    return fCO2_gas_concentration, fH_cc_CO2
