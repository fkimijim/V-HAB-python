class Example(VSys):
    def __init__(self, o_parent, s_name):
        super().__init__(o_parent, s_name, -1)
        eval(self.o_root.o_cfg_params.config_code(self))
        
        # Connecting subsystems
        self.to_children["WPA"] = components.matter.WPA.WPA(self, "WPA")
        
        # Calculate flow rate to WPA
        f_target_volume_to_treat = (35000 / 6.33) * 3600 * 7.98e-4 / 1000
        self.f_flow_rate_to_WPA = (f_target_volume_to_treat * 1000) / 86400
        
        # Properties
        self.f_total_volume_passed_through_WPA = 0
        self.f_resync_modulo_counter = 0
        self.f_last_update_volume = 0

    def create_matter_structure(self):
        super().create_matter_structure()
        
        # Stores
        self.to_stores["WasteWater"] = matter.Store(self, "WasteWater", 1500)
        self.to_stores["ProductWater"] = matter.Store(self, "ProductWater", 1500)
        self.to_stores["Node_3"] = matter.Store(self, "Node_3", 1_000_000)
        
        self.to_stores["WPA_WasteWater_Inlet"] = matter.Store(self, "WPA_WasteWater_Inlet", 1e-6)
        o_WPA_wastewater_inlet = self.to_stores["WPA_WasteWater_Inlet"].create_phase(
            "liquid", "flow", "WPA_WasteWater_Inlet", 1e-6, {"H2O": 1}, 293, 1e5
        )
        
        # Waste water composition
        f_water_mass = 1e6
        f_water_volume = f_water_mass / 998.24
        tf_waste_water = {
            "Naplus": 251e-6 * 1000 * f_water_volume,
            "Kplus": 23.2e-6 * 1000 * f_water_volume,
            "Ca2plus": 3.52e-6 * 1000 * f_water_volume,
            "CMT": 717e-6 * 1000 * f_water_volume,
            "Clminus": 216e-6 * 1000 * f_water_volume,
            "C4H7O2": 65.1e-6 * 1000 * f_water_volume,
            "C2H3O2": 42.5e-6 * 1000 * f_water_volume,
            "HCO3": 38.4e-6 * 1000 * f_water_volume,
            "SO4": 25.1e-6 * 1000 * f_water_volume,
            "H2O": 1e6,
        }
        
        af_waste_water_mass = [0] * self.o_mt.i_substances
        for component, value in tf_waste_water.items():
            af_waste_water_mass[self.o_mt.ti_n2i[component]] = value

        # Gas share in the wastewater
        f_percent_gas = 0.10
        f_waste_water_mass = sum(af_waste_water_mass)
        f_gas_mass = (f_waste_water_mass / (1 - f_percent_gas)) - f_waste_water_mass
        
        af_waste_water_mass[self.o_mt.ti_n2i["N2"]] = f_gas_mass
        
        tr_waste_water_mass_ratios = {
            component: value / sum(af_waste_water_mass)
            for component, value in tf_waste_water.items()
        }
        
        o_waste_water = self.to_stores["WasteWater"].create_phase(
            "mixture", "Water", "liquid", self.to_stores["WasteWater"].f_volume, tr_waste_water_mass_ratios, 293, 1e5
        )
        
        o_atmosphere = self.to_stores["Node_3"].create_phase(
            "gas", "boundary", "Air", self.to_stores["Node_3"].f_volume, {"N2": 8e4, "O2": 2e4, "CO2": 500}, 293, 0.5
        )
        
        o_product_water = self.to_stores["ProductWater"].create_phase(
            "mixture", "Water", "liquid", self.to_stores["ProductWater"].f_volume, {"H2O": 1}, 293, 1e5
        )
        
        # Branches
        matter.Branch(self, o_waste_water, [], o_WPA_wastewater_inlet, "WasteWaterToWPA")
        matter.Branch(self, "Inlet", [], o_WPA_wastewater_inlet)
        matter.Branch(self, "Outlet", [], o_product_water)
        matter.Branch(self, "AirInlet", [], o_atmosphere)
        matter.Branch(self, "AirOutlet", [], o_atmosphere)
        
        self.to_children["WPA"].set_if_flows("Inlet", "Outlet", "AirInlet", "AirOutlet")
        self.to_children["WPA"].set_continous_mode(True, self.f_flow_rate_to_WPA)

    def create_solver_structure(self):
        super().create_solver_structure()
        solver.matter.manual.branch(self.to_branches["WasteWaterToWPA"])
        self.to_branches["WasteWaterToWPA"].o_handler.set_flow_rate(self.f_flow_rate_to_WPA)
        self.to_children["WPA"].switch_off_microbial_check_valve(True)
        self.set_thermal_solvers()

    def exec(self, _):
        super().exec(_)
        
        f_time_step = self.o_timer.f_time - self.f_last_update_volume
        self.f_total_volume_passed_through_WPA += (
            self.to_branches["WasteWaterToWPA"].f_flow_rate /
            self.to_branches["WasteWaterToWPA"].ao_flows[0].get_density() * f_time_step
        )
        self.f_last_update_volume = self.o_timer.f_time
        
        if self.o_timer.f_time % 1800 < self.f_resync_modulo_counter:
            self.o_timer.synchronize_callbacks()
        self.f_resync_modulo_counter = self.o_timer.f_time % 1800
