import numpy as np

class BaseManip:
    """
    BaseManip is used to calculate the pH value in an aqueous solution and 
    convert all participating substances correspondingly. Adjust the miComplex 
    variable if new substances are added that take part in the pH value calculation.
    """

    def __init__(self, oPhase):
        self.fpH = 7  # Initial pH value
        self.abDissociation = oPhase.oMT.afDissociationConstant != 0

        # Initialize variables
        self.afConversionRates = np.zeros(oPhase.oMT.iSubstances)
        self.afConcentrations = np.zeros(oPhase.oMT.iSubstances)
        self.miComplex = np.zeros((oPhase.oMT.iSubstances, oPhase.oMT.iSubstances), dtype=int)
        self.arLastPartials = np.zeros(oPhase.oMT.iSubstances)
        self.rMaxChange = 0.01  # Maximum change percentage for recalculations

        # Populate miComplex with dissociation relationships
        self._initialize_miComplex(oPhase)

        self.aiReactants = np.where(np.diag(self.miComplex) > 0)[0]
        self.iReactants = len(self.aiReactants)

        self.createLinearSystem(oPhase)
        self.arLastPartials = np.zeros(sum(self.abRelevantSubstances))

    def _initialize_miComplex(self, oPhase):
        """
        Initialize the dissociation complexes in the miComplex matrix.
        """
        tiN2I = oPhase.oMT.tiN2I
        tsN2S = oPhase.oMT.tsN2S

        # Example: HCl dissociation
        self.miComplex[tiN2I.HCl, tiN2I.HCl] = 1
        self.miComplex[tiN2I.HCl, tiN2I.Clminus] = 2

        # Add other dissociation complexes
        # ... (Use the same structure as the MATLAB code, e.g., for acids, bases, and salts)

    def setMaxChange(self, rMaxChange):
        """
        Set the maximum percentage change for recalculations.
        """
        self.rMaxChange = rMaxChange

    def calculateNewConcentrations(self, afInitialConcentrations, fInitialMassSum, fCurrentPH):
        """
        Calculate the new concentrations for the phase in equilibrium.
        """
        afCurrentConcentration = afInitialConcentrations.copy()
        afConcentrations = afInitialConcentrations.copy()

        fDissociationConstantWater = self.oMT.afDissociationConstant[self.oMT.tiN2I.H2O]
        fInitialChargeSum = np.dot(
            self.oMT.aiCharge[~self.abRelevantSubstances], 
            afInitialConcentrations[~self.abRelevantSubstances]
        )

        mfInitializationIntervall = np.array([
            1e-20, 1e-14, 1e-13, 1e-12, 1e-11, 1e-10, 1e-9, 1e-8, 1e-7,
            1e-6, 1e-5, 1e-4, 1e-3, 1e-3, 1e-2, 1e-1, 100
        ])
        fMaxError = 1e-7
        fMaxIntervallSize = 1e-18

        # Initializations for iterative solver
        mfInitializatonError = np.zeros(len(mfInitializationIntervall))

        for iBoundary, interval in enumerate(mfInitializationIntervall):
            if fCurrentPH > 8:
                # For high pH values, use OH concentration for pH calculation
                afCurrentConcentration[self.oMT.tiN2I.Hplus] = 10 ** (-np.log10(fDissociationConstantWater) - -np.log10(interval))
            else:
                afCurrentConcentration[self.oMT.tiN2I.Hplus] = interval

            afCurrentConcentration[self.oMT.tiN2I.OH] = (
                55.6 * fDissociationConstantWater / afCurrentConcentration[self.oMT.tiN2I.Hplus]
            )

            afLeftSide = (
                self.afBaseLeftSideVector
                + self.mfMolarSumMatrix @ afInitialConcentrations
            )
            afLeftSide[self.oMT.tiN2I.OH] = fInitialMassSum
            afLeftSide[self.oMT.tiN2I.Hplus] = -fInitialChargeSum

            mfLinearSystem = (
                self.mfDissociationMatrix
                + self.mfHydrogenMatrix * afCurrentConcentration[self.oMT.tiN2I.Hplus]
                + self.mfOHMatrix * afCurrentConcentration[self.oMT.tiN2I.OH]
                + self.mfMolarSumMatrix
            )

            afConcentrations[self.abRelevantSubstances] = np.linalg.solve(
                mfLinearSystem[self.abRelevantSubstances][:, self.abRelevantSubstances],
                afLeftSide[self.abRelevantSubstances]
            )
            mfInitializatonError[iBoundary] = (
                afConcentrations[self.oMT.tiN2I.Hplus] - afCurrentConcentration[self.oMT.tiN2I.Hplus]
            )

        # Continue implementing error handling and the iterative solver here
        # ...

        self.afConcentrations = afConcentrations

    def createLinearSystem(self, oPhase):
        """
        Create the linear system matrices for the dissociation calculations.
        """
        oMT = oPhase.oMT
        self.mfDissociationMatrix = np.zeros((oMT.iSubstances, oMT.iSubstances))
        self.mfHydrogenMatrix = np.zeros((oMT.iSubstances, oMT.iSubstances))
        self.mfOHMatrix = np.zeros((oMT.iSubstances, oMT.iSubstances))
        self.mfMolarSumMatrix = np.zeros((oMT.iSubstances, oMT.iSubstances))
        self.abRelevantSubstances = np.zeros(oMT.iSubstances, dtype=bool)

        self.mfDissociationMatrix[np.diag_indices(oMT.iSubstances)] = oMT.afDissociationConstant

        for iReactant in range(self.iReactants):
            iBaseSubstance = self.aiReactants[iReactant]
            aiComplex = self.miComplex[iBaseSubstance, :]
            aiSubstances = np.where(aiComplex > 0)[0]

            for iK in range(1, len(aiSubstances)):
                iSubstance = aiSubstances[iK]
                iPreviousSubstance = aiSubstances[iK - 1]
                if oMT.aiCharge[iSubstance] > 0:
                    self.mfOHMatrix[iPreviousSubstance, iSubstance] = -1
                else:
                    self.mfHydrogenMatrix[iPreviousSubstance, iSubstance] = -1

            iFinalSubstance = aiComplex[aiComplex > 0][-1]
            self.mfMolarSumMatrix[iFinalSubstance, aiSubstances] = 1

        self.mfMolarSumMatrix[oMT.tiN2I.Hplus, :] = oMT.aiCharge
        self.mfMolarSumMatrix[oMT.tiN2I.OH, :] = oMT.afMolarMass

        self.mfHydrogenMatrix[oMT.tiN2I.H2O, oMT.tiN2I.OH] = 1
        self.mfDissociationMatrix[oMT.tiN2I.H2O, oMT.tiN2I.H2O] = 0

        self.afBaseLeftSideVector = np.zeros(oMT.iSubstances)
        self.afBaseLeftSideVector[oMT.tiN2I.H2O] = oMT.afDissociationConstant[oMT.tiN2I.H2O]

        self.abRelevantSubstances[oMT.tiN2I.Hplus] = True
        self.abRelevantSubstances[oMT.tiN2I.OH] = True
        self.abRelevantSubstances[oMT.tiN2I.H2O] = True

    def calculate_pHValue(self, afConcentrations):
        """
        Calculate the pH value given the concentrations.
        """
        fCalculatedpH = -np.log10(afConcentrations[self.oMT.tiN2I.Hplus])
        if fCalculatedpH > 8:
            fCalculatedpH = (
                -np.log10(self.oMT.afDissociationConstant[self.oMT.tiN2I.H2O])
                - -np.log10(afConcentrations[self.oMT.tiN2I.OH])
            )
        elif fCalculatedpH < 6:
            fCalculatedpH = -np.log10(afConcentrations[self.oMT.tiN2I.Hplus])
        else:
            fCalculatedpH_OH = (
                -np.log10(self.oMT.afDissociationConstant[self.oMT.tiN2I.H2O])
                - -np.log10(afConcentrations[self.oMT.tiN2I.OH])
            )
            fCalculatedpH_H = -np.log10(afConcentrations[self.oMT.tiN2I.Hplus])
            fCalculatedpH = fCalculatedpH_OH if abs(fCalculatedpH_OH - self.fpH) < abs(fCalculatedpH_H - self.fpH) else fCalculatedpH_H

        return fCalculatedpH if not np.isinf(fCalculatedpH) else 7
