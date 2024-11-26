import os
import scipy.io as sio

class LaunchSim:
    """
    CROP execution class with manual input.
    This class is used to test the CROP model with manual input.
    It contains the following static methods:
    - set_parameter
    - set_initial_concentration
    - set_pH_activity_model
    - run
    """

    @staticmethod
    def set_parameter():
        """
        Set rate constants manually (struct `tReaction`).
        """
        # Constants
        K_A, V_A = 10.173436, 0.455
        K_B, V_B = 10.002983, 0.278
        K_C, V_C = 20.013786, 0.459
        V_D = 0

        # Reaction A constants
        tReaction = {
            "A": {
                "a": {"fk_f": K_A * V_A, "fk_r": V_A},
                "b": {"fk_f": K_A * V_A, "fk_r": V_A},
                "c": {"fk_f": 0.000214, "fk_r": 0.983421},
                "d": {"fk_f": 0.000052, "fk_r": 0.887639},
                "e": {"fk_f": 0.000477, "fk_r": 0.000434},
                "f": {"fk_f": 0.000477, "fk_r": 0.000434},
                "g": {"fk_f": K_A * V_A, "fk_r": V_A},
                "h": {"fk_f": 0.000477, "fk_r": 0.000434}
            },
            "D": {"fk_f": V_D, "fk_r": 5.6234e4 * V_D},
            "B": {
                "a": {"fk_f": K_B * V_B, "fk_r": V_B},
                "b": {"fk_f": K_B * V_B, "fk_r": V_B},
                "c": {"fk_f": 0.000046, "fk_r": 1.569257},
                "d": {"fk_f": 0.011483, "fk_r": 1.987534},
                "e": {"fk_f": 0.000391, "fk_r": 0.000315},
                "f": {"fk_f": 0.000391, "fk_r": 0.000315},
                "g": {"fk_f": K_B * V_B, "fk_r": V_B},
                "h": {"fk_f": 0.000391, "fk_r": 0.000315}
            },
            "C": {
                "a": {"fk_f": K_C * V_C, "fk_r": V_C},
                "b": {"fk_f": K_C * V_C, "fk_r": V_C},
                "c": {"fk_f": 0.000156, "fk_r": 2.793547},
                "d": {"fk_f": 0.001014, "fk_r": 1.995478},
                "e": {"fk_f": 0.001010, "fk_r": 0.000509},
                "f": {"fk_f": 0.001010, "fk_r": 0.000509},
                "g": {"fk_f": K_C * V_C, "fk_r": V_C},
                "h": {"fk_f": 0.001010, "fk_r": 0.000509}
            }
        }

        # Save to file
        file_path = os.path.join(os.path.dirname(__file__), "components", "Parameter.mat")
        sio.savemat(file_path, {"tReaction": tReaction})
        print("Parameters are already set.")

    @staticmethod
    def set_initial_concentration(Urea_Percent):
        """
        Set initial concentrations of reactants, enzymes, and inhibitors.
        """
        tfInitial_Settings = {
            "tfConcentration": {
                "AE": 5.061421,
                "AI": 0.000043,
                "AEI": 0,
                "BE": 5.012552,
                "BI": 0.114165,
                "BEI": 0,
                "CE": 5.000041,
                "CI": 0.000234,
                "CEI": 0,
                "COH4N2": 0.249770,
                "NH3": 0,
                "NH4": 0.87 / 30,
                "Cl": (2 * 0.1 + 2 * 0.07 + 0.12 + 2.48 + 0.87) / 30,
                "NO2": 0,
                "NO3": 0,
                "C6H5O7": 0.07 / 30,
                "Na": (2.48 + 2 * 0.5 + 3 * 0.07) / 30,
                "SO4": 0.5 / 30,
                "HPO4": 0.71 / 30,
                "K": (2 * 0.71 + 0.12) / 30,
                "Mg": 0.07 / 30,
                "Ca": 0.1 / 30,
                "CO3": 0,
                "CaCO3": 0.166552
            }
        }

        # Save to file
        file_path = os.path.join(os.path.dirname(__file__), "components", "Initial_Settings.mat")
        sio.savemat(file_path, {"tfInitial_Settings": tfInitial_Settings})
        print(f"The input urine solution is {Urea_Percent}%.")
        print("Initial concentrations for COH4N2, NH3, NH4, NO2 and NO3 are already set.")

    @staticmethod
    def set_pH_activity_model():
        """
        Create and save the pH activity model (`tpH_Diagram`).
        """
        tpH_Diagram = {}
        tfpH_low = {"A": 4, "B": 4, "C": 4}
        tfpH_opt = {"A": 9, "B": 9, "C": 9}
        tfpH_high = {"A": 14, "B": 14, "C": 14}
        tiCurve_Mode = {"A": 3, "B": 6, "C": 2}

        # Generate pH diagram
        for j in ["A", "B", "C"]:
            fpH = []
            rFactor = []
            for i in range(1, 12):
                if i <= 6:
                    fpH.append((tfpH_opt[j] - tfpH_low[j]) / 5 * (i - 1) + tfpH_low[j])
                else:
                    fpH.append((tfpH_high[j] - tfpH_opt[j]) / 5 * (i - 6) + tfpH_opt[j])
            
            if tiCurve_Mode[j] == 3:
                rFactor = [0, 0, 0, 1, 1, 1, 1, 1, 1, 1, 0]
            elif tiCurve_Mode[j] == 6:
                rFactor = [0, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0]
            elif tiCurve_Mode[j] == 2:
                rFactor = [0, 1, 1, 1, 0.4, 0.2, 0.1, 0.05, 0.025, 0, 0]
            
            tpH_Diagram[j] = {"fpH": fpH, "rFactor": rFactor}

        # Save to file
        file_path = os.path.join(os.path.dirname(__file__), "components", "pH_model.mat")
        sio.savemat(file_path, {"tpH_Diagram": tpH_Diagram})
        print("pH activity model is already set.")

    @staticmethod
    def run(Urea_Percent):
        """
        Execute the CROP model with manual inputs.
        """
        LaunchSim.set_parameter()
        LaunchSim.set_pH_activity_model()
        LaunchSim.set_initial_concentration(Urea_Percent)
        print("Running the CROP model setup (mock execution).")
