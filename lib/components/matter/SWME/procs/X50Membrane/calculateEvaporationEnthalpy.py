def calculateEvaporationEnthalpy(_, fTemperature):
    """
    Calculates the evaporation enthalpy of water for a given temperature.

    Parameters:
    _ : Placeholder for unused parameter.
    fTemperature (float): Temperature in Kelvin.

    Returns:
    float: Evaporation enthalpy of water in J/kg.
    """
    # Parameters A-E as found in VDI-Wärmeatlas, chapter D3.1, page 385
    fA = 6.853070
    fB = 7.438040
    fC = -2.937595
    fD = -3.282093
    fE = 8.397378

    # Critical temperature of water in Kelvin (VDI chapter D3.1, page 358)
    fCriticalTemperature = 647.096

    # Calculate dimensionless temperature ratio
    fTau = 1 - (fTemperature / fCriticalTemperature)

    # Specific gas constant for H2O in J/kg*K
    fR = 461.5227

    # Evaporation enthalpy calculation
    fEvaporationEnthalpy = (
        fR
        * fCriticalTemperature
        * (
            fA * fTau**(1/3)
            + fB * fTau**(2/3)
            + fC * fTau
            + fD * fTau**2
            + fE * fTau**6
        )
    )

    return fEvaporationEnthalpy
