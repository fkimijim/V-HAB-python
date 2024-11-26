import os
import scipy.io as sio

class Manual:
    """
    CROP execution class with manual input.
    This class is used to test the CROP model with manual input.
    """

    @staticmethod
    def set_parameter():
        """
        Set rate constants manually (struct `tReaction`).
        """
        # Constants
        K_A, V_A = 1.2, 0.05
        K_B, V_B = 1, 0.025
        K_C, V_C = 3, 0.018
        V_D = 0.005

        # Reaction constants
        tReaction = {
            "A": {
                "a": {"fk_f": K_A * V_A, "fk_r": V_A},
                "b": {"fk_f": K_A * V_A, "fk_r": V_A},
                "c": {"fk_f": 0.005, "fk_r": 0.003},
                "d": {"fk_f": 0.005, "fk_r": 0.003},
                "e": {"fk_f": 0.01, "fk_r": 0.05},
                "f": {"fk_f": 0.01, "fk_r": 0.05},
                "g": {"fk_f": K_A * V_A, "fk_r": V_A},
                "h": {"fk_f": 0.1, "fk_r": 0.5},
            },
            "D": {
                "fk_f": V_D,
                "fk_r": 5.6234e4 * V_D
            },
            "B": {
                "a": {"fk_f": K_B * V_B, "fk_r": V_B},
                "b": {"fk_f": K_B * V_B, "fk_r": V_B},
                "c": {"fk_f": 0.005, "fk_r": 0.003},
                "d": {"fk_f": 0.005, "fk_r": 0.003},
                "e": {"fk_f": 0.005, "fk_r": 0.003},
                "f": {"fk_f": 0.05, "fk_r": 0},
                "g": {"fk_f": K_B * V_B, "fk_r": V_B},
                "h": {"fk_f": 0.5, "fk_r": 0},
            },
            "C": {
                "a": {"fk_f": K_C * V_C, "fk_r": V_C},
                "b": {"fk_f": K_C * V_C, "fk_r": V_C},
                "c": {"fk_f": 0.005, "fk_r": 0.003},
                "d": {"fk_f": 0.005, "fk_r": 0.003},
                "e": {"fk_f": 0.005, "fk_r": 0.003},
                "f": {"fk_f": 0.05, "fk_r": 0},
                "g": {"fk_f": K_C * V_C, "fk_r": V_C},
                "h": {"fk_f": 0.5, "fk_r": 0},
            }
        }

        # Save to file
        file_path = os.path.join(os.path.dirname(__file__), "+components", "Parameter.mat")
        sio.savemat(file_path, {"tReaction": tReaction})
        print("Parameters are already set.")

    @staticmethod
    def set_initial_concentration(Urea_Percent):
        """
        Set initial concentrations of reactants, metal ion balance constant,
        and ammonia vaporization concentration (struct `tfInitial_Settings`).
        """
        tfInitial_Settings = {
            "tfConcentration": {
                "AE": 0.1,
                "AI": 0,
                "AEI": 0,
                "BE": 0.1,
                "BI": 0,
                "BEI": 0,
                "CE": 0.1,
                "CI": 0,
                "CEI": 0,
                "fCon_NH3_Vapor": 0.012,
            }
        }

        # Data series based on Urea_Percent
        if Urea_Percent == 7:
            tfInitial_Settings.update({
                "series": "H",
                "tfConcentration": {
                    **tfInitial_Settings["tfConcentration"],
                    "CH4N2O": 1 / 60,
                    "NH3": 0,
                    "NH4OH": 4e-3,
                    "HNO2": 0,
                    "HNO3": 3e-3,
                    "fK_Metal_Ion": 800,
                }
            })
        elif Urea_Percent == 40:
            tfInitial_Settings.update({
                "series": "D",
                "tfConcentration": {
                    **tfInitial_Settings["tfConcentration"],
                    "CH4N2O": 0.1,
                    "NH3": 0,
                    "NH4OH": 0.03,
                    "HNO2": 0,
                    "HNO3": 0.005,
                    "CE": 0,
                    "fK_Metal_Ion": 0,
                }
            })
        elif Urea_Percent == 3.5:
            tfInitial_Settings.update({
                "series": "C",
                "tfConcentration": {
                    **tfInitial_Settings["tfConcentration"],
                    "CH4N2O": 15e-3,
                    "NH3": 0,
                    "NH4OH": 0.0025,
                    "HNO2": 0,
                    "HNO3": 0.002,
                    "fK_Metal_Ion": 4000,
                }
            })
        elif Urea_Percent == 60:
            tfInitial_Settings.update({
                "series": "E",
                "tfConcentration": {
                    **tfInitial_Settings["tfConcentration"],
                    "CH4N2O": 0.2,
                    "NH3": 0,
                    "NH4OH": 0.02,
                    "HNO2": 0,
                    "HNO3": 2.5e-3,
                    "CE": 0,
                    "fK_Metal_Ion": 200,
                }
            })
        elif Urea_Percent == 80:
            tfInitial_Settings.update({
                "series": "F",
                "tfConcentration": {
                    **tfInitial_Settings["tfConcentration"],
                    "CH4N2O": 0.2,
                    "NH3": 0,
                    "NH4OH": 0.03,
                    "HNO2": 0,
                    "HNO3": 2.5e-3,
                    "BE": 0.06,
                    "CE": 0,
                    "fK_Metal_Ion": 200,
                }
            })
        elif Urea_Percent == 100:
            tfInitial_Settings.update({
                "series": "G",
                "tfConcentration": {
                    **tfInitial_Settings["tfConcentration"],
                    "CH4N2O": 0.1,
                    "NH3": 0,
                    "NH4OH": 0,
                    "HNO2": 0,
                    "HNO3": 0,
                    "fK_Metal_Ion": 0,
                }
            })
        elif Urea_Percent == 20:
            tfInitial_Settings.update({
                "series": "I",
                "tfConcentration": {
                    **tfInitial_Settings["tfConcentration"],
                    "CH4N2O": 50e-3,
                    "NH3": 0.01,
                    "NH4OH": 0.015,
                    "HNO2": 0,
                    "HNO3": 0,
                    "fK_Metal_Ion": 5000,
                }
            })

        # Save to file
        file_path = os.path.join(os.path.dirname(__file__), "+components", "Initial_Settings.mat")
        sio.savemat(file_path, {"tfInitial_Settings": tfInitial_Settings})
        print(f"The input urine solution is {Urea_Percent}%.")
        print("Initial concentrations for CH4N2O, NH3, NH4OH, HNO2 and HNO3 are already set.")

    @staticmethod
    def run(Urea_Percent):
        """
        Execute the CROP model with manual inputs.
        """
        Manual.set_parameter()
        Manual.set_initial_concentration(Urea_Percent)
        print("CROP model execution with manual inputs initiated.")
