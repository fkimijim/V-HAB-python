import numpy as np

def calculateEquilibriumLoading(self, *args):
    """
    Calculates the equilibrium loading of absorber material based on the Toth equation.

    Returns:
        mfEquilibriumLoading: Vector containing the mass (kg) of each substance absorbed by the given absorber mass at equilibrium.
        mfLinearizationConstant: Vector of linearization constants for each substance.
    """
    if len(args) == 1:
        if args[0].sObjectType != "p2p":
            raise ValueError(
                "If only one parameter is provided, it must be a matter.procs.p2p derivative."
            )

        if any(args[0].oOut.oPhase.afMass[self.abAbsorber]):
            afMass = args[0].oOut.oPhase.afMass
            fTemperature = args[0].oOut.oPhase.fTemperature
            afPP = args[0].oIn.oPhase.afPP
        elif any(args[0].oIn.oPhase.afMass[self.abAbsorber]):
            afMass = args[0].oIn.oPhase.afMass
            fTemperature = args[0].oIn.oPhase.fTemperature
            afPP = args[0].oOut.oPhase.afPP
        else:
            # Output zero equilibrium loading
            return [0] * self.iSubstances, [0] * self.iSubstances
    else:
        # TODO: Add error checks for incorrect inputs
        afMass = args[0]
        afPP = args[1]
        fTemperature = args[2]

        if not any(afMass[self.abAbsorber]):
            # Output zero equilibrium loading
            return [0] * self.iSubstances, [0] * self.iSubstances

    # Find absorbers present in the mass
    csAbsorbers = [
        self.csSubstances[i]
        for i, val in enumerate((afMass != 0) * self.abAbsorber)
        if val != 0
    ]

    mfEquilibriumLoadingPerAbsorberMolsPerKG = [
        [0] * self.iSubstances for _ in range(len(csAbsorbers))
    ]
    mfEquilibriumLoadingPerAbsorber = [
        [0] * self.iSubstances for _ in range(len(csAbsorbers))
    ]

    mfLinearizationConstantPerAbsorberMolsPerKG = [
        [0] * self.iSubstances for _ in range(len(csAbsorbers))
    ]
    mfLinearizationConstantPerAbsorber = [
        [0] * self.iSubstances for _ in range(len(csAbsorbers))
    ]

    for iAbsorber, absorber in enumerate(csAbsorbers):
        if absorber == "Zeolite5A":
            (
                mfEquilibriumLoadingPerAbsorberMolsPerKG[iAbsorber],
                mfLinearizationConstantPerAbsorberMolsPerKG[iAbsorber],
            ) = self.calculateEquilibriumLoading_Zeolite5A(afPP, fTemperature)
        elif absorber == "Zeolite5A_RK38":
            (
                mfEquilibriumLoadingPerAbsorberMolsPerKG[iAbsorber],
                mfLinearizationConstantPerAbsorberMolsPerKG[iAbsorber],
            ) = self.calculateEquilibriumLoading_Zeolite5A_RK38(afPP, fTemperature)
        elif absorber == "Zeolite13x":
            (
                mfEquilibriumLoadingPerAbsorberMolsPerKG[iAbsorber],
                mfLinearizationConstantPerAbsorberMolsPerKG[iAbsorber],
            ) = self.calculateEquilibriumLoading_Zeolite13x(afPP, fTemperature)
        elif absorber == "SilicaGel_40":
            (
                mfEquilibriumLoadingPerAbsorberMolsPerKG[iAbsorber],
                mfLinearizationConstantPerAbsorberMolsPerKG[iAbsorber],
            ) = self.calculateEquilibriumLoading_SilicaGel_40(afPP, fTemperature)
        elif absorber == "Sylobead_B125":
            (
                mfEquilibriumLoadingPerAbsorberMolsPerKG[iAbsorber],
                mfLinearizationConstantPerAbsorberMolsPerKG[iAbsorber],
            ) = self.calculateEquilibriumLoading_Sylobead_B125(afPP, fTemperature)
        else:
            raise ValueError(
                "A new absorber substance was defined without adding the required Toth equation function."
            )

        # Convert to absolute kg value and apply molar mass
        mfEquilibriumLoadingPerAbsorber[iAbsorber] = [
            mols_per_kg * afMass[self.tiN2I[absorber]] * molar_mass
            for mols_per_kg, molar_mass in zip(
                mfEquilibriumLoadingPerAbsorberMolsPerKG[iAbsorber], self.afMolarMass
            )
        ]
        mfLinearizationConstantPerAbsorber[iAbsorber] = [
            constant * afMass[self.tiN2I[absorber]] * molar_mass
            for constant, molar_mass in zip(
                mfLinearizationConstantPerAbsorberMolsPerKG[iAbsorber],
                self.afMolarMass,
            )
        ]

    # Summing up to one vector
    mfEquilibriumLoading = [
        sum(x) for x in zip(*mfEquilibriumLoadingPerAbsorber)
    ]
    mfLinearizationConstant = [
        sum(x) / len(csAbsorbers) for x in zip(*mfLinearizationConstantPerAbsorber)
    ]

    return mfEquilibriumLoading, mfLinearizationConstant


def calculateEquilibriumLoading_Zeolite5A(self, afPP, fTemperature):
    # Calculate parameters for Toth equation
    mf_A = (
        self.ttxMatter.Zeolite5A.tAbsorberParameters.tToth.mf_A0
        * np.exp(self.ttxMatter.Zeolite5A.tAbsorberParameters.tToth.mf_E / fTemperature)
    )
    mf_B = (
        self.ttxMatter.Zeolite5A.tAbsorberParameters.tToth.mf_B0
        * np.exp(self.ttxMatter.Zeolite5A.tAbsorberParameters.tToth.mf_E / fTemperature)
    )
    mf_t_T = (
        self.ttxMatter.Zeolite5A.tAbsorberParameters.tToth.mf_T0
        + self.ttxMatter.Zeolite5A.tAbsorberParameters.tToth.mf_C0 / fTemperature
    )

    mfLinearizationConstant = (
        mf_A / (1 + np.sum(mf_B * afPP)) ** mf_t_T
    ) ** (1.0 / mf_t_T)

    mfQ_equ = mfLinearizationConstant * afPP
    return mfQ_equ, mfLinearizationConstant
