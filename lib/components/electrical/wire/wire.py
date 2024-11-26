class Wire:
    """
    WIRE
    Represents a wire component with properties for hydraulic simulation
    and pressure drop calculation.
    """

    # Class-level constant
    Const = {
        'fReynoldsCritical': 2320,  # Critical Reynolds number
    }

    def __init__(self, oContainer, sName, fLength, fDiameter, fRoughness=0):
        """
        Constructor for Wire class.

        :param oContainer: Parent container or system
        :param sName: Name of the wire
        :param fLength: Length of the wire [m]
        :param fDiameter: Diameter of the wire [m]
        :param fRoughness: Surface roughness of the wire
        """
        self.oContainer = oContainer
        self.sName = sName
        self.fLength = fLength
        self.fDiameter = fDiameter
        self.fRoughness = fRoughness
        self.fDeltaPressure = 0
        self.aoFlows = []  # Placeholder for flow objects
        self.oMT = None  # Placeholder for material properties object

    def update(self):
        """
        Update function for hydraulic solver to calculate pressure drop.
        """
        bZeroFlows = any(flow.fFlowRate == 0 for flow in self.aoFlows)

        if not bZeroFlows:
            oFlowIn, _ = self.get_flows()

            fDensity = self.oMT.calculate_density(oFlowIn)
            fDynamicViscosity = self.oMT.calculate_dynamic_viscosity(oFlowIn)
            fFlowSpeed = oFlowIn.fFlowRate / (fDensity * 3.14159 * 0.25 * self.fDiameter**2)

            self.fDeltaPressure = self.pressure_loss_pipe(
                self.fDiameter,
                self.fLength,
                fFlowSpeed,
                fDynamicViscosity,
                fDensity,
                self.fRoughness,
                0
            )

    def solver_deltas(self, fFlowRate):
        """
        Update function for callback solver to calculate pressure deltas.

        :param fFlowRate: Flow rate [m^3/s]
        :return: Pressure delta [Pa]
        """
        if fFlowRate == 0:
            return 0

        oFlowIn, oFlowOut = self.get_flows(fFlowRate)
        fAveragePressure = (oFlowIn.fPressure + oFlowOut.fPressure) / 2

        if fAveragePressure == 0:
            return 0

        try:
            fDensityIn = oFlowIn.get_density()
            fDensityOut = oFlowOut.get_density()
            fDensity = (fDensityIn + fDensityOut) / 2
        except Exception:
            fDensity = self.fallback_density_calculation(oFlowIn, fAveragePressure)

        fFlowSpeed = abs(fFlowRate) / ((3.14159 / 4) * self.fDiameter**2 * fDensity)

        try:
            fEta = oFlowIn.get_dynamic_viscosity()
        except Exception:
            fEta = 17.2 / 10**6

        if self.fDiameter == 0:
            return float('inf')

        if fDensity == 0 or fEta == 0:
            return 0

        fReynolds = fFlowSpeed * self.fDiameter * fDensity / fEta

        pInterp = 0.1
        if fReynolds <= self.Const['fReynoldsCritical'] * (1 - pInterp):
            fLambda = 64 / fReynolds
        elif self.Const['fReynoldsCritical'] * (1 - pInterp) < fReynolds <= self.Const['fReynoldsCritical'] * (1 + pInterp):
            fLambdaLaminar = 64 / fReynolds
            fLambdaTurbulent = self.colebrook(fReynolds, self.fRoughness)
            interp_factor = (-self.Const['fReynoldsCritical'] * (1 - pInterp) + fReynolds) / (self.Const['fReynoldsCritical'] * 2 * pInterp)
            fLambda = fLambdaLaminar + (fLambdaTurbulent - fLambdaLaminar) * interp_factor
        else:
            fLambda = self.colebrook(fReynolds, self.fRoughness)

        fDeltaPressure = fDensity / 2 * fFlowSpeed**2 * (fLambda * self.fLength / self.fDiameter)
        self.fDeltaPressure = fDeltaPressure

        return fDeltaPressure

    def get_flows(self, fFlowRate=None):
        """
        Mock function to retrieve flow objects.
        """
        return self.aoFlows[0], self.aoFlows[1] if len(self.aoFlows) >= 2 else None

    def fallback_density_calculation(self, oFlowIn, fAveragePressure):
        """
        Fallback method for density calculation if the primary method fails.
        """
        if oFlowIn.fMolarMass > 0:
            fMolarMass = oFlowIn.fMolarMass
        else:
            fMolarMass = 1
        return (fAveragePressure * fMolarMass) / (self.oMT.Const.fUniversalGas * oFlowIn.fTemperature)

    def colebrook(self, fReynolds, fRoughness):
        """
        Placeholder for Colebrook equation implementation.
        """
        return 0.3164 / fReynolds**0.25

    def pressure_loss_pipe(self, fDiameter, fLength, fFlowSpeed, fDynamicViscosity, fDensity, fRoughness, option):
        """
        Placeholder function to calculate pressure loss in a pipe.
        """
        return 0
