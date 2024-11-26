class MultifiltrationBED(vsys):
    """
    Creates the MFBed from different resin beds.

    Based on the dynamic modeling of the Water Processor Assembly (WPA) 
    of the International Space Station.
    """

    def __init__(self, oParent, sName, miCells, bModelCellMass=False, bIonBed=False):
        super().__init__(oParent, sName, 60)

        self.bModelCellMass = bModelCellMass
        self.bIonBed = bIonBed
        self.abContaminants = [False] * self.oMT.iSubstances

        x = 2.21 / 132.6  # Linear approximation based on EBCT

        # Resin mass and total capacity setup
        mfResinMass = [
            0.4 * 4522e-3,
            0.6 * 4522e-3,
            374.6e-3,
            2042.1e-3,
            x * (0.4 * 4522e-3),
            x * (0.6 * 4522e-3),
            106e-3,
        ]

        self.mfTotalCapacity = [
            4.72,
            2.64,
            5.70,
            4.72,
            4.72,
            2.64,
            4.72,
        ]

        mfEmptyBedContactTime = [
            0.4 * 150 * 60,
            0.4 * 150 * 60,
            8.8 * 60,
            59 * 60,
            x * (0.4 * 150 * 60),
            x * (0.4 * 150 * 60),
            2.3 * 60,
        ]

        # Create individual ion exchange resins
        self.children = []
        self.mfCurrentFillState = [0] * len(mfResinMass)

        for i, (resin_mass, capacity, ebct) in enumerate(
            zip(mfResinMass, self.mfTotalCapacity, mfEmptyBedContactTime), start=1
        ):
            is_cation = i in {1, 3, 5, 7}
            is_strong = i not in {4}
            child = components.matter.WPA.subsystems.Resin(
                self,
                f"Resin_{i}",
                0.28 if i != 4 else 0.29,
                resin_mass,
                capacity,
                5.72e-3 if i in {1, 2, 5, 6} else (0.422e-3 if i == 3 else 0.094e-3),
                is_cation,
                is_strong,
                miCells[i - 1],
                ebct,
                self.bModelCellMass,
            )
            self.children.append(child)

    def createMatterStructure(self):
        super().createMatterStructure()

        oPreviousLastWaterPhaseResin = None

        # Connect resin compartments
        for i, child in enumerate(self.children, start=1):
            oFirstWaterPhaseResin = child.toStores.Resin.toPhases.Water_1
            iCells = child.iCells

            if i > 1:
                if not self.bModelCellMass:
                    fResinWaterVolume = child.fVolume * child.rVoidFraction
                    store_name = f"ResinStore_{i-1}"
                    self.toStores[store_name] = matter.store(self, store_name, fResinWaterVolume)

                    oWater = self.toStores[store_name].createPhase(
                        "mixture",
                        "Water",
                        "liquid",
                        fResinWaterVolume,
                        {"H2O": 1},
                        293,
                        1e5,
                    )

                    matter.branch(
                        self,
                        oPreviousLastWaterPhaseResin,
                        {},
                        oWater,
                        f"Resin{i-1}_to_ResinStore",
                    )
                    matter.branch(
                        self, oWater, {}, oFirstWaterPhaseResin, f"Resin{i-1}_to_{i}"
                    )
                else:
                    matter.branch(
                        self,
                        oPreviousLastWaterPhaseResin,
                        {},
                        oFirstWaterPhaseResin,
                        f"Resin{i-1}_to_{i}",
                    )

            oPreviousLastWaterPhaseResin = child.toStores.Resin.toPhases[
                f"Water_{iCells}"
            ]
            self.abContaminants = [
                a or b for a, b in zip(self.abContaminants, child.abContaminants)
            ]

        # Organic component removal
        if not self.bIonBed:
            self.toStores["OrganicRemoval"] = matter.store(self, "OrganicRemoval", 0.01)
            oWater = self.toStores["OrganicRemoval"].createPhase(
                "mixture", "flow", "Water", "liquid", 0.005, {"H2O": 1}, 293, 1e5
            )
            oOrganics = matter.phases.mixture(
                self.toStores["OrganicRemoval"], "BigOrganics", "liquid", {}, 293, 1e5
            )

            components.matter.WPA.components.OrganicBed_P2P(
                self.toStores["OrganicRemoval"], "BigOrganics_P2P", oWater, oOrganics
            )

            matter.branch(
                self,
                oPreviousLastWaterPhaseResin,
                {},
                oWater,
                f"Resin{i}_Cell{iCells}_to_OrganicRemoval",
            )

    def createSolverStructure(self):
        super().createSolverStructure()

        # Time step settings for big organics phase
        tTimeStepProperties = {"rMaxChange": float("inf"), "fMaxStep": float("inf")}

        if not self.bIonBed:
            self.toStores["OrganicRemoval"].toPhases.BigOrganics.setTimeStepProperties(
                tTimeStepProperties
            )

        if not self.bModelCellMass:
            for i in range(len(self.children) - 1):
                tTimeStepProperties = {"rMaxChange": 0.1}
                arMaxChange = [0] * self.oMT.iSubstances
                for j, cont in enumerate(self.abContaminants):
                    if cont:
                        arMaxChange[j] = 0.1
                tTimeStepProperties["arMaxChange"] = arMaxChange
                self.toStores[f"ResinStore_{i}"].toPhases.Water.setTimeStepProperties(
                    tTimeStepProperties
                )

        for store_name, store in self.toStores.items():
            for phase in store.aoPhases:
                tTimeStepProperties["fMaxStep"] = self.oParent.fTimeStep * 5
                phase.setTimeStepProperties(tTimeStepProperties)

    def exec(self, _):
        super().exec(_)

        for i, child in enumerate(self.children, start=1):
            oStore = child.toStores.Resin

            fRemainingCapacity = 0
            for iCell in range(1, child.iCells + 1):
                phase = oStore.toPhases[f"Resin_{iCell}"]
                fRemainingCapacity += sum(
                    (phase.afMass[child.iPresaturant] / self.oMT.afMolarMass[child.iPresaturant])
                    * abs(self.oMT.aiCharge[child.iPresaturant])
                ) / child.fResinMass

            self.mfCurrentFillState[i - 1] = 1 - fRemainingCapacity / self.mfTotalCapacity[i - 1]
