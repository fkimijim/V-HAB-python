def find_smallest_time_step(oInput):
    """
    Finds the object setting the smallest time step.

    This function reads the data stored by the timestep observer for debugging
    and displays the location, tick, and timestep of the component with the smallest
    timestep in the last 100 ticks. Call it after finishing or pausing a simulation
    by running `find_smallest_time_step(oLastSimObj)` in your script.

    Parameters:
        oInput: The simulation object containing monitors and observers.
    """
    try:
        # Accessing the time step observer object
        oTimeStepObserver = oInput.toMonitors.oTimeStepObserver
    except AttributeError as oError:
        # Handle the common error where the user forgot to activate the time step observer
        if "'toMonitors' object has no attribute 'oTimeStepObserver'" in str(oError):
            error_message = (
                "It seems like you did not activate the timestep observer. Please add the following lines "
                "to your setup file before defining the simulation:\n"
                "ttMonitorConfig = {}\n"
                "ttMonitorConfig['oTimeStepObserver'] = {\n"
                "    'sClass': 'simulation.monitors.timestepObserver',\n"
                "    'cParams': [0]\n"
                "}\n"
            )
            raise RuntimeError(error_message)
        else:
            raise oError

    # Iterate through the stored values to find the absolute smallest time step
    fMinStep = float('inf')
    csReports = []

    for debug_entry in oTimeStepObserver.tDebug:
        if debug_entry['fTimeStep'] < fMinStep:
            fMinStep = debug_entry['fTimeStep']
            csReports = debug_entry['csReport']

    # Print the report for the object with the minimum time step
    for report in csReports:
        print(f"\n{report}\n")
