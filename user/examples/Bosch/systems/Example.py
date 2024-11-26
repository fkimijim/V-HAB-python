class Example(vsys):
    """
    Example V-HAB system with a Bosch Reactor.
    This system includes all required interfaces for the reactor,
    the reactor itself is located in the library.
    """

    def __init__(self, oParent, sName):
        super().__init__(oParent, sName, 0.1)

        # BoschReactor
        components.matter.Bosch.BoschReactor(self, 'BoschReactor')

    def create_matter_structure(self):
        super().create_matter_structure()

        # Storage tanks for H2 and CO2 for input and output
        matter.store(self, 'TankH2', 5)
        oInH2Phase = self.toStores.TankH2.create_phase(
            'gas', 'boundary', 'H2', 5, {'H2': 2e5}, 293.15, 0
        )

        matter.procs.exmes.gas(oInH2Phase, 'Outlet')
        matter.procs.exmes.gas(oInH2Phase, 'Inlet')

        matter.store(self, 'TankCO2', 5)
        oInCO2Phase = self.toStores.TankCO2.create_phase(
            'gas', 'boundary', 'CO2', 5, {'CO2': 2e5}, 293.15, 0
        )

        matter.procs.exmes.gas(oInCO2Phase, 'Outlet')
        matter.procs.exmes.gas(oInCO2Phase, 'Inlet')

        matter.store(self, 'Condensate', 5)
        oCondensate = self.toStores.Condensate.create_phase(
            'liquid', 'Condensate', 5, {'H2O': 1}, 293.15, 1e5
        )
        matter.procs.exmes.liquid(oCondensate, 'Inlet')

        matter.store(self, 'Carbon', 5)
        oCarbon = self.toStores.Carbon.create_phase(
            'solid', 'C', 5, {'C': 1}, 293.15, 1e5
        )
        matter.procs.exmes.solid(oCarbon, 'Inlet')

        # Adding branches
        matter.branch(self, 'H2_to_Bosch', {}, 'TankH2.Outlet', 'H2_to_Bosch')
        matter.branch(self, 'CO2_to_Bosch', {}, 'TankCO2.Outlet', 'CO2_to_Bosch')

        matter.branch(self, 'H2_from_Bosch', {}, 'TankH2.Inlet', 'H2_from_Bosch')
        matter.branch(self, 'CO2_from_Bosch', {}, 'TankCO2.Inlet', 'CO2_from_Bosch')
        matter.branch(self, 'H2O_from_Bosch', {}, 'Condensate.Inlet', 'H2O_from_Bosch')
        matter.branch(self, 'C_from_Bosch', {}, 'Carbon.Inlet', 'C_from_Bosch')

        self.toChildren.BoschReactor.set_if_flows(
            'H2_to_Bosch', 'CO2_to_Bosch', 'H2O_from_Bosch',
            'CO2_from_Bosch', 'H2_from_Bosch', 'C_from_Bosch'
        )

    def create_solver_structure(self):
        super().create_solver_structure()

        self.set_thermal_solvers()

    def exec(self, _):
        super().exec(_)
        fCO2FlowRate = 0.05
        fFactor = self.oMT.afMolarMass[self.oMT.tiN2I.H2] / self.oMT.afMolarMass[self.oMT.tiN2I.CO2]
        fH2FlowRate = fFactor * fCO2FlowRate

        self.toChildren.BoschReactor.toBranches.H2_Inlet.oHandler.set_flow_rate(-fH2FlowRate)
        self.toChildren.BoschReactor.toBranches.CO2_Inlet.oHandler.set_flow_rate(-fCO2FlowRate)
