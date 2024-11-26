class Fan(matter.procs.f2f):
    """
    Generic fan model with an optional characteristic.
    This dynamic fan model allows control via RPM and supports custom fan characteristics.
    """

    def __init__(self, oContainer, sName, fSpeedSetpoint, bUsePressureRise=False, tCharacteristic=None):
        """
        Constructor for the fan class.

        :param oContainer: Parent container.
        :param sName: Name of the fan.
        :param fSpeedSetpoint: Fan speed setpoint in RPM.
        :param bUsePressureRise: Enables gradual pressure rise on startup.
        :param tCharacteristic: Struct for custom fan characteristics (optional).
        """
        super().__init__(oContainer, sName)

        # Properties
        self.fSpeedSetpoint = fSpeedSetpoint
        self.fPowerFactor = 0.95
        self.fInternalEfficiency = 0.85
        self.fElectricalEfficiency = 0.8
        self.bTurnedOn = False
        self.fPowerConsumtionFan = 0
        self.bUsePressureRise = bUsePressureRise
        self.fTurnOnTime = -1
        self.bPreviouslyOff = True
        self.fMaximumDeltaPressure = 0
        self.fMaximumVolumetricFlowRate = 0
        self.fMaxFlowRateUpper = 0
        self.fMaxFlowRateLower = 0

        # Default characteristic or user-provided
        self.tCharacteristic = tCharacteristic or {
            "fSpeedUpper": 75000,
            "calculateUpperDeltaP": lambda fVolumetricFlowRate: -9064144377.669 * (fVolumetricFlowRate ** 3)
            + 9755592.99525 * (fVolumetricFlowRate ** 2)
            + 4716.6727883 * fVolumetricFlowRate
            + 2607,
            "fSpeedLower": 40000,
            "calculateLowerDeltaP": lambda fVolumetricFlowRate: -6727505231.41735 * (fVolumetricFlowRate ** 3)
            - 7128360.09755 * (fVolumetricFlowRate ** 2)
            + 33153.83752 * fVolumetricFlowRate
            + 752,
            "fTestPressure": 29649,
            "fTestTemperature": 294.26,
            "fTestGasConstant": 287.058,
            "fTestDensity": 0.3510,
            "fZeroCrossingUpper": 0.007,
            "fZeroCrossingLower": 0.0048,
        }

        # Calculate maximum flow rates for upper and lower speeds
        self.fMaxFlowRateUpper = self._find_zero_crossing(self.tCharacteristic["calculateUpperDeltaP"], self.tCharacteristic["fZeroCrossingUpper"])
        self.fMaxFlowRateLower = self._find_zero_crossing(self.tCharacteristic["calculateLowerDeltaP"], self.tCharacteristic["fZeroCrossingLower"])

        # Set fan speed
        self.setFanSpeed(fSpeedSetpoint)

        # Solver support
        self.supportSolver("hydraulic", -1, 1, True, self.solverDeltas)
        self.supportSolver("callback", self.solverDeltas)
        self.supportSolver("manual", True, self.updateManualSolver)

    def switchOn(self):
        """Turn the fan on."""
        self.bTurnedOn = True
        self.oBranch.setOutdated()

    def switchOff(self):
        """Turn the fan off."""
        self.bTurnedOn = False
        self.bPreviouslyOff = True
        self.oBranch.setOutdated()

    def setFanSpeed(self, fFanSpeed):
        """Set a new speed setpoint for the fan."""
        self.fSpeedSetpoint = fFanSpeed
        self.fMaximumDeltaPressure = self.calculateDeltaPressure(0)
        self.fMaximumVolumetricFlowRate = self.fMaxFlowRateLower + (
            (self.fSpeedSetpoint - self.tCharacteristic["fSpeedLower"])
            / (self.tCharacteristic["fSpeedUpper"] - self.tCharacteristic["fSpeedLower"])
            * (self.fMaxFlowRateUpper - self.fMaxFlowRateLower)
        )

    def calculateDeltaPressure(self, fVolumetricFlowRate):
        """
        Calculate the delta pressure using the fan characteristic.
        :param fVolumetricFlowRate: Volumetric flow rate.
        :return: Delta pressure.
        """
        fDeltaPressureLower = self.tCharacteristic["calculateLowerDeltaP"](fVolumetricFlowRate)
        fDeltaPressureHigher = self.tCharacteristic["calculateUpperDeltaP"](fVolumetricFlowRate)

        fDeltaPressure = fDeltaPressureLower + (
            (self.fSpeedSetpoint - self.tCharacteristic["fSpeedLower"])
            / (self.tCharacteristic["fSpeedUpper"] - self.tCharacteristic["fSpeedLower"])
            * (fDeltaPressureHigher - fDeltaPressureLower)
        )

        return fDeltaPressure

    def solverDeltas(self, fFlowRate):
        """
        Solver for pressure and temperature deltas.
        :param fFlowRate: Flow rate.
        :return: Delta pressure.
        """
        if not self.bTurnedOn:
            self.fHeatFlow = 0
            self.fDeltaPressure = 0
            return 0

        oFlowIn, _ = self.getFlows(fFlowRate)
        fDensity = oFlowIn.getDensity()

        if fFlowRate <= 0:
            fDeltaPressure = -self.fMaximumDeltaPressure
        else:
            fVolumetricFlowRate = oFlowIn.calculateVolumetricFlowRate(fFlowRate)
            fInterpolatedDeltaPressure = self.calculateDeltaPressure(fVolumetricFlowRate)

            if fInterpolatedDeltaPressure < 0:
                fInterpolatedDeltaPressure = 0

            fDensityCorrectedDeltaPressure = fInterpolatedDeltaPressure * (fDensity / self.tCharacteristic["fTestDensity"])
            fDeltaPressure = -fDensityCorrectedDeltaPressure

        self.fDeltaPressure = fDeltaPressure
        fDeltaTemperature = abs(fDeltaPressure) / fDensity / oFlowIn.fSpecificHeatCapacity / self.fInternalEfficiency * self.fPowerFactor

        if not (0 < fDeltaTemperature < float("inf")):
            fDeltaTemperature = 0

        self.fHeatFlow = abs(fFlowRate) * oFlowIn.fSpecificHeatCapacity * fDeltaTemperature

        if fFlowRate > 0:
            self.fPowerConsumtionFan = (fDeltaPressure * fVolumetricFlowRate) / self.fElectricalEfficiency
        else:
            self.fPowerConsumtionFan = 0

        if self.bUsePressureRise and fFlowRate >= 0:
            if self.bPreviouslyOff:
                self.fTurnOnTime = self.oTimer.fTime
                self.bPreviouslyOff = False

            fTotalRiseTime = 1
            fCurrentRiseTime = self.oTimer.fTime - self.fTurnOnTime - fTotalRiseTime
            if fCurrentRiseTime < fTotalRiseTime:
                fDeltaPressure = fDeltaPressure * (-1 * (fCurrentRiseTime / fTotalRiseTime) ** 2 + 1)

        return fDeltaPressure

    def updateManualSolver(self):
        """Update method for manual solver."""
        pass

    @staticmethod
    def _find_zero_crossing(func, start_point):
        """
        Helper method to find the zero crossing of a function.
        :param func: Function to evaluate.
        :param start_point: Starting point for search.
        :return: Zero crossing value.
        """
        from scipy.optimize import root_scalar
        result = root_scalar(func, bracket=[start_point * 0.5, start_point * 1.5])
        return result.root if result.converged else start_point
