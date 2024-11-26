import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "matter", "data")))
import AbsorberData

AbsorberData = AbsorberData()

class MatterTable:
    def import_absorber_data(self):
        """
        Loads all data on absorber substances into the matter table.
        Adds parameters specific to absorption processes, including Toth equation parameters.
        """
        # Import Absorber data
        cs_absorbers = dir(AbsorberData)

        # Counting the number of absorbers
        num_absorbers = len(cs_absorbers)

        # Initialize a boolean array for identifying absorbers
        self.abAbsorber = [False] * self.iSubstances

        # Loop through each absorber and add its data to the matter table
        for substance in cs_absorbers:
            substance_index = self.tiN2I[substance]

            # Mark the substance as an absorber
            self.abAbsorber[substance_index] = True

            # Initialize the data fields in the matter table for this substance
            self.ttxMatter[substance]["tAbsorberParameters"] = {
                "tToth": {
                    "mf_A0": [0] * self.iSubstances,
                    "mf_B0": [0] * self.iSubstances,
                    "mf_E": [0] * self.iSubstances,
                    "mf_T0": [0] * self.iSubstances,
                    "mf_C0": [0] * self.iSubstances,
                },
                "mfAbsorptionEnthalpy": [0] * self.iSubstances,
            }

            # Get the absorber data struct for the current substance
            t_data = getattr(AbsorberData, substance)

            # Parse Toth parameters for CO2 absorption
            self.ttxMatter[substance]["tAbsorberParameters"]["tToth"]["mf_A0"][self.tiN2I["CO2"]] = t_data["tToth"]["fA0_CO2"]
            self.ttxMatter[substance]["tAbsorberParameters"]["tToth"]["mf_B0"][self.tiN2I["CO2"]] = t_data["tToth"]["fB0_CO2"]
            self.ttxMatter[substance]["tAbsorberParameters"]["tToth"]["mf_E"][self.tiN2I["CO2"]] = t_data["tToth"]["fE_CO2"]
            self.ttxMatter[substance]["tAbsorberParameters"]["tToth"]["mf_T0"][self.tiN2I["CO2"]] = t_data["tToth"]["fT0_CO2"]
            self.ttxMatter[substance]["tAbsorberParameters"]["tToth"]["mf_C0"][self.tiN2I["CO2"]] = t_data["tToth"]["fC0_CO2"]

            # Parse Toth parameters for H2O absorption
            self.ttxMatter[substance]["tAbsorberParameters"]["tToth"]["mf_A0"][self.tiN2I["H2O"]] = t_data["tToth"]["fA0_H2O"]
            self.ttxMatter[substance]["tAbsorberParameters"]["tToth"]["mf_B0"][self.tiN2I["H2O"]] = t_data["tToth"]["fB0_H2O"]
            self.ttxMatter[substance]["tAbsorberParameters"]["tToth"]["mf_E"][self.tiN2I["H2O"]] = t_data["tToth"]["fE_H2O"]
            self.ttxMatter[substance]["tAbsorberParameters"]["tToth"]["mf_T0"][self.tiN2I["H2O"]] = t_data["tToth"]["fT0_H2O"]
            self.ttxMatter[substance]["tAbsorberParameters"]["tToth"]["mf_C0"][self.tiN2I["H2O"]] = t_data["tToth"]["fC0_H2O"]

            # Parse absorption enthalpy
            self.ttxMatter[substance]["tAbsorberParameters"]["mfAbsorptionEnthalpy"][self.tiN2I["CO2"]] = t_data["fAdsorptionEnthalpy_CO2"]
            self.ttxMatter[substance]["tAbsorberParameters"]["mfAbsorptionEnthalpy"][self.tiN2I["H2O"]] = t_data["fAdsorptionEnthalpy_H2O"]
