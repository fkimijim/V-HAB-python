import numpy as np

class RCATable:
    """
    RCA_Table class for handling adsorption and diffusion processes in RCA filters.
    """

    def __init__(self, oParent):
        # Universal gas constant [J/(mol*K)]
        self.fRe = 8.3145

        # Constants for CO2 adsorption
        self.ft = 0.22  # Surface heterogeneity [-]
        self.fns = 1.1  # Saturation capacity [mol/kg]
        self.fb0 = 300e-10  # Toth isotherm parameter [1/Pa]
        self.fT0 = 762.25  # Toth reference temperature [K]
        self.fQ_ads = 72000  # Heat of adsorption [J/mol]

        # Constants for H2O adsorption
        self.ralphaH2O = 0.00105  # Freundlich isotherm parameter [-]
        self.fRw = 461.52  # Gas constant for water [J/(kg*K)]

        # Modification factors
        self.fEquilibriumModificationFactor = 1
        self.fR_pellet = 3.14e-3  # Pellet radius [m]
        self.fPelletPorosity = 0.4  # Pellet porosity [-]
        self.afD_collision = [2.8, 3.7979, 3.7412, 3.4822]  # Collision diameters [Å]
        self.afLJPotential = [250, 223.675, 88.9525, 103.6955]  # Lennard-Jones potential minima [K]
        self.fR_macropore = 3.2e-7  # Macropore radius [m]
        self.fMacroporeTurt_tau = 5  # Macropore tortuosity [-]

        # Modulation and validation parameters
        self.D_L = np.nan
        self.k_f = np.nan
        self.D_p = np.nan
        self.D_c = np.nan
        self.k_l = np.nan
        self.K = np.nan

        self.csNames = None
        self.afMolMass = None
        self.oParent = oParent
        self.afConcentrationChangeRate = np.zeros(self.oParent.iNumGridPoints - 1)
        self.afPreviousConcentration = np.zeros(self.oParent.iNumGridPoints - 1)
        self.afAverageThermoDymamicConstant = None

    def get_ThermodynConst_K(self, afC_in, fTemperature, fRhoSorbent, csNames, afMolMass):
        """
        Calculates the linearized isotherm constant (K).
        """
        if not np.isnan(self.K):
            K = np.tile(self.K, (len(afC_in), 1)).T
            return K

        K = self.calculate_q_equ(afC_in, fTemperature, fRhoSorbent, csNames, afMolMass) / afC_in
        K[np.isnan(K) | (K < 0)] = 0
        self.afAverageThermoDymamicConstant = K[:, 0]
        return K

    def calculate_q_equ(self, mfConcentration, fTemperature, fRhoSorbent, csNames, afMolMass):
        """
        Calculates the equilibrium values for the loading along the bed.
        """
        mfPP_i = mfConcentration * self.fRe * fTemperature
        mfQ_equ = np.zeros_like(mfPP_i)

        if 'H2O' in csNames:
            h2o_idx = csNames.index('H2O')
            fEw = 610.94 * np.exp((17.625 * (fTemperature - 273.15)) / (243.04 + fTemperature - 273.15))
            delta_sat = fEw / (self.fRw * fTemperature)
            fRH = mfConcentration[h2o_idx, :] * afMolMass[h2o_idx] / delta_sat * 100
            fQ_equ_H2O = self.ralphaH2O * fRH ** 2
            mfQ_equ[h2o_idx, :] = fQ_equ_H2O

        if 'CO2' in csNames:
            co2_idx = csNames.index('CO2')
            fTothParameter_b = self.fb0 * np.exp((self.fQ_ads / (self.fRe * self.fT0)) * (self.fT0 / fTemperature - 1))
            fQ_equ_CO2 = (fTothParameter_b * mfPP_i[co2_idx, :] * self.fns) / \
                         ((1 + (fTothParameter_b * mfPP_i[co2_idx, :]) ** self.ft) ** (1 / self.ft))
            fQ_equ_CO2 *= self.fEquilibriumModificationFactor
            mfQ_equ[co2_idx, :] = fQ_equ_CO2

        mfQ_equ *= fRhoSorbent
        if 'CO2' in csNames:
            co2_idx = csNames.index('CO2')
            self.afConcentrationChangeRate = (mfQ_equ[co2_idx, :] - self.afPreviousConcentration) / self.oParent.fTimeStep
            self.afPreviousConcentration = mfQ_equ[co2_idx, :]

        return mfQ_equ

    def calculateDynamicViscosity(self, fTemperature):
        """
        Calculates the dynamic viscosity using Sutherland's formula.
        """
        fT_0 = 300.55
        fSutherlConst = 111
        fmu_0 = 17.81e-6
        fmu = fmu_0 * (fT_0 + fSutherlConst) / (fTemperature + fSutherlConst) * (fTemperature / fT_0) ** 1.5
        return fmu

    def calculateCollisionIntegral(self, fTemperature):
        """
        Calculates the collision integrals using Lennard-Jones potentials.
        """
        e_i = np.zeros(len(self.csNames))
        if 'H2O' in self.csNames:
            e_i[self.csNames.index('H2O')] = self.afLJPotential[0]
        if 'CO2' in self.csNames:
            e_i[self.csNames.index('CO2')] = self.afLJPotential[1]
        if 'N2' in self.csNames:
            e_i[self.csNames.index('N2')] = self.afLJPotential[2]
        if 'O2' in self.csNames:
            e_i[self.csNames.index('O2')] = self.afLJPotential[3]

        e_ij = fTemperature / np.sqrt(np.outer(e_i, e_i))
        omega_ij = 0.42541 + (0.82133 - 6.8314e-2 / e_ij) / e_ij + 0.2668 * np.exp(-0.012733 * e_ij)
        return omega_ij

    def calculateMolecularDiffusion(self, fTemperature, fPressure, afC_in, omega_ij):
        """
        Calculates the molecular diffusion coefficient using Chapman-Enskog theory.
        """
        v_i = np.zeros(len(self.csNames))
        if 'H2O' in self.csNames:
            v_i[self.csNames.index('H2O')] = self.afD_collision[0]
        if 'CO2' in self.csNames:
            v_i[self.csNames.index('CO2')] = self.afD_collision[1]
        if 'N2' in self.csNames:
            v_i[self.csNames.index('N2')] = self.afD_collision[2]
        if 'O2' in self.csNames:
            v_i[self.csNames.index('O2')] = self.afD_collision[3]

        v_ij = 0.5 * (np.add.outer(v_i, v_i))
        M_ij = np.add.outer(1 / np.array(self.afMolMass), 1 / np.array(self.afMolMass))
        D_ij = 1e-4 * 98.665 * 1.86 * (M_ij ** 0.5) * (fTemperature ** 1.5) / (fPressure * v_ij ** 2 * omega_ij)

        y_i = afC_in / np.sum(afC_in)
        if np.sum(y_i == 0) == len(self.csNames) - 1:
            D_im = y_i * np.diag(D_ij)
        else:
            D_im = (1 - y_i) / (np.sum(np.divide(y_i, D_ij, where=D_ij != 0), axis=1) - y_i / np.diag(D_ij))

        D_m = np.sum(y_i * D_im)
        return D_m

    def calculate_dp(self, fLength, fFluidVelocity, e_b, fTemperature):
        """
        Calculates the pressure drop across the filter bed.
        """
        fT_0 = 291.15
        fSutherlConst = 120
        fConst_mu_0 = 18.27e-6
        fViscosity_dyn = fConst_mu_0 * (fT_0 + fSutherlConst) / (fTemperature + fSutherlConst) * (fTemperature / fT_0) ** 1.5

        fD_p = 2.04e-3
        fDeltaP = (fLength * 150 * fViscosity_dyn * fFluidVelocity * (1 - e_b) ** 2) / (e_b ** 3 * fD_p ** 2)
        return fDeltaP
