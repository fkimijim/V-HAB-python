import numpy as np

class BPA:
    """
    BPA: Brine Processing Assembly
    A simple model simulating delays and recovery rates, not based on first principles.
    """

    def __init__(self, oParent=None, sName="BPA", fTimeStep=60):
        # Constants and properties
        self.fBladderCapacity = 24 * 0.998  # [liters]
        self.fActivationFillBPA = 22.5 * 0.998  # [liters]
        self.fBaseFlowRate = 22.5 * 0.998 / (26 * 24 * 3600)  # [liters/second]
        self.bProcessing = False
        self.bDisposingConcentratedBrine = False
        self.fProcessingFinishTime = -20000  # [seconds]
        self.fProcessingTime = 26 * 24 * 3600  # [seconds]
        self.fPower = 142  # [W]
        
        # Simulation-related variables
        self.oParent = oParent
        self.sName = sName
        self.fTimeStep = fTimeStep
        self.toStores = {"Bladder": None, "ConcentratedBrineDisposal": None}
        self.toBranches = {}
        self.oTimer = {"fTime": 0}  # Simulated timer

        # Initialize
        self.createMatterStructure()
        self.createSolverStructure()

    def createMatterStructure(self):
        """Create the matter structure including phases and connections."""
        self.toStores["Bladder"] = {
            "capacity": self.fBladderCapacity,
            "phases": {
                "Brine": {"mass": 22.5 * 0.998 + 0.01, "state": "liquid", "temp": 293, "pressure": 1e5},
                "Air": {"mass": 0.5, "state": "gas", "temp": 293, "pressure": 0.5}
            }
        }
        
        self.toStores["ConcentratedBrineDisposal"] = {
            "capacity": 2,
            "phases": {
                "ConcentratedBrine": {"mass": 0.1, "state": "liquid", "temp": 293, "pressure": 1e5}
            }
        }

        # Define branches
        self.toBranches = {
            "BrineInlet": {"flow_rate": 0},
            "AirInlet": {"flow_rate": -0.1},
            "AirOutlet": {"flow_rate": 0},
            "ConcentratedBrineDisposal": {"flow_rate": 0}
        }

    def createSolverStructure(self):
        """Define solver properties for the system."""
        tSolverProperties = {
            "fMaxError": 1e-6,
            "iMaxIterations": 1000,
            "fMinimumTimeStep": 1,
            "iIterationsBetweenP2PUpdate": 200,
            "bSolveOnlyFlowRates": True
        }

        # Set timestep properties
        tTimeStepProperties = {"rMaxChange": np.inf}
        self.toStores["Bladder"]["phases"]["Brine"]["timestep_properties"] = tTimeStepProperties
        self.toStores["ConcentratedBrineDisposal"]["phases"]["ConcentratedBrine"]["timestep_properties"] = tTimeStepProperties

    def exec(self):
        """Main execution loop for the BPA."""
        current_time = self.oTimer["fTime"]
        bladder_mass = self.toStores["Bladder"]["phases"]["Brine"]["mass"]

        if bladder_mass >= self.fActivationFillBPA:
            self.bProcessing = True
            self.fProcessingFinishTime = np.inf
            self.toStores["Bladder"]["phases"]["Brine"]["timestep_properties"] = {"rMaxChange": 1e-3}

        if self.bProcessing:
            if current_time >= self.fProcessingFinishTime or bladder_mass == 0:
                self.bProcessing = False
                self.toStores["Bladder"]["phases"]["Brine"]["timestep_properties"] = {"rMaxChange": np.inf}
            elif bladder_mass >= 0.01:
                self.fProcessingFinishTime = current_time + self.fProcessingTime

        if not self.bProcessing and bladder_mass > 0.02:
            self.toBranches["ConcentratedBrineDisposal"]["flow_rate"] = bladder_mass - 0.01
            self.bDisposingConcentratedBrine = True
        else:
            self.bDisposingConcentratedBrine = False

    def setIfFlows(self, sBrineInlet, sAirInlet, sAirOutlet):
        """Connect system and subsystem level branches."""
        self.toBranches["BrineInlet"]["connected"] = sBrineInlet
        self.toBranches["AirInlet"]["connected"] = sAirInlet
        self.toBranches["AirOutlet"]["connected"] = sAirOutlet
