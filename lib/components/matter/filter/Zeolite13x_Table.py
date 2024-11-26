import numpy as np

class Zeolite13xTable:
    def __init__(self):
        """
        Initialize the Zeolite13xTable class with Toth isotherm constants.
        """
        # Constants
        self.csNames = None
        self.fUnivGasConst_R = 8.314  # Universal gas constant [J/(mol*K)]
        self.fR_pellet = 1.1e-3  # Pellet radius [m]
        self.fPelletPorosity = 0.4  # Pellet porosity [-]
        self.afD_collision = [2.8, 3.7979, 3.7412, 3.4822]  # Collision diameters [Å]
        self.afLJPotential = [250, 223.675, 88.9525, 103.6955]  # Lennard-Jones potential minima [K]
        self.fR_macropore = 0  # Average macropore radius [m]
        self.fMacroporeTurt_tau = 1  # Macropore tortuosity [-]

        # Modulation and validation
        self.D_L = np.nan
        self.k_f = np.nan
        self.D_p = np.nan
        self.D_c = np.nan
        self.k_l = [0.0007, 0, 0, 0]  # LDF model kinetic lumped constant [1/s]
        self.K = np.nan

        # Toth table (Values from ICES 2013 paper)
        self.mfToth_table = np.array([
            [15.0622, 2.4100E-07 / 1000, 6852.0, 0.390, -4.20],  # H2O
            [5.7117, 1.0170E-08 / 1000, 5810.2, 0.555, -64.65],  # CO2
            [2.2500, 6.9467E-07 / 1000, 2219.9, 1.000, 0.00],  # N2
            [3.9452, 1.0754E-06 / 1000, 1683.1, 5.200, -1216.33]  # O2
        ])

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
        Calculate equilibrium loading of adsorbent using Toth isotherm.
        """
        mToth_table = np.zeros((len(csNames), 5))

        for idx, name in enumerate(csNames):
            if name == 'H2O':
                mToth_table[idx, :] = self.mfToth_table[0, :]
            elif name == 'CO2':
                mToth_table[idx, :] = self.mfToth_table[1, :]
            elif name == 'N2':
                mToth_table[idx, :] = self.mfToth_table[2, :]
            elif name == 'O2':
                mToth_table[idx, :] = self.mfToth_table[3, :]

        # Partial pressures of species
        p_i = afC_in * self.fUnivGasConst_R * fTemperature  # [Pa]

        if np.isscalar(fTemperature):
            b = mToth_table[:, 1] * np.exp(mToth_table[:, 2] / fTemperature)
            m = mToth_table[:, 3] + mToth_table[:, 4] / fTemperature
        else:
            b = mToth_table[:, 1][:, None] * np.exp(mToth_table[:, 2][:, None] / fTemperature)
            m = mToth_table[:, 3][:, None] + mToth_table[:, 4][:, None] / fTemperature

        q = mToth_table[:, 0]
        sum_b_p = np.sum(b[:, None] * p_i, axis=0)

        q_equ = np.zeros_like(p_i)
        for iVar_2 in range(len(csNames)):
            q_equ[iVar_2, :] = b[iVar_2] * p_i[iVar_2, :] * q[iVar_2] / ((1 + sum_b_p ** m[iVar_2]) ** (1 / m[iVar_2]))

        # Convert to mol/m^3
        q_equ *= fRhoSorbent
        return q_equ

    def calculate_mu(self, fTemperature):
        """
        Calculate dynamic viscosity using Sutherland's law.
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
        Calculate pressure drop using Ergun's equation.
        """
        fmu = self.calculate_mu(fTemperature)
        fDeltaP = (150 * (1 - e_b) ** 2 / e_b ** 2 * fmu * fLength * fFluidVelocity / (2 * self.fR_pellet) ** 2 +
                   1.75 * fDensityFlow * fFluidVelocity ** 2 * fLength / (2 * self.fR_pellet) * (1 - e_b) / e_b)
        return fDeltaP
