import math

def SheathCurrent(fD_o, fD_Shell, fD_Baffle, fD_Batch, fD_Hole, fD_Int, fDist_Baffle, 
                  fDist_Baffle_End, fHeighst_Baffle, fLength_Int, fs_1, fs_2, fN_Pipes, 
                  fN_Rows_Trans, fN_Pipes_Diam, fN_Pipes_Win, fN_Sealings, fN_Baffles, 
                  fN_Resist, fN_Resist_End, fDyn_Visc, fDensity, fMassFlow, fConfig):
    """
    Calculate the pressure loss for the sheath current of a shell and tube heat exchanger in N/m².
    """

    # Decide whether temperature dependency should also be accounted for
    if len(fDyn_Visc) == 2:
        if fConfig == 0:
            fConfig = 2
        elif fConfig == 1:
            fConfig = 3

    # Definition of the kinematic viscosity
    fKin_Visc_m = fDyn_Visc[0] / fDensity[0]

    # Relation between the diameter of the pipes and the spacing
    if fs_2 / fD_o >= 1:
        fPsi = 1 - (math.pi * fD_o) / (4 * fs_1)
    else:
        fPsi = 1 - (math.pi * fD_o**2) / (4 * fs_1 * fs_2)

    # Overflowed length of the pipes
    fOverflow_Length = (math.pi / 2) * fD_o

    # Flow speed
    fFlowSpeed = abs(fMassFlow / fDensity[0])

    # Reynolds number
    fRe = (fFlowSpeed * fOverflow_Length) / (fKin_Visc_m * fPsi)

    # Pressure loss in transverse zone
    fA_SRU = (fN_Pipes - (fN_Pipes_Win / 2)) * (math.pi * (fD_Hole**2 - fD_o**2)) / 4
    fGamma = 2 * math.degrees(math.acos(1 - ((2 * fHeighst_Baffle) / fD_Baffle)))
    fA_SMU = (math.pi / 4) * (fD_Shell**2 - fD_Baffle**2) * (360 - fGamma) / 360
    fFactor_r = -0.15 * (1 + (fA_SMU / (fA_SRU * fA_SMU))) + 0.8

    # Shortest connection length
    if fConfig == 0:
        fDist_Pipes = fs_1 * fD_o
    elif fConfig in [1, 2]:
        if (fs_2 / fD_o) < (0.5 * math.sqrt(2 * (fs_1 / fD_o) + 1)):
            fDist_Pipes = math.sqrt((fs_1 / 2)**2 + fs_2**2) - fD_o
        else:
            fDist_Pipes = fs_1 - fD_o
    else:
        raise ValueError("Invalid configuration input")

    fDist_Pipes_Shell = (fD_Shell - fD_Batch) / 2
    fConnecting_Length = ((fN_Pipes_Diam - 1) * fDist_Pipes) + (2 * fDist_Pipes_Shell)

    # Leakage factor for the sheath current
    fLeackage_Factor = 0.4 * (fA_SRU / (fA_SRU + fA_SMU)) + (1 - (0.4 * 
                     (fA_SRU / (fA_SRU + fA_SMU)))) * math.exp(-1.5 * 
                     (((fA_SRU + fA_SMU) / (fDist_Baffle * fConnecting_Length))**fFactor_r))

    # Bypass factor for the sheath current
    if fRe < 100:
        fBeta = 4.5
    else:
        fBeta = 3.7

    if fDist_Pipes >= (fD_Shell - fD_Batch):
        fA_Bypass = 0
    else:
        fA_Bypass = fDist_Baffle * (fD_Shell - fD_Batch)

    if fN_Sealings <= (fN_Resist / 2):
        fBypass_Factor = math.exp(-fBeta * fA_Bypass / (fDist_Baffle * 
                          fConnecting_Length) * (1 - ((2 * fN_Sealings) / fN_Resist)**(1/3)))
    else:
        fBypass_Factor = 1

    # Pressure loss in the transverse zone
    fDelta_Pressure_0 = PipeBundle(fD_o, fs_1, fs_2, fN_Rows_Trans, 
                                   fFlowSpeed, fDyn_Visc, fDensity, fConfig)
    fDelta_Pressure_Transverse = fLeackage_Factor * fBypass_Factor * fDelta_Pressure_0

    # Pressure loss in the endzone
    if fDist_Baffle_End == fDist_Baffle:
        fDelta_Pressure_End = fBypass_Factor * fDelta_Pressure_0 * fN_Resist_End / fN_Resist
    else:
        fFlowSpeed_End = fFlowSpeed * (fDist_Baffle / fDist_Baffle_End)
        fDelta_Pressure_End = fBypass_Factor * fN_Resist_End * fDelta_Pressure_0

    # Total pressure loss
    fDelta_Pressure = ((fN_Baffles - 1) * fDelta_Pressure_Transverse + 
                       2 * fDelta_Pressure_End)

    return fDelta_Pressure
