class JouleThomson(thermal_heatsource):
    """
    The JouleThomson heat source models the heat released or consumed by a pressure change
    using the Joule-Thomson coefficient. It works only with "normal" phases or capacities,
    not with flow or boundary types.
    """

    def __init__(self, sName):
        """
        Initializes the JouleThomson heat source.
        
        Args:
            sName: The name of the heat source.
        """
        super().__init__(sName, 0)
        self.sName = sName

    def setCapacity(self, oCapacity):
        """
        Assign a capacity to the heat source and bind a callback to the phase's mass update event.
        
        Args:
            oCapacity: The capacity object.
        """
        if self.oCapacity is None:
            self.oCapacity = oCapacity
        else:
            raise RuntimeError("Heatsource already has a capacity object")

        # Bind callback to update the heat source after a mass update in the phase
        oCapacity.oPhase.bind("massupdate_post", lambda: self.update())

    def update(self):
        """
        Calculate the current heat flow based on the pressure change in the phase.
        """
        oPhase = self.oCapacity.oPhase

        # Calculate the current Joule-Thomson coefficient
        fJouleThomson = self.oCapacity.oMT.calculateJouleThomson(oPhase)

        if oPhase.sType == "gas":
            # Equation from https://link.springer.com/book/10.1007/978-3-642-05098-5
            # Delta T = JT * Delta P. Pressure difference is based on current mass change.
            self.fHeatFlow = oPhase.fMassToPressure * oPhase.fCurrentTotalMassInOut * fJouleThomson
        else:
            raise NotImplementedError("Calculation for non-gases is not implemented")
