import numpy as np

class MatterTable:
    # Assuming necessary methods and attributes are implemented in this class

    def calculate_property(self, s_property, f_temperature, ar_partial_mass, cs_phase, ai_phase, ai_indices, af_partial_pressures, b_use_isobaric_data):
        """
        Calculates requested matter property for the given parameters.

        :param s_property: Property to calculate (string)
        :param f_temperature: Temperature (float)
        :param ar_partial_mass: Array of partial masses
        :param cs_phase: List of phase names
        :param ai_phase: Array of phase indices
        :param ai_indices: Array of indices for the substances
        :param af_partial_pressures: Array of partial pressures
        :param b_use_isobaric_data: Boolean for isobaric data usage
        :return: Calculated property value
        """
        # If no mass is given, return 0
        if np.sum(ar_partial_mass) == 0:
            return 0

        # Ensure there are no NaN values in the mass array
        if np.isnan(ar_partial_mass).any():
            raise ValueError("Invalid entries in mass vector.")

        i_num_indices = len(ai_indices)

        # Initialize an array for storing property values
        af_property = np.zeros(i_num_indices)

        for i, index in enumerate(ai_indices):
            # Prepare the parameter dictionary for find_property
            t_parameters = {
                "sSubstance": self.cs_substances[index],
                "sProperty": s_property,
                "sFirstDepName": "Temperature",
                "fFirstDepValue": f_temperature,
                "sPhaseType": cs_phase[round(ai_phase[index])],
                "sSecondDepName": "Pressure",
                "fSecondDepValue": af_partial_pressures[index],
                "bUseIsobaricData": b_use_isobaric_data
            }

            try:
                af_property[i] = self.find_property(t_parameters)
            except Exception as s_msg:
                # Handle phase transition and find closest valid matter entry
                i_phase = self.determine_phase(
                    t_parameters["sSubstance"],
                    f_temperature,
                    af_partial_pressures[index]
                )
                if i_phase % 1 != 0:  # Indicates a phase change
                    af_property[i] = self.find_closest_valid_matter_entry(t_parameters)
                else:
                    raise s_msg

        # Ensure there are no NaN values in the property array
        if np.isnan(af_property).any():
            raise ValueError("Invalid entries in specific property vector.")

        # Ensure vector dimensions match
        if af_property.shape[0] != ar_partial_mass[ai_indices].shape[0]:
            raise ValueError("Vectors must be of the same length but one transposed.")

        # Calculate the property of the mixture
        f_property = np.dot(ar_partial_mass[ai_indices] / np.sum(ar_partial_mass[ai_indices]), af_property)

        # Validate the result
        if np.isnan(f_property) or f_property < 0:
            raise ValueError(f"Invalid {s_property}: {f_property}")

        return f_property
