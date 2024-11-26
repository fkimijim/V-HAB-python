import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sys")))
import Sys

Sys = Sys()

class Root(Sys):
    """
    Root system of a V-HAB Simulation.
    Every system object needs a parent, except for this one. The root system
    is the top-level system in a V-HAB simulation, and its parent property
    points to itself. Other than that, it functions like any other system.
    """

    def __init__(self, sName):
        """
        Constructor for the root system.
        
        Args:
            sName (str): Name of the root system.
        """
        # Call the parent constructor, passing None as the parent.
        # This bypasses the parent check in Sys.
        super().__init__(None, sName)
        
        # Setting the root reference to itself
        self.oRoot = self

    def set_parent(self, _):
        """
        Overridden method to prevent assigning a parent.
        The root system points to itself as its parent.
        """
        self.oParent = self
