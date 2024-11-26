def SAT_3_2(tHX_Parameters, Fluid_1, Fluid_2, fThermalConductivitySolid):
    """
    Calculate the outlet temperatures and pressure drops for a 3-2 shell and tube heat exchanger.

    Parameters:
        tHX_Parameters (dict): Geometric parameters of the heat exchanger.
        Fluid_1 (dict): Properties of fluid 1.
        Fluid_2 (dict): Properties of fluid 2.
        fThermalConductivitySolid (float): Thermal conductivity of the heat exchanger material.

    Returns:
        tuple: fOutlet_Temp_1, fOutlet_Temp_2, fDelta_P_1, fDelta_P_2, fR_alpha_i, fR_alpha_o, fR_lambda
    """

    import math
    from functions import calculateHeatTransferCoefficient, calculateDeltaPressure, HX

    # Area of the window
    fArea_Win = ((tHX_Parameters["fShellDiameter"] / 2) ** 2 * 
                 math.acos(1 - (tHX_Parameters["fBaffleHeight"] / (tHX_Parameters["fShellDiameter"] / 2))) -
                 math.sqrt(tHX_Parameters["fBaffleHeight"] * tHX_Parameters["fShellDiameter"] -
                           tHX_Parameters["fBaffleHeight"] ** 2) *
                 (tHX_Parameters["fShellDiameter"] - tHX_Parameters["fBaffleHeight"]))

    # Assumptions for user inputs specified as unknown ('x')
    if tHX_Parameters["fInnerDiameter"] == 'x' and tHX_Parameters["fOuterDiameter"] != 'x':
        tHX_Parameters["fInnerDiameter"] = tHX_Parameters["fOuterDiameter"] - 0.001
    elif tHX_Parameters["fOuterDiameter"] == 'x' and tHX_Parameters["fInnerDiameter"] != 'x':
        tHX_Parameters["fOuterDiameter"] = tHX_Parameters["fInnerDiameter"] + 0.001
    elif tHX_Parameters["fInnerDiameter"] == 'x' and tHX_Parameters["fOuterDiameter"] == 'x':
        raise ValueError("At least one of fInnerDiameter or fOuterDiameter must be specified.")

    if tHX_Parameters["fBaffleDiameter"] == 'x':
        tHX_Parameters["fBaffleDiameter"] = tHX_Parameters["fShellDiameter"] - (0.01 * tHX_Parameters["fShellDiameter"])

    if tHX_Parameters["fBatchDiameter"] == 'x':
        tHX_Parameters["fBatchDiameter"] = tHX_Parameters["fShellDiameter"] - (0.015 * tHX_Parameters["fShellDiameter"])

    if tHX_Parameters["fHoleDiameter"] == 'x':
        tHX_Parameters["fHoleDiameter"] = tHX_Parameters["fOuterDiameter"] + 0.0005

    if tHX_Parameters["iNumberOfPipesInWindow"] == 'x':
        tHX_Parameters["iNumberOfPipesInWindow"] = int(
            tHX_Parameters["iNumberOfPipes"] * (fArea_Win / (math.pi * (tHX_Parameters["fShellDiameter"] / 2) ** 2))
        )

    if tHX_Parameters["iNumberOfResistancesEndZone"] == 'x':
        tHX_Parameters["iNumberOfResistancesEndZone"] = math.ceil(
            tHX_Parameters["iNumberOfResistances"] /
            ((math.pi * (tHX_Parameters["fShellDiameter"] / 2) ** 2) - fArea_Win) *
            (math.pi * (tHX_Parameters["fShellDiameter"] / 2) ** 2)
        )

    if tHX_Parameters["iNumberOfPipes_Diam"] == 'x':
        tHX_Parameters["iNumberOfPipes_Diam"] = math.floor(
            (tHX_Parameters["fShellDiameter"] + 0.01 + tHX_Parameters["fPerpendicularSpacing"]) /
            (tHX_Parameters["fOuterDiameter"] + tHX_Parameters["fPerpendicularSpacing"])
        )

    if ((math.pi * (tHX_Parameters["fShellDiameter"] / 2) ** 2) -
            (tHX_Parameters["iNumberOfPipes"] * (math.pi * (tHX_Parameters["fOuterDiameter"] / 2) ** 2))) < 0:
        raise ValueError("Shell diameter is smaller than the combined area of the pipes.")

    # Fluid flow speeds
    fFlowSpeed_Fluid1 = Fluid_1["fMassflow"] / (
        (tHX_Parameters["iNumberOfPipes"] / 2) * math.pi * (tHX_Parameters["fInnerDiameter"] / 2) ** 2 * Fluid_1["fDensity"][0]
    )
    fFlowSpeed_Fluid2 = Fluid_2["fMassflow"] / (
        ((math.pi * (tHX_Parameters["fShellDiameter"] / 2) ** 2) -
         (tHX_Parameters["iNumberOfPipes"] * (math.pi * (tHX_Parameters["fOuterDiameter"] / 2) ** 2))) * Fluid_2["fDensity"][0]
    )

    # Heat capacity flows
    fHeat_Capacity_Flow_1 = abs(Fluid_1["fMassflow"]) * Fluid_1["fSpecificHeatCapacity"][0]
    fHeat_Capacity_Flow_2 = abs(Fluid_2["fMassflow"]) * Fluid_2["fSpecificHeatCapacity"][0]

    # Heat exchange area
    fArea = (tHX_Parameters["iNumberOfPipes"] * (math.pi * (tHX_Parameters["fInnerDiameter"] / 2) ** 2))

    # Distance between baffles
    fS_e = tHX_Parameters["fLength"] - tHX_Parameters["fBaffleDistance"]

    # Number of transverse rows and baffles
    tHX_Parameters["iNumberOfPipes_Trans"] = (
        tHX_Parameters["iNumberOfPipes"] - (2 * tHX_Parameters["iNumberOfPipesInWindow"])
    )
    fN_Rows_Trans = tHX_Parameters["iNumberOfPipes_Trans"] / (tHX_Parameters["iNumberOfPipes_Diam"] / 1.5)
    fN_Baffles = 2

    # Outer convection coefficient
    if len(tHX_Parameters) == 21:
        falpha_sheath = calculateHeatTransferCoefficient.convectionSheathCurrent(
            tHX_Parameters["fOuterDiameter"], tHX_Parameters["fBaffleDiameter"],
            tHX_Parameters["fBatchDiameter"], tHX_Parameters["fHoleDiameter"],
            tHX_Parameters["fShellDiameter"], tHX_Parameters["fPerpendicularSpacing"],
            tHX_Parameters["fParallelSpacing"], tHX_Parameters["iNumberOfPipes"],
            tHX_Parameters["iNumberOfPipesInWindow"], tHX_Parameters["iNumberOfResistances"],
            tHX_Parameters["iNumberOfSealings"], tHX_Parameters["iNumberOfPipes_Diam"],
            tHX_Parameters["fBaffleDistance"], tHX_Parameters["fBaffleHeight"],
            fFlowSpeed_Fluid2, Fluid_2["fDynamicViscosity"], Fluid_2["fDensity"],
            Fluid_2["fThermalConductivity"], Fluid_2["fSpecificHeatCapacity"],
            tHX_Parameters["iConfiguration"], tHX_Parameters["fPipeRowOffset"]
        )
    else:
        falpha_sheath = calculateHeatTransferCoefficient.convectionSheathCurrent(
            # Adjust for cases without offset parameter
            ...
        )

    fR_alpha_o = 1 / (fArea * falpha_sheath)

    # Inner convection coefficient
    falpha_pipe = calculateHeatTransferCoefficient.convectionPipe(
        tHX_Parameters["fInnerDiameter"], tHX_Parameters["fLength"], fFlowSpeed_Fluid1,
        Fluid_1["fDynamicViscosity"], Fluid_1["fDensity"],
        Fluid_1["fThermalConductivity"], Fluid_1["fSpecificHeatCapacity"], 0
    )

    fR_alpha_i = 1 / (fArea * falpha_pipe)

    # Thermal resistivity
    fR_lambda = calculateHeatTransferCoefficient.conductionResistance(
        fThermalConductivitySolid, 0, tHX_Parameters["fInnerDiameter"] / 2,
        tHX_Parameters["fOuterDiameter"] / 2, tHX_Parameters["fLength"]
    )

    # Heat exchange coefficient
    fU = 1 / (fArea * (fR_alpha_o + fR_alpha_i + fR_lambda))

    if fU == 0:
        fOutlet_Temp_1 = Fluid_1["fEntryTemperature"]
        fOutlet_Temp_2 = Fluid_2["fEntryTemperature"]
    else:
        fOutlet_Temp_1, fOutlet_Temp_2 = HX.temperature_3_2_sat(
            fArea, fU, fHeat_Capacity_Flow_1, fHeat_Capacity_Flow_2,
            Fluid_1["fEntryTemperature"], Fluid_2["fEntryTemperature"]
        )

    fDelta_P_1_OverPipe = calculateDeltaPressure.Pipe(
        tHX_Parameters["fInnerDiameter"], tHX_Parameters["fLength"], fFlowSpeed_Fluid1,
        Fluid_1["fDynamicViscosity"], Fluid_1["fDensity"], 0
    )
    fDelta_P_1_InOut = calculateDeltaPressure.PipeBundleInletOutlet(
        tHX_Parameters["fInnerDiameter"], tHX_Parameters["fPerpendicularSpacing"],
        tHX_Parameters["fParallelSpacing"], fFlowSpeed_Fluid1,
        Fluid_1["fDynamicViscosity"], Fluid_1["fDensity"]
    )

    fDelta_P_1 = fDelta_P_1_OverPipe + fDelta_P_1_InOut

    if tHX_Parameters["iConfiguration"] == 2:
        tHX_Parameters["iConfiguration_press_loss"] = 1
    else:
        tHX_Parameters["iConfiguration_press_loss"] = tHX_Parameters["iConfiguration"]

    fDelta_P_2 = calculateDeltaPressure.SheathCurrent(
        # Parameters for sheath current pressure loss calculation
        ...
    )

    return fOutlet_Temp_1, fOutlet_Temp_2, fDelta_P_1, fDelta_P_2, fR_alpha_i, fR_alpha_o, fR_lambda
