import numpy as np

def find_closest_valid_matter_entry(self, t_parameters):
    """
    Find the closest valid value for the demanded property stored in the matter table.
    Does not use interpolation but looks for the closest valid value.

    Args:
        t_parameters (dict): Dictionary containing the necessary parameters.
            Mandatory:
                - sSubstance (str): Name of the substance.
                - sProperty (str): Desired property.
                - sFirstDepName (str): Name of the first dependency.
                - fFirstDepValue (float): Value of the first dependency.
                - sPhaseType (str): Phase type ('solid', 'liquid', 'gas', 'supercritical').
            Optional:
                - sSecondDepName (str): Name of the second dependency.
                - fSecondDepValue (float): Value of the second dependency.
                - bUseIsobaricData (bool): Use isobaric data if True; otherwise, use isochoric data.

    Returns:
        float: Closest matching value for the demanded property.
    """
    # Input validation
    s_substance = t_parameters["sSubstance"]
    if not isinstance(s_substance, str):
        raise ValueError("Substance name must be a string.")

    s_property = t_parameters["sProperty"]
    if not isinstance(s_property, str):
        raise ValueError("Property name must be a string.")

    s_first_dep_name = t_parameters["sFirstDepName"]
    if not isinstance(s_first_dep_name, str):
        raise ValueError("First dependency name must be a string.")

    f_first_dep_value = t_parameters["fFirstDepValue"]
    if not isinstance(f_first_dep_value, (int, float)):
        raise ValueError("First dependency value must be numeric.")

    s_phase_type = t_parameters["sPhaseType"]
    if not isinstance(s_phase_type, str):
        raise ValueError("Phase type must be a string.")

    # Optional parameters
    s_second_dep_name = t_parameters.get("sSecondDepName")
    f_second_dep_value = t_parameters.get("fSecondDepValue")
    b_use_isobaric_data = t_parameters.get("bUseIsobaricData", True)

    i_dependencies = 2 if s_second_dep_name and f_second_dep_value else 1

    if not isinstance(b_use_isobaric_data, bool):
        raise ValueError("Isobaric data selector must be a boolean.")

    tx_matter_for_substance = self.ttx_matter[s_substance]

    # Determine the type of data
    if tx_matter_for_substance["bIndividualFile"]:
        s_type_struct = "tIsobaricData" if b_use_isobaric_data else "tIsochoricData"
        if s_property == "Heat Capacity":
            s_property = "Isobaric Heat Capacity" if b_use_isobaric_data else "Isochoric Heat Capacity"
    else:
        raise ValueError("Non-individual files are not supported in this implementation.")

    s_phase_struct_name = {
        "solid": "tSolid",
        "liquid": "tLiquid",
        "gas": "tGas",
        "supercritical": "tSupercritical",
    }.get(s_phase_type)

    if not s_phase_struct_name:
        raise ValueError(f"Invalid phase type: {s_phase_type}")

    tx_matter_for_substance_and_type = tx_matter_for_substance[s_type_struct]
    tx_matter_for_substance_and_type_and_aggregate = tx_matter_for_substance_and_type[s_phase_struct_name]

    # Get the column for the desired property
    i_column = tx_matter_for_substance_and_type["tColumns"].get(s_property.replace(" ", ""))
    if i_column is None:
        raise ValueError(f"Cannot find property {s_property} in the matter table for {s_substance}.")

    # Handle first dependency
    s_first_dep_name_no_spaces = s_first_dep_name.replace(" ", "")
    i_column_first = tx_matter_for_substance_and_type["tColumns"].get(s_first_dep_name_no_spaces)
    if i_column_first is None:
        raise ValueError(f"Cannot find property {s_first_dep_name} in the matter table for {s_substance}.")

    f_min = tx_matter_for_substance_and_type_and_aggregate["ttExtremes"][f"t{s_first_dep_name_no_spaces}"]["Min"]
    f_max = tx_matter_for_substance_and_type_and_aggregate["ttExtremes"][f"t{s_first_dep_name_no_spaces}"]["Max"]

    if f_first_dep_value > f_max:
        f_first_dep_value = f_max
    elif f_first_dep_value < f_min:
        f_first_dep_value = f_min

    if i_dependencies == 1:
        # Single dependency
        af_temporary = tx_matter_for_substance_and_type_and_aggregate["mfData"][:, [i_column, i_column_first]]
        af_temporary = af_temporary[~np.isnan(af_temporary).any(axis=1)]
        af_temporary = np.unique(af_temporary, axis=0)

        af_root_square_sum = np.abs(af_temporary[:, 1] - f_first_dep_value)
        closest_index = np.argmin(af_root_square_sum)
        f_property = af_temporary[closest_index, 0]

    else:
        # Two dependencies
        s_second_dep_name_no_spaces = s_second_dep_name.replace(" ", "")
        i_column_second = tx_matter_for_substance_and_type["tColumns"].get(s_second_dep_name_no_spaces)
        if i_column_second is None:
            raise ValueError(f"Cannot find property {s_second_dep_name} in the matter table for {s_substance}.")

        f_min = tx_matter_for_substance_and_type_and_aggregate["ttExtremes"][f"t{s_second_dep_name_no_spaces}"]["Min"]
        f_max = tx_matter_for_substance_and_type_and_aggregate["ttExtremes"][f"t{s_second_dep_name_no_spaces}"]["Max"]

        if f_second_dep_value > f_max:
            f_second_dep_value = f_max
        elif f_second_dep_value < f_min:
            f_second_dep_value = f_min

        af_temporary = tx_matter_for_substance_and_type_and_aggregate["mfData"][:, [i_column, i_column_first, i_column_second]]
        af_temporary = af_temporary[~np.isnan(af_temporary).any(axis=1)]
        af_temporary = np.unique(af_temporary, axis=0)

        af_root_square_sum = np.sqrt(
            (af_temporary[:, 1] - f_first_dep_value) ** 2 + (af_temporary[:, 2] - f_second_dep_value) ** 2
        )
        closest_index = np.argmin(af_root_square_sum)
        f_property = af_temporary[closest_index, 0]

    return f_property
