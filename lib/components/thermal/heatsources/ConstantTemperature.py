class ConstantTemperature(thermal_heatsource):
    """
    The ConstantTemperature heat source maintains a capacity at a constant temperature
    by calculating and setting the required heat flow.
    """

    def __init__(self, sName):
        """
        Initializes the ConstantTemperature heat source.
        
        Args:
            sName: The name of the heat source.
        """
        super().__init__(sName, 0)
        self.sName = sName
        self.fTemperature = None

    def setCapacity(self, oCapacity, fTemperature=None):
        """
        Assign a capacity to the heat source and bind temperature update callbacks.
        
        Args:
            oCapacity: The capacity object.
            fTemperature: Desired temperature (defaults to the capacity's current temperature).
        """
        if self.oCapacity is None:
            self.oCapacity = oCapacity
            self.fTemperature = fTemperature if fTemperature is not None else oCapacity.fTemperature
        else:
            raise RuntimeError("Heatsource already has a capacity object")

        # Bind callback to update heat source before updating capacity heat flows
        oCapacity.bind("calculateHeatsource_pre", lambda: self.update())
        oCapacity.bind("calculateFlowConstantTemperature", lambda: self.update())

    def setTemperature(self, fTemperature):
        """
        Set the target temperature for the heat source.
        
        Args:
            fTemperature: Desired target temperature.
        """
        self.fTemperature = fTemperature
        # Trigger an update in the capacity to recalculate the heat flow
        self.oCapacity.setOutdatedTS()

    def update(self):
        """
        Calculate and set the required heat flow to maintain the target temperature.
        """
        fHeatSourceFlow = sum(
            hs.fHeatFlow for hs in self.oCapacity.coHeatSource if hs != self
        )

        # Calculate the required temperature adjustment
        fRequiredTemperatureAdjustment = self.fTemperature - self.oCapacity.fTemperature

        if self.oCapacity.oPhase.bFlow:
            # Handle flow node case
            mfFlowRate = []
            mfSpecificHeatCapacity = []
            mfTemperature = []

            for exme in self.oCapacity.aoExmes:
                if isinstance(exme.oBranch.oHandler, solver_thermal_basic_fluidic_branch):
                    if exme.oBranch.oMatterObject.coExmes[0].oPhase == self.oCapacity.oPhase:
                        iMatterExme, iOtherExme = 0, 1
                    else:
                        iMatterExme, iOtherExme = 1, 0

                    fFlowRate = (
                        exme.oBranch.oMatterObject.fFlowRate
                        * exme.oBranch.oMatterObject.coExmes[iMatterExme].iSign
                    )

                    if fFlowRate > 0:
                        mfFlowRate.append(fFlowRate)
                        mfSpecificHeatCapacity.append(
                            exme.oBranch.oMatterObject.coExmes[iOtherExme].oFlow.fSpecificHeatCapacity
                        )
                        if iOtherExme == 1:
                            mfTemperature.append(exme.oBranch.afTemperatures[-1])
                        else:
                            mfTemperature.append(exme.oBranch.afTemperatures[0])

            fOverallHeatCapacityFlow = sum(
                fr * shc for fr, shc in zip(mfFlowRate, mfSpecificHeatCapacity)
            )

            if fOverallHeatCapacityFlow == 0:
                self.fHeatFlow = 0
            else:
                adjusted_temp = self.oCapacity.fTemperature + fRequiredTemperatureAdjustment
                weighted_temp = sum(
                    fr * shc * temp
                    for fr, shc, temp in zip(mfFlowRate, mfSpecificHeatCapacity, mfTemperature)
                ) / fOverallHeatCapacityFlow
                self.fHeatFlow = -fHeatSourceFlow + (adjusted_temp - weighted_temp) * fOverallHeatCapacityFlow
        else:
            # Handle non-flow node case
            fExmeHeatFlow = sum(
                exme.iSign * exme.fHeatFlow for exme in self.oCapacity.aoExmes
            )
            fTemperatureAdjustmentHeatFlow = (
                fRequiredTemperatureAdjustment * self.oCapacity.fTotalHeatCapacity
            ) / self.oCapacity.fMaxStep

            self.fHeatFlow = -fExmeHeatFlow - fHeatSourceFlow + fTemperatureAdjustmentHeatFlow
