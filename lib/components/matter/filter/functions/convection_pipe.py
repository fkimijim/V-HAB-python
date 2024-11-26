import numpy as np

def convection_pipe(fD_Hydraulic, fLength, fFlowSpeed, fDyn_Visc, fDensity, fThermal_Conductivity, fC_p, fConfig):
    """
    Returns the convection coefficient alpha for the interior of a single pipe in W/m²K.

    Parameters:
    fD_Hydraulic (float): Inner hydraulic diameter of the pipe in m
    fLength (float): Length of the pipe in m
    fFlowSpeed (float): Flow speed of the fluid in the pipe in m/s
    fDyn_Visc (float or list): Dynamic viscosity of the fluid in kg/(m s)
    fDensity (float or list): Density of the fluid in kg/m³
    fThermal_Conductivity (float or list): Thermal conductivity of the fluid in W/(m K)
    fC_p (float or list): Heat capacity of the fluid in J/K
    fConfig (int): 0 for disturbed flow, 1 for non-disturbed flow

    Returns:
    fConvection_alpha (float): Convection coefficient in W/m²K
    """

    # Check if temperature dependency is considered
    if isinstance(fDyn_Visc, list) and len(fDyn_Visc) == 2 and fConfig == 0:
        fConfig = 2
    elif isinstance(fDyn_Visc, list) and len(fDyn_Visc) == 2 and fConfig == 1:
        fConfig = 3

    # Calculate kinematic viscosity
    fKin_Visc_m = fDyn_Visc[0] / fDensity[0]

    # Calculate Reynolds number
    fRe = (fFlowSpeed * fD_Hydraulic) / fKin_Visc_m

    # Calculate Prandtl number
    if fConfig in [0, 1]:
        fPr_m = (fDyn_Visc * fC_p) / fThermal_Conductivity
    elif fConfig in [2, 3]:
        fPr_m = (fDyn_Visc[0] * fC_p[0]) / fThermal_Conductivity[0]
        fPr_w = (fDyn_Visc[1] * fC_p[1]) / fThermal_Conductivity[1]

    # Determine the flow regime and calculate Nusselt number
    if fRe < 2300 and fRe != 0:  # Laminar flow
        fNu_1 = 3.66
        fNu_2 = 1.615 * (fRe * fPr_m * (fD_Hydraulic / fLength) ** (1 / 3))
        fNu_3 = 0
        if fConfig in [1, 3]:
            fNu_3 = (2 / (1 + 22 * fPr_m)) ** (1 / 6) * (fRe * fPr_m * (fD_Hydraulic / fLength) ** (1 / 2))
        fNu = ((fNu_1 ** 3) + (0.7 ** 3) + ((fNu_2 - 0.7) ** 3) + (fNu_3 ** 3)) ** (1 / 3)

    elif 10 ** 4 < fRe < 10 ** 6 and 0.1 < fPr_m < 1000:  # Turbulent flow
        fFriction_Factor = (1.8 * np.log10(fRe) - 1.5) ** (-2)
        fNu = ((fFriction_Factor / 8) * fRe * fPr_m) / (1 + 12.7 * np.sqrt(fFriction_Factor / 8) * ((fPr_m ** (2 / 3)) - 1)) * (1 + (fD_Hydraulic / fLength) ** (2 / 3))

    elif 2300 <= fRe <= 10 ** 4 and 0.6 < fPr_m < 1000:  # Transient flow
        fInterpolation_Factor = (fRe - 2300) / (10 ** 4 - 2300)
        fNu_1 = 3.66
        fNu_2 = 1.615 * (fRe * fPr_m * (fD_Hydraulic / fLength) ** (1 / 3))
        fNu_3 = 0
        if fConfig in [1, 3]:
            fNu_3 = (2 / (1 + 22 * fPr_m)) ** (1 / 6) * (fRe * fPr_m * (fD_Hydraulic / fLength) ** (1 / 2))
        fNu_Laminar = ((fNu_1 ** 3) + (0.7 ** 3) + ((fNu_2 - 0.7) ** 3) + (fNu_3 ** 3)) ** (1 / 3)
        fFriction_Factor = (1.8 * np.log10(fRe) - 1.5) ** (-2)
        fNu_Turbulent = ((fFriction_Factor / 8) * fRe * fPr_m) / (1 + 12.7 * np.sqrt(fFriction_Factor / 8) * ((fPr_m ** (2 / 3)) - 1)) * (1 + (fD_Hydraulic / fLength) ** (2 / 3))
        fNu = (1 - fInterpolation_Factor) * fNu_Laminar + fInterpolation_Factor * fNu_Turbulent

    elif fRe == 0:
        fNu = 0

    else:
        raise ValueError(
            f"Reynolds or Prandtl number out of bounds. Reynolds: {fRe}, Prandtl: {fPr_m}, Flow Speed: {fFlowSpeed}, Kinematic Viscosity: {fKin_Visc_m}"
        )

    if fConfig in [2, 3]:
        fNu *= (fPr_m / fPr_w) ** 0.11

    # Calculate convection coefficient alpha
    fConvection_alpha = (fNu * fThermal_Conductivity[0]) / fD_Hydraulic

    return fConvection_alpha
