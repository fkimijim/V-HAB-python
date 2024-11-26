import numpy as np

def wmean(x, w, dim=None):
    """
    Weighted Average or Mean Value.
    
    Parameters:
        x (np.ndarray): Array of values.
        w (np.ndarray): Array of non-negative weights (same shape as x).
        dim (int, optional): Dimension along which to compute the weighted mean. 
                             Default is the first non-singleton dimension.
    
    Returns:
        np.ndarray: Weighted mean along the specified dimension.
    
    Raises:
        ValueError: If inputs are not the same size, weights are negative, 
                    or all weights are zero.
    
    Example:
        x = np.random.rand(5, 2)
        w = np.random.rand(5, 2)
        y = wmean(x, w)
    """
    # Check that dimensions of x and w match
    if x.shape != w.shape:
        raise ValueError("Inputs x and w must be the same size.")

    # Check that all weights are non-negative
    if np.any(w < 0):
        raise ValueError("All weights, w, must be non-negative.")

    # Check that there is at least one non-zero weight
    if np.all(w == 0):
        raise ValueError("At least one weight must be non-zero.")

    # If dim is not provided, find the first non-singleton dimension
    if dim is None:
        dim = next((i for i, s in enumerate(x.shape) if s > 1), 0)

    # Calculate the weighted mean
    return np.sum(w * x, axis=dim) / np.sum(w, axis=dim)
