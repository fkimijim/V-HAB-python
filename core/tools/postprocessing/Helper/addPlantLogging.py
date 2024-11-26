def add_plant_logging(o_logger, o_system, o_setup):
    """
    Adds logging for plant data.

    Args:
        o_logger: Logger object for managing logs.
        o_system: System object containing plant data.
        o_setup: Setup object for configuring logs.
    """
    o_setup["tiPlantLogs"] = {}

    for i_plant, plant_name in enumerate(o_system["csPlants"], start=1):
        num_subcultures = len(o_system["miSubcultures"][i_plant - 1])
        o_setup["tiPlantLogs"][i_plant] = {
            "miMass": [0] * num_subcultures,
            "miEdibleMass": [0] * num_subcultures,
            "miWaterUptake": [0] * num_subcultures,
            "miO2": [0] * num_subcultures,
            "miCO2": [0] * num_subcultures,
            "miTranspiration": [0] * num_subcultures,
            "miEdibleGrowth": [0] * num_subcultures,
            "miInedibleGrowth": [0] * num_subcultures,
            "miNO3UptakeStorage": [0] * num_subcultures,
            "miNO3UptakeStructure": [0] * num_subcultures,
            "miNO3UptakeEdible": [0] * num_subcultures,
        }

        cs_mass = []
        cs_edible_mass = []
        cs_water_uptake = []
        cs_o2 = []
        cs_co2 = []
        cs_transpiration = []
        cs_edible_growth = []
        cs_inedible_growth = []
        cs_no3_uptake_storage = []
        cs_no3_uptake_structure = []
        cs_no3_uptake_edible = []

        for i_subculture in range(1, num_subcultures + 1):
            culture_name = f"{plant_name}_{i_subculture}"

            o_setup["tiPlantLogs"][i_plant]["miMass"][i_subculture - 1] = o_logger.add_value(
                f"{o_system['sName']}.toChildren.{culture_name}.toStores.Plant_Culture.toPhases.Plants",
                "fMass", "kg", f"{culture_name} Mass"
            )
            o_setup["tiPlantLogs"][i_plant]["miEdibleMass"][i_subculture - 1] = o_logger.add_value(
                f"{o_system['sName']}.toChildren.{culture_name}.toStores.Plant_Culture.toPhases.Plants",
                f"this.afMass(this.oMT.tiN2I.{plant_name})", "kg", f"{culture_name} Edible Biomass"
            )

            o_setup["tiPlantLogs"][i_plant]["miWaterUptake"][i_subculture - 1] = o_logger.add_value(
                f"{o_system['sName']}.toChildren.{culture_name}", "fWaterConsumptionRate",
                "kg/s", f"{culture_name} Water Consumption Rate"
            )

            o_setup["tiPlantLogs"][i_plant]["miO2"][i_subculture - 1] = o_logger.add_value(
                f"{o_system['sName']}.toChildren.{culture_name}", "this.tfGasExchangeRates.fO2ExchangeRate",
                "kg/s", f"{culture_name} O2 Rate"
            )
            o_setup["tiPlantLogs"][i_plant]["miCO2"][i_subculture - 1] = o_logger.add_value(
                f"{o_system['sName']}.toChildren.{culture_name}", "this.tfGasExchangeRates.fCO2ExchangeRate",
                "kg/s", f"{culture_name} CO2 Rate"
            )
            o_setup["tiPlantLogs"][i_plant]["miTranspiration"][i_subculture - 1] = o_logger.add_value(
                f"{o_system['sName']}.toChildren.{culture_name}", "this.tfGasExchangeRates.fTranspirationRate",
                "kg/s", f"{culture_name} Transpiration Rate"
            )
            o_setup["tiPlantLogs"][i_plant]["miEdibleGrowth"][i_subculture - 1] = o_logger.add_value(
                f"{o_system['sName']}.toChildren.{culture_name}", "this.tfBiomassGrowthRates.fGrowthRateEdible",
                "kg/s", f"{culture_name} Edible Growth Rate"
            )
            o_setup["tiPlantLogs"][i_plant]["miInedibleGrowth"][i_subculture - 1] = o_logger.add_value(
                f"{o_system['sName']}.toChildren.{culture_name}", "this.tfBiomassGrowthRates.fGrowthRateInedible",
                "kg/s", f"{culture_name} Inedible Growth Rate"
            )

            o_setup["tiPlantLogs"][i_plant]["miNO3UptakeStorage"][i_subculture - 1] = o_logger.add_value(
                f"{o_system['sName']}.toChildren.{culture_name}", "this.tfUptakeRate_Storage.NO3",
                "kg/s", f"{culture_name} NO3 Uptake Storage"
            )
            o_setup["tiPlantLogs"][i_plant]["miNO3UptakeStructure"][i_subculture - 1] = o_logger.add_value(
                f"{o_system['sName']}.toChildren.{culture_name}", "this.tfUptakeRate_Structure.NO3",
                "kg/s", f"{culture_name} NO3 Uptake Structure"
            )
            o_setup["tiPlantLogs"][i_plant]["miNO3UptakeEdible"][i_subculture - 1] = o_logger.add_value(
                f"{o_system['sName']}.toChildren.{culture_name}", "this.tfUptakeRate_Structure.fEdibleUptakeNO3",
                "kg/s", f"{culture_name} NO3 Uptake Edible"
            )

            cs_mass.append(f'"{o_logger.t_log_values[o_setup["tiPlantLogs"][i_plant]["miMass"][i_subculture - 1]].sLabel}" +')
            cs_edible_mass.append(f'"{o_logger.t_log_values[o_setup["tiPlantLogs"][i_plant]["miEdibleMass"][i_subculture - 1]].sLabel}" +')
            cs_water_uptake.append(f'"{o_logger.t_log_values[o_setup["tiPlantLogs"][i_plant]["miWaterUptake"][i_subculture - 1]].sLabel}" +')
            cs_o2.append(f'"{o_logger.t_log_values[o_setup["tiPlantLogs"][i_plant]["miO2"][i_subculture - 1]].sLabel}" +')
            cs_co2.append(f'"{o_logger.t_log_values[o_setup["tiPlantLogs"][i_plant]["miCO2"][i_subculture - 1]].sLabel}" +')
            cs_transpiration.append(f'"{o_logger.t_log_values[o_setup["tiPlantLogs"][i_plant]["miTranspiration"][i_subculture - 1]].sLabel}" +')
            cs_edible_growth.append(f'"{o_logger.t_log_values[o_setup["tiPlantLogs"][i_plant]["miEdibleGrowth"][i_subculture - 1]].sLabel}" +')
            cs_inedible_growth.append(f'"{o_logger.t_log_values[o_setup["tiPlantLogs"][i_plant]["miInedibleGrowth"][i_subculture - 1]].sLabel}" +')
            cs_no3_uptake_storage.append(f'"{o_logger.t_log_values[o_setup["tiPlantLogs"][i_plant]["miNO3UptakeStorage"][i_subculture - 1]].sLabel}" +')
            cs_no3_uptake_structure.append(f'"{o_logger.t_log_values[o_setup["tiPlantLogs"][i_plant]["miNO3UptakeStructure"][i_subculture - 1]].sLabel}" +')
            cs_no3_uptake_edible.append(f'"{o_logger.t_log_values[o_setup["tiPlantLogs"][i_plant]["miNO3UptakeEdible"][i_subculture - 1]].sLabel}" +')

        # Add virtual values (cumulative and rates)
        def add_virtual(cs_values, label, unit):
            s_values = ''.join(cs_values)[:-1]  # Remove trailing '+'
            o_logger.add_virtual_value(s_values, unit, label)

        add_virtual(cs_mass, f"{plant_name} current Biomass", "kg")
        add_virtual(cs_edible_mass, f"{plant_name} current Edible Biomass", "kg")
        add_virtual(cs_water_uptake, f"{plant_name} Water Uptake", "kg/s")
        add_virtual(cs_o2, f"{plant_name} O2 Exchange", "kg/s")
        add_virtual(cs_co2, f"{plant_name} CO2 Exchange", "kg/s")
        add_virtual(cs_transpiration, f"{plant_name} Transpiration", "kg/s")
        add_virtual(cs_edible_growth, f"{plant_name} Edible Growth", "kg/s")
        add_virtual(cs_inedible_growth, f"{plant_name} Inedible Growth", "kg/s")
        add_virtual(cs_no3_uptake_storage, f"{plant_name} NO3 Storage Uptake", "kg/s")
        add_virtual(cs_no3_uptake_structure, f"{plant_name} NO3 Structure Uptake", "kg/s")
        add_virtual(cs_no3_uptake_edible, f"{plant_name} NO3 Edible Uptake", "kg/s")
