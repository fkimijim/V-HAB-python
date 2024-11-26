def determine_phase(self, s_substance, f_temperature, f_pressure):
    """
    Determine the phase of a substance based on temperature and pressure.

    Args:
        s_substance (str or list): Substance name or mass vector.
        f_temperature (float): Temperature in Kelvin.
        f_pressure (float or list): Pressure in Pascal.

    Returns:
        mi_phase (int): Phase indicator (1=solid, 2=liquid, 3=gas, 4=supercritical).
        cs_possible_phase (list): Possible phases.
    """
    cs_phase = ["Solid", "Liquid", "Gas", "Supercritical"]

    if isinstance(s_substance, list):  # Case for a mass vector
        cs_substances = [self.cs_substances[i] for i, mass in enumerate(s_substance) if mass != 0]

        if any(self.ab_compound[i] for i, mass in enumerate(s_substance) if mass != 0):
            raise ValueError("Resolve compound masses using the `resolve_compound_mass` function before using `determine_phase`.")

        mi_phase = [0] * self.i_substances
        for substance in cs_substances:
            phase, _ = self._determine_phase_for_substance(substance, f_temperature, f_pressure[self.ti_n2i[substance]])
            mi_phase[self.ti_n2i[substance]] = phase

        try:
            cs_possible_phase = [cs_phase[i - 1] for i in set(mi_phase) if i != 0]
        except Exception:
            cs_possible_phase = ["PhaseChanging"]

    else:  # Single substance
        mi_phase, cs_possible_phase = self._determine_phase_for_substance(s_substance, f_temperature, f_pressure)

    return mi_phase, cs_possible_phase

def _determine_phase_for_substance(self, s_substance, f_temperature, f_pressure):
    """
    Determine phase for a specific substance.

    Args:
        s_substance (str): Substance name.
        f_temperature (float): Temperature in Kelvin.
        f_pressure (float): Pressure in Pascal.

    Returns:
        mi_phase (int): Phase indicator.
        cs_possible_phase (list): Possible phases.
    """
    cs_phase = ["Solid", "Liquid", "Gas", "Supercritical"]

    if not self.ttx_matter[s_substance]["bIndividualFile"]:
        cs_possible_phase = [phase.replace("t", "") for phase in self.ttx_matter[s_substance]["ttxPhases"].keys()]
        mi_phase = cs_phase.index(cs_possible_phase[0]) + 1
        return mi_phase, cs_possible_phase

    if "tPhaseIdentification" not in self.ttx_matter[s_substance]["tIsobaricData"]:
        # Construct mfData matrix
        mf_data = []
        for i_phase, phase in enumerate(cs_phase):
            data = self.ttx_matter[s_substance]["tIsobaricData"][f"t{phase}"]["mfData"]
            temperature, pressure = data[:, 0], data[:, 1]
            mf_data.extend([[t, p, i_phase + 1] for t, p in zip(temperature, pressure) if not (t is None or p is None)])

        # Remove duplicates
        mf_data = list({tuple(row) for row in mf_data})

        # Create interpolation
        mf_data.sort()
        temperatures, pressures, phases = zip(*mf_data)
        interpolation = self.create_interpolation(temperatures, pressures, phases)
        self.ttx_matter[s_substance]["tIsobaricData"]["tPhaseIdentification"] = {
            "tInterpolation": interpolation,
            "bInterpolation": True,
            "ttExtremes": {
                "tTemperature": {"Min": min(temperatures), "Max": max(temperatures)},
                "tPressure": {"Min": min(pressures), "Max": max(pressures)},
            },
        }

    # Adjust temperature and pressure if outside interpolation bounds
    extremes = self.ttx_matter[s_substance]["tIsobaricData"]["tPhaseIdentification"]["ttExtremes"]
    f_temperature = max(min(f_temperature, extremes["tTemperature"]["Max"]), extremes["tTemperature"]["Min"])
    f_pressure = max(min(f_pressure, extremes["tPressure"]["Max"]), extremes["tPressure"]["Min"])

    # Perform interpolation
    interpolation = self.ttx_matter[s_substance]["tIsobaricData"]["tPhaseIdentification"]["tInterpolation"]
    f_phase = interpolation(f_temperature, f_pressure)

    # Handle numerical errors
    f_phase = round(f_phase, 6)

    cs_possible_phase = cs_phase[int(f_phase) - 1 : int(f_phase)]
    mi_phase = int(f_phase)

    return mi_phase, cs_possible_phase

def create_interpolation(self, temperatures, pressures, phases):
    """
    Create an interpolation function for phase determination.

    Args:
        temperatures (list): List of temperatures.
        pressures (list): List of pressures.
        phases (list): List of phases.

    Returns:
        interpolation: Interpolation function.
    """
    from scipy.interpolate import LinearNDInterpolator
    points = list(zip(temperatures, pressures))
    return LinearNDInterpolator(points, phases)
