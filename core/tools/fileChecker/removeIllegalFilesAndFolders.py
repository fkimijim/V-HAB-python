def remove_illegal_files_and_folders(tInputStruct):
    """
    Removes illegal files and folders from an input list of file information.

    Args:
        tInputStruct (list): List of dictionaries containing file or folder information, 
                             typically returned by `os.listdir` or a custom directory scan.

    Returns:
        list: Filtered list of dictionaries with illegal files and folders removed.
    """
    # Initializing a list to store valid entries
    tOutputStruct = []

    # Iterate through the input struct to filter illegal files and folders
    for entry in tInputStruct:
        # Check for illegal entries: names starting with '.' or containing '~'
        if not entry['name'].startswith('.') and '~' not in entry['name']:
            tOutputStruct.append(entry)
    
    return tOutputStruct

# Example usage:
if __name__ == "__main__":
    # Simulate tInputStruct as a list of file information dictionaries
    tInputStruct = [
        {'name': 'file1.txt', 'isdir': False},
        {'name': '.hidden', 'isdir': True},
        {'name': 'temp~', 'isdir': False},
        {'name': 'folder', 'isdir': True},
    ]
    
    # Call the function and print the result
    tOutputStruct = remove_illegal_files_and_folders(tInputStruct)
    print("Filtered Output:", tOutputStruct)
