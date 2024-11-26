import numpy as np
from scipy.integrate import solve_ivp

class BaseWeakBaseAnionP2P:
    """
    Weak Base Anion (WBA) P2P performing ion exchange in Multifiltration beds.
    """

    def __init__(self, oStore, oDesorptionP2P):
        self.oDesorptionP2P = oDesorptionP2P
        self.rVoidFraction = oStore.oContainer.rVoidFraction
        self.fResinMass = oStore.oContainer.fResinMass / oStore.oContainer.iCells
        self.fCellVolume = oStore.oContainer.fVolume / oStore.oContainer.iCells
        self.iPresaturant = oStore.oContainer.iPresaturant
        self.fInitialPresaturantMass = oStore.oContainer.afMass[self.iPresaturant]
        self.fEmptyBedContactTime = oStore.oContainer.fEmptyBedContactTime / oStore.oContainer.iCells

        # Exchange rate constants (m^3)^2 / eq^2
        self.afExchangeRateConstants = np.zeros(oStore.oMT.iSubstances)
        self.afExchangeRateConstants[oStore.oMT.tiN2I["CMT"]] = 3.44e4
        self.afExchangeRateConstants[oStore.oMT.tiN2I["Clminus"]] = 1.06e3
        self.afExchangeRateConstants[oStore.oMT.tiN2I["C4H7O2"]] = 541
        self.afExchangeRateConstants[oStore.oMT.tiN2I["C2H3O2"]] = 588
        self.afExchangeRateConstants[oStore.oMT.tiN2I["SO4"]] = 1.47e4
        self.afExchangeRateConstants[oStore.oMT.tiN2I["C3H5O3"]] = 382

        self.mfExchangeRateConstants = np.zeros((oStore.oMT.iSubstances, oStore.oMT.iSubstances))
        for key in ["CMT", "Clminus", "C4H7O2", "C2H3O2", "SO4", "C3H5O3"]:
            idx = oStore.oMT.tiN2I[key]
            self.mfExchangeRateConstants[idx, :] = self.afExchangeRateConstants
        np.fill_diagonal(self.mfExchangeRateConstants, 0)

        # Separation factors
        self.afSeperationFactors = np.zeros(oStore.oMT.iSubstances)
        self.afSeperationFactors[oStore.oMT.tiN2I["CMT"]] = 32.4
        self.afSeperationFactors[oStore.oMT.tiN2I["Clminus"]] = 1
        self.afSeperationFactors[oStore.oMT.tiN2I["C4H7O2"]] = 0.510
        self.afSeperationFactors[oStore.oMT.tiN2I["C2H3O2"]] = 0.555
        self.afSeperationFactors[oStore.oMT.tiN2I["SO4"]] = 13.9
        self.afSeperationFactors[oStore.oMT.tiN2I["C3H5O3"]] = 0.360

        self.abIons = self.afSeperationFactors != 0
        self.mfSeperationFactors = np.zeros((oStore.oMT.iSubstances, oStore.oMT.iSubstances))
        self.mfSeperationFactors[np.ix_(self.abIons, self.abIons)] = (
            self.afSeperationFactors[self.abIons][:, None] / self.afSeperationFactors[self.abIons]
        )
        np.fill_diagonal(self.mfSeperationFactors, 0)

        self.afCurrentInletConcentrations = np.zeros(oStore.oMT.iSubstances)
        self.afPreviousFlowRates = np.zeros(oStore.oMT.iSubstances)
        self.afCurrentLoading = np.zeros(np.sum(self.abIons))

        self.hCalculateOutletConcentrationChangeRate = lambda t, afOutletConcentrations: self.calculateOutletConcentrationChangeRate(
            afOutletConcentrations, t
        )

    def calculateOutletConcentrationChangeRate(self, afOutletConcentrations, _):
        fOutletHplusConcentration = afOutletConcentrations[self.oMT.tiN2I["Hplus"]]

        afHelperVariable1 = (
            self.fTotalCapacity
            * self.afExchangeRateConstants[self.abIons]
            * fOutletHplusConcentration
        )
        fHelperVariable2 = (
            1
            + fOutletHplusConcentration
            * np.sum(self.afExchangeRateConstants[self.abIons] * afOutletConcentrations[self.abIons])
        )
        afExchangeRateConstantSumsWithoutSelf = np.sum(
            self.mfExchangeRateConstants[np.ix_(self.abIons, self.abIons)] * afOutletConcentrations[self.abIons],
            axis=1,
        )

        afOutletConcentrationChange = np.zeros_like(afOutletConcentrations)
        afOutletConcentrationChange[self.abIons] = self.fVolumetricFlowRate * (
            self.afCurrentInletConcentrations[self.abIons] - afOutletConcentrations[self.abIons]
        ) / (
            self.fResinMass
            * (
                (1 + fOutletHplusConcentration * afExchangeRateConstantSumsWithoutSelf)
                * afHelperVariable1
                / fHelperVariable2**2
            )
            + self.fCellVolume * self.rVoidFraction
        )
        return afOutletConcentrationChange

    def calculateExchangeRates(self, afPartialInFlows):
        afNewEquivalentInletFlows = (
            afPartialInFlows / self.oMT.afMolarMass * np.abs(self.oMT.aiCharge)
        )
        afNewEquivalentInletFlows[~self.abIons] = 0

        fDensity = self.oIn.oPhase.fDensity
        self.fVolumetricFlowRate = np.sum(afPartialInFlows) / fDensity

        self.fTotalCapacity = (
            self.oOut.oPhase.afMass[self.iPresaturant] / self.oMT.afMolarMass[self.iPresaturant]
        ) / self.fResinMass

        afCurrentOutletConcentrations = (
            0.1 * afNewEquivalentInletFlows / self.fVolumetricFlowRate
        )
        afCurrentOutletConcentrations[self.oMT.tiN2I["Hplus"]] = max(
            afCurrentOutletConcentrations[self.oMT.tiN2I["Hplus"]], 10**-7 * 1000
        )

        afNewInletConcentrations = afNewEquivalentInletFlows / self.fVolumetricFlowRate
        afNewLoading = (
            self.oOut.oPhase.afMass[self.abIons] / self.fResinMass
        ) * (np.abs(self.oMT.aiCharge[self.abIons]) / self.oMT.afMolarMass[self.abIons])

        arChangeInletConcentrations = np.abs(
            self.afCurrentInletConcentrations - afNewInletConcentrations
        ) / afNewInletConcentrations
        arChangeLoading = np.abs(self.afCurrentLoading - afNewLoading) / afNewLoading

        if np.any(arChangeInletConcentrations > 0.02) or np.any(arChangeLoading > 0.02):
            self.afCurrentInletConcentrations = afNewInletConcentrations
            self.afCurrentLoading = afNewLoading

            result = solve_ivp(
                self.hCalculateOutletConcentrationChangeRate,
                [0, self.fEmptyBedContactTime],
                afCurrentOutletConcentrations,
                method="RK45",
                rtol=1e-3,
                atol=1e-4,
            )

            afOutletConcentrations = result.y[:, -1]
            afOutletFlows = (
                afOutletConcentrations[self.abIons]
                * self.oMT.afMolarMass[self.abIons]
                / np.abs(self.oMT.aiCharge[self.abIons])
                * self.fVolumetricFlowRate
            )
            afPartialFlowRates = np.zeros_like(afPartialInFlows)
            afPartialFlowRates[self.abIons] = afPartialInFlows[self.abIons] - afOutletFlows
            self.afPreviousFlowRates = afPartialFlowRates
        else:
            afPartialFlowRates = self.afPreviousFlowRates

        return afPartialFlowRates
