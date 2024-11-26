import numpy as np

def convectionMultiplePipeRow(fD_o, fs_1, fs_2, fFlowSpeed, fDyn_Visc, fDensity, fThermal_Conductivity, fC_p, fConfig, fs_3=None):
    """
    Returns the convection coefficient alpha for multiple rows of pipes
    in W/m²K.

    Parameters:
        fD_o: float
            Outer diameter of the pipes in m.
        fs_1: float
            Distance between the centers of two adjacent pipes (perpendicular to flow direction) in m.
        fs_2: float
            Distance between the centers of two adjacent pipes (in flow direction) in m.
        fFlowSpeed: float
            Flow speed of the fluid outside the pipes in m/s.
        fDyn_Visc: list or float
            Dynamic viscosity of the fluid in kg/(m s). Can be a single value or a list of two values for T_m and T_w.
        fDensity: list or float
            Density of the fluid in kg/m³. Can be a single value or a list of two values for T_m and T_w.
        fThermal_Conductivity: list or float
            Thermal conductivity of the fluid in W/(m K). Can be a single value or a list of two values for T_m and T_w.
        fC_p: list or float
            Heat capacity of the fluid in J/K.
        fConfig: int
            Configuration parameter:
            - 0: Aligned pipes.
            - 1: Shifted pipes.
            - 2: Partially shifted pipes.
        fs_3: float, optional
            Distance between the centers of two pipes in different rows (perpendicular to flow direction) in m.
            Used only for `fConfig=2`.

    Returns:
        fConvection_Alpha: float
            Convection coefficient in W/m²K.
    """
    # Determine if temperature-dependent material values are used
    if isinstance(fDyn_Visc, list) and len(fDyn_Visc) == 2:
        fTemp_Dep = 1
    elif isinstance(fDyn_Visc, (float, int)):
        fTemp_Dep = 0
    else:
        raise ValueError("Invalid number of inputs for material values")

    # Kinematic viscosity
    if fTemp_Dep == 0:
        fKin_Visc_m = fDyn_Visc / fDensity
    else:
        fKin_Visc_m = fDyn_Visc[0] / fDensity[0]
        fKin_Visc_w = fDyn_Visc[1] / fDensity[1]

    fFlowSpeed = abs(fFlowSpeed)

    # Overflow length
    fOverflow_Length = (np.pi / 2) * fD_o

    # Psi calculation
    if fs_2 / fD_o >= 1:
        fPsi = 1 - (np.pi * fD_o) / (4 * fs_1)
    else:
        fPsi = 1 - (np.pi * fD_o**2) / (4 * fs_1 * fs_2)

    # Reynolds number
    fRe = (fFlowSpeed * fOverflow_Length) / (fKin_Visc_m * fPsi)

    # Prandtl number
    if fTemp_Dep == 0:
        fPr_m = (fDyn_Visc * fC_p) / fThermal_Conductivity
    else:
        fPr_m = (fKin_Visc_m * fC_p[0]) / fThermal_Conductivity[0]
        fPr_w = (fKin_Visc_w * fC_p[1]) / fThermal_Conductivity[1]

    # Check validity of Reynolds and Prandtl numbers
    if 0 < fRe < 10**6 and 0.6 < fPr_m < 10**3:
        # Nusselt number for laminar flow
        fNu_Laminar = 0.664 * np.sqrt(fRe) * np.cbrt(fPr_m)

        # Nusselt number for turbulent flow
        fNu_Turbulent = (0.037 * (fRe**0.8) * fPr_m) / (1 + 2.443 * (fRe**-0.1) * (fPr_m**(2/3) - 1))

        # Pipe positioning factor
        if fConfig == 2:
            if fs_3 < (fs_1 / 4):
                fFactor_a = 1 + (0.7 / (fPsi**1.5)) * ((fs_2 / fs_1) - 0.3) / (((fs_2 / fs_1) + 0.7)**2)
            else:
                fFactor_a = 1 + (2 * fD_o) / (3 + fs_2)
        elif fConfig == 0:
            fFactor_a = 1 + (0.7 / (fPsi**1.5)) * ((fs_2 / fs_1) - 0.3) / (((fs_2 / fs_1) + 0.7)**2)
        elif fConfig == 1:
            fFactor_a = 1 + (2 * fD_o) / (3 * fs_2)
        else:
            raise ValueError("Invalid input for fConfig")

        # Nusselt number
        fNu = fFactor_a * (0.3 + np.sqrt(fNu_Laminar**2 + fNu_Turbulent**2))
    elif fRe == 0:
        fNu = 0
    else:
        raise ValueError("Reynolds or Prandtl number out of bounds")

    # Temperature-dependent adjustments
    if fTemp_Dep == 1:
        if fPr_m / fPr_w < 1:  # Cooling
            fNu *= (fPr_m / fPr_w)**0.11
        else:  # Heating
            fNu *= (fPr_m / fPr_w)**0.25

    # Convection coefficient
    fConvection_Alpha = (fNu * fThermal_Conductivity[0]) / fOverflow_Length

    return fConvection_Alpha
