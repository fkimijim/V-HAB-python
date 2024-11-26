import math

def calculateNusseltFlatGap(fRe, fPr, fD_Hydraulic, fLength, fConfig):
    """
    Calculate the Nusselt number for a flat gap based on Reynolds and Prandtl numbers.
    Parameters:
        fRe (float): Reynolds number
        fPr (float): Prandtl number
        fD_Hydraulic (float): Hydraulic diameter
        fLength (float): Length of the gap
        fConfig (int): Configuration parameter
    Returns:
        float: Nusselt number
    """

    # Laminar flow
    if fRe < 3.2e3 and fRe != 0:
        fNu1 = 7.541
        fNu2 = 1.841 * (fRe * fPr * fD_Hydraulic / fLength) ** (1 / 3)
        fNu = (fNu1**3 + fNu2**3) ** (1 / 3)

    # Turbulent flow
    elif 1e4 < fRe < 1e6 and 0.1 < fPr < 1000:
        fFriction_Factor = (1.8 * math.log10(fRe) - 1.5) ** -2
        fNu = ((fFriction_Factor / 8) * fRe * fPr) / (
            1 + 12.7 * math.sqrt(fFriction_Factor / 8) * ((fPr**(2 / 3)) - 1)
        ) * (1 + (fD_Hydraulic / fLength) ** (2 / 3))

    # Transient area
    elif 2300 <= fRe <= 1e4 and 0.6 < fPr < 1000:
        fInterpolation_Factor = (fRe - 2300) / (1e4 - 2300)

        fNu_1 = 3.66
        fNu_2 = 1.615 * (fRe * fPr * (fD_Hydraulic / fLength) ** (1 / 3))
        if fConfig in [1, 3]:
            fNu_3 = (2 / (1 + 22 * fPr)) ** (1 / 6) * (fRe * fPr * (fD_Hydraulic / fLength) ** (1 / 2))
        else:
            fNu_3 = 0

        fNu_Laminar = ((fNu_1**3) + (0.7**3) + ((fNu_2 - 0.7)**3) + (fNu_3**3)) ** (1 / 3)

        fFriction_Factor = (1.8 * math.log10(fRe) - 1.5) ** -2
        fNu_Turbulent = ((fFriction_Factor / 8) * fRe * fPr) / (
            1 + 12.7 * math.sqrt(fFriction_Factor / 8) * ((fPr**(2 / 3)) - 1)
        ) * (1 + (fD_Hydraulic / fLength) ** (2 / 3))

        fNu = (1 - fInterpolation_Factor) * fNu_Laminar + fInterpolation_Factor * fNu_Turbulent

    # Zero flow speed
    elif fRe == 0:
        fNu = 0

    # Invalid parameters
    else:
        raise ValueError(
            f"Invalid Reynolds or Prandtl number. Reynolds must be < 1e6 and > 0. Prandtl must be between 0.6 and 1000. "
            f"Given: fRe={fRe}, fPr={fPr}"
        )

    return fNu
