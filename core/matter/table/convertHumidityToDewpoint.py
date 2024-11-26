import math

def convert_humidity_to_dewpoint(self, *args):
    """
    Converts a relative humidity value (0 to 1) into dewpoint temperature in Kelvin.

    This function can take a gas phase object as input, from which it extracts the required parameters.
    Alternatively, it can take the following parameters in this order:
        rRelativeHumidity: Relative Humidity between 0 and 1 [-]
        fTemperature: Temperature of the gas for which the dewpoint shall be calculated [K]

    If you want to convert a dew point into a humidity, calculate the vapor pressure of water at the dew point
    temperature and then calculate the current vapor pressure of water at the actual temperature. By dividing
    the partial pressure by the vapor pressure, you obtain the relative humidity:
        rRelHumidity = oMT.calculate_vapor_pressure(fDewPoint, 'H2O') / oMT.calculate_vapor_pressure(fTemperature, 'H2O')
    """

    if len(args) == 1:
        o_phase = args[0]
        f_temperature = o_phase["fTemperature"]
        f_partial_pressure = o_phase["afPP"][self.tiN2I["H2O"]]
    else:
        r_relative_humidity = args[0]
        f_temperature = args[1]
        f_partial_pressure = r_relative_humidity * self.calculate_vapor_pressure(f_temperature, "H2O")

    # Values for Antoine equation from NIST Chemistry WebBook
    if 255.9 <= f_temperature < 379:
        # Parameters for the vapor pressure calculation
        f_a = 4.6543
        f_b = 1435.264
        f_c = -64.848
    elif 379 <= f_temperature < 573:
        # Parameters for the vapor pressure calculation
        f_a = 3.55959
        f_b = 643.748
        f_c = -198.043
    elif f_temperature < 255.9:
        # Below limits: substance is liquid, dewpoint is effectively 0 K
        return 0
    elif f_temperature >= 573:
        # Above limits: substance is gaseous, dewpoint is effectively infinite
        return float('inf')

    # Solve Antoine Equation for temperature
    try:
        f_dew_point = f_b / (f_a - math.log10(f_partial_pressure / 1e5)) - f_c
    except ValueError:
        # Handle log10 errors for invalid pressure values
        f_dew_point = float('nan')

    return f_dew_point
