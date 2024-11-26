class Example(VSys):
    """
    Example simulation for a CROP filter in V-HAB 2.0
    """

    def __init__(self, o_parent, s_name):
        super().__init__(o_parent, s_name, 60)

        # Adding UPA
        self.to_children["UPA"] = components.matter.UPA.UPA(self, "UPA")

        # Adding BPA
        self.to_children["BPA"] = components.matter.BPA.BPA(self, "BPA")

        # Evaluate configuration parameters
        eval(self.o_root.o_cfg_params.config_code(self))

    def create_matter_structure(self):
        super().create_matter_structure()

        # Create 'Cabin' store
        self.to_stores["Cabin"] = matter.Store(self, "Cabin", 50)

        # Add a phase to the 'Cabin' store
        o_cabin_phase = self.to_stores["Cabin"].create_phase(
            phase_type="gas",
            boundary_type="boundary",
            name="CabinAir",
            volume=48,
            composition={"N2": 5.554e4, "O2": 1.476e4, "CO2": 40},
            temperature=293,
            pressure=0.506,
        )

        # Create the potable water reserve
        self.to_stores["UrineStorage"] = matter.Store(self, "UrineStorage", 1000)
        o_urine_phase = matter.phases.Mixture(
            self.to_stores["UrineStorage"],
            "Urine",
            phase_type="liquid",
            composition={"Urine": 1.6e4},
            temperature=295,
            pressure=101325,
        )

        self.to_stores["BrineStorage"] = matter.Store(self, "BrineStorage", 0.1)
        o_brine_phase = matter.phases.Mixture(
            self.to_stores["BrineStorage"],
            "Brine",
            phase_type="liquid",
            composition={"Brine": 0.01},
            temperature=295,
            pressure=101325,
        )

        self.to_stores["WaterStorage"] = matter.Store(self, "WaterStorage", 1000)
        o_water = self.to_stores["WaterStorage"].create_phase(
            phase_type="liquid",
            boundary_type="boundary",
            name="water",
            volume=self.to_stores["WaterStorage"].f_volume,
            composition={"H2O": 1},
            temperature=293,
            pressure=1e5,
        )

        # UPA connections
        matter.Branch(self, "InletUPA", [], o_urine_phase)
        matter.Branch(self, "OutletUPA", [], o_water)
        matter.Branch(self, "BrineOutletUPA", [], o_brine_phase)
        self.to_children["UPA"].set_if_flows("InletUPA", "OutletUPA", "BrineOutletUPA")

        # BPA connections
        matter.Branch(self, "BrineInletBPA", [], o_brine_phase)
        matter.Branch(self, "AirInletBPA", [], o_cabin_phase)
        matter.Branch(self, "AirOutletBPA", [], o_cabin_phase)
        self.to_children["BPA"].set_if_flows("BrineInletBPA", "AirInletBPA", "AirOutletBPA")

    def create_solver_structure(self):
        super().create_solver_structure()

        t_time_step_properties = {
            "r_max_change": float("inf"),
            "f_max_step": self.f_time_step,
        }
        self.to_stores["UrineStorage"].to_phases["Urine"].set_time_step_properties(t_time_step_properties)
        self.to_stores["BrineStorage"].to_phases["Brine"].set_time_step_properties(t_time_step_properties)

        self.set_thermal_solvers()

    def exec(self, _):
        """
        Execute function for this system. Called at each simulation step.
        """
        super().exec(_)

        # BPA flowrate logic
        bpa = self.to_children["BPA"]
        if not bpa.b_processing and not bpa.b_disposing_concentrated_brine and \
           not bpa.to_branches["BrineInlet"].o_handler.b_mass_transfer_active and \
           not (bpa.to_stores["Bladder"].to_phases["Brine"].f_mass >= bpa.f_activation_fill_bpa):
            if self.to_stores["BrineStorage"].to_phases["Brine"].f_mass > bpa.f_activation_fill_bpa:
                bpa.to_branches["BrineInlet"].o_handler.set_mass_transfer(-bpa.f_activation_fill_bpa, 300)

        self.o_timer.synchronize_callbacks()
