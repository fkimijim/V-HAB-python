import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "event")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "matter")))
import Flow
import Source
from phase.phase import Phase

MatterFlow = Flow()
EventSource = Source()
MatterPhase = Phase()

class P2P(MatterFlow, EventSource):
    """
    P2P (Phase-to-Phase) Processor

    Moves matter from one phase to another within a single store. It allows for phase changes 
    and specific substance transfers, such as condensation, vaporization, or selective 
    adsorption of substances like CO2 from air.
    """

    def __init__(self, oStore, sName, xIn, xOut):
        """
        Initializes the P2P processor.

        Args:
            oStore (object): Store object where the P2P is located.
            sName (str): Name of the processor.
            xIn (str or object): Input phase and ExMe name in dot notation ('phase.exme') or a phase object.
            xOut (str or object): Output phase and ExMe name in dot notation ('phase.exme') or a phase object.
        """
        super().__init__(oStore)
        self.sObjectType = 'p2p'
        self.sName = sName
        self.fLastUpdate = -1
        self.oThermalBranch = None
        self.fSpecificHeatCapacityP2P = None
        self.fPressureLastHeatCapacityUpdate = None
        self.fTemperatureLastHeatCapacityUpdate = None
        self.arPartialMassLastHeatCapacityUpdate = None
        self.hBindPostTickUpdate = None
        self.coExmes = []
        self.bTriggersetMatterPropertiesCallbackBound = False

        self._initialize_phases(oStore, sName, xIn, xOut)

    def _initialize_phases(self, oStore, sName, xIn, xOut):
        """
        Initializes input and output phases and ExMe connections.
        """
        oPhaseIn, sExMeIn = self._get_phase_and_exme(oStore, xIn, f"{sName}_In")
        oPhaseOut, sExMeOut = self._get_phase_and_exme(oStore, xOut, f"{sName}_Out")

        oPhaseIn.toProcsEXME[sExMeIn].addFlow(self)
        oPhaseOut.toProcsEXME[sExMeOut].addFlow(self)

        self.coExmes = [oPhaseIn.toProcsEXME[sExMeIn], oPhaseOut.toProcsEXME[sExMeOut]]

        self.hBindPostTickUpdate = oStore.oTimer.registerPostTick(self.update, 'matter', 'P2Ps')

    def _get_phase_and_exme(self, oStore, x, default_exme):
        """
        Retrieves or creates a phase and its associated ExMe.

        Args:
            oStore (object): Store object.
            x (str or object): Phase and ExMe name in dot notation or a phase object.
            default_exme (str): Default ExMe name if none provided.

        Returns:
            tuple: Phase object and ExMe name.
        """
        if isinstance(x, str):
            sPhase, sExMe = x.split('.') if '.' in x else (x, '')
            oPhase = getattr(oStore.toPhases, sPhase, None)
            if oPhase is None:
                raise ValueError(f"Phase could not be found: {sPhase}")
            if not sExMe:
                sExMe = default_exme
                oPhase.addExMe(sExMe)
        elif isinstance(x, MatterPhase):
            oPhase = x
            if oPhase.oStore != oStore:
                raise ValueError(f"P2P and phase are not in the same store: {oStore.sName}, {oPhase.oStore.sName}")
            sExMe = default_exme
            oPhase.addExMe(sExMe)
        else:
            raise ValueError(f"Invalid input for P2P: {x}")
        return oPhase, sExMe

    def setThermalBranch(self, oThermalBranch):
        """
        Sets the thermal branch for the P2P.

        Args:
            oThermalBranch (object): Thermal branch object.
        """
        self.oThermalBranch = oThermalBranch

    def getInEXME(self):
        """
        Retrieves the current input ExMe based on the flow direction.

        Returns:
            object: Input ExMe object.
        """
        return self.coExmes[1] if self.fFlowRate < 0 else self.coExmes[0]

    def registerUpdate(self):
        """
        Registers the post-tick callback for the P2P with the timer.
        """
        self.hBindPostTickUpdate()

    def update(self, fFlowRate=None, arPartials=None):
        """
        Updates the P2P flow rate and partial mass properties.

        Args:
            fFlowRate (float, optional): Total mass flow rate in kg/s.
            arPartials (list, optional): Partial mass ratios.
        """
        if fFlowRate is not None:
            self.setMatterProperties(fFlowRate, arPartials)
        elif arPartials is not None:
            self.setMatterProperties(fFlowRate, arPartials)
        else:
            self.setMatterProperties()
        self.fLastUpdate = self.oStore.oTimer.fTime

    def setMatterProperties(self, fFlowRate=None, arPartialMass=None, fTemperature=None, fPressure=None, arCompoundMass=None):
        """
        Sets the P2P matter flow properties.

        Args:
            fFlowRate (float, optional): Total flow rate in kg/s.
            arPartialMass (list, optional): Partial mass ratios.
            fTemperature (float, optional): Flow temperature.
            fPressure (float, optional): Flow pressure.
            arCompoundMass (list, optional): Compound mass properties.
        """
        if fFlowRate is None:
            fFlowRate = self.fFlowRate
        else:
            self.fFlowRate = fFlowRate

        oExme = self.getInEXME() if fFlowRate >= 0 else self.coExmes[1]

        self.arPartialMass = arPartialMass or oExme.oPhase.arPartialMass
        self.fTemperature = fTemperature or oExme.getExMeProperties()[1]
        self.fPressure = fPressure or oExme.getExMeProperties()[0]
        self.arCompoundMass = arCompoundMass or oExme.oPhase.arCompoundMass

        self.coExmes[0].oPhase.registerMassupdate()
        self.coExmes[1].oPhase.registerMassupdate()

        if self.fFlowRate == 0:
            self.fSpecificHeatCapacityP2P = 0
            return

        afMass = [ratio * self.fFlowRate for ratio in self.arPartialMass]
        self.fMolarMass = self.oMT.calculateMolarMass(afMass)

        if self.bTriggersetMatterPropertiesCallbackBound:
            self.trigger('setMatterProperties')
