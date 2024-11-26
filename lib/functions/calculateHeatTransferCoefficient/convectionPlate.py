def convectionPlate(fLength, fFlowSpeed, fDyn_Visc, fDensity, fThermal_Conductivity, fC_p):
    """
    Returns the convection coefficient alpha for a flow along a plate in W/m²K.
    
    Parameters:
    fLength (float): Length of the plate parallel to flow direction in m.
    fFlowSpeed (float): Flow speed of the fluid in the pipe in m/s.
    fDyn_Visc (list): Dynamic viscosity of the fluid in kg/(m s).
    fDensity (list): Density of the fluid in kg/m³.
    fThermal_Conductivity (list): Thermal conductivity of the fluid in W/(m K).
    fC_p (list): Specific heat capacity of the fluid in J/kg K.
    
    Returns:
    fConvection_alpha (float): Convection coefficient in W/m²K.
    """
    fKin_Visc = fDyn_Visc[0] / fDensity[0]
    fFlowSpeed = abs(fFlowSpeed)

    # Reynolds number
    fRe = (fFlowSpeed * fLength) / fKin_Visc

    # Prandtl number
    fPr = (fDyn_Visc[0] * fC_p[0]) / fThermal_Conductivity[0]

    # Case checks
    if (fRe < 3.2 * 10**5) and (fRe != 0) and (0.01 < fPr) and (fPr < 1000):
        # Correction factor for Prandtl number
        if fPr <= 0.1:
            fCorrection_Pr = 0.72 + (0.91 - 0.72) / (0.1 - 0.01) * (fPr - 0.01)
        elif 0.1 < fPr <= 0.7:
            fCorrection_Pr = 0.91 + (0.99 - 0.91) / (0.7 - 0.1) * (fPr - 0.1)
        elif 0.7 < fPr <= 1:
            fCorrection_Pr = 0.99 + (1.0 - 0.99) / (1 - 0.7) * (fPr - 0.7)
        elif 1 < fPr <= 10:
            fCorrection_Pr = 1 + (1.012 - 1) / (10 - 1) * (fPr - 1)
        elif 10 < fPr <= 100:
            fCorrection_Pr = 1.012 + (1.027 - 1.012) / (100 - 10) * (fPr - 10)
        elif 100 < fPr <= 1000:
            fCorrection_Pr = 1.027 + (1.058 - 1.027) / (1000 - 100) * (fPr - 100)
        # Nusselt number for laminar flow
        fNu = 0.664 * fRe**(1/2) * fPr**(1/3) * fCorrection_Pr

    elif (3.2 * 10**5 < fRe < 10**7) and (fRe != 0) and (0.6 < fPr < 1000):
        # Nusselt number for turbulent flow
        fNu = 0.037 * (fRe**0.8 - 23100) * fPr**(1/3)

    elif fRe == 0:
        # No flow case
        fNu = 0

    else:
        # Out-of-boundary error
        raise ValueError(
            f"Either the Reynolds or the Prandtl number are out of bounds.\n"
            f"Reynolds is valid for Re < 10^7. The value is {fRe}\n"
            f"Prandtl is valid between 0.6 and 10^3. The value is {fPr}\n"
            f"The flow speed is: {fFlowSpeed}\n"
            f"The kinematic viscosity is {fKin_Visc}"
        )

    # Convection coefficient
    fConvection_alpha = (fNu * fThermal_Conductivity[0]) / fLength
    return fConvection_alpha
