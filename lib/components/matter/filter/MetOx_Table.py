class MetOxTable:
    """
    Helper class for MetOx filter modeling. Handles the specific properties 
    and functions required for absorption and desorption processes.
    """

    def __init__(self):
        # Properties
        self.fFrequencyFactor = 1.9e+10  # Pre-exponential factor [1/s]
        self.fActivationEnergy = 13.3 * 4184  # Activation energy [J]
        self.R_m = 8.3145  # Universal gas constant [J/(mol*K)]
        self.fLogistic_1 = 5  # First logistic factor for coupling function [-]
        self.fLogistic_2 = 50  # Second logistic factor for coupling function [-]
        self.mrLoad_saved = [0, 0]  # Saved loading ratio for ['H2O', 'CO2']
        self.fCO2Capacity = 0.851  # Max absorbable amount of CO2 [-]
        self.fH2OCapacity = 0.18  # Max absorbable amount of H2O [-]
        self.mfAbsorbed = None  # Absorbed mass matrix
        self.iOnce = 1  # Logical operator to initialize the loading ratio matrix

    def get_AxialDispersion_D_L(self, *args):
        """
        Returns the axial dispersion coefficient for MetOx.
        :param args: Optional inputs for further customization
        :return: Dispersion coefficient D_L in [m^2/s]
        """
        D_L = 0  # [m^2/s]
        return D_L

    def calculate_C_new(self, mfC_in, dt, fTemperature, csNames, fVolSolid, x_length, afMolMass):
        """
        Calculate the new concentration after absorption.

        :param mfC_in: Initial concentrations matrix [mol/m^3]
        :param dt: Time step [s]
        :param fTemperature: Temperature [K]
        :param csNames: List of substance names ['H2O', 'CO2', etc.]
        :param fVolSolid: Volume of the solid material [m^3]
        :param x_length: Number of grid points
        :param afMolMass: Array of molar masses [kg/mol]
        :return: Updated concentrations matrix mfC_new
        """
        # Initialize absorption data once
        if self.iOnce == 1:
            self.mrLoad_saved = [[0] * len(mfC_in[0])] * 2
            self.mfAbsorbed = [[0] * len(mfC_in[0])] * 2
            self.iOnce = 2

        mrLoad = [[1] * len(mfC_in[0]) for _ in range(len(mfC_in))]
        if 'H2O' in csNames:
            h2o_idx = csNames.index('H2O')
            mrLoad[h2o_idx] = self.mrLoad_saved[0]
        if 'CO2' in csNames:
            co2_idx = csNames.index('CO2')
            mrLoad[co2_idx] = self.mrLoad_saved[1]

        # Reaction rate constant calculation
        fReactionRateConstant = self.fFrequencyFactor * \
            (2.71828 ** (-self.fActivationEnergy / (self.R_m * fTemperature)))

        # Logistic coupling for CO2 absorption
        mfReactionRateConstant = [[0] * len(mfC_in[0]) for _ in range(len(mfC_in))]
        if 'H2O' in csNames:
            mfReactionRateConstant[h2o_idx] = [fReactionRateConstant] * len(mfC_in[0])
            rCoupling = [1 / (1 + self.fLogistic_1 * (2.71828 ** (-self.fLogistic_2 * load)))
                         for load in mrLoad[h2o_idx]]
            fReactionRateConstantEff = [fReactionRateConstant * r for r in rCoupling]
        else:
            fReactionRateConstantEff = [fReactionRateConstant] * len(mfC_in[0])

        if 'CO2' in csNames:
            mfReactionRateConstant[co2_idx] = fReactionRateConstantEff

        # Concentration ratio calculation
        mrConcentrationRatio = [[(2.71828 ** (-k * (1 - l) * dt)) for k, l in zip(rate_row, load_row)]
                                 for rate_row, load_row in zip(mfReactionRateConstant, mrLoad)]

        # Calculate updated concentrations
        mfC_new = [[cr * c for cr, c in zip(cr_row, c_row)]
                   for cr_row, c_row in zip(mrConcentrationRatio, mfC_in)]

        # Save the loading ratio
        fVol_element = fVolSolid / (x_length - 2)
        if 'H2O' in csNames:
            self.mfAbsorbed[0] = [
                absorbed + (cin - cnew) * fVol_element * afMolMass[h2o_idx]
                for absorbed, cin, cnew in zip(self.mfAbsorbed[0], mfC_in[h2o_idx], mfC_new[h2o_idx])
            ]
        if 'CO2' in csNames:
            self.mfAbsorbed[1] = [
                absorbed + (cin - cnew) * fVol_element * afMolMass[co2_idx]
                for absorbed, cin, cnew in zip(self.mfAbsorbed[1], mfC_in[co2_idx], mfC_new[co2_idx])
            ]

        self.mrLoad_saved[0] = [absorbed / (self.fH2OCapacity / (x_length - 2))
                                for absorbed in self.mfAbsorbed[0]]
        self.mrLoad_saved[1] = [absorbed / (self.fCO2Capacity / (x_length - 2))
                                for absorbed in self.mfAbsorbed[1]]

        return mfC_new

    def calculate_dp(self):
        """
        Calculate the pressure drop across the filter bed.
        
        :return: Pressure drop fDeltaP in [Pa]
        """
        fPressureDrop = 0.785  # Pressure drop in inH2O
        fConv_inH2O_Pa = 248.84  # Conversion factor from inH2O to Pa
        fDeltaP = fPressureDrop * fConv_inH2O_Pa  # [Pa]
        return fDeltaP
