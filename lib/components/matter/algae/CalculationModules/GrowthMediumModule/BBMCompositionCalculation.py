class BBMCompositionCalculation:
    """
    Calculates the mass of the components of the Bold's Basal Medium (BBM) based on the desired volume.
    The resulting composition is returned as a structure containing the components and their masses.
    """

    def __init__(self, fMediumVolume, oMT, oSystem):
        self.fMediumVolume = fMediumVolume  # [m3]
        self.oMT = oMT  # Matter Table Object

        self.tfBBMComposition = {}  # Composition struct [kg]
        self.fDisodiumEDTASaltConc = 0  # [moles/m3]
        self.fDisodiumEDTASaltMoles = 0  # [moles]

        self.fDibasicPotassiumPhosphateConc = 0  # [moles/m3]
        self.fDibasicPotassiumPhosphateMoles = 0  # [moles]

        self.fMonobasicPotassiumPhosphateConc = 0  # [moles/m3]
        self.fMonobasicPotassiumPhosphateMoles = 0  # [moles]

        self.fKOHConc = 0  # [moles/m3]
        self.fKOHMoles = 0  # [moles]

        self.fSodiumNitrateConc = 0  # [moles/m3]
        self.fSodiumNitrateMoles = 0  # [moles]

        # Active components
        fDisodiumEDTASaltInConcentrate = 3180.5 * 10 ** -3  # [kg/m3]
        bDisodiumEDTAActive = True

        fPotassiumHydroxideInConcentrate = 1550 * 10 ** -3  # [kg/m3]
        bPotassiumHydroxideActive = True

        fDibasicPotassiumPhosphateInConcentrate = 3750 * 10 ** -3  # [kg/m3]
        bDibasicPotassiumPhosphateActive = True

        fMonobasicPotassiumPhosphateInConcentrate = 8750 * 10 ** -3  # [kg/m3]
        bMonobasicPotassiumPhosphateActive = True

        fSodiumChlorideInConcentrate = 1250 * 10 ** -3  # [kg/m3]
        bSodiumChlorideActive = True

        fSodiumNitrateInConcentrate = 12500 * 10 ** -3  # [kg/m3]
        bSodiumNitrateActive = True

        fWaterDensity = self.oMT.calculateDensity('liquid', {'H2O': 1})
        fWaterInConcentrate = fWaterDensity - 30.98  # [kg/m3]
        bWaterActive = True

        # Determine volumes of water and concentrate
        fWaterVolume = fMediumVolume * (980 / 1000)  # [m3]
        fConcentrateVolume = fMediumVolume - fWaterVolume  # [m3]

        # Calculate water mass
        fWaterMass = fWaterVolume * fWaterDensity  # [kg]

        # Calculate active component masses
        fDisodiumEDTASaltMass = fDisodiumEDTASaltInConcentrate * fConcentrateVolume if bDisodiumEDTAActive else 0
        fPotassiumHydroxideMass = fPotassiumHydroxideInConcentrate * fConcentrateVolume if bPotassiumHydroxideActive else 0
        fDibasicPotassiumPhosphateMass = fDibasicPotassiumPhosphateInConcentrate * fConcentrateVolume if bDibasicPotassiumPhosphateActive else 0
        fMonobasicPotassiumPhosphateMass = fMonobasicPotassiumPhosphateInConcentrate * fConcentrateVolume if bMonobasicPotassiumPhosphateActive else 0
        fSodiumChlorideMass = fSodiumChlorideInConcentrate * fConcentrateVolume if bSodiumChlorideActive else 0
        fSodiumNitrateMass = fSodiumNitrateInConcentrate * fConcentrateVolume if bSodiumNitrateActive else 0
        fWaterInConcentrateMass = fWaterInConcentrate * fConcentrateVolume if bWaterActive else 0

        # Calculate concentrations and moles
        self.fDisodiumEDTASaltConc = (fDisodiumEDTASaltMass / oMT.afMolarMass[oMT.tiN2I['DisodiumEDTASalt']]) / (fMediumVolume * 1000)
        self.fDisodiumEDTASaltMoles = fDisodiumEDTASaltMass / oMT.afMolarMass[oMT.tiN2I['DisodiumEDTASalt']]

        self.fDibasicPotassiumPhosphateConc = (fDibasicPotassiumPhosphateMass / oMT.afMolarMass[oMT.tiN2I['DibasicPotassiumPhosphate']]) / (fMediumVolume * 1000)
        self.fDibasicPotassiumPhosphateMoles = fDibasicPotassiumPhosphateMass / oMT.afMolarMass[oMT.tiN2I['DibasicPotassiumPhosphate']]

        self.fMonobasicPotassiumPhosphateConc = (fMonobasicPotassiumPhosphateMass / oMT.afMolarMass[oMT.tiN2I['MonobasicPotassiumPhosphate']]) / (fMediumVolume * 1000)
        self.fMonobasicPotassiumPhosphateMoles = fMonobasicPotassiumPhosphateMass / oMT.afMolarMass[oMT.tiN2I['MonobasicPotassiumPhosphate']]

        self.fKOHConc = (fPotassiumHydroxideMass / oMT.afMolarMass[oMT.tiN2I['KOH']]) / (fMediumVolume * 1000)
        self.fKOHMoles = fPotassiumHydroxideMass / oMT.afMolarMass[oMT.tiN2I['KOH']]

        self.fSodiumNitrateConc = (fSodiumNitrateMass / oMT.afMolarMass[oMT.tiN2I['SodiumNitrate']]) / (fMediumVolume * 1000)
        self.fSodiumNitrateMoles = fSodiumNitrateMass / oMT.afMolarMass[oMT.tiN2I['SodiumNitrate']]

        # Create struct with masses and modeled substances
        self.tfBBMComposition = {
            'H2O': fWaterMass + fWaterInConcentrateMass,
            'C10H14N2O8': self.fDisodiumEDTASaltMoles * oMT.afMolarMass[oMT.tiN2I['C10H14N2O8']],
            'HPO4': self.fDibasicPotassiumPhosphateMoles * oMT.afMolarMass[oMT.tiN2I['HydrogenPhosphate']],
            'H2PO4': self.fMonobasicPotassiumPhosphateMoles * oMT.afMolarMass[oMT.tiN2I['DihydrogenPhosphate']],
            'Kplus': (2 * self.fDibasicPotassiumPhosphateMoles + self.fMonobasicPotassiumPhosphateMoles + self.fKOHMoles) * oMT.afMolarMass[oMT.tiN2I['PotassiumIon']],
            'NaCl': fSodiumChlorideMass,
            'NO3': self.fSodiumNitrateMoles * oMT.afMolarMass[oMT.tiN2I['NO3']],
            'Naplus': (self.fSodiumNitrateMoles + 2 * self.fDisodiumEDTASaltMoles) * oMT.afMolarMass[oMT.tiN2I['SodiumIon']],
            'OH': self.fKOHMoles * oMT.afMolarMass[oMT.tiN2I['OH']]
        }

        # Check charge balance
        fChargeBalanceNatrium = (
            (self.tfBBMComposition['C10H14N2O8'] / oMT.afMolarMass[oMT.tiN2I['C10H14N2O8']]) * (-2) +
            (self.tfBBMComposition['NO3'] / oMT.afMolarMass[oMT.tiN2I['NO3']]) * (-1) +
            (self.tfBBMComposition['Naplus'] / oMT.afMolarMass[oMT.tiN2I['Naplus']]) * (+1)
        )

        fChargeBalanceKalium = (
            (self.tfBBMComposition['HPO4'] / oMT.afMolarMass[oMT.tiN2I['HPO4']]) * (-2) +
            (self.tfBBMComposition['H2PO4'] / oMT.afMolarMass[oMT.tiN2I['H2PO4']]) * (-1) +
            (self.tfBBMComposition['OH'] / oMT.afMolarMass[oMT.tiN2I['OH']]) * (-1) +
            (self.tfBBMComposition['Kplus'] / oMT.afMolarMass[oMT.tiN2I['Kplus']]) * (+1)
        )

        if abs(fChargeBalanceNatrium) > 1e-12 or abs(fChargeBalanceKalium) > 1e-12:
            raise ValueError("Charge balance validation failed.")
