def calculate_ppm(self, afMass):
    """
    Calculate the concentration of substances in parts per million (PPM).

    Parameters:
        afMass (list or ndarray): Vector containing the total partial masses of each substance in kg.

    Returns:
        list: Concentration of substances in parts per million (PPM).
    """
    # Calculate the number of moles for each substance
    afMols = afMass / self.afMolarMass

    # Calculate PPM as the molar fraction multiplied by 10^6
    afPPM = (afMols / sum(afMols)) * 1e6

    return afPPM
