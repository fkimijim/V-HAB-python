class Resin(vsys):
    """
    Creates resins for the MFBeds, based on dynamic modeling of the 
    Water Processor Assembly of the International Space Station.
    """

    def __init__(self, oParent, sName, rVoidFraction, fResinMass, fTotalCapacity,
                 fVolume, bCationResin, bStrong, iCells, fEmptyBedContactTime, bModelCellMass=False):
        super().__init__(oParent, sName, float('inf'))
        eval(self.oRoot.oCfgParams.configCode(self))

        self.rVoidFraction = rVoidFraction
        self.fResinMass = fResinMass
        self.fTotalCapacity = fTotalCapacity
        self.fVolume = fVolume
        self.bCationResin = bCationResin
        self.bStrong = bStrong
        self.iCells = iCells
        self.fEmptyBedContactTime = fEmptyBedContactTime
        self.bModelCellMass = bModelCellMass

        self.iPresaturant = None
        self.abContaminants = [False] * self.oMT.iSubstances

    def createMatterStructure(self):
        super().createMatterStructure()

        self.toStores['Resin'] = matter.store(self, 'Resin', self.fVolume)
        fVolumeFilter = self.fVolume

        # Creating ion phases and presaturating them
        if self.bCationResin:
            self.iPresaturant = self.oMT.tiN2I.Hplus
            tfIonMasses = {
                'Hplus': (self.fResinMass * self.fTotalCapacity * self.oMT.afMolarMass[self.iPresaturant]) / self.iCells
            }
        else:
            self.iPresaturant = self.oMT.tiN2I.OH
            tfIonMasses = {
                'OH': (self.fResinMass * self.fTotalCapacity * self.oMT.afMolarMass[self.iPresaturant]) / self.iCells
            }

        # Creating phases and P2Ps for each cell
        for iCell in range(1, self.iCells + 1):
            # Resin phase for this cell
            oResinPhase = matter.phases.mixture(
                self.toStores['Resin'], f"Resin_{iCell}", 'liquid', tfIonMasses, 293, 1e5
            )

            # Water phase for this cell
            if self.bModelCellMass:
                oWaterPhase = self.toStores['Resin'].createPhase(
                    'mixture', f"Water_{iCell}", 'liquid',
                    self.rVoidFraction * fVolumeFilter / self.iCells,
                    {'H2O': 1}, 293, 1e5
                )
                oDesorptionP2P = components.matter.WPA.components.stationaryDesorption_P2P(
                    self.toStores['Resin'], f"Ion_Desorption_P2P{iCell}", oWaterPhase, oResinPhase
                )

                if self.bStrong:
                    oP2P = components.matter.WPA.components.stationaryMixedBed_P2P(
                        self.toStores['Resin'], f"Ion_P2P{iCell}", oWaterPhase, oResinPhase, oDesorptionP2P
                    )
                else:
                    oP2P = components.matter.WPA.components.stationaryWeakBaseAnion_P2P(
                        self.toStores['Resin'], f"Ion_P2P{iCell}", oWaterPhase, oResinPhase, oDesorptionP2P
                    )
            else:
                oWaterPhase = self.toStores['Resin'].createPhase(
                    'mixture', 'flow', f"Water_{iCell}", 'liquid',
                    self.rVoidFraction * fVolumeFilter / self.iCells,
                    {'H2O': 1}, 293, 1e5
                )
                oDesorptionP2P = components.matter.WPA.components.flowDesorption_P2P(
                    self.toStores['Resin'], f"Ion_Desorption_P2P{iCell}", oWaterPhase, oResinPhase
                )

                if self.bStrong:
                    oP2P = components.matter.WPA.components.flowMixedBed_P2P(
                        self.toStores['Resin'], f"Ion_P2P{iCell}", oWaterPhase, oResinPhase, oDesorptionP2P
                    )
                else:
                    oP2P = components.matter.WPA.components.flowWeakBaseAnion_P2P(
                        self.toStores['Resin'], f"Ion_P2P{iCell}", oWaterPhase, oResinPhase, oDesorptionP2P
                    )

            self.abContaminants = [
                a or b for a, b in zip(self.abContaminants, oP2P.abIons)
            ]

            # Creating a branch between consecutive cells
            if iCell > 1:
                matter.branch(
                    self, oPreviousWaterPhase, {}, oWaterPhase,
                    f"Cell_{iCell-1}_to_Cell_{iCell}"
                )

            oPreviousWaterPhase = oWaterPhase

    def createSolverStructure(self):
        super().createSolverStructure()

        # Time step properties for thermal solvers
        self.setThermalSolvers()

        csStoreNames = self.toStores.keys()
        for store_name in csStoreNames:
            for phase in self.toStores[store_name].aoPhases:
                tTimeStepProperties = {'fMaxStep': self.oParent.oParent.fTimeStep * 5}
                phase.setTimeStepProperties(tTimeStepProperties)
                phase.oCapacity.setTimeStepProperties(tTimeStepProperties)

    def exec(self, _):
        super().exec(_)
