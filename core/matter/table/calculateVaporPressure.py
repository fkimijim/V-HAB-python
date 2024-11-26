def calculate_vapor_pressure(self, f_temperature, s_substance):
    """
    Calculates the vapor pressure for a given substance at a given temperature.

    The vapor pressure over temperature is required for the calculation of
    condensation in heat exchangers. The vapor pressure returned is 0 if the
    substance is liquid at all pressures, and inf if it is a gas at all pressures.

    Args:
        f_temperature (float): The temperature in K.
        s_substance (str): The substance for which to calculate vapor pressure.

    Returns:
        float: The vapor pressure in Pa.
    """
    try:
        # If an interpolation for vapor pressure already exists, use it
        t_matter = self.ttx_matter[s_substance]
        f_vapor_pressure = t_matter["tInterpolations"]["VaporPressure"](f_temperature)

    except KeyError:
        # If no interpolation exists, create it
        antoine_data = self.matter_data["AntoineData"][s_substance]

        mf_limits = [limit for range_data in antoine_data["Range"] for limit in range_data["mfLimits"]]

        # Create temperature array (0 to 1000 K, step of 1 K)
        af_temperature = list(range(0, 1001))

        af_vapor_pressure = [
            self._create_interpolation(temp, antoine_data, mf_limits) for temp in af_temperature
        ]

        # Store the interpolation in the matter data
        from scipy.interpolate import interp1d
        self.ttx_matter[s_substance]["tInterpolations"]["VaporPressure"] = interp1d(
            af_temperature, af_vapor_pressure, kind="linear", bounds_error=False, fill_value="extrapolate"
        )

        # Calculate vapor pressure using the newly created interpolation
        f_vapor_pressure = self.ttx_matter[s_substance]["tInterpolations"]["VaporPressure"](f_temperature)

    return f_vapor_pressure


def _create_interpolation(self, f_temperature, antoine_data, mf_limits):
    """
    Helper function to create vapor pressure interpolation for a given temperature.

    Args:
        f_temperature (float): The temperature in K.
        antoine_data (dict): Antoine equation data for the substance.
        mf_limits (list): List of temperature limits for the Antoine ranges.

    Returns:
        float: Vapor pressure in Pa.
    """
    if f_temperature < mf_limits[0]:
        # Temperature below the limits: substance is liquid, vapor pressure is 0
        return 0
    elif f_temperature > mf_limits[-1]:
        # Temperature above the limits: substance is gaseous, vapor pressure is inf
        return float('inf')
    else:
        for range_data in antoine_data["Range"]:
            if mf_limits[0] <= f_temperature <= mf_limits[1]:
                f_a = range_data["fA"]
                f_b = range_data["fB"]
                f_c = range_data["fC"]

                # Antoine Equation (source: NIST Chemistry WebBook)
                f_vapor_pressure = (10 ** (f_a - (f_b / (f_temperature + f_c)))) * 1e5
                return f_vapor_pressure

    raise ValueError("Temperature is outside the defined ranges for Antoine data.")
