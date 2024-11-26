from abc import ABC, abstractmethod
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "matter")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "thermal")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "electrical")))
from matter.phase import Phase
from thermal import Capacity
from electrical import Component, Node, terminal
from matter.procs.exme import ExMe as MExMe
from thermal.procs import ExMe as TExMe

Phase = Phase()
Capacity = Capacity()
Component = Component()
Node = Node()
MatterProcExMe = MExMe()
ThermalProcExMe = TExMe()
ElectricalTerminal = terminal()

class Branch(ABC):
    """
    Abstract class describing the flow path between two objects.
    This is the base class for all branches in different domains, such as matter or energy.
    """

    def __init__(self, oContainer, xLeft, csProcs, xRight, sCustomName=None, sType=None):
        """
        Initializes a branch with the given container, left port, components, and right port.

        Args:
            oContainer: Parent container.
            xLeft: Left port.
            csProcs: List of components.
            xRight: Right port.
            sCustomName: Custom name for the branch (optional).
            sType: Type of the branch, e.g., 'matter', 'thermal' (optional).
        """
        self.oContainer = oContainer
        self.sCustomName = sCustomName
        self.sType = sType
        self.bSealed = False
        self.bOutdated = False

        self.csNames = ["", ""]
        self.abIf = [False, False]
        self.coExmes = [None, None]
        self.coBranches = [None, None]
        self.oHandler = None

        self.sName = None
        self.oMT = None
        self.oTimer = None

        if sType in ["matter", "thermal"]:
            self.oRoot = oContainer.oRoot
        elif sType == "electrical":
            self.oRoot = oContainer.oParent.oRoot

        self.oMT = self.oRoot.oMT
        self.oTimer = self.oRoot.oTimer

        # Handle custom name
        if sCustomName:
            self.sCustomName = sCustomName

        # Handle the left side
        sLeftSideName = self._handle_side("left", xLeft)

        # Add the components/processors to the branch
        self.createProcs(csProcs)

        # Handle the right side
        sRightSideName = self._handle_side("right", xRight)

        # Set the name property for this branch object
        self.csNames = [sLeftSideName, sRightSideName]
        sTempName = f"{sLeftSideName}___{sRightSideName}"
        self.sName = self._normalize_path(sTempName)

    def _normalize_path(self, path):
        """
        Normalizes a given path to ensure it adheres to name length constraints.
        """
        max_length = 63  # MATLAB-like maximum field name length
        return path[:max_length]

    def _handle_side(self, side, xInput):
        """
        Handles the left or right side of a branch.

        Args:
            side (str): Either 'left' or 'right'.
            xInput: Input for the side.

        Returns:
            str: Name of the side.
        """
        iSideIndex = 0 if side == "left" else 1
        bCreatePort = False
        bInterface = False

        # Determine the type of xInput
        if isinstance(xInput, (Phase, Capacity, Component, Node)):
            bCreatePort = True
        elif isinstance(xInput, str) and "." not in xInput:
            bInterface = True

        if bInterface:
            self.abIf[iSideIndex] = True
            sSideName = xInput
        else:
            if bCreatePort:
                oExMe, sSideName = self._create_ports(xInput)
            else:
                sObject, sExMe = xInput.split(".", 1)
                if self.sType == "matter":
                    oExMe = self.oContainer.toStores[sObject].getExMe(sExMe)
                elif self.sType == "thermal":
                    oExMe = self.oContainer.toStores[sObject].getThermalExMe(sExMe)
                elif self.sType == "electrical":
                    oExMe = self.oContainer.toNodes[sObject].getTerminal(sExMe)
                sSideName = xInput.replace(".", "__")

            self.coExmes[iSideIndex] = oExMe

        return sSideName

    def _create_ports(self, xInput):
        """
        Automatically generates ports for the given input.

        Args:
            xInput: Input object.

        Returns:
            tuple: Created port and side name.
        """
        if self.sType == "matter":
            csPorts = xInput.oStore.csExMeNames
            iNumber = len(csPorts) + 1 if csPorts else 1
            sPortName = f"Port_{iNumber}"
            oExMe = MatterProcExMe(xInput, sPortName)
            sSideName = f"{xInput.oStore.sName}__{sPortName}"
        elif self.sType == "thermal":
            toPorts = xInput.toProcsEXME
            iNumber = len(toPorts) + 1 if toPorts else 1
            sPortName = f"Port_{iNumber}"
            oExMe = ThermalProcExMe(xInput, sPortName)
            sSideName = f"{xInput.oPhase.oStore.sName}__{sPortName}"
        elif self.sType == "electrical":
            toPorts = xInput.toTerminals
            iNumber = len(toPorts) + 1 if toPorts else 1
            sPortName = f"Port_{iNumber}"
            oExMe = ElectricalTerminal(xInput, sPortName)
            sSideName = f"{xInput.sName}__{sPortName}"

        return oExMe, sSideName

    def connectTo(self, sInterface):
        """
        Connects this branch to an interface.

        Args:
            sInterface (str): Name of the interface to connect to.
        """
        pass

    def setOutdated(self):
        """
        Marks the branch as outdated, triggering updates for recalculation.
        """
        if not self.bOutdated:
            self.bOutdated = True
            self._trigger_event("outdated")

    def _trigger_event(self, event_name):
        """
        Placeholder for triggering events.

        Args:
            event_name (str): Name of the event.
        """
        pass

    @abstractmethod
    def createProcs(self, csProcs):
        """
        Abstract method to create components for the branch.
        """
        pass
