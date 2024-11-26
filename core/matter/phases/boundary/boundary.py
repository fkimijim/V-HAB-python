class BoundaryPhase:
    """
    A phase that is modeled as containing an infinite amount of matter
    with specifiable (and changeable) values for the composition and
    temperature. The intended use case is, e.g., to model vacuum in space
    and environmental conditions in test cases.
    """

    def __init__(self, store, name, tf_mass, temperature):
        """
        Constructor for the BoundaryPhase class.

        :param store: Reference to the parent store
        :param name: Name of the phase
        :param tf_mass: Dictionary containing mass values for each species
        :param temperature: Temperature of matter in phase
        """
        self.store = store
        self.name = name
        self.tf_mass = tf_mass
        self.temperature = temperature

        self.volume = float('inf')
        self.af_mass_change = [0] * self.store.oMT.i_substances
        self.mass = sum(tf_mass.values())
        self.mass_to_pressure = 0 if self.mass == 0 else self.store.oMT.calculate_mass_to_pressure(self.mass)
        self.molar_mass = self.store.oMT.calculate_molar_mass(tf_mass) if self.mass != 0 else 0
        self.partial_mass = (
            [tf_mass[sub] / self.mass for sub in tf_mass] if self.mass != 0 else [0] * self.store.oMT.i_substances
        )
        self.density = self.store.oMT.calculate_density(self) if self.mass != 0 else 0
        self.boundary = True
        self.set_time_step_properties({"rMaxChange": float("inf"), "fMaxStep": float("inf")})

    def set_time_step_properties(self, properties):
        """
        Set the time step properties for the boundary phase.
        :param properties: A dictionary with keys 'rMaxChange' and 'fMaxStep'
        """
        self.time_step_properties = properties

    def set_boundary_properties(self, properties):
        """
        Set the properties of the boundary phase.

        :param properties: A dictionary containing:
            - 'afMass': Partial mass composition of the phase
            - 'fPressure': Total pressure
            - 'fTemperature': Temperature of the boundary
        """
        if 'fTemperature' in properties:
            self.temperature = properties['fTemperature']

        if 'fPressure' in properties:
            pressure = properties['fPressure']
            relative_pressure_change = pressure / self.mass_to_pressure if self.mass_to_pressure != 0 else 1
            for key in self.tf_mass:
                self.tf_mass[key] *= relative_pressure_change
            self.mass = sum(self.tf_mass.values())
            self.mass_to_pressure = pressure / self.mass if self.mass != 0 else 0

        if 'afMass' in properties:
            self.tf_mass = properties['afMass']
            self.mass = sum(self.tf_mass.values())

        if self.mass != 0:
            self.mass_to_pressure = pressure / self.mass
            self.molar_mass = self.store.oMT.calculate_molar_mass(self.tf_mass)
            self.partial_mass = [self.tf_mass[sub] / self.mass for sub in self.tf_mass]
            self.density = self.store.oMT.calculate_density(self)
        else:
            self.mass_to_pressure = 0
            self.molar_mass = 0
            self.partial_mass = [0] * self.store.oMT.i_substances
            self.density = 0

        self.set_branches_outdated()

    def set_branches_outdated(self):
        """
        Mark branches as outdated after boundary property updates.
        """
        self.branches_outdated = True

    def mass_update(self):
        """
        Updates the mass changes for the boundary phase over the simulation time.
        """
        current_time = self.store.timer.f_time
        elapsed_time = current_time - getattr(self, "last_mass_update", 0)

        if elapsed_time == 0:
            return

        self.last_mass_update = current_time
        total_in_out = self.get_total_mass_change()

        if hasattr(self, "substance_manipulator") and self.substance_manipulator:
            total_in_out = [x + y for x, y in zip(total_in_out, self.substance_manipulator.partial_flows)]

        total_mass_change = [flow * elapsed_time for flow in total_in_out]
        self.af_mass_change = [x + y for x, y in zip(self.af_mass_change, total_mass_change)]
        self.set_outdated_ts()

    def get_total_mass_change(self):
        """
        Compute the total mass changes for the boundary phase.
        """
        return [0] * self.store.oMT.i_substances  # Placeholder implementation

    def set_outdated_ts(self):
        """
        Mark the time step as outdated after mass updates.
        """
        self.time_step_outdated = True
