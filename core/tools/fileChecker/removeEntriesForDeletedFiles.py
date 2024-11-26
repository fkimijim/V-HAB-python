import os
import re

def remove_entries_for_deleted_files(s_path, t_info):
    """
    Remove entries in the data structure for files or folders that no longer exist.

    Args:
        s_path (str): Path to the folder or file.
        t_info (dict): Dictionary containing saved information for the path.

    Returns:
        tuple: Updated t_info dictionary and a boolean indicating if items were removed.
    """
    # Extract field names from the dictionary
    cs_field_names = list(t_info.keys())

    # Remove special metadata fields
    cs_field_names = [
        name for name in cs_field_names if name not in ['bInitialScanComplete', 'bLastActionComplete']
    ]

    # Boolean array to track removed entries
    ab_removed = [False] * len(cs_field_names)

    # Loop through all field names
    for i, field_name in enumerate(cs_field_names):
        # Handle numeric entries (file modification dates)
        if isinstance(t_info[field_name], (int, float)):
            # Parse the field name to reconstruct the file name
            match = re.search(r'_(?P<type>[^_]+)_file$', field_name)
            if match:
                file_name = f"{field_name[:match.start()]}.{match.group('type')}"
            else:
                file_name = field_name

            # Get the directory contents
            dir_info = os.listdir(s_path) if s_path else os.listdir()

            # Search for the file in the current directory
            file_found = any(re.fullmatch(re.escape(file_name), item) for item in dir_info)

            # If the file is not found, remove it from t_info
            if not file_found:
                t_info.pop(field_name, None)
                ab_removed[i] = True
                print(f"'{os.path.join(s_path, file_name)}' was removed.")

        else:  # Handle folder entries
            folder_name = field_name[2:] if field_name.startswith('p_') else field_name
            s_new_path = f"@{folder_name[3:]}" if folder_name.startswith('at_') else f"+{folder_name}"

            # Check if the folder exists
            folder_path = os.path.join(s_path, s_new_path)
            if not os.path.isdir(folder_path):
                dir_info = os.listdir(s_path) if s_path else os.listdir()

                # Build a search expression to match the folder name
                search_pattern = re.sub(r'[^a-zA-Z0-9]', '.?', s_new_path, flags=re.IGNORECASE)
                folder_found = any(re.fullmatch(search_pattern, item) for item in dir_info)

                if folder_found:
                    matching_folder = next(item for item in dir_info if re.fullmatch(search_pattern, item))
                    s_new_path = os.path.join(s_path, matching_folder)
                else:
                    # Remove the folder from t_info
                    t_info.pop(field_name, None)
                    ab_removed[i] = True
                    print(f"'{os.path.join(s_path, folder_name)}' was removed.")
                    continue

            # Recursively check the folder for deleted files
            t_info[field_name], ab_removed[i] = remove_entries_for_deleted_files(
                os.path.join(s_path, s_new_path), t_info[field_name]
            )

    # Determine if any files or folders were removed
    b_removed = any(ab_removed)
    return t_info, b_removed
