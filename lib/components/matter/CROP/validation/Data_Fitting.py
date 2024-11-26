# This script is used to launch the data fitting process.

import numpy as np
from scipy.optimize import least_squares
from suyi.CROP.validation import Para_Initial_in_Fitting, Residual_Fun

# Set the initial parameter set for the fitting
x0 = Para_Initial_in_Fitting()

# The residual function for the fitting
def fun(x):
    return Residual_Fun(x)

# Define a callback function for displaying progress (similar to MATLAB's OutputFcn)
def outfun(xk, *args):
    print(f"Current parameters: {xk}")
    return False

# Fitting options for the solver "least_squares"
options = {
    'verbose': 2,  # Display progress (similar to MATLAB's 'Display','iter')
    'xtol': 1e-2,  # Step tolerance (StepTolerance in MATLAB)
    'method': 'lm'  # Use Levenberg-Marquardt algorithm (MATLAB equivalent)
}

# Launch the data fitting process with the solver "least_squares"
result = least_squares(fun, x0, **options)

# Extract results from the fitting process
x = result.x                  # Optimized parameters
resnorm = result.cost * 2     # Sum of squared residuals (cost is 0.5 * sum of squares in scipy)
residual = result.fun         # Residuals
exitflag = result.status      # Exit flag indicating optimization status
output = result               # Full result object containing detailed information

# Display the fitting results
print("\nOptimization Results:")
print(f"Fitted parameters (x): {x}")
print(f"Residual norm (resnorm): {resnorm}")
print(f"Residuals: {residual}")
print(f"Exit flag: {exitflag}")
print(f"Output details: {output}")
