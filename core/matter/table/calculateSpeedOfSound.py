def calculate_speed_of_sound(self, *args):
    """
    Calculate the speed of sound for the provided matter.

    This function calculates the speed of sound by adding the single
    substance speeds of sound weighted with their mass fraction. It can use
    either a phase object as input parameter, or the phase type (sType) and
    the masses array (afMasses). Optionally, temperature and pressure can be
    passed as additional parameters.

    Returns:
        float: Speed of sound in m/s.
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

    # Calculation of the speed of sound
    f_speed_of_sound = self.calculate_property(
        'Speed Of Sound',
        f_temperature,
        ar_partial_mass,
        cs_phase,
        ai_phase,
        ai_indices,
        af_partial_pressures,
        b_use_isobaric_data
    )

    return f_speed_of_sound
