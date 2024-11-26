import numpy as np

class SilicaGelTable:
    def __init__(self, k_l=None):
        """
        Initialize the SilicaGelTable class with default or provided values.
        """
        # Constants
        self.csNames = None
        self.mfTothParamter_a0 = np.array([7.678E-6, 1.767E2, 0, 0]) / 1000  # Convert from [1/kPa] to [1/Pa]
        self.mfTothParamter_b0 = np.array([5.164E-7, 2.787E-5, 0, 0]) / 1000  # Convert from [1/kPa] to [1/Pa]
        self.mfTothParamter_E = np.array([2.330E3, 1.093E3, 0, 0])
        self.mfTothParamter_t0 = np.array([-3.053E-1, -1.190E-3, 0, 0])
        self.mfTothParamter_c0 = np.array([2.386E2, 2.213E1, 0, 0])
        self.fUnivGasConst_R = 8.314  # Universal gas constant [J/(mol*K)]
        self.fR_pellet = 1.125e-3  # Pellet radius [m]
        self.fPelletPorosity = 0.4  # Pellet porosity [-]
        self.afD_collision = [2.8, 3.7979, 3.7412, 3.4822]  # Collision diameter of [H2O, CO2, N2, O2] [Å]
        self.afLJPotential = [250, 223.675, 88.9525, 103.6955]  # Lennard-Jones potential minima [K]
        self.fR_macropore = 0  # Average macropore radius [m]
        self.fMacroporeTurt_tau = 1  # Macropore tortuosity [-]

        # Modulation and validation
        self.D_L = np.nan
        self.k_f = np.nan
        self.D_p = np.nan
        self.D_c = np.nan
        self.k_l = np.array([0.00125, 0, 0, 0]) if k_l is None else np.array(k_l)
        self.K = np.nan

    def get_ThermodynConst_K(self, afC_in, fTemperature, fRhoSorbent, csNames, afMolMass):
        """
        Calculate the linearized isotherm constant (K).
        """
        if not np.isnan(self.K).all():
            return np.tile(self.K, (len(afC_in), 1)).T

        K = self.calculate_q_equ(afC_in, fTemperature, fRhoSorbent, csNames, afMolMass) / afC_in
        K[np.isnan(K) | (K < 0)] = 0
        return K

    def calculate_q_equ(self, afC_in, fTemperature, fRhoSorbent, csNames, _):
        """
        Calculate equilibrium loading of adsorbent.
        """
        # Partial pressures of species
        p_i = afC_in * self.fUnivGasConst_R * fTemperature  # [Pa]

        if np.isscalar(fTemperature):
            a = self.mfTothParamter_a0 * np.exp(self.mfTothParamter_E / fTemperature)
            b = self.mfTothParamter_b0 * np.exp(self.mfTothParamter_E / fTemperature)
            t_T = self.mfTothParamter_t0 + self.mfTothParamter_c0 / fTemperature
        else:
            a = self.mfTothParamter_a0 * np.exp(self.mfTothParamter_E / fTemperature)
            b = np.outer(self.mfTothParamter_b0, np.exp(self.mfTothParamter_E / fTemperature))
            t_T = np.outer(self.mfTothParamter_t0, np.ones_like(fTemperature)) + \
                  np.outer(self.mfTothParamter_c0, 1 / fTemperature)

        sum_b_p = np.sum(b * p_i, axis=0)
        q_equ = np.zeros_like(p_i)

        for iVar_2 in range(len(csNames)):
            q_equ[iVar_2, :] = a[iVar_2] * p_i[iVar_2, :] / ((1 + sum_b_p ** t_T[iVar_2]) ** (1 / t_T[iVar_2]))

        q_equ *= fRhoSorbent  # Convert to mol/m^3
        return q_equ

    def calculate_mu(self, fTemperature):
        """
        Calculate dynamic viscosity according to Sutherland's law.
        """
        fT_0 = 291.15  # Reference temperature [K]
        fSutherlConst = 120  # Sutherland constant [K]
        fmu_0 = 18.27e-6  # Reference dynamic viscosity [Pa·s]
        return fmu_0 * (fT_0 + fSutherlConst) / (fTemperature + fSutherlConst) * (fTemperature / fT_0) ** 1.5

    def calculate_collision_integral(self, fTemperature):
        """
        Calculate collision integral using Lennard-Jones potentials.
        """
        e_i = np.zeros(len(self.csNames))
        for idx, name in enumerate(self.csNames):
            if name == 'H2O':
                e_i[idx] = self.afLJPotential[0]
            elif name == 'CO2':
                e_i[idx] = self.afLJPotential[1]
            elif name == 'N2':
                e_i[idx] = self.afLJPotential[2]
            elif name == 'O2':
                e_i[idx] = self.afLJPotential[3]

        e_ij = fTemperature / np.sqrt(np.outer(e_i, e_i))
        omega_ij = 0.42541 + (0.82133 - 6.8314e-2 / e_ij) / e_ij + 0.2668 * np.exp(-0.012733 * e_ij)
        return omega_ij

    def calculate_D_m(self, fTemperature, fPressure, afC_in, omega_ij):
        """
        Calculate molecular diffusion coefficient.
        """
        v_i = np.zeros(len(self.csNames))
        for idx, name in enumerate(self.csNames):
            if name == 'H2O':
                v_i[idx] = self.afD_collision[0]
            elif name == 'CO2':
                v_i[idx] = self.afD_collision[1]
            elif name == 'N2':
                v_i[idx] = self.afD_collision[2]
            elif name == 'O2':
                v_i[idx] = self.afD_collision[3]

        v_ij = 0.5 * (v_i[:, None] + v_i[None, :])
        M_ij = 1 / self.afMolMass[:, None] + 1 / self.afMolMass[None, :]
        D_ij = 1e-4 * 98.665 * 1.86 * np.sqrt(M_ij) * fTemperature ** 1.5 / (fPressure * v_ij ** 2 * omega_ij)

        y_i = afC_in / np.sum(afC_in)
        if np.sum(y_i == 0) == len(self.csNames) - 1:
            D_im = y_i * np.diag(D_ij)
        else:
            D_im = (1 - y_i) / (np.sum(y_i[:, None] / D_ij, axis=0) - y_i / np.diag(D_ij))

        D_im[np.isnan(D_im)] = 0
        D_im[np.isinf(D_im)] = 2.9e-3
        return np.sum(y_i * D_im)

    def calculate_dp(self, fLength, fFluidVelocity, e_b, fTemperature, fDensityFlow):
        """
        Calculate pressure drop across packed bed using Ergun equation.
        """
        fmu = self.calculate_mu(fTemperature)
        fDeltaP = 150 * (1 - e_b) ** 2 / e_b ** 2 * fmu * fLength * fFluidVelocity / (2 * self.fR_pellet) ** 2 + \
                  1.75 * fDensityFlow * fFluidVelocity ** 2 * fLength / (2 * self.fR_pellet) * (1 - e_b) / e_b
        return fDeltaP
