from Layers.Digestion import Digestion
from Layers.Metabolic import Metabolic
from Layers.Respiration import Respiration
from Layers.Thermal import Thermal
from Layers.WaterBalance import WaterBalance

DigestionLayer = Digestion()
MetabolicLayer = Metabolic()
RespirationLayer = Respiration()
ThermalLayer = Thermal()
WaterBalanceLayer = WaterBalance()

class Human:
    def __init__(self, parent, name, crew_planner, time_step):
        self.parent = parent
        self.name = name
        self.crew_planner = crew_planner
        self.time_step = time_step

        # Human properties
        self.fBodyCoreTemperature = 309.95
        self.fAge = 25  # Years
        self.fHeight = 1.80  # [m]

        # Scheduler parameters
        self.iState = 1
        self.fStateStartTime = 0
        self.txCrewPlaner = crew_planner
        self.iEvent = 1
        self.fPostExerciseStartTime = 0
        self.fNominalAcitivityLevel = 0.05

        # Branches
        self.aoP2PBranches = []
        self.toP2PBranches = {}

        # Update registration
        self.bUpdateRegistered = False
        self.hBindPostTickUpdate = None

        # Initialize layers
        self.initialize_layers()

    def initialize_layers(self):
        self.digestion = DigestionLayer(self, "Digestion")
        self.metabolic = MetabolicLayer(self, "Metabolic")
        self.respiration = RespirationLayer(self, "Respiration")
        self.thermal = ThermalLayer(self, "Thermal")
        self.water_balance = WaterBalanceLayer(self, "WaterBalance")

    def create_matter_structure(self):
        # Define the phases with IFs of the different layers
        self.oLungPhase = self.respiration.lung.air
        self.oBrainTissue = self.respiration.brain.tissue
        self.oTissueTissue = self.respiration.tissue.tissue

        self.oMetabolism = self.metabolic.metabolism

        self.oBloodPlasma = self.water_balance.blood_plasma
        self.oInterstitialFluid = self.water_balance.interstitial_fluid
        self.oBladder = self.water_balance.bladder
        self.oPerspirationFlow = self.water_balance.perspiration_flow

        self.oStomach = self.digestion.stomach
        self.oDuodenum = self.digestion.duodenum
        self.oJejunum = self.digestion.jejunum
        self.oIleum = self.digestion.ileum
        self.oLargeIntestine = self.digestion.large_intestine
        self.oRectum = self.digestion.rectum

    def create_solver_structure(self):
        # Define solvers for branches
        self.configure_solvers()

    def configure_solvers(self):
        self.configure_matter_solvers()
        self.configure_thermal_solvers()

    def configure_matter_solvers(self):
        # Define matter solvers for branches
        self.matter_solvers = {
            "O2_from_Brain": None,
            "O2_from_Tissue": None,
            "CO2_to_Brain": None,
            "CO2_to_Tissue": None,
        }

    def configure_thermal_solvers(self):
        # Define thermal solvers
        self.thermal_solvers = {
            "SensibleHeatOutput": None,
        }

    def update(self):
        # Update layers
        self.digestion.update()
        self.metabolic.update()
        self.respiration.update()
        self.water_balance.update()
        self.thermal.update()

    def exec(self):
        # Execution logic, including scheduling and state management
        self.handle_scheduling()

    def handle_scheduling(self):
        current_time = self.get_current_time()

        # Handle scheduling based on crew planner
        if (
            current_time >= self.txCrewPlaner["events"][self.iEvent]["start"]
            and not self.txCrewPlaner["events"][self.iEvent]["started"]
        ):
            self.txCrewPlaner["events"][self.iEvent]["started"] = True
            self.set_state(self.txCrewPlaner["events"][self.iEvent]["state"])

            # Set activity level based on state
            if self.iState == 0:
                self.metabolic.set_activity_level(0, False, False)
            elif self.iState in [2, 3]:
                self.metabolic.set_activity_level(
                    self.txCrewPlaner["events"][self.iEvent]["VO2_percent"],
                    True,
                    False,
                )
            else:
                self.metabolic.set_activity_level(self.fNominalAcitivityLevel, False, False)

        if (
            current_time >= self.txCrewPlaner["events"][self.iEvent]["end"]
            and not self.txCrewPlaner["events"][self.iEvent]["ended"]
        ):
            self.txCrewPlaner["events"][self.iEvent]["ended"] = True
            if self.txCrewPlaner["events"][self.iEvent]["state"] in [2, 3]:
                self.set_state(4)
                self.fPostExerciseStartTime = current_time
            else:
                self.set_state(1)
                self.metabolic.set_activity_level(self.fNominalAcitivityLevel, False, False)

        if self.iState == 4:
            self.handle_post_exercise_recovery()

    def handle_post_exercise_recovery(self):
        # Handle recovery state
        current_time = self.get_current_time()
        post_exercise_duration = (
            self.metabolic.get_post_exercise_duration(current_time, self.fPostExerciseStartTime)
        )
        if post_exercise_duration:
            self.set_state(1)
            self.metabolic.set_activity_level(self.fNominalAcitivityLevel, False, False)

    def set_state(self, state):
        self.iState = state
        self.fStateStartTime = self.get_current_time()

    def bind_update(self):
        if not self.bUpdateRegistered:
            self.hBindPostTickUpdate()

    def get_current_time(self):
        # Simulated time function
        return self.time_step
