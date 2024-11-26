from abc import ABC, abstractmethod

class Manip(ABC):
    """
    Manip: Basic manipulator class.
    All manipulators inherit from this base class. It is used to manipulate
    phase attributes such as volume or substance composition.
    """

    def __init__(self, sName, oPhase, sRequiredType=None):
        """
        Constructor for the manipulator base class.
        
        Args:
            sName (str): Name of the manipulator.
            oPhase: Phase object this manipulator is attached to.
            sRequiredType (str): Required type of phase. Default is None.
        """
        self.sName = sName
        self.sRequiredType = sRequiredType
        self.oPhase = None
        self.oMT = oPhase.oMT
        self.oTimer = oPhase.oTimer
        self.bAttached = False
        self.hDetach = None  # Function handle for detaching manip

        # Attach to the phase
        self.reattach_manip(oPhase)

    @abstractmethod
    def hBindPostTickUpdate(self):
        """
        Abstract property for post-tick update binding. Must be defined in child classes.
        """
        pass

    @abstractmethod
    def fLastExec(self):
        """
        Abstract property for the time of last execution.
        """
        pass

    def detach_manip(self):
        """
        Detaches the manipulator from its phase. The manipulator will still exist but cannot be updated.
        """
        if self.oPhase:
            # Unbind all events if the manipulator has registered events.
            if hasattr(self, "unbind_all_events") and callable(self.unbind_all_events):
                self.unbind_all_events()
            
            # Detach the manipulator from the phase.
            self.hDetach()
            self.hDetach = None
            self.oPhase = None
            self.bAttached = False

    def reattach_manip(self, oPhase):
        """
        Reattaches the manipulator to a phase.

        Args:
            oPhase: A phase object that fulfills the manipulator's required phase type.
        """
        if self.oPhase:
            raise RuntimeError(
                f"The manipulator {self.sName} is still connected to phase {self.oPhase.sName}. "
                "Detach it first before reattaching."
            )
        
        # Check if the phase type matches the required type.
        if self.sRequiredType:
            sCompareField = "sPhaseType" if oPhase.sType == "mixture" else "sType"
            if getattr(oPhase, sCompareField) != self.sRequiredType:
                raise RuntimeError(
                    f"Provided phase (name {oPhase.sName}, store {oPhase.oStore.sName}) "
                    f"is not a {self.sRequiredType}."
                )
        
        # Attach the manipulator to the phase.
        self.oPhase = oPhase
        self.hDetach = self.oPhase.add_manipulator(self)
        self.bAttached = True

    def register_update(self):
        """
        Registers a post-tick update function call for the manipulator.
        """
        if self.bAttached:
            self.hBindPostTickUpdate()

    @abstractmethod
    def update(self):
        """
        Abstract method to be implemented in child classes for specific manipulations.
        """
        pass

    def get_total_flow_rates(self):
        """
        Calculates total inward flow rates for all substances.

        Returns:
            afFlowRates (list): Total flow rates in kg/s for each substance.
        """
        afFlowRates, mrInPartials = self.get_in_flows()

        if afFlowRates:
            afFlowRates = [sum(flow * partial for flow, partial in zip(afFlowRates, col))
                           for col in zip(*mrInPartials)]
        else:
            afFlowRates = [0] * self.oMT.iSubstances

        return afFlowRates

    def get_in_flows(self):
        """
        Calculates inward flow rates and their partial mass ratios.

        Returns:
            afInFlowrates (list): Total inward flow rates in kg/s per ExMe.
            mrInPartials (list of lists): Partial mass ratios for each inward flow.
        """
        iNumberOfEXMEs = self.oPhase.iProcsEXME
        mrInPartials = [[0] * self.oMT.iSubstances for _ in range(iNumberOfEXMEs)]
        afInFlowrates = [0] * iNumberOfEXMEs

        # Log flows that are not inward flows.
        abOutFlows = [True] * iNumberOfEXMEs

        for i in range(iNumberOfEXMEs):
            afFlowRates, mrFlowPartials, _ = self.oPhase.coProcsEXME[i].get_flow_data()

            abInf = [flow > 0 for flow in afFlowRates]
            if any(abInf):
                mrInPartials[i] = [mrFlowPartials[j] for j, is_inf in enumerate(abInf) if is_inf]
                afInFlowrates[i] = sum(flow for flow, is_inf in zip(afFlowRates, abInf) if is_inf)
                abOutFlows[i] = False

        # Remove out-flows from the matrices.
        mrInPartials = [row for row, is_out in zip(mrInPartials, abOutFlows) if not is_out]
        afInFlowrates = [rate for rate, is_out in zip(afInFlowrates, abOutFlows) if not is_out]

        return afInFlowrates, mrInPartials
