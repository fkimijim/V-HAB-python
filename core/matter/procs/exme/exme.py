import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import Flow
from p2ps.flow import FlowP2P
from p2ps.stationary import StationaryP2P
import MatterBranch

MatterFlow = Flow()
MatterProcP2PFlow = FlowP2P()
MatterProcP2PStationary = StationaryP2P()
SolverMatterMultiBranchIterativeBranch = MatterBranch()

class ExMe:
    """
    ExMe (Extract/Merge) processor

    The ExMe is the basic port within V-HAB to remove or add mass to a phase.
    It is used by both branches and P2Ps to connect two different phases. ExMes
    can also be created automatically by providing a phase object as reference
    during branch definition.
    """

    def __init__(self, oPhase, sName):
        """
        Initializes the ExMe object.

        Args:
            oPhase (object): The phase the ExMe is attached to.
            sName (str): The name of the processor.
        """
        if sName in oPhase.oStore.csExMeNames:
            raise ValueError(f"An ExMe named '{sName}' already exists in store '{oPhase.oStore.sName}'.")

        self.sName = sName
        self.oMT = oPhase.oMT
        self.oTimer = oPhase.oTimer

        self.oPhase = oPhase
        self.oFlow = None
        self.bHasFlow = False
        self.bFlowIsAProcP2P = False
        self.iSign = 0

        self.oNewPhase = None
        self.hReconnectExme = self.oTimer.registerPostTick(self.reconnectExMePostTick, 'matter', 'post_phase_update')

        oPhase.addProcEXME(self)

    def addFlow(self, oFlow):
        """
        Adds a flow to this ExMe and sets the corresponding properties.

        Args:
            oFlow (object): The matter flow object to connect to this ExMe.

        Raises:
            ValueError: If the flow is invalid or the store is sealed.
        """
        if self.oPhase.oStore.bSealed:
            raise ValueError("Cannot add ports to a sealed store.")

        if self.oFlow:
            raise ValueError("A flow is already connected to this ExMe. Create another one.")

        if not isinstance(oFlow, MatterFlow):
            raise ValueError("The provided flow object is not a MatterFlow.")

        self.oFlow = oFlow
        self.bHasFlow = True
        self.bFlowIsAProcP2P = isinstance(oFlow, (MatterProcP2PFlow, MatterProcP2PStationary))

        try:
            self.iSign = oFlow.addProc(self, lambda: self.removeFlow())
        except Exception as err:
            self.oFlow = None
            raise err

    def reconnectExMe(self, oNewPhase):
        """
        Changes the phase to which the ExMe is connected.

        Args:
            oNewPhase (object): The new phase to connect to.
        """
        if self.oPhase == oNewPhase:
            return

        self.oNewPhase = oNewPhase
        self.hReconnectExme()

        if self.iSign == 1:
            iExme = 2
        else:
            iExme = 1

        self.oFlow.oBranch.oThermalBranch.coExmes[iExme].reconnectExMe(oNewPhase.oCapacity, True)

    def getFlowData(self, fFlowRate=None):
        """
        Retrieves information about the ExMe flow properties.

        Args:
            fFlowRate (float, optional): Mass flow rate in kg/s. Defaults to the flow's rate.

        Returns:
            tuple: Flow rate, partial mass ratios, flow properties, compound masses.
        """
        if fFlowRate is not None:
            fFlowRate *= self.iSign
        else:
            fFlowRate = self.oFlow.fFlowRate * self.iSign

        if self.bFlowIsAProcP2P:
            arPartials = self.oFlow.arPartialMass
            afProperties = [self.oFlow.fTemperature, self.oFlow.fSpecificHeatCapacity]
            arCompoundMass = self.oFlow.arCompoundMass
        else:
            if fFlowRate > 0:
                if self.oFlow.fFlowRate >= 0:
                    arPartials = self.oFlow.oBranch.coExmes[0].oPhase.arPartialMass
                else:
                    arPartials = self.oFlow.oBranch.coExmes[1].oPhase.arPartialMass

                afProperties = [self.oFlow.fTemperature, self.oFlow.fSpecificHeatCapacity]
                arCompoundMass = self.oFlow.arCompoundMass
            else:
                arPartials = self.oPhase.arPartialMass
                arCompoundMass = self.oPhase.arCompoundMass

                try:
                    afProperties = [self.oPhase.fTemperature, self.oPhase.oCapacity.fSpecificHeatCapacity]
                except AttributeError:
                    afProperties = [self.oPhase.fTemperature, self.oMT.calculateSpecificHeatCapacity(self.oPhase)]

        return fFlowRate, arPartials, afProperties, arCompoundMass

    def removeFlow(self):
        """
        Removes the flow from this ExMe.
        """
        self.oFlow = None
        self.iSign = 0

    def reconnectExMePostTick(self):
        """
        Reconnects the ExMe to a new phase during the post-tick phase.
        """
        if self.oFlow.oBranch.coExmes[0] == self:
            if self.oNewPhase.oStore.oContainer != self.oPhase.oStore.oContainer:
                raise RuntimeError(f"Cannot change the left-hand ExMe to a phase in a different system ({self.sName}).")

        oOldPhase = self.oPhase
        self.oPhase = self.oNewPhase
        oOldPhase.removeExMe(self)
        self.oPhase.addExMe(self)
        self.oNewPhase = None

        if isinstance(self.oFlow.oBranch.oHandler, SolverMatterMultiBranchIterativeBranch):
            self.oFlow.oBranch.oHandler.initialize()

    def disconnectFlow(self):
        """
        Disconnects the ExMe from its connected flow.
        """
        self.oFlow = None

    def reconnectFlow(self, oFlow):
        """
        Reconnects the ExMe to a previously disconnected flow.

        Args:
            oFlow (object): The flow to reconnect to.
        """
        self.oFlow = oFlow
