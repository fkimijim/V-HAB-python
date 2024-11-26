def FinConfig(l, k, tFinOutput, tFinInput):
    """
    This function calculates the additional thermal resistance of a fin in a
    numeric cell dependent on the position of the cell and the fin.
    """

    # Inputs
    fFinBroadness_1 = tFinInput['fFinBroadness_1']
    fFinBroadness_2 = tFinInput['fFinBroadness_2']
    fIncrementalLenght = tFinInput['fIncrementalLenght']
    fIncrementalBroadness = tFinInput['fIncrementalBroadness']
    iFinCounterAir = tFinOutput['iFinCounterAir']
    iFinCounterCoolant = tFinOutput['iFinCounterCoolant']
    iCellCounterAir = tFinOutput['iCellCounterAir']
    iCellCounterCoolant = tFinOutput['iCellCounterCoolant']
    fOverhangAir = tFinOutput['fOverhangAir']
    fOverhangCoolant = tFinOutput['fOverhangCoolant']
    fFinOverhangAir = tFinOutput['fFinOverhangAir']
    fFinOverhangCoolant = tFinOutput['fFinOverhangCoolant']

    # Air loop
    if fIncrementalLenght <= fFinBroadness_1:
        fCellPositionAir = fFinBroadness_1 - (iCellCounterAir * fIncrementalLenght + fOverhangAir)
        if fCellPositionAir >= 0:
            iFinStateAir = iFinCounterAir % 2
            fFinFactorAir = 1
            iCellCounterAir += 1
        else:
            iFinStateAir = iFinCounterAir % 2
            fOverhangAir = (iCellCounterAir * fIncrementalLenght + fOverhangAir) - fFinBroadness_1
            fLeftOverAir = fIncrementalLenght - fOverhangAir

            if iFinStateAir == 1:
                fFinFactorAir = fLeftOverAir / fFinBroadness_1
            else:
                fFinFactorAir = fOverhangAir / fFinBroadness_1

            iFinCounterAir += 1
            iCellCounterAir = 1
    else:
        while fFinBroadness_1 * iFinCounterAir - fIncrementalLenght * l < 0:
            iFinCounterAir += 1
        iFinStateAir = iFinCounterAir % 2
        fFinOverhangAir = fFinBroadness_1 * iFinCounterAir - (fIncrementalLenght * l + fFinOverhangAir)
        if fFinOverhangAir == 0:
            if iFinStateAir == 0:
                fFinFactorAir = 0.5
            else:
                fFinFactorAir = (((iFinCounterAir - 1) / 2) + 1) / iFinCounterAir
        else:
            fFinLeftoverAir = fFinBroadness_1 - fFinOverhangAir
            if iFinStateAir == 0:
                fFinFactorAir = ((((iFinCounterAir - 1) - 1) / 2) + 1) / (iFinCounterAir - 1) - (1 / iFinCounterAir) * fFinLeftoverAir
            else:
                fFinFactorAir = (((iFinCounterAir - 1) / 2) + 1) / iFinCounterAir - (1 / iFinCounterAir) * fFinLeftoverAir

    # Coolant loop
    if fIncrementalBroadness <= fFinBroadness_2:
        fCellPositionCoolant = fFinBroadness_2 - (iCellCounterCoolant * fIncrementalBroadness + fOverhangCoolant)
        if fCellPositionCoolant >= 0:
            iFinStateCoolant = iFinCounterCoolant % 2
            fFinFactorCoolant = 1
            iCellCounterCoolant += 1
        else:
            iFinStateCoolant = iFinCounterCoolant % 2
            fOverhangCoolant = (iCellCounterCoolant * fIncrementalBroadness + fOverhangCoolant) - fFinBroadness_2
            fLeftOverCoolant = fIncrementalBroadness - fOverhangCoolant

            if iFinStateCoolant == 1:
                fFinFactorCoolant = fLeftOverCoolant / fFinBroadness_2
            else:
                fFinFactorCoolant = fOverhangCoolant / fFinBroadness_2

            iFinCounterCoolant += 1
            iCellCounterCoolant = 1
    else:
        while fFinBroadness_2 * iFinCounterCoolant - fIncrementalBroadness * k < 0:
            iFinCounterCoolant += 1
        iFinStateCoolant = iFinCounterCoolant % 2
        fFinOverhangCoolant = fFinBroadness_2 * iFinCounterCoolant - (fIncrementalBroadness * k + fFinOverhangCoolant)
        if fFinOverhangCoolant == 0:
            if iFinStateCoolant == 0:
                fFinFactorCoolant = 0.5
            else:
                fFinFactorCoolant = (((iFinCounterCoolant - 1) / 2) + 1) / iFinCounterCoolant
        else:
            fFinLeftoverCoolant = fFinBroadness_2 - fFinOverhangCoolant
            if iFinStateCoolant == 0:
                fFinFactorCoolant = ((((iFinCounterCoolant - 1) - 1) / 2) + 1) / (iFinCounterCoolant - 1) - (1 / iFinCounterCoolant) * fFinLeftoverCoolant
            else:
                fFinFactorCoolant = (((iFinCounterCoolant - 1) / 2) + 1) / iFinCounterCoolant - (1 / iFinCounterCoolant) * fFinLeftoverCoolant

    # Outputs
    tFinOutput['iFinCounterAir'] = iFinCounterAir
    tFinOutput['iFinCounterCoolant'] = iFinCounterCoolant
    tFinOutput['iCellCounterAir'] = iCellCounterAir
    tFinOutput['iCellCounterCoolant'] = iCellCounterCoolant
    tFinOutput['fOverhangAir'] = fOverhangAir
    tFinOutput['fOverhangCoolant'] = fOverhangCoolant
    tFinOutput['fFinFactorAir'] = fFinFactorAir
    tFinOutput['fFinFactorCoolant'] = fFinFactorCoolant
    tFinOutput['iFinStateAir'] = iFinStateAir
    tFinOutput['iFinStateCoolant'] = iFinStateCoolant

    return tFinOutput
