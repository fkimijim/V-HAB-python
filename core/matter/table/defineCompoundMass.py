import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "simulation")))
import Infrastructure
import Table

SimulationInfrastructure = Infrastructure()
MatterTable = Table()

def define_compound_mass(self, o_caller, s_compound_name, tr_base_composition, b_edible_substance=False):
    """
    Define a new compound mass type based on a basic composition of substances.

    Args:
        self: The current object context.
        o_caller: Caller object (either `simulation.infrastructure` or `matter.table`).
        s_compound_name: Name of the compound mass.
        tr_base_composition: Dictionary containing base composition with substances as keys and ratios as values.
        b_edible_substance: Boolean indicating if the compound is an edible substance (default: False).

    Raises:
        ValueError: If called outside the appropriate context or if invalid composition is provided.
    """

    # Validate the caller
    b_error = True
    if isinstance(o_caller, SimulationInfrastructure):
        if not o_caller.o_simulation_container.to_children:
            b_error = False
    elif isinstance(o_caller, MatterTable):
        b_error = False

    if b_error:
        raise ValueError("Defining a compound mass is only possible within the matter table or the setup phase.")

    # Check if the compound name already exists
    if s_compound_name in self.ttx_matter and not self.ab_compound[self.ti_n2i[s_compound_name]]:
        raise ValueError(f"The entry {s_compound_name} already exists in the matter table.")

    # Validate and normalize the base composition
    r_total_ratio = sum(tr_base_composition.values())
    if abs(r_total_ratio - 1) > 1e-3:
        raise ValueError(f"The compound mass {s_compound_name} has a base ratio that does not sum to 1.")

    if r_total_ratio != 1:
        for key in tr_base_composition:
            tr_base_composition[key] /= r_total_ratio

    # Add to ttx_matter
    self.ttx_matter[s_compound_name] = {
        "trBaseComposition": tr_base_composition,
        "csComposition": list(tr_base_composition.keys())
    }

    # Add the compound if it doesn't exist
    if s_compound_name not in self.ti_n2i:
        self.i_substances += 1
        self.cs_substances.append(s_compound_name)
        self.ti_n2i[s_compound_name] = self.i_substances
        self.cs_i2n = list(self.ti_n2i.keys())

        self.ts_s2n[s_compound_name] = s_compound_name
        self.ts_n2s[s_compound_name] = s_compound_name

        self.ab_absorber.append(False)
        self.ab_compound.append(True)

        if b_edible_substance:
            self.ab_edible_substances.append(True)
        else:
            self.ab_edible_substances.append(False)

        self.ttx_matter[s_compound_name].update({
            "bIndividualFile": False,
            "sName": s_compound_name
        })

        ar_base_composition = [0] * self.i_substances
        for key, value in tr_base_composition.items():
            ar_base_composition[self.ti_n2i[key] - 1] = value

        # Calculate molar mass
        self.af_molar_mass.append(
            sum(m * c for m, c in zip(self.af_molar_mass, ar_base_composition))
        )

        # Default properties
        self.af_nutritional_energy.append(0)
        self.ai_charge.append(0)
        self.af_dissociation_constant.append(0)

        # Update absorber parameters
        for absorber_index in [i for i, is_absorber in enumerate(self.ab_absorber) if is_absorber]:
            absorber_name = self.cs_substances[absorber_index]
            absorber_params = self.ttx_matter[absorber_name]["tAbsorberParameters"]
            for param in ["mfAbsorptionEnthalpy", "mf_A0", "mf_B0", "mf_E", "mf_T0", "mf_C0"]:
                absorber_params["tToth"][param].append(0)
    else:
        # If the compound already exists, update its molar mass
        ar_base_composition = [0] * self.i_substances
        for key, value in tr_base_composition.items():
            ar_base_composition[self.ti_n2i[key] - 1] = value

        self.af_molar_mass[self.ti_n2i[s_compound_name] - 1] = sum(
            m * c for m, c in zip(self.af_molar_mass, ar_base_composition)
        )
