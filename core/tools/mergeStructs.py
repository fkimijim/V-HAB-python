def mergeStructs(tOriginal, tNew):
    """
    Merges two dictionaries, similar to MATLAB structs.
    If both dictionaries have the same field name, the second dictionary takes precedence.
    
    Parameters:
        tOriginal (dict): The original dictionary.
        tNew (dict): The new dictionary, whose values will take precedence in case of overlap.

    Returns:
        dict: A merged dictionary with precedence given to tNew.
    """
    # Getting the field names of the new dictionary
    csFields = tNew.keys()

    # Initializing the result dictionary with the original
    tResult = tOriginal.copy()

    # Looping through the fields
    for sField in csFields:
        # If both dictionaries have the same field and both are dictionaries, call recursively
        if (
            sField in tOriginal
            and isinstance(tOriginal[sField], dict)
            and isinstance(tNew[sField], dict)
        ):
            tResult[sField] = mergeStructs(tOriginal[sField], tNew[sField])
        else:
            # Otherwise, tNew takes precedence and overwrites the original
            tResult[sField] = tNew[sField]

    return tResult
