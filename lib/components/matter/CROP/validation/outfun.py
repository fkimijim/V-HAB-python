def outfun(x, optim_values, state):
    """
    This function is used to stop the data fitting process with criteria set by users.

    Parameters:
    x : array
        Current parameter values.
    optim_values : dict
        A dictionary containing current optimization state, such as residual norm (`resnorm`).
    state : str
        Current state of the optimization process ('init', 'iter', 'done').

    Returns:
    stop : bool
        A flag to indicate whether to stop the optimization process.
    """
    stop = False
    # Check if residual norm is less than 1e-5
    if optim_values['resnorm'] < 1e-5:
        stop = True
    return stop
