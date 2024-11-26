class Gas:
    """
    Gas boundary class

    A gas phase that is modeled as containing an infinite amount of matter
    with specifiable (and changeable) values for the composition and
    temperature. Intended for cases such as vacuum in space or environmental
    conditions in test cases.
    """

    sType = 'gas'

    def __init__(self, oStore, sName, tfMass, fVolume=None, fTemperature=None, fPressure=None):
        """
        Initializes the gas boundary class.

        Args:
            oStore (str): Name of parent store.
            sName (str): Name of the phase.
            tfMass (dict): Dictionary containing mass values for each species.
            fVolume (float, optional): Ignored, included for compatibility.
            fTemperature (float): Temperature of the phase.
            fPressure (float, optional): Pressure of the phase.
        """
        self.oStore = oStore
        self.sName = sName
        self.tfMass = tfMass
        self.fTemperature = fTemperature

        self.fMass = sum(tfMass.values()) if tfMass else 0
        self.afPP = None
        self.afPartsPerMillion = None
        self.rRelHumidity = None

        if fVolume is not None and (fPressure is None):
            # Calculate pressure using the ideal gas law: p*V = m*R*T
            self.fMassToPressure = (
                0 if self.fMass == 0 else self.oMT.Const.fUniversalGas * fTemperature / (self.fMolarMass * fVolume)
            )
        elif fPressure is not None:
            self.fMassToPressure = fPressure / self.fMass

        # Set initial properties
        tProperties = {"afMass": tfMass}
        self.set_boundary_properties(tProperties)

    def set_boundary_properties(self, tProperties):
        """
        Updates the properties of the gas boundary phase.

        Args:
            tProperties (dict): A dictionary of properties to update.
        """
        if "fTemperature" in tProperties:
            self.oCapacity.set_boundary_temperature(tProperties["fTemperature"])

        fPressure = getattr(self, "fPressure", 0)

        if "afMass" in tProperties:
            if "fPressure" in tProperties:
                fPressure = tProperties["fPressure"]

            self.tfMass = tProperties["afMass"]
            self.fMass = sum(self.tfMass.values())

            if self.fMass != 0:
                afMols = {k: v / self.oMT.afMolarMass[k] for k, v in self.tfMass.items()}
                arMolFractions = {k: v / sum(afMols.values()) for k, v in afMols.items()}
                self.afPP = {k: fPressure * v for k, v in arMolFractions.items()}

        elif "afPP" in tProperties:
            self.afPP = tProperties["afPP"]
            fPressure = sum(self.afPP.values())

            arMolFractions = {k: v / sum(self.afPP.values()) for k, v in self.afPP.items()}
            self.tfMass = {k: arMolFractions[k] * self.oMT.afMolarMass[k] for k in arMolFractions}
            self.fMass = sum(self.tfMass.values())

        if self.fMass != 0:
            self.fMassToPressure = fPressure / self.fMass
            self.fMolarMass = self.fMass / sum(
                v / self.oMT.afMolarMass[k] for k, v in self.tfMass.items()
            )
            self.afPartsPerMillion = {
                k: (v / self.fMolarMass) / (self.oMT.afMolarMass[k] / self.fMass) * 1e6
                for k, v in self.tfMass.items()
            }
            self.arPartialMass = {k: v / self.fMass for k, v in self.tfMass.items()}
            self.fDensity = fPressure / ((self.oMT.Const.fUniversalGas / self.fMolarMass) * self.fTemperature)

            if "H2O" in self.afPP:
                fSaturationVapourPressure = self.oMT.calculate_vapor_pressure(self.fTemperature, "H2O")
                self.rRelHumidity = self.afPP["H2O"] / fSaturationVapourPressure
            else:
                self.rRelHumidity = 0

        else:
            self.fMassToPressure = 0
            self.fMolarMass = 0
            self.afPartsPerMillion = {}
            self.arPartialMass = {}
            self.fDensity = 0
            self.afPP = {}

        try:
            self.oCapacity.set_boundary_temperature(self.fTemperature)
        except AttributeError:
            pass

        self.set_branches_outdated()

    def set_branches_outdated(self):
        """
        Placeholder for branch update logic.
        """
        pass
