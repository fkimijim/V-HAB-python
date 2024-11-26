import math

def PipeBundle(fD_o, fs_1, fs_2, fN_Rows, fFlowSpeed, fDyn_Visc, fDensity, fConfig):
    """
    Calculate the pressure loss for a pipe bundle in N/m² (Pa).

    Args:
        fD_o: Outer hydraulic diameter of the pipes in m.
        fs_1: Distance between the centers of two adjacent pipes perpendicular to the flow direction in m.
        fs_2: Distance between the centers of two adjacent pipes in the flow direction in m.
        fN_Rows: Number of pipe rows.
        fFlowSpeed: Flow speed of the fluid in the pipe in m/s.
        fDyn_Visc: Dynamic viscosity of the fluid in kg/(m s). Can be a list for temperature dependency.
        fDensity: Density of the fluid in kg/m³. Can be a list for temperature dependency.
        fConfig: Pipe configuration (0 = aligned, 1 = shifted).

    Returns:
        fDelta_Pressure: Pressure loss in N/m².
    """
    if len(fDyn_Visc) == 2 and fConfig == 0:
        fConfig = 2
    elif len(fDyn_Visc) == 2 and fConfig == 1:
        fConfig = 3

    fKin_Visc_m = fDyn_Visc[0] / fDensity[0]

    # Overflowed length of the pipes
    fOverflow_Length = (math.pi / 2) * fD_o

    # Calculate fPsi
    if fs_2 / fD_o >= 1:
        fPsi = 1 - (math.pi * fD_o) / (4 * fs_1)
    else:
        fPsi = 1 - (math.pi * fD_o**2) / (4 * fs_1 * fs_2)

    # Reynolds number
    fFlowSpeed = abs(fFlowSpeed)
    fRe = (fFlowSpeed * fOverflow_Length) / (fKin_Visc_m * fPsi)

    # Laminar friction factor
    if fConfig in [0, 2]:
        fFriction_Factor_Lam = (280 * math.pi * (((fs_2 / fD_o)**0.5 - 0.6)**2 + 0.75)) / \
                               (fRe * (4 * (fs_1 * fs_2 / (fD_o**2)) - math.pi) * (fs_1 / fD_o)**1.6)
    elif fConfig in [1, 3]:
        if fs_2 / fD_o >= 0.5 * math.sqrt(2 * fs_1 / fD_o + 1):
            fFriction_Factor_Lam = (280 * math.pi * (((fs_2 / fD_o)**0.5 - 0.6)**2 + 0.75)) / \
                                   (fRe * (4 * (fs_1 * fs_2 / (fD_o**2)) - math.pi) * (fs_1 / fD_o)**1.6)
        else:
            fFriction_Factor_Lam = (280 * math.pi * (((fs_2 / fD_o)**0.5 - 0.6)**2 + 0.75)) / \
                                   (fRe * (4 * (fs_1 * fs_2 / (fD_o**2)) - math.pi) *
                                   (math.sqrt((fs_1 / (2 * fD_o))**2 + (fs_2 / fD_o)**2))**1.6)

    # Turbulent friction factor
    if fConfig in [0, 2]:
        fFriction_Factor_Turb = ((0.22 + 1.2 * ((1 - 0.94 * fD_o / fs_2)**0.6) /
                                  (((fs_1 / fD_o) - 0.85)**1.3)) *
                                 10**(0.47 * (fs_2 / fs_1 - 1.5)) +
                                 (0.03 * (fs_1 / fD_o - 1) * (fs_2 / fD_o - 1))) / (fRe**(0.1 * fs_2 / fs_1))
    elif fConfig in [1, 3]:
        fFriction_Factor_Turb = (2.5 + (1.2 / ((fs_1 / fD_o - 0.85)**1.08)) +
                                 0.4 * (fs_2 / fs_1 - 1)**3 - 0.01 * (fs_1 / fs_2 - 1)**3) / (fRe**(0.1 * fs_2 / fs_1))

    # Temperature dependency factors
    if fConfig in [2, 3] and fN_Rows > 9:
        fLaminar_Factor = (fDyn_Visc[1] / fDyn_Visc[0])**(0.57 / (((4 * fs_1 * fs_2 / (math.pi * fD_o**2) - 1) * fRe)**0.25))
        fTemp_Turb_Factor = (fDyn_Visc[1] / fDyn_Visc[0])**0.14
    elif fConfig in [2, 3] and fN_Rows <= 9:
        fLaminar_Factor = (fDyn_Visc[1] / fDyn_Visc[0])**(0.57 * ((fN_Rows / 10)**0.25) /
                                                         (((4 * fs_1 * fs_2 / (math.pi * fD_o**2) - 1) * fRe)**0.25))
        fTemp_Turb_Factor = (fDyn_Visc[1] / fDyn_Visc[0])**0.14
    else:
        fLaminar_Factor = 1
        fTemp_Turb_Factor = 1

    # Turbulent flow factor for number of rows
    if fConfig in [1, 3] and (fs_2 / fD_o) < 0.5 * math.sqrt(2 * fs_1 / fD_o + 1):
        fFriction_Factor_0 = (2 * (math.sqrt((fs_1 / (2 * fD_o))**2 + (fs_2 / fD_o)**2) - 1)) / \
                             (fs_1 / fD_o * (fs_1 / fD_o - 1))
    else:
        fFriction_Factor_0 = (fD_o**2) / (fs_1**2)

    if 4 < fN_Rows < 10:
        fRow_Turb_Factor = fFriction_Factor_0 * (1 / fN_Rows - 1 / 10)
    else:
        fRow_Turb_Factor = 0

    # Combined friction factor
    if fConfig in [0, 2]:
        fFriction_Factor = fFriction_Factor_Lam * fLaminar_Factor + \
                           (fFriction_Factor_Turb * fTemp_Turb_Factor + fRow_Turb_Factor) * \
                           (1 - math.exp(-(fRe + 1000) / 2000))
    elif fConfig in [1, 3]:
        fFriction_Factor = fFriction_Factor_Lam * fLaminar_Factor + \
                           (fFriction_Factor_Turb * fTemp_Turb_Factor + fRow_Turb_Factor) * \
                           (1 - math.exp(-(fRe + 200) / 2000))
    else:
        raise ValueError("Invalid fConfig value in pressure_loss_pipe_bundle")

    # Number of resistances
    if fConfig in [1, 3] and (fs_2 / fD_o) < 0.5 * math.sqrt(2 * fs_1 / fD_o + 1):
        fN_Resistances = fN_Rows - 1
    else:
        fN_Resistances = fN_Rows

    # Pressure loss
    fDelta_Pressure = fFriction_Factor * fN_Resistances * (fDensity[0] * fFlowSpeed**2) / 2

    return fDelta_Pressure
