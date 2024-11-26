import numpy as np
from scipy.interpolate import interp1d, RegularGridInterpolator

def find_property(self, t_parameters):
    """
    Helper method to find substance properties in the matter table.

    Args:
        t_parameters (dict): Input parameters including:
            Mandatory:
                - sSubstance (str): Substance name (e.g., 'CO2').
                - sProperty (str): Desired property (e.g., 'Pressure').
                - sFirstDepName (str): First dependency name.
                - fFirstDepValue (float): Value of the first dependency.
                - sPhaseType (str): Phase type ('solid', 'liquid', 'gas', 'supercritical').
            Optional:
                - sSecondDepName (str): Second dependency name.
                - fSecondDepValue (float): Value of the second dependency.
                - bUseIsobaricData (bool): Use isobaric data if True; otherwise, use isochoric data.

    Returns:
        float: The interpolated or nearest valid property value.
    """
    # Extract and validate mandatory parameters
    s_substance = t_parameters["sSubstance"]
    s_property = t_parameters["sProperty"]
    s_first_dep_name = t_parameters["sFirstDepName"]
    f_first_dep_value = t_parameters["fFirstDepValue"]
    s_phase_type = t_parameters["sPhaseType"]

    if not all(isinstance(param, str) for param in [s_substance, s_property, s_first_dep_name, s_phase_type]):
        raise ValueError("Substance, property, dependency name, and phase type must be strings.")
    if not isinstance(f_first_dep_value, (int, float)):
        raise ValueError("First dependency value must be numeric.")

    # Optional parameters
    s_second_dep_name = t_parameters.get("sSecondDepName")
    f_second_dep_value = t_parameters.get("fSecondDepValue")
    b_use_isobaric_data = t_parameters.get("bUseIsobaricData", True)

    i_dependencies = 2 if s_second_dep_name and f_second_dep_value else 1

    if not isinstance(b_use_isobaric_data, bool):
        raise ValueError("Isobaric data selector must be a boolean.")

    # Fetch matter data for the substance
    tx_matter_for_substance = self.ttx_matter[s_substance]

    # Determine the type of data
    s_type_struct = "tIsobaricData" if b_use_isobaric_data else "tIsochoricData"
    s_property = f"Isobaric {s_property}" if b_use_isobaric_data and s_property == "Heat Capacity" else s_property

    s_phase_struct_name = {
        "solid": "tSolid",
        "liquid": "tLiquid",
        "gas": "tGas",
        "supercritical": "tSupercritical"
    }.get(s_phase_type)

    if not s_phase_struct_name:
        raise ValueError(f"Invalid phase type: {s_phase_type}")

    tx_matter_for_substance_and_type = tx_matter_for_substance[s_type_struct]
    tx_matter_for_substance_and_type_and_aggregate = tx_matter_for_substance_and_type[s_phase_struct_name]

    # Find the column of the desired property
    i_column = tx_matter_for_substance_and_type["tColumns"].get(s_property.replace(" ", ""))
    if i_column is None:
        raise ValueError(f"Cannot find property {s_property} for substance {s_substance}.")

    # First dependency handling
    s_first_dep_name_no_spaces = s_first_dep_name.replace(" ", "")
    i_column_first = tx_matter_for_substance_and_type["tColumns"].get(s_first_dep_name_no_spaces)
    if i_column_first is None:
        raise ValueError(f"Cannot find dependency {s_first_dep_name} for substance {s_substance}.")

    f_min = tx_matter_for_substance_and_type_and_aggregate["ttExtremes"][f"t{s_first_dep_name_no_spaces}"]["Min"]
    f_max = tx_matter_for_substance_and_type_and_aggregate["ttExtremes"][f"t{s_first_dep_name_no_spaces}"]["Max"]

    if f_first_dep_value > f_max:
        f_first_dep_value = f_max
    elif f_first_dep_value < f_min:
        f_first_dep_value = f_min

    if i_dependencies == 1:
        af_temporary = tx_matter_for_substance_and_type_and_aggregate["mfData"][:, [i_column, i_column_first]]
        af_temporary = af_temporary[~np.isnan(af_temporary).any(axis=1)]
        af_temporary = np.unique(af_temporary, axis=0)

        h_interpolation = interp1d(af_temporary[:, 1], af_temporary[:, 0], bounds_error=False, fill_value="extrapolate")
        f_property = h_interpolation(f_first_dep_value)

    else:
        s_second_dep_name_no_spaces = s_second_dep_name.replace(" ", "")
        i_column_second = tx_matter_for_substance_and_type["tColumns"].get(s_second_dep_name_no_spaces)
        if i_column_second is None:
            raise ValueError(f"Cannot find dependency {s_second_dep_name} for substance {s_substance}.")

        f_min = tx_matter_for_substance_and_type_and_aggregate["ttExtremes"][f"t{s_second_dep_name_no_spaces}"]["Min"]
        f_max = tx_matter_for_substance_and_type_and_aggregate["ttExtremes"][f"t{s_second_dep_name_no_spaces}"]["Max"]

        if f_second_dep_value > f_max:
            f_second_dep_value = f_max
        elif f_second_dep_value < f_min:
            f_second_dep_value = f_min

        af_temporary = tx_matter_for_substance_and_type_and_aggregate["mfData"][:, [i_column, i_column_first, i_column_second]]
        af_temporary = af_temporary[~np.isnan(af_temporary).any(axis=1)]
        af_temporary = np.unique(af_temporary, axis=0)

        h_interpolation = RegularGridInterpolator(
            (af_temporary[:, 1], af_temporary[:, 2]), af_temporary[:, 0], bounds_error=False, fill_value=None
        )
        f_property = h_interpolation([f_first_dep_value, f_second_dep_value])

    if f_property is None or np.isnan(f_property):
        raise ValueError(f"No valid value for {s_property} of {s_substance} in {s_phase_type} phase.")

    return f_property
