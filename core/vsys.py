class TimedSystem:
    """
    Base class to manage time-stepped execution.
    """
    def __init__(self, parent, name, timestep=None):
        self.parent = parent
        self.name = name
        self.timestep = timestep if timestep is not None else False
        self.children = {}

    def exec(self):
        """
        Execution logic for timed systems.
        """
        print(f"Executing system: {self.name}")


class MatterContainer:
    """
    Base class for matter-related simulations.
    """
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.matter_branches = []

    def disconnect_matter_branches(self):
        print(f"Disconnecting matter branches for {self.name}")

    def reconnect_matter_branches(self):
        print(f"Reconnecting matter branches for {self.name}")


class ThermalContainer:
    """
    Base class for thermal-related simulations.
    """
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.thermal_branches = []

    def disconnect_thermal_branches(self):
        print(f"Disconnecting thermal branches for {self.name}")

    def reconnect_thermal_branches(self):
        print(f"Reconnecting thermal branches for {self.name}")


class ElectricalContainer:
    """
    Base class for electrical-related simulations.
    """
    def __init__(self, parent, name):
        self.parent = parent
        self.name = name
        self.electrical_branches = []

    def disconnect_electrical_branches(self):
        print(f"Disconnecting electrical branches for {self.name}")

    def reconnect_electrical_branches(self):
        print(f"Reconnecting electrical branches for {self.name}")


class BaseSystem(TimedSystem, MatterContainer, ThermalContainer, ElectricalContainer):
    """
    Base class for V-HAB systems (vsys in MATLAB).
    """
    def __init__(self, parent, name, timestep=None):
        # Initialize all parent classes
        TimedSystem.__init__(self, parent, name, timestep)
        MatterContainer.__init__(self, parent, name)
        ThermalContainer.__init__(self, parent, name)
        ElectricalContainer.__init__(self, parent, name)
        self.sealed = False

    def create_solver_structure(self):
        """
        Calls the create_solver_structure method for all children.
        """
        for child_name, child in self.children.items():
            child.create_solver_structure()

    def disconnect_branches_for_saving(self):
        """
        Disconnects all branches for saving (matter, thermal, and electrical).
        """
        self.disconnect_matter_branches()
        self.disconnect_thermal_branches()
        self.disconnect_electrical_branches()

        for child in self.children.values():
            child.disconnect_branches_for_saving()

    def reconnect_branches(self):
        """
        Reconnects all branches after loading.
        """
        self.reconnect_matter_branches()
        self.reconnect_thermal_branches()
        self.reconnect_electrical_branches()

        for child in self.children.values():
            child.reconnect_branches()

    def exec(self):
        """
        Executes the system logic and calls the parent exec method.
        """
        print(f"Executing BaseSystem: {self.name}")
        super().exec()
