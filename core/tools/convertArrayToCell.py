def convert_array_to_cell(axArray):
    """
    Converts an array into a linear list.

    Parameters:
        axArray (iterable): Input array (list or numpy array).

    Returns:
        list: A list containing the elements of the input array.
    """
    # Get the length of the input array
    iLength = len(axArray)

    # Initialize the return variable as a list
    cxCell = [None] * iLength

    # Loop through the array items and add them to the list
    for iI in range(iLength):
        cxCell[iI] = axArray[iI]

    return cxCell

# Example usage
if __name__ == "__main__":
    axArray = [1, 2, 3, 4]
    cxCell = convert_array_to_cell(axArray)
    print(cxCell)  # Output: [1, 2, 3, 4]
