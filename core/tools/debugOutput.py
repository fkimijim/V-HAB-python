class DebugOutput:
    """
    Handles global debugging output using `output()`.
    """

    MESSAGE = 1
    INFO = 2
    NOTICE = 3
    WARN = 4
    ERROR = 5

    IDX_TO_CHAR = ['M', 'I', 'N', 'W', 'E']

    def __init__(self):
        self.bOff = True
        self.bCreateStack = False
        self.bCollect = False

        self.tCollection = []
        self.chCallbacks = []
        self.chFilters = []
        self.coHandlers = []

        self.tiUuidsToCallback = {}

    def output(self, oObj, iLevel, iVerbosity, sIdentifier, sMessage, cParams):
        if self.bOff:
            return

        if oObj.sUUID not in self.tiUuidsToCallback or not self.tiUuidsToCallback[oObj.sUUID]:
            return

        hCallBack = self.tiUuidsToCallback[oObj.sUUID]

        tStack = None
        try:
            raise Exception
        except Exception as e:
            tStack = e.__traceback__

        tPayload = {
            'oObj': oObj,
            'iLevel': iLevel,
            'iVerbosity': iVerbosity,
            'sIdentifier': sIdentifier,
            'sMessage': sMessage,
            'tStack': tStack if self.bCreateStack else None,
            'cParams': cParams,
        }

        if self.bCollect:
            self.tCollection.append(tPayload)
        else:
            hCallBack(tPayload)

    def flush(self):
        self.bOff = True

        self.chCallbacks.clear()
        self.chFilters.clear()
        self.coHandlers.clear()

        self.tiUuidsToCallback.clear()
        self.bCollect = False
        self.tCollection = []

    def bind(self, hCallBack, hFilterFct, oHandlerObj):
        self.chCallbacks.append(hCallBack)
        self.chFilters.append(hFilterFct)
        self.coHandlers.append(oHandlerObj)
        return len(self.chCallbacks)

    def unbind(self, iId):
        if 0 <= iId < len(self.chCallbacks):
            del self.chCallbacks[iId]
            del self.chFilters[iId]
            del self.coHandlers[iId]

    def add(self, oObj):
        self.tiUuidsToCallback[oObj.sUUID] = None

        for iC in range(len(self.chCallbacks) - 1, -1, -1):
            if not self.chFilters[iC](oObj):
                continue

            self.tiUuidsToCallback[oObj.sUUID] = self.chCallbacks[iC]
            break

    def set_output_state(self, bOutput):
        self.bOff = not bOutput

    def toggle_output_state(self):
        self.bOff = not self.bOff

    def set_create_stack(self, bCreateStack):
        self.bCreateStack = bool(bCreateStack)

    def toggle_create_stack(self):
        self.bCreateStack = not self.bCreateStack

    def set_collect(self, bCollect):
        if self.bCollect and not bCollect:
            for tPayload in self.tCollection:
                oObj = tPayload['oObj']
                if oObj.sUUID in self.tiUuidsToCallback and self.tiUuidsToCallback[oObj.sUUID]:
                    self.tiUuidsToCallback[oObj.sUUID](tPayload)

            self.tCollection = []

        self.bCollect = bCollect
