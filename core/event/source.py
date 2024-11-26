class Source:
    """
    Source class provides a framework for event handling.
    Classes that want to use bind or trigger functions must inherit from this class.
    """

    def __init__(self):
        """
        Initializes the Source object with default properties.
        """
        # Initialize the default, empty event object
        self.tcEventCallbacks = {}  # Dictionary to store event callbacks
        self.bHasCallbacks = False  # Boolean indicating if callbacks exist
        self.tDefaultEvent = {
            'sType': None,
            'oCaller': self,
            'tData': None,
        }

    def bind(self, sName, hCallBack):
        """
        Binds a function handle to the event with the given name.

        Args:
            sName (str): Name of the event (can be hierarchical, e.g., 'schedule.exercise.bicycle').
            hCallBack (function): Callback function to bind.

        Returns:
            function: A handle to unbind the callback.
        """
        # Create entry for the event if it doesn't exist
        if sName not in self.tcEventCallbacks:
            self.tcEventCallbacks[sName] = []

        # Add the callback to the event
        self.tcEventCallbacks[sName].append(hCallBack)

        # Mark that this object has callbacks
        self.bHasCallbacks = True

        # Return a handle to unbind this specific callback
        iCallBack = len(self.tcEventCallbacks[sName]) - 1
        return lambda: self.unbind(sName, iCallBack)

    def unbind(self, sName, iId):
        """
        Unbinds a callback from this object.

        Args:
            sName (str): Name of the event.
            iId (int): Index of the callback to remove.
        """
        if sName in self.tcEventCallbacks and 0 <= iId < len(self.tcEventCallbacks[sName]):
            del self.tcEventCallbacks[sName][iId]

            # Clean up empty event entries
            if not self.tcEventCallbacks[sName]:
                del self.tcEventCallbacks[sName]

    def unbindAllEvents(self):
        """
        Unbinds all callbacks associated with this object.
        """
        self.tcEventCallbacks = {}
        self.bHasCallbacks = False

    def trigger(self, sName, tData=None):
        """
        Triggers the execution of all callbacks registered to the event called sName.

        Args:
            sName (str): Name of the event.
            tData (any): Additional data for the event.
        """
        # If there are no callbacks, do nothing
        if not self.bHasCallbacks:
            return

        # Check if there are callbacks for the given event name
        cCallbackCell = self.tcEventCallbacks.get(sName, None)
        if cCallbackCell is None:
            return

        # Prepare the event data
        tEvent = self.tDefaultEvent.copy()
        tEvent['sType'] = sName
        tEvent['tData'] = tData

        # Execute all callbacks for this event
        for callback in cCallbackCell:
            callback(tEvent)


# def sample_callback(event):
#     print(f"Event triggered: {event['sType']}, Data: {event['tData']}")

# # オブジェクトの作成
# event_source = Source()

# # イベントにコールバックをバインド
# unbind_callback = event_source.bind("example_event", sample_callback)

# # イベントをトリガー
# event_source.trigger("example_event", {"key": "value"})

# # コールバックをアンバインド
# unbind_callback()

# # 再びイベントをトリガー（コールバックは呼び出されない）
# event_source.trigger("example_event", {"key": "value"})
