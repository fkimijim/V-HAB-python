import sympy as sp
import numpy as np

def temperature_3_2_sat(fArea, fU, fHeat_Cap_Flow_1, fHeat_Cap_Flow_2, fEntry_Temp_1, fEntry_Temp_2):
    # Number of cells
    fCells = 3 * 2

    # Number of Transfer units for fluid 1 and fluid 2
    fNTU_1 = (fU * fArea) / fHeat_Cap_Flow_1
    fNTU_2 = (fU * fArea) / fHeat_Cap_Flow_2

    # Number of transfer units per cell
    fNTU_1_c = fNTU_1 / fCells
    fNTU_2_c = fNTU_2 / fCells

    # Preallocate vectors for temperatures
    myT10 = sp.Matrix([sp.Symbol(f'T10_{i + 1}') for i in range(fCells)])
    myT11 = sp.Matrix([sp.Symbol(f'T11_{i + 1}') for i in range(fCells)])
    myT20 = sp.Matrix([sp.Symbol(f'T20_{i + 1}') for i in range(fCells)])
    myT21 = sp.Matrix([sp.Symbol(f'T21_{i + 1}') for i in range(fCells)])

    # Set inlet values
    myT10[0] = fEntry_Temp_1
    myT20[2] = fEntry_Temp_2

    # Define symbolic functions
    yT1_i, yT2_i = sp.symbols('yT1_i yT2_i')

    f1 = lambda yT1_i, yT2_i: yT2_i + (yT1_i - yT2_i) * sp.exp(-(fNTU_1_c / fNTU_2_c) * (1 - sp.exp(-fNTU_2_c)))
    f2 = lambda yT1_i, yT2_i: (fHeat_Cap_Flow_1 / fHeat_Cap_Flow_2) * \
                               (yT1_i - f1(yT1_i, yT2_i)) + yT2_i

    # Calculate outlet temperatures for each cell
    for fk in range(fCells):
        myT11[fk] = f1(myT10[fk], myT20[fk])
        myT21[fk] = f2(myT10[fk], myT20[fk])

    # Preallocate vectors A and B
    mA = sp.zeros(2 * (fCells - 1), 1)
    mB = sp.zeros(2 * (fCells - 1), 1)

    # Fill vector A
    for fk in range(fCells - 1):
        mA[fk, 0] = myT10[fk + 1]
    mA[5, 0] = myT20[0]
    mA[6, 0] = myT20[1]
    mA[7, 0] = myT20[3]
    mA[8, 0] = myT20[4]
    mA[9, 0] = myT20[5]

    # Fill vector B
    for fk in range(fCells - 1):
        mB[fk, 0] = myT11[fk]
    mB[5, 0] = myT21[1]
    mB[6, 0] = myT21[4]
    mB[7, 0] = myT21[2]
    mB[8, 0] = myT21[3]
    mB[9, 0] = myT21[0]

    # Solve equations
    csolution = sp.solve(mA - mB, dict=True)

    # Extract solutions
    fT106 = csolution[sp.Symbol(f'T10_{fCells}')]
    fT206 = csolution[sp.Symbol(f'T20_{fCells}')]

    # Calculate outlet temperatures for cell 6
    fOutlet_Temp_1 = f1(fT106, fT206)
    fOutlet_Temp_2 = f2(fT106, fT206)

    # Convert to numerical values
    fOutlet_Temp_1 = float(fOutlet_Temp_1.evalf())
    fOutlet_Temp_2 = float(fOutlet_Temp_2.evalf())

    return fOutlet_Temp_1, fOutlet_Temp_2
