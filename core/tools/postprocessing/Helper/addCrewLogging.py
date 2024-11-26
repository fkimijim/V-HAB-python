def add_crew_logging(o_logger, o_system):
    """
    Add crew-related logging to the logger.
    
    Args:
        o_logger: Logger object to manage logging.
        o_system: System object containing crew member data.
    """
    # Initialize log categories for crew members
    crew_logs = {
        "CO2FlowRates": [],
        "O2FlowRates": [],
        "IngestedWaterFlowRates": [],
        "RespirationWaterFlowRates": [],
        "PerspirationWaterFlowRates": [],
        "MetabolismWaterFlowRates": [],
        "StomachWaterFlowRates": [],
        "FecesWaterFlowRates": [],
        "UrineWaterFlowRates": [],
        "FoodFlowRates": [],
        "FecesProteinFlowRates": [],
        "FecesFatFlowRates": [],
        "FecesGlucoseFlowRates": [],
        "FecesFiberFlowRates": [],
        "FecesSodiumFlowRates": [],
        "UrineSodiumFlowRates": [],
        "UrinePotassiumFlowRates": [],
        "UrineUreaFlowRates": [],
        "FecesConverterWaterFlowRates": [],
        "UrineConverterWaterFlowRates": []
    }

    # Loop through each crew member to add logs
    for i_human in range(1, o_system.i_crew_members + 1):
        base_path = f"{o_system.name}:c:Human_{i_human}"

        # Add various flow rate logs
        o_logger.add_value(f"{base_path}.toBranches.Potable_Water_In", "fFlowRate", "kg/s", f"Ingested Water Flow Rate {i_human}")
        o_logger.add_value(f"{base_path}.toBranches.RespirationWaterOutput", "fFlowRate", "kg/s", f"Respiration Water Flow Rate {i_human}")
        o_logger.add_value(f"{base_path}.toBranches.PerspirationWaterOutput", "fFlowRate", "kg/s", f"Perspiration Water Flow Rate {i_human}")
        o_logger.add_value(f"{base_path}.toBranches.Urine_Out", "fFlowRate", "kg/s", f"Urine Flow Rate {i_human}")
        o_logger.add_value(f"{base_path}.toBranches.Food_In", "fFlowRate", "kg/s", f"Food Flow Rate {i_human}")

        # Add CO2 and O2 flow rates
        o_logger.add_value(f"{base_path}.toBranches.Air_In.aoFlows(1)", "this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.CO2)", "kg/s", f"CO2 Inlet Flowrate {i_human}")
        o_logger.add_value(f"{base_path}.toBranches.Air_Out.aoFlows(1)", "this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.CO2)", "kg/s", f"CO2 Outlet Flowrate {i_human}")
        o_logger.add_value(f"{base_path}.toBranches.Air_In.aoFlows(1)", "this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.O2)", "kg/s", f"O2 Inlet Flowrate {i_human}")
        o_logger.add_value(f"{base_path}.toBranches.Air_Out.aoFlows(1)", "this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.O2)", "kg/s", f"O2 Outlet Flowrate {i_human}")

        # Add to categories
        crew_logs["CO2FlowRates"].append(f'"CO2 Outlet Flowrate {i_human}" + "CO2 Inlet Flowrate {i_human}" +')
        crew_logs["O2FlowRates"].append(f'"O2 Outlet Flowrate {i_human}" + "O2 Inlet Flowrate {i_human}" +')

    # Generate virtual values for cumulative metrics
    for category, items in crew_logs.items():
        if items:
            flow_rates = " ".join(items).strip("+")
            o_logger.add_virtual_value(f"cumsum(({flow_rates}) * 'Timestep')", "kg", category)

    # Example: CO2 and O2 cumulative calculations
    co2_flow_rates = " ".join(crew_logs["CO2FlowRates"]).strip("+")
    o_logger.add_virtual_value(f"cumsum(({co2_flow_rates}) * 'Timestep')", "kg", "Exhaled CO2")

    o2_flow_rates = " ".join(crew_logs["O2FlowRates"]).strip("+")
    o_logger.add_virtual_value(f"cumsum(({o2_flow_rates}) * 'Timestep')", "kg", "Inhaled O2")

    print("Crew logging setup complete.")
