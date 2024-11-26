import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "..")))
from core.matter.store.store import Store
from core.matter.phases.mixture import Mixture as pMixture
from core.matter.phases.flow.mixture import Mixture
from core.matter.procs.exmes.mixture import mixture
from lib.components.matter.P2Ps.ManualP2P import ManualP2P
from core.matter.branch import Branch

Store = Store()
Mixture = Mixture()
mixture = mixture()
pMixture = pMixture()
ManualP2P = ManualP2P()
Branch = Branch()

class FoodStore(Store):
    """
    Generic Store for food, includes the necessary exmes and functions to supply humans with food and receive food.
    """

    def __init__(self, oParentSys, sName, fVolume, tfFood):
        """
        Constructor for the FoodStore class.

        :param oParentSys: Parent system.
        :param sName: Name of the food store.
        :param fVolume: Volume of the food store (in m^3).
        :param tfFood: Initial food composition.
        """
        # Adding 1 m^3 for the human interface phases
        super().__init__(oParentSys, sName, fVolume + 1)

        # Create the food phase
        pMixture(
            self, "Food", "solid", tfFood, self.oMT.Standard.Temperature, self.oMT.Standard.Pressure
        )

        # Initialize properties
        self.iHumans = 0
        self.iInputs = 0
        self.oParent = oParentSys

    def registerHuman(self, sPort):
        """
        Registers a human to the food store.

        :param sPort: Port for the human connection.
        :return: Function to request food for the human.
        """
        self.iHumans += 1

        oPhase = Mixture(
            self,
            f"Food_Output_{self.iHumans}",
            "solid",
            [],
            self.oMT.Standard.Temperature,
            self.oMT.Standard.Pressure,
        )

        mixture(self.toPhases.Food, f"FoodPrepOut_{self.iHumans}")
        mixture(oPhase, f"FoodPrepIn_{self.iHumans}")

        ManualP2P(
            self,
            f"FoodPrepP2P_{self.iHumans}",
            f"Food.FoodPrepOut_{self.iHumans}",
            f"Food_Output_{self.iHumans}.FoodPrepIn_{self.iHumans}",
        )

        mixture(oPhase, f"Outlet_{self.iHumans}")

        Branch(
            self.oParent, sPort, {}, f"{self.sName}.Outlet_{self.iHumans}", f"Food_Out_{self.iHumans}"
        )

        iHuman = self.iHumans

        def requestFood(*args):
            return self.requestFood(iHuman, *args)

        return requestFood

    def registerInput(self, _):
        """
        Registers an input to the food store.

        :return: The name of the input exme.
        """
        self.iInputs += 1
        sInputExme = f"FoodIn_{self.iInputs}"
        mixture(self.toPhases.Food, sInputExme)
        return sInputExme

    def requestFood(self, iHuman, fEnergy, fTime, arComposition=None):
        """
        Requests food for a human.

        :param iHuman: The human ID requesting the food.
        :param fEnergy: Energy required in joules.
        :param fTime: Time over which the food is consumed, in seconds.
        :param arComposition: (Optional) Desired composition of the food.
        :return: Partial masses of the food provided.
        """
        oP2P = self.toProcsP2P[f"FoodPrepP2P_{iHuman}"]

        if arComposition is not None:
            afResolvedFoodMass = self.oMT.resolveCompoundMass(
                arComposition, self.toPhases.Food.arCompoundMass
            )

            fNutritionalEnergy = sum(afResolvedFoodMass * self.oMT.afNutritionalEnergy)

            fMassToTransfer = fEnergy / fNutritionalEnergy

            afPartialMasses = arComposition * fMassToTransfer

            abLimitedFoodSupply = self.toPhases.Food.afMass < afPartialMasses
            if any(abLimitedFoodSupply):
                csLimitedFood = [
                    self.oMT.csI2N[i] for i, limited in enumerate(abLimitedFoodSupply) if limited
                ]
                for sFood in csLimitedFood:
                    fFoodRequested = afPartialMasses[self.oMT.tiN2I[sFood]]
                    fFoodAvailable = self.toPhases.Food.afMass[self.oMT.tiN2I[sFood]]
                    print(
                        f"A Human is going hungry because {fFoodRequested} kg of {sFood} "
                        f"were requested but only {fFoodAvailable} kg of it were available."
                    )

                afPartialMasses[abLimitedFoodSupply] = self.toPhases.Food.afMass[abLimitedFoodSupply]

        else:
            afResolvedMass = self.oMT.resolveCompoundMass(
                self.toPhases.Food.afMass, self.toPhases.Food.arCompoundMass
            )
            afNutritionalEnergy = afResolvedMass * self.oMT.afNutritionalEnergy
            fNutritionalEnergy = sum(afNutritionalEnergy)

            afPartialMasses = self.toPhases.Food.arPartialMass * (
                (self.toPhases.Food.fMass / fNutritionalEnergy) * fEnergy
            )

        if fNutritionalEnergy == 0:
            afPartialMasses = [0] * self.oMT.iSubstances
            print(f"A Human is going hungry because there is nothing edible left in store {self.sName}")

        oP2P.setMassTransfer(afPartialMasses, fTime)
        return afPartialMasses
