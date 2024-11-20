from abc import ABC, abstractmethod
import terminal

class store(ABC):
    """
    A class describing a store of electrical energy.
    This abstract class describes a device that stores electrical energy, such as a battery.
    Stores have only two terminals: one positive and one negative. The main property is its
    capacity in Joules or Watt-seconds.
    """

    def __init__(self, oCircuit, sName, fCapacity=float('inf')):
        """
        Constructor for the store class.

        Parameters:
        - oCircuit: Reference to the circuit object.
        - sName: Name of the store.
        - fCapacity: Capacity of the store in [Ws] or [J] (default: inf).
        """
        self.oCircuit = oCircuit  # Reference to the circuit
        self.sName = sName  # Name of the store
        self.fCapacity = fCapacity  # Capacity of the store
        self.bSealed = False  # Indicates if the store is sealed
        self.oTimer = oCircuit.oTimer  # Reference to the timer
        self.fLastUpdate = 0  # Time of the last update
        self.fTimeStep = 0  # Time step of the store
        self.fFixedTimeStep = None  # Fixed time step for updating
        self.hSetTimeStep = None  # Handle to the timer's set time step method

        # Add this store to the circuit
        self.oCircuit.addStore(self)

        # Create positive and negative terminals
        self.oPositiveTerminal = terminal(self)
        self.oNegativeTerminal = terminal(self)

    def update(self):
        """
        Re-calculates the time step and updates the last update time.
        """
        self.calculateTimeStep()
        self.fLastUpdate = self.oTimer.fTime

    def seal(self):
        """
        Seals this store so nothing can be changed later on.
        """
        if self.bSealed:
            return

        if self.fFixedTimeStep is None:
            # Bind the `update` method to the timer with a default time step of 0
            self.hSetTimeStep = self.oTimer.bind(self.update, 0)
        else:
            self.hSetTimeStep = self.oTimer.bind(self.update, self.fFixedTimeStep)

        self.bSealed = True

    def getTerminal(self, sTerminalName):
        """
        Returns a reference to either the positive or negative terminal of the store.

        Parameters:
        - sTerminalName: 'positive' or 'negative'.

        Returns:
        - The corresponding terminal object.

        Raises:
        - ValueError: If the terminal name is invalid.
        """
        if sTerminalName == 'positive':
            return self.oPositiveTerminal
        elif sTerminalName == 'negative':
            return self.oNegativeTerminal
        else:
            raise ValueError(f"There is no terminal '{sTerminalName}' on store {self.sName}.")

    def setFixedTimeStep(self, fFixedTimeStep):
        """
        Sets a fixed time step for updating the store.

        Parameters:
        - fFixedTimeStep: Fixed time step to set.
        """
        self.fFixedTimeStep = fFixedTimeStep

    @abstractmethod
    def calculateTimeStep(self):
        """
        Abstract method to calculate the time step for the timer.
        Must be implemented by child classes.
        """
        pass
