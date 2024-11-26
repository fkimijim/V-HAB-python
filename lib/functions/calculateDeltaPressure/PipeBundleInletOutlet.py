import math

def PipeBundleInletOutlet(fD_i, fs_1, fs_2, fFlowSpeed, fDyn_Visc, fDensity):
    """
    Calculate the pressure loss for the in- and outlet of a pipe bundle in N/m² (Pa).

    Args:
        fD_i: Inner hydraulic diameter of the pipes in m.
        fs_1: Distance between the center of two pipes next to each other perpendicular to flow direction in m.
        fs_2: Distance between the center of two pipes next to each other in flow direction in m.
        fFlowSpeed: Flow speed of the fluid in the pipe in m/s.
        fDyn_Visc: Dynamic viscosity of the fluid in kg/(m s). Can be a list for temperature dependency.
        fDensity: Density of the fluid in kg/m³. Can be a list for temperature dependency.

    Returns:
        fDelta_Pressure: Total pressure loss in N/m².
    """
    # Definition of the kinematic viscosity
    fKin_Visc_m = fDyn_Visc[0] / fDensity[0]

    # Reynolds number
    fFlowSpeed = abs(fFlowSpeed)
    fRe = (fFlowSpeed * fD_i) / fKin_Visc_m

    # Area relation between supply pipe and pipe bundle
    fArea_Relation = (math.pi / 4) * (fD_i**2 / (fs_1 * fs_2))

    # Interpolation for the friction factor at the inlet of the bundle
    if fRe < 2000:
        fFriction_Factor = 1.1 - 0.4 * fArea_Relation
    elif 2000 <= fRe < 10000:
        fFriction_Factor = 0.55 - 0.4 * fArea_Relation
    elif 10000 <= fRe < 1000000:
        fFriction_Factor = 0.5 - 0.4 * fArea_Relation
    elif fRe >= 1000000:
        fFriction_Factor = 0.4 - 0.4 * fArea_Relation
    else:
        raise ValueError("Invalid Reynolds number range for interpolation.")

    # Pressure loss at the inlet of the bundle
    fDelta_Pressure_In = fFriction_Factor * (fDensity[0] * fFlowSpeed**2) / 2

    # Pressure loss at the outlet of the bundle
    fDelta_Pressure_Out = ((1 - fArea_Relation)**2) * (fDensity[0] * fFlowSpeed**2) / 2

    # Total pressure loss
    fDelta_Pressure = fDelta_Pressure_In + fDelta_Pressure_Out

    return fDelta_Pressure
