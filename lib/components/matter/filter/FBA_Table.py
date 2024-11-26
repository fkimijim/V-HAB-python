import numpy as np

class FBA_Table:
    def __init__(self):
        # Boolean variable to apply JAXA's CDR simulation conditions
        self.bCDR = True

        # Constants
        self.csNames = None
        self.mfToth_table = np.array([
            [15.0622, 2.4100E-07, 6852.0, 0.390, -4.20],     # H2O
            [5.7117, 1.0170E-08, 5810.2, 0.555, -64.65],     # CO2
            [2.2500, 6.9467E-07, 2219.9, 1.000, 0.00],       # N2
            [3.9452, 1.0754E-06, 1683.1, 5.200, -1216.33]    # O2
        ])
        # Convert units from [1/kPa] to [1/Pa]
        self.mfToth_table[:, 1] /= 1000

        # Universal constants
        self.fUnivGasConst_R = 8.314  # Universal gas constant [J/(mol*K)]
        self.fR_pellet = 3.14e-3      # Pellet radius [m]
        self.fPelletPorosity = 0.4    # Pellet porosity [-]
        self.afD_collision = [2.8, 3.7979, 3.7412, 3.4822]  # Collision diameter [Angstrom]
        self.afLJPotential = [250, 223.675, 88.9525, 103.6955]  # Lennard-Jones potential minima [K]
        self.fR_macropore = 0         # Average macropore radius [m]
        self.fMacroporeTurt_tau = 1   # Macropore tortuosity [-]

        # Adjustable properties
        self.D_L = np.nan
        self.k_f = np.nan
        self.D_p = np.nan
        self.D_c = np.nan
        self.k_l = np.nan
        self.K = np.nan

        # JAXA CDR conditions
        if self.bCDR:
            self.D_L = 2.432E-03
            self.fR_pellet = 1.7e-3
            self.fMacroporeTurt_tau = 5
            self.fR_macropore = 3.2e-7
            self.k_l = [0, 1.190e-03, 6.412e-03, 0]

    def get_AxialDispersion_D_L(self, fFluidVelocity, fTemperature, fPressure, afC_in, csNames, afMolMass):
        if not np.isnan(self.D_L):
            return self.D_L
        self.csNames = csNames
        self.afMolMass = afMolMass

        omega_ij = self.calculate_collision_integral(fTemperature)
        D_m = self.calculate_D_m(fTemperature, fPressure, afC_in, omega_ij)
        D_L = 0.73 * D_m + self.fR_pellet * fFluidVelocity / (1 + 4.85 * D_m / fFluidVelocity / self.fR_pellet)
        return D_L

    def get_KineticConst_k_l(self, K, fTemperature, fPressure, fDensityFlow, afC_in, fRhoSorbent, fVolumetricFlowRate, e_b, csNames, afMolMass):
        self.afMolMass = afMolMass
        self.csNames = csNames

        if not np.isnan(self.k_l).all():
            k_l = np.zeros(len(K))
            for i, name in enumerate(csNames):
                if name == "H2O":
                    k_l[i] = self.k_l[0]
                elif name == "CO2":
                    k_l[i] = self.k_l[1]
                elif name == "N2":
                    k_l[i] = self.k_l[2]
                elif name == "O2":
                    k_l[i] = self.k_l[3]
            return k_l

        mu = self.calculate_mu(fTemperature)
        omega_ij = self.calculate_collision_integral(fTemperature)
        D_m = self.calculate_D_m(fTemperature, fPressure, afC_in, omega_ij)
        D_k = self.calculate_D_k(fTemperature, afC_in)
        D_s = self.calculate_D_s(fTemperature)
        K_avg = self.get_ThermodynConst_K(afC_in, fTemperature, fRhoSorbent, csNames, afMolMass)

        k_f = self.calculate_k_f(fVolumetricFlowRate, fDensityFlow, e_b, D_m, mu)
        D_p = self.calculate_D_p(K_avg, D_m, D_k, D_s, afC_in)
        D_c = self.calculate_D_c(fTemperature)

        R_c = 30e-6  # Microcrystal radius [m]
        k_l = 1.0 / ((K * self.fR_pellet / 3 / k_f) +
                     (K * self.fR_pellet ** 2 / 13 / self.fPelletPorosity / D_p) +
                     (R_c ** 2 / 15 / D_c))
        k_l[np.isnan(k_l) | (k_l < 0)] = 0
        return k_l

    def calculate_mu(self, fTemperature):
        fT_0 = 291.15
        fSutherlConst = 120
        fmu_0 = 18.27e-6
        fmu = fmu_0 * (fT_0 + fSutherlConst) / (fTemperature + fSutherlConst) * (fTemperature / fT_0) ** 1.5
        return fmu

    def calculate_collision_integral(self, fTemperature):
        e_i = np.zeros(len(self.csNames))
        for i, name in enumerate(self.csNames):
            if name == "H2O":
                e_i[i] = self.afLJPotential[0]
            elif name == "CO2":
                e_i[i] = self.afLJPotential[1]
            elif name == "N2":
                e_i[i] = self.afLJPotential[2]
            elif name == "O2":
                e_i[i] = self.afLJPotential[3]
        e_ij = fTemperature / np.sqrt(np.outer(e_i, e_i))
        omega_ij = 0.42541 + (0.82133 - 6.8314e-2 / e_ij) / e_ij + 0.2668 * np.exp(-0.012733 * e_ij)
        return omega_ij

    def calculate_D_m(self, fTemperature, fPressure, afC_in, omega_ij):
        v_i = np.zeros(len(self.csNames))
        for i, name in enumerate(self.csNames):
            if name == "H2O":
                v_i[i] = self.afD_collision[0]
            elif name == "CO2":
                v_i[i] = self.afD_collision[1]
            elif name == "N2":
                v_i[i] = self.afD_collision[2]
            elif name == "O2":
                v_i[i] = self.afD_collision[3]
        v_ij = 0.5 * (np.add.outer(v_i, v_i))
        M_ij = np.add.outer(1 / np.array(self.afMolMass), 1 / np.array(self.afMolMass))
        D_ij = 1e-4 * 98.665 * 1.86 * np.sqrt(M_ij) * fTemperature ** 1.5 / (fPressure * v_ij ** 2 * omega_ij)
        y_i = afC_in / sum(afC_in)
        if sum(y_i == 0) == len(self.csNames) - 1:
            D_im = y_i * np.diag(D_ij)
        else:
            D_im = (1 - y_i) / (np.sum(y_i / D_ij, axis=1) - y_i / np.diag(D_ij))
        D_m = sum(y_i * D_im)
        return D_m

    def calculate_D_k(self, fTemperature, afC_in):
        D_k = 970000 * self.fR_macropore * (fTemperature * np.reciprocal(self.afMolMass)) ** 0.5
        D_k = sum(D_k * afC_in) / sum(afC_in) * 1e-4
        return D_k

    def calculate_D_s(self, fTemperature):
        fD_s_inf = 6.95e-7
        fE_s_act = 18241
        D_s = fD_s_inf * np.exp(-fE_s_act / (self.fUnivGasConst_R * fTemperature))
        return D_s

    def get_ThermodynConst_K(self, afC_in, fTemperature, fRhoSorbent, csNames, afMolMass):
        if not np.isnan(self.K):
            return np.tile(self.K, (len(afC_in), 1)).T
        K = self.calculate_q_equ(afC_in, fTemperature, fRhoSorbent, csNames, afMolMass) / afC_in
        K[np.isnan(K) | (K < 0)] = 0
        return K

    # More methods to be implemented based on the MATLAB code...
