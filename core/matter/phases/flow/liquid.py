import Flow

Flow = Flow()

class Liquid(Flow):
    """
    Liquid flow node class

    A liquid phase modeled as containing no matter. For implementation purposes,
    the phase does have a mass, but calculations enforce zero mass change for 
    the phase and calculate all values based on the inflows.
    """

    sType = 'liquid'

    def __init__(self, oStore, sName, tfMasses, fTemperature, fPressure):
        """
        Initializes the liquid flow node.

        Args:
            oStore (str): Name of parent store.
            sName (str): Name of phase.
            tfMasses (dict): Dictionary containing mass value for each species.
            fTemperature (float): Temperature of matter in phase.
            fPressure (float): Pressure of the phase.
        """
        # Calling the parent constructor
        # Volume is initially set to 1e-6 as a placeholder and updated later.
        super().__init__(oStore, sName, tfMasses, 1e-6, fTemperature)

        # Setting the pressure.
        self.fVirtualPressure = fPressure
        self.update_pressure()

        # Updating density and volume
        self.fDensity = self.oMT.calculateDensity(self)
        self.fVolume = self.fMass / self.fDensity if self.fDensity else 0
