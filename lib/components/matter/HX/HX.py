class HX:
    """
    HX: Generic heat exchanger model.
    Calculates outlet temperatures and pressure drops for various heat exchanger types.
    """

    def __init__(self, oParent, sName, tHX_Parameters, sHX_type, fHX_TC=float('inf'), fTempChangeToRecalc=0.05, rChangeToRecalc=0.01):
        """
        Initialize the HX object.

        :param oParent: Parent system.
        :param sName: Name of the heat exchanger.
        :param tHX_Parameters: Geometry and configuration of the heat exchanger.
        :param sHX_type: Heat exchanger type (e.g., 'CounterPlate', 'Cross').
        :param fHX_TC: Thermal conductivity of the heat exchanger material.
        :param fTempChangeToRecalc: Temperature change threshold for recalculation.
        :param rChangeToRecalc: Relative change threshold for recalculation.
        """
        self.oParent = oParent
        self.sName = sName
        self.tHX_Parameters = tHX_Parameters
        self.fHX_TC = fHX_TC
        self.fTempChangeToRecalc = fTempChangeToRecalc
        self.rChangeToRecalc = rChangeToRecalc

        # Parse and set the HX type and flow configuration
        if "Parallel" in sHX_type:
            self.tHX_Parameters["bParallelFlow"] = True
            self.sHX_type = sHX_type.replace("Parallel", "")
        elif "Counter" in sHX_type:
            self.tHX_Parameters["bParallelFlow"] = False
            self.sHX_type = sHX_type.replace("Counter", "")
        else:
            self.sHX_type = sHX_type

        # Flow processors for input/output
        self.oF2F_1 = None
        self.oF2F_2 = None

        # Outlet temperatures for plotting
        self.fTempOut_Fluid1 = None
        self.fTempOut_Fluid2 = None

        # Previous iteration values
        self.fEntryTemp_Old_1 = None
        self.fEntryTemp_Old_2 = None
        self.fMassFlow_Old_1 = None
        self.fMassFlow_Old_2 = None
        self.arPartialMass1Old = None
        self.arPartialMass2Old = None
        self.fOldPressureFlow1 = None
        self.fOldPressureFlow2 = None

        # Iteration control
        self.iFirst_Iteration = True
        self.fLastUpdate = -1

    def update(self, oFlows_1, oFlows_2, oTimer):
        """
        Update the heat exchanger based on the current flow conditions.

        :param oFlows_1: Flow data for fluid 1.
        :param oFlows_2: Flow data for fluid 2.
        :param oTimer: Timer object to track updates.
        """
        if not oTimer.fTime:
            return

        fMassFlow_1 = abs(oFlows_1.fFlowRate)
        fMassFlow_2 = abs(oFlows_2.fFlowRate)

        if fMassFlow_1 == 0 or fMassFlow_2 == 0:
            self.oF2F_1.set_out_flow(0, 0)
            self.oF2F_2.set_out_flow(0, 0)
            return

        fEntryTemp_1 = oFlows_1.fTemperature
        fEntryTemp_2 = oFlows_2.fTemperature
        fCp_1 = oFlows_1.fSpecificHeatCapacity
        fCp_2 = oFlows_2.fSpecificHeatCapacity

        if (
            self.iFirst_Iteration
            or abs(fEntryTemp_1 - self.fEntryTemp_Old_1) > self.fTempChangeToRecalc
            or abs(1 - (fMassFlow_1 / self.fMassFlow_Old_1)) > self.rChangeToRecalc
            or abs(fEntryTemp_2 - self.fEntryTemp_Old_2) > self.fTempChangeToRecalc
            or abs(1 - (fMassFlow_2 / self.fMassFlow_Old_2)) > self.rChangeToRecalc
        ):
            # Update fluid properties
            fDensity_1 = self.calculate_density(oFlows_1)
            fDensity_2 = self.calculate_density(oFlows_2)
            fDynVisc_1 = self.calculate_dynamic_viscosity(oFlows_1)
            fDynVisc_2 = self.calculate_dynamic_viscosity(oFlows_2)
            fConductivity_1 = self.calculate_thermal_conductivity(oFlows_1)
            fConductivity_2 = self.calculate_thermal_conductivity(oFlows_2)

            Fluid_1 = {
                "fMassflow": fMassFlow_1,
                "fEntryTemperature": fEntryTemp_1,
                "fDynamicViscosity": fDynVisc_1,
                "fDensity": fDensity_1,
                "fThermalConductivity": fConductivity_1,
                "fSpecificHeatCapacity": fCp_1,
            }

            Fluid_2 = {
                "fMassflow": fMassFlow_2,
                "fEntryTemperature": fEntryTemp_2,
                "fDynamicViscosity": fDynVisc_2,
                "fDensity": fDensity_2,
                "fThermalConductivity": fConductivity_2,
                "fSpecificHeatCapacity": fCp_2,
            }

            # Call the appropriate HX calculation function
            calculation_function = getattr(self, self.sHX_type, None)
            if not calculation_function:
                raise ValueError(f"Unsupported HX type: {self.sHX_type}")

            fTempOut_1, fTempOut_2, fDeltaPress_1, fDeltaPress_2 = calculation_function(
                self.tHX_Parameters, Fluid_1, Fluid_2, self.fHX_TC
            )

            # Update output temperatures
            self.fTempOut_Fluid1 = fTempOut_1
            self.fTempOut_Fluid2 = fTempOut_2

            # Update heat flows
            fHeatFlow_1 = fMassFlow_1 * fCp_1 * (fTempOut_1 - fEntryTemp_1)
            fHeatFlow_2 = fMassFlow_2 * fCp_2 * (fTempOut_2 - fEntryTemp_2)

            self.oF2F_1.set_out_flow(fHeatFlow_1, fDeltaPress_1)
            self.oF2F_2.set_out_flow(fHeatFlow_2, fDeltaPress_2)

            # Store current values for next iteration
            self.iFirst_Iteration = False
            self.fEntryTemp_Old_1 = fEntryTemp_1
            self.fEntryTemp_Old_2 = fEntryTemp_2
            self.fMassFlow_Old_1 = fMassFlow_1
            self.fMassFlow_Old_2 = fMassFlow_2

        self.fLastUpdate = oTimer.fTime

    # Placeholder methods for required calculations
    def calculate_density(self, flow):
        return flow.fDensity

    def calculate_dynamic_viscosity(self, flow):
        return flow.fDynamicViscosity

    def calculate_thermal_conductivity(self, flow):
        return flow.fThermalConductivity
