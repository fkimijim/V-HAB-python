def add_CROP_logging(o_logger, o_system):
    """
    Adds logging for CROP systems.

    Args:
        o_logger: Logger object for managing logs.
        o_system: System object containing CROP data.
    """
    # Initialize flow rate lists
    cs_urine_in_flow_rates = [None] * o_system.iCROPs
    cs_water_in_flow_rates = [None] * o_system.iCROPs
    cs_urea_in_flow_rates = [None] * o_system.iCROPs
    cs_water_out_flow_rates = [None] * o_system.iCROPs
    cs_urea_out_flow_rates = [None] * o_system.iCROPs
    cs_NO3_out_flow_rates = [None] * o_system.iCROPs
    cs_NH4_out_flow_rates = [None] * o_system.iCROPs
    cs_CO2_out_flow_rates = [None] * o_system.iCROPs
    cs_O2_in_flow_rates = [None] * o_system.iCROPs
    cs_NH3_out_flow_rates = [None] * o_system.iCROPs

    # Loop through each CROP
    for i_crop in range(1, o_system.iCROPs + 1):
        crop_name = f"{o_system.sName}.toChildren.CROP_{i_crop}"
        o_logger.add_value(f"{crop_name}.toBranches.CROP_Urine_Inlet.aoFlows(1)",
                           'this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.Urine)', 'kg/s',
                           f"Urine to CROP {i_crop}")
        o_logger.add_value(f"{crop_name}.toStores.CROP_Tank.toPhases.TankSolution.toManips.substance",
                           'this.afPartialFlows(this.oMT.tiN2I.H2O)', 'kg/s', f"H2O to CROP {i_crop}")
        o_logger.add_value(f"{crop_name}.toStores.CROP_Tank.toPhases.TankSolution.toManips.substance",
                           'this.afPartialFlows(this.oMT.tiN2I.CH4N2O)', 'kg/s', f"Urea to CROP {i_crop}")

        o_logger.add_value(f"{crop_name}.toBranches.CROP_Solution_Outlet.aoFlows(1)",
                           'this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.H2O)', 'kg/s',
                           f"H2O from CROP {i_crop}")
        o_logger.add_value(f"{crop_name}.toBranches.CROP_Solution_Outlet.aoFlows(1)",
                           'this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.CH4N2O)', 'kg/s',
                           f"Urea from CROP {i_crop}")
        o_logger.add_value(f"{crop_name}.toBranches.CROP_Solution_Outlet.aoFlows(1)",
                           'this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.NO3)', 'kg/s',
                           f"NO3 from CROP {i_crop}")
        o_logger.add_value(f"{crop_name}.toBranches.CROP_Solution_Outlet.aoFlows(1)",
                           'this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.NH4)', 'kg/s',
                           f"NH4 from CROP {i_crop}")

        o_logger.add_value(f"{crop_name}.toStores.CROP_Tank.toProcsP2P.CO2_Outgassing_Tank",
                           'this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.CO2)', 'kg/s',
                           f"CO2 from CROP {i_crop}")
        o_logger.add_value(f"{crop_name}.toStores.CROP_Tank.toProcsP2P.O2_to_TankSolution",
                           'this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.O2)', 'kg/s',
                           f"O2 to CROP {i_crop}")
        o_logger.add_value(f"{crop_name}.toStores.CROP_Tank.toProcsP2P.NH3_Outgassing_Tank",
                           'this.fFlowRate * this.arPartialMass(this.oMT.tiN2I.NH3)', 'kg/s',
                           f"NH3 from CROP {i_crop}")

        o_logger.add_value(f"{crop_name}.toStores.CROP_Tank.toPhases.TankSolution",
                           'this.afMass(this.oMT.tiN2I.H2O)', 'kg', f"H2O in CROP {i_crop}")
        o_logger.add_value(f"{crop_name}.toStores.CROP_Tank.toPhases.TankSolution",
                           'this.afMass(this.oMT.tiN2I.CH4N2O)', 'kg', f"Urea in CROP {i_crop}")
        o_logger.add_value(f"{crop_name}.toStores.CROP_Tank.toPhases.TankSolution",
                           'this.afMass(this.oMT.tiN2I.NO3)', 'kg', f"NO3 in CROP {i_crop}")
        o_logger.add_value(f"{crop_name}.toStores.CROP_Tank.toPhases.TankSolution",
                           'this.afMass(this.oMT.tiN2I.NH4)', 'kg', f"NH4 in CROP {i_crop}")
        o_logger.add_value(f"{crop_name}.toStores.CROP_Tank.toPhases.TankSolution",
                           'this.afMass(this.oMT.tiN2I.Urine)', 'kg', f"Urine in CROP {i_crop}")

        # Collect flow rates for virtual values
        cs_urine_in_flow_rates[i_crop - 1] = f'"Urine to CROP {i_crop}" +'
        cs_water_in_flow_rates[i_crop - 1] = f'"H2O to CROP {i_crop}" +'
        cs_urea_in_flow_rates[i_crop - 1] = f'"Urea to CROP {i_crop}" +'
        cs_water_out_flow_rates[i_crop - 1] = f'"H2O from CROP {i_crop}" +'
        cs_urea_out_flow_rates[i_crop - 1] = f'"Urea from CROP {i_crop}" +'
        cs_NO3_out_flow_rates[i_crop - 1] = f'"NO3 from CROP {i_crop}" +'
        cs_NH4_out_flow_rates[i_crop - 1] = f'"NH4 from CROP {i_crop}" +'
        cs_CO2_out_flow_rates[i_crop - 1] = f'"CO2 from CROP {i_crop}" +'
        cs_O2_in_flow_rates[i_crop - 1] = f'"O2 to CROP {i_crop}" +'
        cs_NH3_out_flow_rates[i_crop - 1] = f'"NH3 from CROP {i_crop}" +'

    # Add virtual values for cumulative flow rates
    for flow_rates, label in zip(
        [cs_urine_in_flow_rates, cs_water_in_flow_rates, cs_urea_in_flow_rates, cs_water_out_flow_rates,
         cs_urea_out_flow_rates, cs_NO3_out_flow_rates, cs_NH4_out_flow_rates, cs_CO2_out_flow_rates,
         cs_O2_in_flow_rates, cs_NH3_out_flow_rates],
        ['Urine to CROP', 'Water to CROP', 'Urea to CROP', 'Water from CROP', 'Urea from CROP',
         'NO3 from CROP', 'NH4 from CROP', 'CO2 from CROP', 'O2 to CROP', 'NH3 from CROP']
    ):
        flow_string = ''.join(flow_rates)[:-1]  # Remove the trailing '+'
        o_logger.add_virtual_value(flow_string, 'kg/s', label)
        o_logger.add_virtual_value(f'cumsum(({flow_string}) * "Timestep")', 'kg', f'{label} Mass')
