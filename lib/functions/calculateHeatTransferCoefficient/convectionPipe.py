import numpy as np

def convectionPipe(fD_Hydraulic, fLength, fFlowSpeed, fDyn_Visc, fDensity, 
                   fThermal_Conductivity, fC_p, fConfig):
    """
    Returns the convection coefficient alpha for the interior of a single pipe in W/m²K.
    """
    # Config update for temperature dependency
    if len(fDyn_Visc) == 2 and fConfig == 0:
        fConfig = 2
    elif len(fDyn_Visc) == 2 and fConfig == 1:
        fConfig = 3

    fFlowSpeed = abs(fFlowSpeed)

    # Kinematic viscosity
    fKin_Visc_m = fDyn_Visc[0] / fDensity[0]

    # Reynolds number
    fRe = (fFlowSpeed * fD_Hydraulic) / fKin_Visc_m

    # Prandtl number
    if fConfig in [0, 1]:
        fPr_m = (fDyn_Visc * fC_p) / fThermal_Conductivity
    elif fConfig in [2, 3]:
        fPr_m = (fDyn_Visc[0] * fC_p[0]) / fThermal_Conductivity[0]
        fPr_w = (fDyn_Visc[1] * fC_p[1]) / fThermal_Conductivity[1]

    # Laminar flow
    if fRe < 2300 and fRe != 0:
        fNu_1 = 3.66
        fNu_2 = 1.615 * (fRe * fPr_m * (fD_Hydraulic / fLength) ** (1 / 3))
        if fConfig in [1, 3]:
            fNu_3 = (2 / (1 + 22 * fPr_m)) ** (1 / 6) * (fRe * fPr_m * (fD_Hydraulic / fLength) ** (1 / 2))
        else:
            fNu_3 = 0
        fNu = ((fNu_1 ** 3) + (0.7 ** 3) + ((fNu_2 - 0.7) ** 3) + (fNu_3 ** 3)) ** (1 / 3)

    # Turbulent flow
    elif 10**4 < fRe < 10**6 and 0.1 < fPr_m < 1000:
        fFriction_Factor = (1.8 * np.log10(fRe) - 1.5) ** (-2)
        fNu = ((fFriction_Factor / 8) * fRe * fPr_m) / \
              (1 + 12.7 * np.sqrt(fFriction_Factor / 8) * (fPr_m ** (2 / 3) - 1)) * \
              (1 + (fD_Hydraulic / fLength) ** (2 / 3))

    # Transient flow
    elif 2300 <= fRe <= 10**4 and 0.6 < fPr_m < 1000:
        fInterpolation_Factor = (fRe - 2300) / (10**4 - 2300)
        fNu_1 = 3.66
        fNu_2 = 1.615 * (fRe * fPr_m * (fD_Hydraulic / fLength) ** (1 / 3))
        if fConfig in [1, 3]:
            fNu_3 = (2 / (1 + 22 * fPr_m)) ** (1 / 6) * (fRe * fPr_m * (fD_Hydraulic / fLength) ** (1 / 2))
        else:
            fNu_3 = 0
        fNu_Laminar = ((fNu_1 ** 3) + (0.7 ** 3) + ((fNu_2 - 0.7) ** 3) + (fNu_3 ** 3)) ** (1 / 3)

        fFriction_Factor = (1.8 * np.log10(fRe) - 1.5) ** (-2)
        fNu_Turbulent = ((fFriction_Factor / 8) * fRe * fPr_m) / \
                        (1 + 12.7 * np.sqrt(fFriction_Factor / 8) * (fPr_m ** (2 / 3) - 1)) * \
                        (1 + (fD_Hydraulic / fLength) ** (2 / 3))
        fNu = (1 - fInterpolation_Factor) * fNu_Laminar + fInterpolation_Factor * fNu_Turbulent

    # No flow
    elif fRe == 0:
        fNu = 0

    else:
        raise ValueError(f"Reynolds or Prandtl number out of bounds. fRe: {fRe}, fPr_m: {fPr_m}")

    if fConfig in [2, 3]:
        fNu = fNu * ((fPr_m / fPr_w) ** 0.11)

    # Convection coefficient
    fConvection_alpha = (fNu * fThermal_Conductivity[0]) / fD_Hydraulic

    return fConvection_alpha
