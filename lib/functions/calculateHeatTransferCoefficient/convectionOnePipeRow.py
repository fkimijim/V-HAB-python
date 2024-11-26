import numpy as np

def convectionOnePipeRow(fD_o, fs_1, fFlowSpeed, fDyn_Visc, fDensity, fThermal_Conductivity, fC_p):
    """
    Returns the convection coefficient alpha for a row of pipes.
    """
    # Differentiating between temperature-dependent and independent material values
    if isinstance(fDyn_Visc, (float, int)):
        fTemp_Dep = 0
    elif isinstance(fDyn_Visc, (list, np.ndarray)) and len(fDyn_Visc) == 2:
        fTemp_Dep = 1
    else:
        raise ValueError('Invalid number of inputs for material values')
    
    fFlowSpeed = abs(fFlowSpeed)
    
    # Definition of the kinematic viscosity
    if fTemp_Dep == 0:
        fKin_Visc_m = fDyn_Visc / fDensity
    elif fTemp_Dep == 1:
        fKin_Visc_m = fDyn_Visc[0] / fDensity[0]
        fKin_Visc_w = fDyn_Visc[1] / fDensity[1]
    
    # Definition of the overflowed length of the pipes
    fOverflow_Length = (np.pi / 2) * fD_o

    # Definition of fPsi
    fPsi = 1 - (np.pi * fD_o) / (4 * fs_1)
    if fPsi < 0:
        raise ValueError('fPsi = 1 - (pi * fD_o)/(4 * fs_1) should not be negative for correct inputs')
    
    # Definition of the Reynolds number
    fRe = (fFlowSpeed * fOverflow_Length) / (fKin_Visc_m * fPsi)

    # Definition of the Prandtl number
    if fTemp_Dep == 0:
        fPr_m = (fDyn_Visc * fC_p) / fThermal_Conductivity
    elif fTemp_Dep == 1:
        fPr_m = (fKin_Visc_m * fC_p[0]) / fThermal_Conductivity[0]
        fPr_w = (fKin_Visc_w * fC_p[1]) / fThermal_Conductivity[1]

    # Calculating Nusselt number and convection coefficient
    if 10 < fRe < 10**6 and 0.6 < fPr_m < 10**3:
        # Laminar case
        fNu_Laminar = 0.664 * np.sqrt(fRe) * np.cbrt(fPr_m)
        # Turbulent case
        fNu_Turbulent = (0.037 * fRe**0.8 * fPr_m) / (1 + 2.443 * fRe**-0.1 * (fPr_m**(2/3) - 1))
        # Combined Nusselt number
        fNu = 0.3 + np.sqrt(fNu_Laminar**2 + fNu_Turbulent**2)

    elif fRe == 0:
        fNu = 0
    else:
        raise ValueError(f'Reynolds or Prandtl number out of bounds.\n'
                         f'Reynolds: {fRe} (valid: 10 to 10^6)\n'
                         f'Prandtl: {fPr_m} (valid: 0.6 to 10^3)\n'
                         f'Flow speed: {fFlowSpeed}\n'
                         f'Kinematic viscosity: {fKin_Visc_m}')
    
    if fTemp_Dep == 1:
        # Adjust Nusselt number for temperature-dependent material values
        if fPr_m / fPr_w < 1:  # Cooling
            fNu *= (fPr_m / fPr_w)**0.11
        else:  # Heating
            fNu *= (fPr_m / fPr_w)**0.25
    
    # Convection coefficient
    fConvection_alpha = (fNu * fThermal_Conductivity[0]) / fOverflow_Length
    return fConvection_alpha
