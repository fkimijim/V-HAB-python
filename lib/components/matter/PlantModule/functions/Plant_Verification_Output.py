def Plant_Verification_Output(oCulture):
    """
    Outputs the plant verification metrics, including oxygen production, carbon dioxide uptake,
    water transpiration, and biomass production rates.

    Parameters:
        oCulture (object): An object representing the culture with attributes for tracking various metrics.
    """
    fOxygenProduction = sum(oCulture.mfOxygenProduction)
    fCarbonDioxideUptake = sum(oCulture.mfCarbonDioxideUptake)
    fWaterTranspiration = sum(oCulture.mfWaterTranspiration)
    fTotalBioMass = sum(oCulture.mfTotalBioMass)
    fInedibleMass = sum(oCulture.mfInedibleMass)
    fEdibleMass = sum(oCulture.mfEdibleMass)

    # Averaging over the length and converting to daily metrics
    fOxygenProduction = (fOxygenProduction / len(oCulture.mfOxygenProduction)) * 24 * 3600 * 1000
    fCarbonDioxideUptake = (fCarbonDioxideUptake / len(oCulture.mfCarbonDioxideUptake)) * 24 * 3600 * 1000
    fWaterTranspiration = (fWaterTranspiration / len(oCulture.mfWaterTranspiration)) * 24 * 3600
    fTotalBioMass = (fTotalBioMass / len(oCulture.mfTotalBioMass)) * 24 * 3600 * 1000
    fInedibleMass = (fInedibleMass / len(oCulture.mfInedibleMass)) * 24 * 3600 * 1000
    fEdibleMass = (fEdibleMass / len(oCulture.mfEdibleMass)) * 24 * 3600 * 1000

    # Uncomment the following lines if dry basis calculations are needed
    # fInedibleMassDryBasis = sum(oCulture.mfInedibleMassDryBasis)
    # fEdibleMassDryBasis = sum(oCulture.mfEdibleMassDryBasis)
    # fInedibleMassDryBasis = (fInedibleMassDryBasis / len(oCulture.mfInedibleMassDryBasis)) * 24 * 3600 * 1000
    # fEdibleMassDryBasis = (fEdibleMassDryBasis / len(oCulture.mfEdibleMassDryBasis)) * 24 * 3600 * 1000

    print(f'The mass of produced oxygen is: {fOxygenProduction:.2f} [gram/m²/d]')
    print(f'The mass of consumed carbon dioxide is: {fCarbonDioxideUptake:.2f} [gram/m²/d]')
    print(f'The mass of transpirated water is {fWaterTranspiration:.2f} [kg/m²/d]')
    print(f'The mass of produced Total Biomass is {fTotalBioMass:.2f} [gram/m²/d]')
    print(f'The mass of produced Inedible Biomass is {fInedibleMass:.2f} [gram/m²/d]')
    print(f'The mass of produced Edible Biomass is {fEdibleMass:.2f} [gram/m²/d]')

    # Uncomment the following lines if dry basis outputs are needed
    # print(f'The mass of produced Inedible Biomass on Dry Basis is {fInedibleMassDryBasis:.2f} [gram/m²/d]')
    # print(f'The mass of produced Edible Biomass on Dry Basis is {fEdibleMassDryBasis:.2f} [gram/m²/d]')
