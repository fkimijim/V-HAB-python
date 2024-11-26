from abc import ABC, abstractmethod

class Monitor(ABC):
    """
    Basic class providing the framework for all other monitor subclasses.
    This class provides common functionality, including automatic binding to events
    posted by the simulation infrastructure.
    """

    def __init__(self, oSimulationInfrastructure, csEvents=None):
        """
        Constructor for the Monitor class.

        Parameters:
        - oSimulationInfrastructure: Reference to the simulation infrastructure object.
        - csEvents: List of events that the monitor implements (optional).
        """
        self.oSimulationInfrastructure = oSimulationInfrastructure

        # Events and their corresponding methods
        self.tsEvents = {
            'init_pre': self.onInitPre,
            'init_post': self.onInitPost,
            'step_pre': self.onStepPre,
            'step_post': self.onStepPost,
            'pause': self.onPause,
            'finish': self.onFinish,
            'run': self.onRun,
        }

        self.csEvents = csEvents or []

        # Bind events to their corresponding methods
        for sEvent in self.csEvents:
            if sEvent in self.tsEvents:
                self.oSimulationInfrastructure.bind(sEvent, self.tsEvents[sEvent])
            else:
                raise ValueError(f"Unknown event: {sEvent}")

    @abstractmethod
    def onInitPre(self, *args, **kwargs):
        """Placeholder for pre-initialization logic."""
        pass

    @abstractmethod
    def onInitPost(self, *args, **kwargs):
        """Placeholder for post-initialization logic."""
        pass

    @abstractmethod
    def onStepPre(self, *args, **kwargs):
        """Placeholder for pre-step logic."""
        pass

    @abstractmethod
    def onStepPost(self, *args, **kwargs):
        """Placeholder for post-step logic."""
        pass

    @abstractmethod
    def onPause(self, *args, **kwargs):
        """Placeholder for pause logic."""
        pass

    @abstractmethod
    def onFinish(self, *args, **kwargs):
        """Placeholder for finish logic."""
        pass

    @abstractmethod
    def onRun(self, *args, **kwargs):
        """Placeholder for run logic."""
        pass
