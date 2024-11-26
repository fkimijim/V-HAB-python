class Filter(matter.Store):
    """
    Generic filter model
    This filter is modeled as a store with two phases:
    - A flow phase representing the gas flow volume.
    - A filtered phase representing the volume taken up by the material absorbing matter.
    The two phases are connected by a phase-to-phase (P2P) processor.
    """

    def __init__(self, oContainer, sName, fCapacity):
        """
        Initializes the Filter store.

        Args:
            oContainer: The parent container.
            sName: Name of the store.
            fCapacity: Absorption capacity of the filter.
        """
        # Initialize the store with a volume of 0.025 m^2
        super().__init__(oContainer, sName, 0.025)

        # Creating the flow phase using the 'air' helper
        # The volume is set to 0.015 m^2, with a temperature of 293.15 K
        oFlow = self.create_phase("air", "FlowPhase", 0.015, 293.15)

        # Creating the filtered phase manually
        # The initial mass includes a small amount of matter to aid startup
        self.create_phase(
            matter.phases.Gas(
                self,
                "FilteredPhase",  # Phase name
                {"O2": 0.0001},   # Phase contents
                0.01,             # Phase volume
                293.15            # Phase temperature
            )
        )

        # Create external connections for the air stream to be filtered
        matter.procs.Exmes.Gas(oFlow, "FilterIn")
        matter.procs.Exmes.Gas(oFlow, "FilterOut")

        # Creating the P2P processor
        # Inputs: parent, name, flow phase, absorber phase, species, capacity
        self.oProc = tutorials.thermal.components.AbsorberExample(
            self, "filterproc", "FlowPhase", "FilteredPhase", "O2", fCapacity
        )
