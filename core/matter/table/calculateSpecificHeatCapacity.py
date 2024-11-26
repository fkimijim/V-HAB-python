def calculate_specific_heat_capacity(self, *args):
    """
    Calculate the specific heat capacity of a mixture.

    This function calculates the specific heat capacity by adding the single
    substance capacities weighted with their mass fraction. It can use either
    a phase object as input, or the phase type and the masses array.
    Optionally, temperature and pressure can be passed as additional parameters.

    Examples:
        f_specific_heat_capacity = calculate_specific_heat_capacity(oFlow)
        f_specific_heat_capacity = calculate_specific_heat_capacity(oPhase)
        f_specific_heat_capacity = calculate_specific_heat_capacity(sType, afMass, fTemperature, afPartialPressures)

    Returns:
        float: Specific, isobaric heat capacity of the mixture in J/kgK.
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

    # Calculation of specific heat capacity
    f_specific_heat_capacity = self.calculate_property(
        'Heat Capacity',
        f_temperature,
        ar_partial_mass,
        cs_phase,
        ai_phase,
        ai_indices,
        af_partial_pressures,
        b_use_isobaric_data
    )

    # Ensure heat capacity is physically valid
    if f_specific_heat_capacity < 0:
        raise ValueError(
            "Negative specific heat capacity detected. "
            "Check thermodynamic equilibrium and input data."
        )

    return f_specific_heat_capacity
