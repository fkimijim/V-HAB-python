import numpy as np
from sympy import symbols, solve, Matrix, real

def temperature_1_n_sat(mArea, mU, fHeat_Capacity_Flow_1, fHeat_Capacity_Flow_2, fEntry_Temp_1, fEntry_Temp_2):
    if len(mArea) != len(mU):
        raise ValueError("The number of areas and heat exchange coefficients have to be equal")
    
    fPasses = len(mArea)
    fUA_total = np.sum(np.multiply(mU, mArea))
    fN1 = fUA_total / fHeat_Capacity_Flow_1
    fN2 = fUA_total / fHeat_Capacity_Flow_2
    
    mepsilon = np.zeros(fPasses)
    for fi in range(fPasses):
        mepsilon[fi] = (mArea[fi] * mU[fi]) / fUA_total
    
    # Avoid duplicate epsilon values
    delta = 1e-5
    for i in range(fPasses):
        for j in range(i + 1, fPasses):
            if mepsilon[i] == mepsilon[j]:
                mepsilon[i] -= delta
                mepsilon[j] += delta

    # Matrix A and B
    mA = np.zeros((fPasses, fPasses))
    for fi in range(fPasses):
        for fk in range(fPasses):
            mA[fi, fk] = (mepsilon[fk] ** fi) * (-1) ** (fi * (fk + 1))
    
    mB = np.zeros((fPasses, fPasses + 1))
    mB[0, 0] = 1
    mB[0, 1] = fN1 / fN2
    A_sum = np.sum(mA, axis=1)
    for fi in range(1, fPasses):
        for fk in range(1, fPasses):
            if fi == fk:
                if fi % 2 == 0:
                    mB[fi, fk] = 1
                else:
                    mB[fi, fk] = 1 / fN2
            if fi == fk:
                if fi % 2 == 0:
                    mB[fi, fk + 1] = 1 / fN2
                else:
                    mB[fi, fk + 1] = 1 / (fN1 * fN2)
    
    for fi in range(2, fPasses):
        for fk in range(1, fPasses):
            if fi > fk:
                mB[fi, fk] = ((1 / fN1) ** (fk - 1)) * A_sum[fi - fk]
    
    mC = np.linalg.inv(mA) @ mB

    # Coefficients of the differential equation
    fSum1_for_K = 0
    fSum2_for_K = 0
    mK = np.zeros(fPasses + 1)
    for fi in range(fPasses):
        for fk in range(fPasses):
            fSum1_for_K += (mepsilon[fk] ** (fPasses + 1 - fi)) * (-1) ** ((fk + 1) * (fPasses + ((1 - (-1) ** fi) // 2)))
            fSum2_for_K += (mepsilon[fk] ** fPasses) * mC[fk, fi + 1] * (-1) ** ((fk + 1) * (fPasses + 1))
        mK[fi] = (fN2 * (fN1 ** (fPasses - fi)) * fSum1_for_K) - ((fN2 * (fN1 ** (fPasses - 1))) * fSum2_for_K)
    mK[-1] = 1

    yl = symbols('yl')
    mylambda = Matrix([yl ** i for i in range(fPasses + 1)])
    ychar_pol = sum(mK[i] * mylambda[i] for i in range(fPasses + 1))
    mm = solve(ychar_pol, yl)
    mm = [real(x) for x in mm]

    K_0_serpent = fN2 * (fN1 ** (fPasses - 1)) * sum((mepsilon[k] ** fPasses) * (-1) ** ((fPasses + 1) * (k + 1)) for k in range(fPasses))
    mZ = np.zeros(2 * fPasses)
    mZ[0] = 1 - ((K_0_serpent * (-fN1 / fN2)) / mK[0])
    mZ[1] = mZ[0]
    
    for fi in range(1, fPasses):
        for fk in range(fPasses):
            mZ[2 * fi] -= (mepsilon[fk] ** fi) * (-1) ** ((fi + 1) * (fk + 1))
        mZ[2 * fi + 1] = mZ[2 * fi]
    
    mD = np.zeros((2 * fPasses, 2 * fPasses))
    for j in range(fPasses):
        mD[0, j] = 1
    
    for fi in range(1, 2 * fPasses):
        if fi % 2 != 0:
            for j in range(fPasses):
                for fk in range(2, (fi + 2) // 2):
                    mD[fi, j] += mB[(fi + 1) // 2, fk] * (mm[j] ** (fk - 1))
        else:
            for j in range(fPasses):
                mD[fi, j] = mD[fi - 1, j] * np.exp(mm[j])
    
    mSolution = np.linalg.solve(mD, mZ)
    fOutlet_Temp_1 = (mSolution[-1] * (fEntry_Temp_2 - fEntry_Temp_1)) + fEntry_Temp_1
    fOutlet_Temp_2 = -(fHeat_Capacity_Flow_1 / fHeat_Capacity_Flow_2) * (fOutlet_Temp_1 - fEntry_Temp_1) + fEntry_Temp_2
    
    return fOutlet_Temp_1, fOutlet_Temp_2
