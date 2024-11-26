import re
import os
import warnings

def normalizePath(sInputPath, bFolder=False):
    """
    Convert a path to a form without special characters.
    
    Parameters:
    sInputPath (str): A string containing the path to a file or folder.
    bFolder (bool): Boolean flag indicating whether the path is a folder. Default is False.
    
    Returns:
    str: A string containing a version of the provided path without any characters 
         that would prevent its use as a struct field name.
    """
    
    # Checking if the provided string is empty
    if not sInputPath:
        sOutputName = ''
        warnings.warn(
            'The string you have provided to the normalizePath() function is empty.',
            UserWarning
        )
        return sOutputName
    
    # Checking if there are any space characters in the string. This is not permitted.
    if bFolder:
        if ' ' in sInputPath:
            raise ValueError(
                f"The file you are adding\n({sInputPath})\n"
                "contains space characters in its path. This is not permitted within Python.\n"
                "Please change all file and folder names accordingly."
            )
    
    # Define separators for replacements
    tSeparators = {
        'package': '__',
        'class': '_aaat_',
        'filesep': '_p_'
    }
    
    # Make sure path starts with a file separator
    if not sInputPath.startswith(os.sep):
        sOutputName = os.sep + sInputPath
    else:
        sOutputName = sInputPath
    
    # Replace package and class folder designators with special keywords
    sOutputName = sOutputName.replace(f"{os.sep}+", tSeparators['package'])
    sOutputName = sOutputName.replace(f"{os.sep}@", f"{tSeparators['class']}at_")
    
    # Drop any leading non-alphanumeric characters and replace path separators
    sOutputName = re.sub(r'^[^a-z0-9]*', '', sOutputName, flags=re.IGNORECASE)
    sOutputName = sOutputName.replace(os.sep, tSeparators['filesep'])
    
    # Replace the file extension including its leading dot
    sOutputName = re.sub(r'\.(\w+)$', r'_\1_file', sOutputName)
    
    # Replace all other invalid characters with an underscore
    sOutputName = re.sub(r'[^a-z0-9_]', '_', sOutputName, flags=re.IGNORECASE)
    
    # Ensure the field name starts with a letter
    sOutputName = re.sub(r'^([^a-z])', r'p_\1', sOutputName, flags=re.IGNORECASE)
    
    return sOutputName
