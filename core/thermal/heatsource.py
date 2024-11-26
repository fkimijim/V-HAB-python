import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "base")))
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "event")))
from branch import Branch
from event.source import Source

BaseBranch = Branch()
EventSource = Source()

class HeatSource(BaseBranch, EventSource):
    """
    A heat source connected to a thermal capacity object.
    Modifies the internal energy of the connected capacity via the `fHeatFlow` property.
    """

    def __init__(self, sName, fHeatFlow=0):
        """
        Create a heat source.

        Args:
            sName (str): The name of the heat source.
            fHeatFlow (float): Initial heat flow in watts (optional, default is 0).
        """
        super().__init__()
        self.sName = sName
        self.fHeatFlow = fHeatFlow  # Current heat flow [W]
        self.fRequestedHeatFlow = fHeatFlow  # Requested heat flow [W]
        self.oCapacity = None  # Reference to the connected capacity
        self.hBindPostTickUpdate = None  # Handle to bind post-tick update
        self.chUnbindFunctions = []  # List of unbind functions
        self.bTriggerUpdateCallbackBound = False  # Trigger for update callback
        self.bTriggerSetFlowRateCallbackBound = False  # Trigger for flow rate callback

    def setHeatFlow(self, fHeatFlow):
        """
        Change the heat flow of the heat source.

        Args:
            fHeatFlow (float): New heat flow in watts.
        """
        self.fRequestedHeatFlow = fHeatFlow

        # Update the connected capacity if the heat flow changes
        if self.fHeatFlow != self.fRequestedHeatFlow:
            if self.oCapacity:
                self.oCapacity.setOutdatedTS()
                if self.hBindPostTickUpdate:
                    self.hBindPostTickUpdate()

        # Trigger event if there are listeners for the heat flow change
        if self.bTriggerSetFlowRateCallbackBound:
            self.trigger('setHeatFlow', {
                'fHeatFlowOld': self.fHeatFlow,
                'fHeatFlow': self.fRequestedHeatFlow
            })

    def setCapacity(self, oCapacity):
        """
        Assign a capacity to the heat source.

        Args:
            oCapacity: The thermal capacity object to connect to.
        """
        if self.oCapacity is None:
            self.oCapacity = oCapacity
            self.hBindPostTickUpdate, unbind_fn = self.oCapacity.oTimer.registerPostTick(
                self.updateHeatFlow, 'thermal', 'heatsources'
            )
            self.chUnbindFunctions.append(unbind_fn)
        else:
            raise ValueError("Heatsource already has a capacity object.")

    def bind(self, sType, callBack):
        """
        Bind a callback to an event and set trigger flags accordingly.

        Args:
            sType (str): Event type to bind to.
            callBack (callable): The callback function.
        """
        super().bind(sType, callBack)

        if sType == 'update':
            self.bTriggerUpdateCallbackBound = True
        elif sType == 'setHeatFlow':
            self.bTriggerSetFlowRateCallbackBound = True

    def updateHeatFlow(self):
        """
        Update the heat flow to the requested value.
        """
        self.fHeatFlow = self.fRequestedHeatFlow
