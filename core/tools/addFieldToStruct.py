def add_field_to_struct(tStruct, sFieldName):
    """
    Adds a new field (key) to a given dictionary with an empty value.

    Parameters:
        tStruct (dict): The dictionary to which the field will be added.
        sFieldName (str): The name of the new field.

    Returns:
        dict: The updated dictionary with the new field added.
    """
    tStruct[sFieldName] = None
    return tStruct

# Example usage
if __name__ == "__main__":
    tStruct = {'existingField': 42}
    print("Before:", tStruct)

    tStruct = add_field_to_struct(tStruct, 'newField')
    print("After:", tStruct)
