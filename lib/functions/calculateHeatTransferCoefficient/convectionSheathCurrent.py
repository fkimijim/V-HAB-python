import numpy as np

def convectionSheathCurrent(
    fD_o, fD_Baffle, fD_Batch, fD_Hole, fD_Shell, fs_1, fs_2, fN_Pipes, 
    fN_Pipes_Win, fN_FlowResist, fN_Sealings, fN_Pipes_Diam, fDist_Baffle,
    fHeight_Baffle, fFlowSpeed, fDyn_Visc, fDensity, fThermal_Conductivity, 
    fC_p, fConfig, fs_3=None
):
    # Checks the number of input parameters
    if fs_3 is None and fConfig == 2:
        raise ValueError("fs_3 is required for fConfig = 2")
    
    # Definition of the kinematic viscosity
    fKin_Visc = fDyn_Visc[0] / fDensity[0]
    
    fFlowSpeed = abs(fFlowSpeed)

    # Definition of the overflowed length of the pipes
    fOverflow_Length = (np.pi / 2) * fD_o

    # Definition of fPsi
    if fs_2 / fD_o >= 1:
        fPsi = 1 - (np.pi * fD_o) / (4 * fs_1)
    else:
        fPsi = 1 - (np.pi * fD_o**2) / (4 * fs_1 * fs_2)

    # Definition of the Reynolds number
    fRe = (fFlowSpeed * fOverflow_Length) / (fKin_Visc * fPsi)

    # Nußelt number for different configurations
    if fConfig == 0 or fConfig == 1:
        fAlpha_Batch = convection_multiple_pipe_row(
            fD_o, fs_1, fs_2, fFlowSpeed, fDyn_Visc, fDensity, 
            fThermal_Conductivity, fC_p, fConfig
        )
    elif fConfig == 2:
        fAlpha_Batch = convection_multiple_pipe_row(
            fD_o, fs_1, fs_2, fFlowSpeed, fDyn_Visc, fDensity, 
            fThermal_Conductivity, fC_p, fConfig, fs_3
        )
    else:
        raise ValueError("Invalid input for fConfig")

    fNu_batch = (fAlpha_Batch * fOverflow_Length) / fThermal_Conductivity[0]

    # Geometric correction factor
    fGeometry_Factor = 1 - (fN_Pipes_Win / fN_Pipes) + 0.524 * (fN_Pipes_Win / fN_Pipes)**0.32

    # Shortest connection length
    if fConfig == 0:
        fDist_Pipes = fs_1 * fD_o
    elif fConfig == 1 or fConfig == 2:
        if (fs_2 / fD_o) < (0.5 * np.sqrt(2 * (fs_1 / fD_o) + 1)):
            fDist_Pipes = np.sqrt((fs_1 / 2)**2 + fs_2**2) - fD_o
        else:
            fDist_Pipes = fs_1 - fD_o
    else:
        raise ValueError("Invalid input for fConfig")

    fDist_Pipes_Shell = (fD_Shell - fD_Batch) / 2
    fConnecting_Length = ((fN_Pipes_Diam - 1) * fDist_Pipes) + (2 * fDist_Pipes_Shell)

    # Gap area calculations
    fA_SRU = (fN_Pipes - (fN_Pipes_Win / 2)) * (np.pi * (fD_Hole**2 - fD_o**2)) / 4
    fGamma = 2 * np.degrees(np.arccos(1 - ((2 * fHeight_Baffle) / fD_Baffle)))
    fA_SMU = (np.pi / 4) * ((fD_Shell**2) - (fD_Baffle**2)) * (360 - fGamma) / 360

    # Leakage factor
    fLeakage_Factor = 0.4 * (fA_SRU / (fA_SRU + fA_SMU)) + \
                      (1 - (0.4 * (fA_SRU / (fA_SRU + fA_SMU)))) * \
                      np.exp(-1.5 * ((fA_SRU + fA_SMU) / (fDist_Baffle * fConnecting_Length)))

    # Bypass factor
    fBeta = 1.5 if fRe < 100 else 1.35

    if fDist_Pipes >= (fD_Shell - fD_Batch):
        fA_Bypass = 0
    else:
        fA_Bypass = fDist_Baffle * (fD_Shell - fD_Batch)

    if fN_Sealings <= (fN_FlowResist / 2):
        fBypass_Factor = np.exp(-fBeta * fA_Bypass / (fDist_Baffle * fConnecting_Length) * \
                                (1 - ((2 * fN_Sealings) / fN_FlowResist)**(1/3)))
    else:
        fBypass_Factor = 1

    # Nußelt number and convection coefficient
    fNu = fGeometry_Factor * fLeakage_Factor * fBypass_Factor * fNu_batch
    fConvection_alpha = (fNu * fThermal_Conductivity[0]) / ((np.pi / 2) * fD_o)

    return fConvection_alpha
