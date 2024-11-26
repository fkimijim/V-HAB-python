class Battery:
    """
    Simple Battery Model
    This simple battery model updates its charge based on the
    outflowing current. If the charge reaches zero, the battery
    sets its voltage to zero and displays a message to the user.
    """

    def __init__(self, oCircuit, sName, fCapacity, fVoltage):
        """
        Constructor for the Battery class.

        :param oCircuit: The electrical circuit this battery belongs to
        :param sName: Name of the battery
        :param fCapacity: Initial battery capacity (ampere-hours) [Ah]
        :param fVoltage: Initial battery voltage [V]
        """
        # Parent class initialization
        self.oCircuit = oCircuit
        self.sName = sName
        self.fVoltage = fVoltage
        self.fMaxVoltage = 20.5
        self.fMaxCurrent = 5

        # Terminals with constant voltages
        self.oPositiveTerminal = Terminal(fVoltage)
        self.oNegativeTerminal = Terminal(0)

        # Initializing the battery charge
        self.fCharge = fCapacity

        # Timer and last update time
        self.oTimer = Timer()  # This represents a global or shared timer
        self.fLastUpdate = self.oTimer.get_time()

    def update(self):
        """
        Updates the battery state based on elapsed time and current flow.
        """
        # Get elapsed time since the last update
        fElapsedTime = self.oTimer.get_time() - self.fLastUpdate

        # If no time has passed since the last update, return early
        if fElapsedTime == 0:
            return

        # Calculate the change in charge
        fCurrent = self.oPositiveTerminal.oFlow.get_current()
        self.fCharge -= fElapsedTime / 3600 * fCurrent

        # Check if the battery is empty
        if round(self.fCharge, 7) <= 0:
            self.fCharge = 0
            self.fVoltage = 0
            self.oPositiveTerminal.set_voltage(0)
            self.oNegativeTerminal.set_voltage(0)
            print(f"{self.oTimer.get_tick()} ({self.oTimer.get_time():.7f}s) Battery '{self.sName}' is empty.")

        # Call parent class update (if applicable)
        # This can trigger additional behavior such as time step calculations
        self.parent_update()

    def parent_update(self):
        """
        Placeholder for calling the parent class's update method.
        To be implemented as needed for inherited behavior.
        """
        pass


class Terminal:
    """
    Represents a terminal in the electrical circuit.
    """

    def __init__(self, voltage):
        self.voltage = voltage
        self.oFlow = Flow()

    def set_voltage(self, voltage):
        self.voltage = voltage


class Flow:
    """
    Represents the current flow in the circuit.
    """

    def __init__(self):
        self.fCurrent = 0  # Initial current [A]

    def get_current(self):
        return self.fCurrent


class Timer:
    """
    Represents a timer for tracking simulation time.
    """

    def __init__(self):
        self.fTime = 0.0  # Current time [s]
        self.iTick = 0    # Current tick count

    def get_time(self):
        """
        Returns the current time in seconds.
        """
        return self.fTime

    def get_tick(self):
        """
        Returns the current tick count.
        """
        return self.iTick
