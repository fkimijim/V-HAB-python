def ChlorellaContentCalculation(oSystem):
    """
    CHLORELLACONTENTCALCULATION determines the initial Chlorella mass in the
    system by taking the celldensity (t=0) value from the growth rate
    calculation and multiplying that with the total medium volume.
    
    :param oSystem: The system object containing relevant parameters.
    :return: fChlorellaMass [kg]
    """
    # Get parameters for this calculation
    fInitialBiomassConcentration = oSystem.oGrowthRateCalculationModule.fInitialBiomassConcentration  # [kg/m3]
    fMediumVolume = oSystem.oParent.fGrowthVolume  # [m3]

    # Calculate the Chlorella mass
    fChlorellaMass = fInitialBiomassConcentration * fMediumVolume  # [kg]
    
    return fChlorellaMass
