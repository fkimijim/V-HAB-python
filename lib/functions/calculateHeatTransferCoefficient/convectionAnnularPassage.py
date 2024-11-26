import math

def convectionAnnularPassage(fD_i, fD_o, fLength, fFlowSpeed, fDyn_Visc, 
                              fDensity, fThermal_Conductivity, fC_p, fConfig):
    """
    Returns the convection coefficient alpha for an annular passage 
    between two pipes in W/m²K.

    Parameters:
    - fD_i: Outer diameter of the inner pipe in m
    - fD_o: Inner diameter of the outer pipe in m
    - fLength: Length of the pipe in m
    - fFlowSpeed: Flow speed of the fluid in the pipe in m/s
    - fDyn_Visc: Dynamic viscosity of the fluid in kg/(m·s)
    - fDensity: Density of the fluid in kg/m³
    - fThermal_Conductivity: Thermal conductivity of the fluid in W/(m·K)
    - fC_p: Heat capacity of the fluid in J/(kg·K)
    - fConfig: Configuration parameter (0: disturbed flow, 1: non-disturbed flow)

    Returns:
    - fConvection_Alpha: Convection coefficient in W/m²K
    """
    # Determine configuration for temperature-dependent material values
    if len(fDyn_Visc) == 2:
        fConfig += 2

    fFlowSpeed = abs(fFlowSpeed)

    # Kinematic viscosity
    fKin_Visc_m = fDyn_Visc[0] / fDensity[0]

    # Hydraulic diameter
    fD_Hydraulic = fD_o - fD_i

    # Reynolds number
    fRe = (fFlowSpeed * fD_Hydraulic) / fKin_Visc_m

    # Prandtl number
    if fConfig in [0, 1]:
        fPr_m = (fDyn_Visc * fC_p) / fThermal_Conductivity
    else:
        fPr_m = (fDyn_Visc[0] * fC_p[0]) / fThermal_Conductivity[0]
        fPr_w = (fDyn_Visc[1] * fC_p[1]) / fThermal_Conductivity[1]

    # Cases for laminar flow, turbulent flow, transient area, or zero flow speed
    if fRe < 2300 and fRe != 0:
        # Laminar flow
        fNu_1 = 3.66 + 1.2 * (fD_i / fD_o) ** -0.8
        fNu_2 = 1.615 * (1 + 0.14 * (fD_i / fD_o) ** -0.5) * (fRe * fPr_m * (fD_Hydraulic / fLength) ** (1/3))
        fNu_3 = (2 / (1 + 22 * fPr_m)) ** (1/6) * (fRe * fPr_m * (fD_i / fLength) ** 0.5) if fConfig == 1 else 0
        fNu = (fNu_1**3 + fNu_2**3 + fNu_3**3)**(1/3)
    elif 1e4 < fRe < 1e6 and 0.6 < fPr_m < 1000:
        # Turbulent flow
        fFriction_Coeff = (1.8 * math.log10(fRe) - 1.5) ** -2
        fNu_pipe = ((fFriction_Coeff / 8) * fRe * fPr_m) / (1 + 12.7 * math.sqrt(fFriction_Coeff / 8) * (fPr_m ** (2/3) - 1)) * (1 + (fD_Hydraulic / fLength) ** (2/3))
        fNu = fNu_pipe * 0.86 * (fD_i / fD_o) ** -0.16
    elif 2300 <= fRe <= 1e4 and 0.6 < fPr_m < 1000:
        # Transient area
        fInterpolation_Factor = (fRe - 2300) / (1e4 - 2300)
        fNu_1 = 3.66 + 1.2 * (fD_i / fD_o) ** -0.8
        fNu_2 = 1.615 * (1 + 0.14 * (fD_i / fD_o) ** -0.5) * (fRe * fPr_m * (fD_Hydraulic / fLength) ** (1/3))
        fNu_3 = (2 / (1 + 22 * fPr_m)) ** (1/6) * (fRe * fPr_m * (fD_i / fLength) ** 0.5) if fConfig == 1 else 0
        fNu_Laminar = (fNu_1**3 + fNu_2**3 + fNu_3**3)**(1/3)
        fFriction_Coeff = (1.8 * math.log10(fRe) - 1.5) ** -2
        fNu_pipe = ((fFriction_Coeff / 8) * fRe * fPr_m) / (1 + 12.7 * math.sqrt(fFriction_Coeff / 8) * (fPr_m ** (2/3) - 1)) * (1 + (fD_Hydraulic / fLength) ** (2/3))
        fNu_Turbulent = fNu_pipe * 0.86 * (fD_i / fD_o) ** -0.16
        fNu = (1 - fInterpolation_Factor) * fNu_Laminar + fInterpolation_Factor * fNu_Turbulent
    elif fRe == 0:
        fNu = 0
    else:
        raise ValueError(f"Invalid Reynolds or Prandtl number: Re={fRe}, Pr_m={fPr_m}")

    # Adjust for temperature-dependent material values
    if fConfig in [2, 3]:
        fNu *= (fPr_m / fPr_w) ** 0.11

    # Convection coefficient
    fConvection_Alpha = (fNu * fThermal_Conductivity[0]) / fD_Hydraulic
    return fConvection_Alpha
