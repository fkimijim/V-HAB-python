import os
import pickle
import time
from pathlib import Path

class FileChecker:
    def __init__(self):
        self.saved_info = {}
        self.save_path = None

    def check_for_changes(self, s_file_or_folder_path="", s_caller="Default"):
        """
        Check if a folder or file contains changes.

        Args:
            s_file_or_folder_path (str): Path to the folder or file to check.
            s_caller (str): Identifier for the caller to store separate file statuses.

        Returns:
            bool: True if changes are detected, False otherwise.
        """
        # Save path for the persistent file
        self.save_path = Path("data") / f"FolderStatusFor{s_caller}.pkl"
        b_changed = False

        # Load or initialize saved_info
        if not self.saved_info:
            if self.save_path.exists():
                with open(self.save_path, "rb") as f:
                    self.saved_info = pickle.load(f)
            else:
                self.saved_info = {}

        if not s_file_or_folder_path:
            s_file_or_folder_path = os.getcwd()

        # Normalize and clean up the path
        s_file_or_folder_path = os.path.abspath(s_file_or_folder_path)
        b_first_call = not bool(self.saved_info)

        # Initialize scan metadata if this is the first run
        if b_first_call and not self.saved_info.get("bInitialScanComplete", False):
            self.saved_info["bInitialScanInProgress"] = True
            self.saved_info["bInitialScanComplete"] = False

            print("Performing initial scan. This may take some time...")

            # Time the scan
            start_time = time.time()

            b_changed = self._initial_scan(s_file_or_folder_path)

            elapsed_time = time.time() - start_time
            print(f"Initial scan completed in {elapsed_time:.2f} seconds.")

            # Mark scan as complete
            self.saved_info["bInitialScanComplete"] = True
            self.saved_info.pop("bInitialScanInProgress", None)

            self._save_info()

            return b_changed

        # Perform the change detection for subsequent runs
        b_changed = self._detect_changes(s_file_or_folder_path)

        if b_first_call:
            self._save_info()

        return b_changed

    def _initial_scan(self, folder_path):
        """
        Perform an initial scan of all files and folders.

        Args:
            folder_path (str): Path to the folder to scan.

        Returns:
            bool: Always True sin
        """
