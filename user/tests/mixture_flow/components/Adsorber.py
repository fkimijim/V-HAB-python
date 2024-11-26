class Adsorber(matter.procs.p2ps.flow):
    """
    P2P processor to model a very basic adsorption process.
    """
    def __init__(self, oStore, sName, sPhaseIn, sPhaseOut):
        """
        Constructor for the Adsorber class.

        Args:
            oStore: The store this processor belongs to.
            sName: Name of the processor.
            sPhaseIn: Name of the input phase.
            sPhaseOut: Name of the output phase.
        """
        super().__init__(oStore, sName, sPhaseIn, sPhaseOut)
        self.afPartialInFlows = None

    def calculate_flow_rate(self, afInsideInFlowRates, aarInsideInPartials, *args):
        """
        Calculate the flow rate for adsorption.

        Args:
            afInsideInFlowRates: The incoming flow rates.
            aarInsideInPartials: The partial mass fractions of the incoming flows.
            *args: Placeholder for unused arguments.
        """
        if afInsideInFlowRates and not all(sum(aarInsideInPartials) == 0):
            self.afPartialInFlows = sum(
                (afInsideInFlowRates * aarInsideInPartials), axis=0
            )
        else:
            self.afPartialInFlows = [0] * self.oMT.iSubstances

        # Determine if recalculation is necessary
        if self.afPartialInFlows[self.oMT.tiN2I["N2"]] != 0 or all(
            x == 0 for x in self.afPartialInFlows
        ):
            fAdsorptionFlow = 0.9 * self.afPartialInFlows[self.oMT.tiN2I["CO2"]]
            arPartialsAdsorption = [0] * self.oMT.iSubstances
            arPartialsAdsorption[self.oMT.tiN2I["CO2"]] = 1

            self.set_matter_properties(fAdsorptionFlow, arPartialsAdsorption)

    def update(self):
        """
        Update method (no additional behavior for this processor).
        """
        pass
