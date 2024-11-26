import math

def Pipe(fD_Hydraulic, fLength, fFlowSpeed, fDyn_Visc, fDensity, fRoughness=0, fConfig=0, fD_o=None):
    """
    Calculate the pressure loss for a pipe in N/m² (Pa).

    Args:
        fD_Hydraulic: Inner hydraulic diameter of the pipe in m.
        fLength: Length of the pipe in m.
        fFlowSpeed: Flow speed of the fluid in the pipe in m/s.
        fDyn_Visc: Dynamic viscosity of the fluid in kg/(m s).
        fDensity: Density of the fluid in kg/m³.
        fRoughness: Surface roughness K of the pipe in m (default: 0).
        fConfig: Configuration parameter (default: 0).
            0 = round pipe.
            1 = square pipe.
            2 = annular passage (requires fD_o).
        fD_o: Inner diameter of the outer pipe in m (required if fConfig = 2).

    Returns:
        fDelta_Pressure: Pressure loss in N/m².
    """
    # Kinematic viscosity
    fKin_Visc_m = fDyn_Visc / fDensity

    # Reynolds number
    fFlowSpeed = abs(fFlowSpeed)
    fRe = (fFlowSpeed * fD_Hydraulic) / fKin_Visc_m

    # Friction factor calculation
    if fRe < 2320:  # Laminar flow
        if fConfig == 0:  # Round pipe
            fFriction_Factor = 64 / fRe
        elif fConfig == 1:  # Square pipe
            fFriction_Factor = 0.89 * 64 / fRe
        elif fConfig == 2:  # Annular passage
            if fD_o is None:
                raise ValueError("fD_o is required for annular passage configuration (fConfig = 2).")
            fD_i = fD_o - fD_Hydraulic
            fRatio = fD_o / fD_i
            if 1 < fRatio < 2:
                fFriction_Factor = 1.5 * 64 / fRe
            elif 2 <= fRatio < 9:
                fFriction_Factor = (1.5 + (1.4 - 1.5) / (9 - 2) * (fRatio - 2)) * 64 / fRe
            elif 9 <= fRatio < 40:
                fFriction_Factor = (1.4 + (1.3 - 1.4) / (40 - 9) * (fRatio - 9)) * 64 / fRe
            elif 40 <= fRatio < 100:
                fFriction_Factor = (1.3 + (1.25 - 1.3) / (100 - 40) * (fRatio - 40)) * 64 / fRe
            else:
                raise ValueError("fD_o/fD_i ratio larger than 100 is not supported.")
        else:
            raise ValueError("Invalid fConfig value.")
    elif fRoughness == 0:  # Smooth pipe
        if 2320 <= fRe < 100000:
            fFriction_Factor = 0.3164 / (fRe ** 0.25)
            if fRe < 3320:  # Smooth transition
                fFriction_Factor = ((64 / 2320) * (3320 - fRe) / 1000) + (fFriction_Factor * (fRe - 2320) / 1000)
        elif 100000 <= fRe < 1e6:
            fFriction_Factor = (1.8 * math.log10(fRe) - 1.5) ** -2
        elif fRe >= 1e6:
            fFriction_Factor = (1 / (1.819 * math.log10(fRe) - 1.64)) ** 2
        else:
            raise ValueError(f"Reynolds number out of bounds: {fRe}")
    else:  # Rough pipe
        fLimitEpsilon = (-9.990299708991270e-11 * fRe) + 0.050001498544956
        fEpsilon = fRoughness / fD_Hydraulic
        if fEpsilon > fLimitEpsilon:
            fFriction_Factor = (1 / (2 * math.log10(fD_Hydraulic / fRoughness) + 1.14)) ** 2
        else:
            # Colebrook equation
            X1 = (fRoughness / fD_Hydraulic) * fRe * 0.123968186335417556
            X2 = math.log(fRe) - 0.779397488455682028
            fFriction_Factor = X2 - 0.2
            for _ in range(2):  # Two iterations for high accuracy
                E = (math.log(X1 + fFriction_Factor) - 0.2) / (1 + X1 + fFriction_Factor)
                fFriction_Factor -= (1 + X1 + fFriction_Factor + 0.5 * E) * E * (X1 + fFriction_Factor) / (
                    1 + X1 + fFriction_Factor + E * (1 + E / 3))
            fFriction_Factor = (1.151292546497022842 / fFriction_Factor) ** 2
            if fRe < 3320:  # Smooth transition
                fFriction_Factor = ((64 / 2320) * (3320 - fRe) / 1000) + (fFriction_Factor * (fRe - 2320) / 1000)

    # Pressure loss calculation
    if fFlowSpeed == 0:
        fDelta_Pressure = 0
    else:
        fDelta_Pressure = fFriction_Factor * fLength / fD_Hydraulic * (fDensity * fFlowSpeed ** 2) / 2

    return fDelta_Pressure
