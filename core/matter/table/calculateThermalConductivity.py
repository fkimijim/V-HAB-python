def calculate_thermal_conductivity(self, *args):
    """
    Calculate the thermal conductivity of the matter in a phase or flow.

    Calculates the conductivity of the matter inside a phase or the matter
    flowing through the flow object. This is done by adding the single
    substance conductivities at the current temperature and pressure and
    weighing them with their mass fraction.

    Examples:
        f_thermal_conductivity = calculate_thermal_conductivity(o_flow)
        f_thermal_conductivity = calculate_thermal_conductivity(o_phase)
        f_thermal_conductivity = calculate_thermal_conductivity(s_type, af_mass, f_temperature, af_partial_pressures)

    Returns:
        float: Thermal conductivity of the matter in the current state in W/mK.
    """
    (
        f_temperature,
        ar_partial_mass,
        cs_phase,
        ai_phase,
        ai_indices,
        af_partial_pressures,
        _,
        _,
        b_use_isobaric_data
    ) = self.get_necessary_parameters(*args)

    # Calculate the thermal conductivity
    f_thermal_conductivity = self.calculate_property(
        'Thermal Conductivity',
        f_temperature,
        ar_partial_mass,
        cs_phase,
        ai_phase,
        ai_indices,
        af_partial_pressures,
        b_use_isobaric_data
    )

    return f_thermal_conductivity
