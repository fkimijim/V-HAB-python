import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "sys")))
import Sys

Sys = Sys()

class Timed(Sys):
    """
    TIMED class adds timing-related properties and methods to derived classes.
    This abstract class provides a timer, a setTimeStep method for setting
    execution intervals, and an exec method for performing time-dependent
    actions.
    """

    def __init__(self, oParent, sName, fTimeStep=None):
        """
        Constructor for the Timed class.
        
        Args:
            oParent (object): Parent system.
            sName (str): Name of the system.
            fTimeStep (float or None): Initial time step (optional).
        """
        super().__init__(oParent, sName)

        # Setting the timer property
        self.oTimer = oParent.oTimer

        # Default properties
        self.fTimeStep = None
        self.fLastExec = -1
        self.fLastTimeStep = 0

        # Private properties for callbacks
        self.hSetTimeStepCB = None
        self.hUnbindTimerCB = None
        self.hUnbindParentCB = None

        # Set initial time step
        if fTimeStep is not None and fTimeStep != 0:
            self.set_time_step(fTimeStep)
        else:
            self.set_time_step()

    def exec(self, _=None):
        """
        Executes the actions required in a system.
        Contains operations like control logic for valves or system updates.
        """
        # Calculate the time since the last execution
        self.fLastTimeStep = self.oTimer.fTime - self.fLastExec

        # Trigger the exec event for bound objects
        self.trigger('exec', self.oTimer.fTime)

        # Update the last execution time
        self.fLastExec = self.oTimer.fTime

    def set_time_step(self, xTimeStep=None):
        """
        Sets the time step for the system's execution.
        
        Args:
            xTimeStep (float or bool or None): Time step for execution.
                - None or -1: Execute every tick.
                - False: Bind to parent's exec method.
                - Positive float: Use specified time step.
                - Negative float or 0: Use minimum time step.
        """
        if xTimeStep is None:
            xTimeStep = -1

        self.fTimeStep = xTimeStep

        if isinstance(xTimeStep, bool) and not xTimeStep:
            # Bind exec() to the parent system
            if self.hUnbindTimerCB:
                self.hUnbindTimerCB()
                self.hUnbindTimerCB = None
                self.hSetTimeStepCB = None

            if not self.hUnbindParentCB:
                _, self.hUnbindParentCB = self.oParent.bind('exec', self.exec)
        else:
            # Bind exec() to the timer object
            if self.hUnbindParentCB:
                self.hUnbindParentCB()
                self.hUnbindParentCB = None

            if not self.hUnbindTimerCB:
                # Register with the timer
                self.hSetTimeStepCB, self.hUnbindTimerCB = self.oTimer.bind(
                    self.exec,
                    xTimeStep,
                    {
                        'sMethod': 'exec',
                        'sDescription': 'The .exec method of a timed system',
                        'oSrcObj': self,
                    },
                )
            else:
                # Update the time step via the callback
                self.hSetTimeStepCB(xTimeStep)

            if self.fTimeStep <= 0:
                self.fTimeStep = self.oTimer.fMinimumTimeStep
