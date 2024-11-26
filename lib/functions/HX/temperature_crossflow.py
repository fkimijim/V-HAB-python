import math
from sympy import symbols, exp, factorial, summation, integrate

def temperature_crossflow(fN_Rows, fArea, fU, fHeat_Cap_Flow_1, fHeat_Cap_Flow_2, fEntry_Temp_1, fEntry_Temp_2, x0=None):
    """
    Calculates the outlet temperatures of a crossflow heat exchanger with zero to n rows of pipes.
    Returns fOutlet_Temp_1 and fOutlet_Temp_2 in K.
    """
    if fN_Rows < 0:
        raise ValueError("A negative number for pipe rows is not possible")

    # Number of Transfer Units fluid 1 and fluid 2
    fNTU_1 = (fU * fArea) / fHeat_Cap_Flow_1
    fNTU_2 = (fU * fArea) / fHeat_Cap_Flow_2

    if fN_Rows == 0:
        # Pure crossflow case
        fSummands = 10
        yXi, yEta = symbols('yXi yEta')
        yTheta_2, yTheta_1 = symbols('yTheta_2 yTheta_1')

        yPhi_n = [0] * fSummands

        for fk in range(1, fSummands + 1):
            yVariable_1 = (1 / math.factorial(fk - 1)) * (fNTU_1**(fk - 1)) * (yXi**(fk - 1)) * exp(-fNTU_1 * yXi)
            yVariable_2 = summation(yVariable_1, (yXi, 0, 1))
            yPhi_n[fk - 1] = (1 / math.factorial(fk)) * (fNTU_2**fk) * (yEta**fk) * exp(-fNTU_2 * yEta) * (1 - yVariable_2)

        yTheta_2 = exp(-fNTU_2 * yEta) + summation(yPhi_n)
        yT2 = yTheta_2 * (fEntry_Temp_2 - fEntry_Temp_1) + fEntry_Temp_1

        fOutlet_Temp_2 = integrate(yT2.subs(yEta, 1), (yXi, 0, 1)).evalf()
        fOutlet_Temp_1 = fEntry_Temp_1 - (fHeat_Cap_Flow_2 / fHeat_Cap_Flow_1) * (fOutlet_Temp_2 - fEntry_Temp_2)
    else:
        # Crossflow with up to n rows of pipes
        fepsilon = ((fNTU_1 * fN_Rows) / (fNTU_2 * x0)) * (1 - exp(-fNTU_2 / fN_Rows))
        yVariable_1 = []

        for fp in range(1, fN_Rows):
            yVariable_2 = []

            for fm in range(fp + 1):
                yVariable_3 = []

                for fr in range(fm + 1):
                    yVariable_3.append(((fepsilon * x0)**fr) / math.factorial(fr))

                yVariable_2.append(
                    math.factorial(fp) / (math.factorial(fm) * math.factorial(fp - fm)) *
                    ((1 - exp(-fNTU_2 / fN_Rows))**fm) * exp(-(fp - fm) * fNTU_2 / fN_Rows) * sum(yVariable_3)
                )

            yVariable_1.append(sum(yVariable_2))

        fOutlet_Temp_2 = fEntry_Temp_2 + (fEntry_Temp_1 - fEntry_Temp_2) * \
                         (fHeat_Cap_Flow_1 / (fN_Rows * fHeat_Cap_Flow_2)) * \
                         (fN_Rows - (1 + sum(yVariable_1)) * exp(-fepsilon * x0))
        fOutlet_Temp_1 = fEntry_Temp_1 - (fHeat_Cap_Flow_2 / fHeat_Cap_Flow_1) * (fOutlet_Temp_2 - fEntry_Temp_2)

    return fOutlet_Temp_1, fOutlet_Temp_2
