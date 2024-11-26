class Timer:
    """
    Timer class handles all timing operations within the simulation framework.
    """

    def __init__(self, fMinimumTimeStep=1e-8, fStart=None):
        """
        Initializes the Timer object.

        Args:
            fMinimumTimeStep (float): Minimum allowed time step.
            fStart (float): Start time for the simulation.
        """
        self.fMinimumTimeStep = fMinimumTimeStep
        self.fStart = fStart if fStart is not None else -1 * fMinimumTimeStep
        self.fTime = self.fStart
        self.fTimeStep = 0
        self.fTimeStepFinal = 0
        self.iTick = -1

        # Callback-related properties
        self.cCallBacks = []
        self.afTimeSteps = []
        self.afLastExec = []
        self.ctPayload = []
        self.abDependent = []

        # Post-tick execution properties
        self.txPostTicks = {
            'matter': {
                'phase_massupdate': [],
                'volumeManips': [],
                'phase_update': [],
                'solver': [],
                'P2Ps': [],
                'substanceManips': [],
                'multibranch_solver': [],
                'residual_solver': []
            },
            'electrical': {
                'circuits': []
            },
            'thermal': {
                'capacity_temperatureupdate': [],
                'solver': [],
                'heatsources': [],
                'multibranch_solver': [],
                'residual_solver': [],
                'flow_capacity_temperatureupdate': []
            },
            'post_physics': {
                'timestep': []
            }
        }

        self.csPostTickGroups = list(self.txPostTicks.keys())
        self.tiPostTickGroup = {}
        self.tcsPostTickLevel = {}
        self.aiNumberOfPostTickLevel = []
        self.cabPostTickControl = {}
        self.abCallbacksRegistered = []

        self.iCurrentPostTickGroup = 0
        self.iCurrentPostTickLevel = 0

        self._initialize_post_ticks()

    def _initialize_post_ticks(self):
        """
        Initializes the post-tick structures for execution order.
        """
        for group_index, (group_name, levels) in enumerate(self.txPostTicks.items(), start=1):
            self.tiPostTickGroup[group_name] = group_index
            self.tcsPostTickLevel[group_name] = []

            for level_name in levels.keys():
                pre_level = f"pre_{level_name}"
                post_level = f"post_{level_name}"

                self.txPostTicks[group_name][pre_level] = []
                self.txPostTicks[group_name][post_level] = []

                self.tcsPostTickLevel[group_name].extend([pre_level, level_name, post_level])

            self.aiNumberOfPostTickLevel.append(len(self.tcsPostTickLevel[group_name]))

    def setMinStep(self, fMinStep):
        """
        Sets the minimum time step of the solver.
        """
        self.fMinimumTimeStep = fMinStep
        self.fTime = -1 * self.fMinimumTimeStep

    def synchronizeCallBacks(self):
        """
        Sets a flag to resynchronize all callbacks.
        """
        self.bSynchronizeExecuteCallBack = True

    def setSimulationPrecision(self, iPrecision):
        """
        Sets the precision of the simulation (e.g., rounding small values to zero).
        """
        self.iPrecision = iPrecision

    def bind(self, hCallBack, fTimeStep=None, tInputPayload=None):
        """
        Registers a callback with the timer object.

        Args:
            hCallBack (function): Callback function to bind.
            fTimeStep (float): Time step for the callback.
            tInputPayload (dict): Optional payload for debugging.

        Returns:
            tuple: A handle to set the time step and a handle to unbind the callback.
        """
        tPayload = {'oSrcObj': None, 'sMethod': None, 'sDescription': None, 'cAdditional': []}
        if tInputPayload and isinstance(tInputPayload, dict):
            tPayload.update(tInputPayload)

        iIdx = len(self.afTimeSteps)

        self.cCallBacks.append(hCallBack)
        self.afLastExec.append(-float('inf'))
        self.ctPayload.append(tPayload)
        self.afTimeSteps.append(fTimeStep if fTimeStep is not None else self.fMinimumTimeStep)
        self.abDependent.append(fTimeStep == -1 if fTimeStep is not None else False)

        return (
            lambda fTimeStep, bReset=False: self._setTimeStep(iIdx, fTimeStep, bReset),
            lambda: self.unbind(iIdx)
        )

    def unbind(self, iCB):
        """
        Unbinds a callback.

        Args:
            iCB (int): Index of the callback to remove.
        """
        del self.cCallBacks[iCB]
        del self.afTimeSteps[iCB]
        del self.abDependent[iCB]
        del self.afLastExec[iCB]
        del self.ctPayload[iCB]

    def tick(self):
        """
        Advances the timer by one global time step.
        """
        while (self.fTime + self.fMinimumTimeStep) == self.fTime:
            self.fMinimumTimeStep *= 10

        fThisStep = max(self.fTimeStepFinal, self.fMinimumTimeStep)
        self.fTime += fThisStep
        self.iTick += 1

        abExec = [(last_exec + step <= self.fTime) for last_exec, step in zip(self.afLastExec, self.afTimeSteps)]
        if hasattr(self, 'bSynchronizeExecuteCallBack') and self.bSynchronizeExecuteCallBack:
            abExec = [True] * len(self.afTimeSteps)
            self.bSynchronizeExecuteCallBack = False

        aiExec = [i for i, exec_ in enumerate(abExec) if exec_]

        for i in aiExec:
            self.cCallBacks[i](self)
            self.afLastExec[i] = self.fTime

        # Post-tick execution logic
        self._execute_post_ticks()

        # Determine the next time step
        self._determine_next_time_step()

    def _execute_post_ticks(self):
        """
        Executes registered post-tick callbacks in the defined order.
        """
        for group_name in self.csPostTickGroups[:-1]:
            group_index = self.tiPostTickGroup[group_name]
            levels = self.tcsPostTickLevel[group_name]

            for level_name in levels:
                while any(self.cabPostTickControl.get(group_index, {}).get(level_name, [])):
                    for idx, should_execute in enumerate(self.cabPostTickControl[group_index][level_name]):
                        if should_execute:
                            self.chPostTicks[group_index][level_name][idx]()
                            self.cabPostTickControl[group_index][level_name][idx] = False

    def _determine_next_time_step(self):
        """
        Determines the next time step based on callback execution times.
        """
        fNextExecutionTime = min([
            last_exec + step
            for last_exec, step, dependent in zip(self.afLastExec, self.afTimeSteps, self.abDependent)
            if not dependent
        ], default=self.fTime + self.fMinimumTimeStep)

        self.fTimeStepFinal = max(fNextExecutionTime - self.fTime, self.fMinimumTimeStep)

    def _setTimeStep(self, iCB, fTimeStep, bResetLastExecuted=False):
        """
        Sets the time step for a specific callback.

        Args:
            iCB (int): Index of the callback.
            fTimeStep (float): New time step.
            bResetLastExecuted (bool): Whether to reset the last executed time.
        """
        self.abDependent[iCB] = (fTimeStep == -1)
        self.afTimeSteps[iCB] = max(fTimeStep, 0)
        if bResetLastExecuted:
            self.afLastExec[iCB] = self.fTime
