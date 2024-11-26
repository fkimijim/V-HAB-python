def cross(tHX_Parameters, Fluid_1, Fluid_2, fThermalConductivitySolid):
    """
    Calculate outlet temperatures and pressure drops for a heat exchanger.

    Parameters:
    - tHX_Parameters: Dictionary with geometric and configuration information.
    - Fluid_1: Dictionary containing properties of fluid 1 (inside the pipe).
    - Fluid_2: Dictionary containing properties of fluid 2 (outside the pipe).
    - fThermalConductivitySolid: Thermal conductivity of the solid material.

    Returns:
    - fOutlet_Temp_1: Outlet temperature of Fluid 1.
    - fOutlet_Temp_2: Outlet temperature of Fluid 2.
    - fDelta_P_1: Pressure drop for Fluid 1.
    - fDelta_P_2: Pressure drop for Fluid 2.
    - fR_alpha_i: Thermal resistance from convection on the inside.
    - fR_alpha_o: Thermal resistance from convection on the outside.
    - fR_lambda: Thermal resistance from conduction.
    """

    if tHX_Parameters["iNumberOfRows"] > 0:
        # Flow speeds
        fFlowSpeed_Fluid1 = Fluid_1["fMassflow"] / (
            tHX_Parameters["iNumberOfPipes"]
            * math.pi
            * (tHX_Parameters["fInnerDiameter"] / 2) ** 2
            * Fluid_1["fDensity"][0]
        )
        fFlowSpeed_Fluid2 = Fluid_2["fMassflow"] / (
            (
                (tHX_Parameters["fPerpendicularSpacing"] - tHX_Parameters["fInnerDiameter"])
                * tHX_Parameters["fLength"]
                * (tHX_Parameters["iNumberOfPipes"] / tHX_Parameters["iNumberOfRows"])
            )
            * Fluid_2["fDensity"][0]
        )

        # Heat capacity flows
        fHeat_Capacity_Flow_1 = abs(Fluid_1["fMassflow"]) * Fluid_1["fSpecificHeatCapacity"][0]
        fHeat_Capacity_Flow_2 = abs(Fluid_2["fMassflow"]) * Fluid_2["fSpecificHeatCapacity"][0]

        # Heat exchange area
        fArea = tHX_Parameters["iNumberOfPipes"] * math.pi * (tHX_Parameters["fInnerDiameter"] / 2) ** 2

        # Pressure loss for Fluid 1
        fDelta_P_1_OverPipe = calculate_pressure_loss_pipe(
            tHX_Parameters["fInnerDiameter"],
            tHX_Parameters["fLength"],
            fFlowSpeed_Fluid1,
            Fluid_1["fDynamicViscosity"],
            Fluid_1["fDensity"],
            0,
        )
        fDelta_P_1_InOut = calculate_pressure_loss_pipe_bundle_inlet_outlet(
            tHX_Parameters["fInnerDiameter"],
            tHX_Parameters["fPerpendicularSpacing"],
            tHX_Parameters["fParallelSpacing"],
            fFlowSpeed_Fluid1,
            Fluid_1["fDynamicViscosity"],
            Fluid_1["fDensity"],
        )
        fDelta_P_1 = fDelta_P_1_OverPipe + fDelta_P_1_InOut

        # Pressure loss for Fluid 2
        if tHX_Parameters["iConfiguration"] == 0:
            fDelta_P_2 = calculate_pressure_loss_pipe_bundle(
                tHX_Parameters["fOuterDiameter"],
                tHX_Parameters["fPerpendicularSpacing"],
                tHX_Parameters["fParallelSpacing"],
                tHX_Parameters["iNumberOfRows"],
                fFlowSpeed_Fluid2,
                Fluid_2["fDynamicViscosity"],
                Fluid_2["fDensity"],
                0,
            )
        elif tHX_Parameters["iConfiguration"] in [1, 2]:
            fDelta_P_2 = calculate_pressure_loss_pipe_bundle(
                tHX_Parameters["fOuterDiameter"],
                tHX_Parameters["fPerpendicularSpacing"],
                tHX_Parameters["fParallelSpacing"],
                tHX_Parameters["iNumberOfRows"],
                fFlowSpeed_Fluid2,
                Fluid_2["fDynamicViscosity"],
                Fluid_2["fDensity"],
                1,
            )
        else:
            raise ValueError("Invalid input for tHX_Parameters.iConfiguration")

    elif tHX_Parameters["iNumberOfRows"] == 0:
        # Flow speeds for plate heat exchanger
        fFlowSpeed_Fluid1 = Fluid_1["fMassflow"] / (
            tHX_Parameters["fHeight_1"] * tHX_Parameters["fBroadness"] * Fluid_1["fDensity"][0]
        )
        fFlowSpeed_Fluid2 = Fluid_2["fMassflow"] / (
            tHX_Parameters["fHeight_2"] * tHX_Parameters["fBroadness"] * Fluid_2["fDensity"][0]
        )

        # Heat capacity flows
        fHeat_Capacity_Flow_1 = abs(Fluid_1["fMassflow"]) * Fluid_1["fSpecificHeatCapacity"][0]
        fHeat_Capacity_Flow_2 = abs(Fluid_2["fMassflow"]) * Fluid_2["fSpecificHeatCapacity"][0]

        # Heat exchange area
        fArea = tHX_Parameters["fBroadness"] * tHX_Parameters["fLength"]

        # Convection coefficients
        falpha_o = calculate_convection_coefficient_plate(
            tHX_Parameters["fLength"],
            fFlowSpeed_Fluid1,
            Fluid_1["fDynamicViscosity"],
            Fluid_1["fDensity"],
            Fluid_1["fThermalConductivity"],
            Fluid_1["fSpecificHeatCapacity"],
        )
        falpha_pipe = calculate_convection_coefficient_plate(
            tHX_Parameters["fLength"],
            fFlowSpeed_Fluid2,
            Fluid_2["fDynamicViscosity"],
            Fluid_2["fDensity"],
            Fluid_2["fThermalConductivity"],
            Fluid_2["fSpecificHeatCapacity"],
        )

        # Conduction resistance
        fR_lambda = calculate_conduction_resistance(
            fThermalConductivitySolid,
            2,
            fArea,
            tHX_Parameters["fThickness"],
            tHX_Parameters["fLength"],
        )

        # Pressure losses
        fDelta_P_1 = calculate_pressure_loss_pipe(
            (4 * tHX_Parameters["fBroadness"] * tHX_Parameters["fHeight_1"])
            / (2 * tHX_Parameters["fBroadness"] + 2 * tHX_Parameters["fHeight_1"]),
            tHX_Parameters["fLength"],
            fFlowSpeed_Fluid1,
            Fluid_1["fDynamicViscosity"],
            Fluid_1["fDensity"],
            0,
        )
        fDelta_P_2 = calculate_pressure_loss_pipe(
            (4 * tHX_Parameters["fBroadness"] * tHX_Parameters["fHeight_2"])
            / (2 * tHX_Parameters["fBroadness"] + 2 * tHX_Parameters["fHeight_2"]),
            tHX_Parameters["fLength"],
            fFlowSpeed_Fluid2,
            Fluid_2["fDynamicViscosity"],
            Fluid_2["fDensity"],
            1,
        )

    else:
        raise ValueError("Number of pipe rows cannot be negative")

    # Calculate thermal resistances
    fR_alpha_i = 1 / (fArea * falpha_pipe)
    fR_alpha_o = 1 / (fArea * falpha_o)

    # Heat exchange coefficient
    fU = 1 / (fArea * (fR_alpha_o + fR_alpha_i + fR_lambda))

    # Heat transfer and outlet temperatures
    if fU == 0:
        fOutlet_Temp_1 = Fluid_1["fEntryTemperature"]
        fOutlet_Temp_2 = Fluid_2["fEntryTemperature"]
    else:
        fOutlet_Temp_1, fOutlet_Temp_2 = calculate_temperature_crossflow(
            tHX_Parameters["iNumberOfRows"],
            fArea,
            fU,
            fHeat_Capacity_Flow_1,
            fHeat_Capacity_Flow_2,
            Fluid_1["fEntryTemperature"],
            Fluid_2["fEntryTemperature"],
        )

    return fOutlet_Temp_1, fOutlet_Temp_2, fDelta_P_1, fDelta_P_2, fR_alpha_i, fR_alpha_o, fR_lambda


# Placeholder functions for calculations
def calculate_pressure_loss_pipe(*args):
    return 0.0


def calculate_pressure_loss_pipe_bundle_inlet_outlet(*args):
    return 0.0


def calculate_pressure_loss_pipe_bundle(*args):
    return 0.0


def calculate_convection_coefficient_plate(*args):
    return 1.0


def calculate_conduction_resistance(*args):
    return 1.0


def calculate_temperature_crossflow(*args):
    return args[4], args[5]
