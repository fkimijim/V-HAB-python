class CrewRespiratorySimulatorO2:
    """
    A phase manipulator to simulate the O2 consumption from respiration
    by the crew. Should be used in the store where the crew is present, and
    a gas phase in the same store represents (part) of the human environment.

    Allows setting the number of crew members and their respiratory rates 
    (e.g., when a crew member is working heavily or is on EVA).
    """

    def __init__(self, oStore, sName, sPhaseIn, sPhaseOut, mbCrewMembers, oSystem):
        """
        Initialize the CrewRespiratorySimulatorO2 object.

        :param oStore: Store object
        :param sName: Name of the simulator
        :param sPhaseIn: Phase input identifier
        :param sPhaseOut: Phase output identifier
        :param mbCrewMembers: Boolean array representing crew members
        :param oSystem: System object with crew metabolic values
        """
        self.oStore = oStore
        self.sName = sName
        self.sPhaseIn = sPhaseIn
        self.sPhaseOut = sPhaseOut
        self.mbCrewMembers = mbCrewMembers  # Boolean array representing active crew members
        self.oSystem = oSystem

        # Initialize the array defining which species are extracted
        self.arExtractPartials = [0] * self.oStore.oMT.iSubstances
        self.arExtractPartials[self.oStore.oMT.tiN2I["O2"]] = 1

    def set_crew(self, mbCrewMembers):
        """
        Set the crew members contributing to O2 consumption.

        :param mbCrewMembers: Boolean array representing active crew members
        """
        self.mbCrewMembers = mbCrewMembers

    def update(self):
        """
        Update the O2 flow rate based on crew respiration simulation.
        """
        iCrewMembers = sum(self.mbCrewMembers)  # Total number of active crew members
        iIndexCM = [index for index, member in enumerate(self.mbCrewMembers) if member]

        mfO2Flow = []
        for k in iIndexCM:
            # Retrieve O2 consumption for the current crew member's state
            mfO2Flow.append(self.oSystem.tHumanMetabolicValues[self.oSystem.cCrewState[k]]["fO2Consumption"])

        fFlowRate = sum(mfO2Flow)  # Total O2 flow rate

        # Set the new flow rate using the extracted partials
        self.set_matter_properties(fFlowRate, self.arExtractPartials)

    def set_matter_properties(self, fFlowRate, arExtractPartials):
        """
        Set the matter properties for the O2 consumption simulator.

        This method serves as a placeholder for interfacing with the simulation system.

        :param fFlowRate: Flow rate of O2
        :param arExtractPartials: Array defining extracted partials
        """
        # Implement logic to interface with the simulation system's methods for setting flow rates.
        # Example: self.oSystem.set_flow_rate(self.sPhaseIn, fFlowRate, arExtractPartials)
        pass
