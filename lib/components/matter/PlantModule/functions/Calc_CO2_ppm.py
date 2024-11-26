def Calc_CO2_ppm(oPhase):
    """
    Calculates the ppm level of CO2 for the given phase.

    Parameters:
        oPhase (object): An object representing the phase with attributes afMass, fMass, fMolarMass, and oMT.

    Returns:
        float: The CO2 concentration in ppm.
    """
    # Mass of CO2 in the considered phase [kg]
    fMassCO2 = oPhase.afMass[oPhase.oMT.tiN2I["CO2"]]
    # Total gas mass in the considered phase [kg]
    fTotalGasMass = oPhase.fMass
    # Molar mass of CO2 [kg/mol]
    fMolarMassCO2 = oPhase.oMT.afMolarMass[oPhase.oMT.tiN2I["CO2"]]
    # Molar mass of the phase [kg/mol]
    fMolarMassPhase = oPhase.fMolarMass

    # Calculating ppm of CO2
    CO2ppm = (fMassCO2 * fMolarMassPhase) / (fTotalGasMass * fMolarMassCO2) * 1e6  # [-]
    return CO2ppm
