import os
import time
from datetime import datetime
import multiprocessing
import matplotlib.pyplot as plt
from pathlib import Path


class TestVHAB:
    """
    A class to run and manage tests for V-HAB simulations.
    """

    @staticmethod
    def test_vhab(s_compare_to_state="server", f_sim_time=None, b_force_execution=False, b_debug_mode_on=False):
        """
        Runs all tests and saves the figures to a folder.

        Args:
            s_compare_to_state (str): State to compare to ('server' or 'local').
            f_sim_time (float): Simulation time (optional).
            b_force_execution (bool): Force execution regardless of changes.
            b_debug_mode_on (bool): Run simulations in debug mode.
        """

        # Starting timer for execution
        h_timer = time.time()

        # Validate and process input parameters
        if s_compare_to_state not in ["server", "local"]:
            raise ValueError("Unknown state to compare testVHAB run ('server' or 'local').")

        # Prepare paths and directories
        s_test_directory = os.path.join("user", "+tests")
        t_tests = TestVHAB._get_tests(s_test_directory)
        s_folder_path = TestVHAB._create_data_folder_path()

        # Check for changes
        b_changed, changes_description = TestVHAB._check_for_changes()
        if b_changed:
            print(f"{changes_description}changed. All tests will be executed!\n")
        elif b_force_execution:
            print("Forced execution. All tests will be executed!\n")
        else:
            print("Nothing has changed. No tests will be performed.\n")
            return

        # Run tests (parallel or serial)
        if b_changed or b_force_execution:
            if TestVHAB._has_parallel_support():
                TestVHAB._run_parallel_tests(t_tests, s_test_directory, s_folder_path, f_sim_time, b_debug_mode_on)
            else:
                TestVHAB._run_serial_tests(t_tests, s_test_directory, s_folder_path, f_sim_time, b_debug_mode_on)

        # Save test data
        TestVHAB._save_test_data(t_tests)

        # Display summary
        TestVHAB._display_summary(t_tests)

        # Compare to previous state if needed
        if b_changed or b_force_execution:
            TestVHAB._compare_to_previous_state(t_tests, s_compare_to_state)

        print("======================================")
        print("======= Finished running tests =======")
        print("======================================\n")

        # Print total runtime
        elapsed_time = time.time() - h_timer
        print(f"Total elapsed time: {TestVHAB._secs_to_hms(elapsed_time)}")

    @staticmethod
    def _get_tests(s_test_directory):
        """
        Fetch tests from the specified directory.
        """
        t_tests = []
        for item in os.listdir(s_test_directory):
            if item.startswith("+") and os.path.isdir(os.path.join(s_test_directory, item)):
                t_tests.append({"name": item, "status": None, "error_report": None})
        return t_tests

    @staticmethod
    def _create_data_folder_path():
        """
        Generate a unique data folder path for saving results.
        """
        base_path = Path("data/figures/Test")
        timestamp = datetime.now().strftime("%Y%m%d")
        for i in range(1, 1000):
            folder_path = base_path / f"{timestamp}_Test_Run_{i}"
            if not folder_path.exists():
                folder_path.mkdir(parents=True, exist_ok=True)
                return str(folder_path)
        raise RuntimeError("Failed to create unique folder path.")

    @staticmethod
    def _check_for_changes():
        """
        Check if core, library, or test files have changed.
        """
        # Example: Check if files in specific directories have been modified
        directories = ["core", "lib", "user/+tests"]
        changed = False
        descriptions = []

        for directory in directories:
            if TestVHAB._has_directory_changed(directory):
                changed = True
                descriptions.append(directory)

        return changed, ", ".join(descriptions)

    @staticmethod
    def _has_directory_changed(directory):
        """
        Check if a directory has changed based on timestamps (dummy implementation).
        """
        # Placeholder: Check file modification times against a saved state
        return True

    @staticmethod
    def _run_parallel_tests(t_tests, s_test_directory, s_folder_path, f_sim_time, b_debug_mode_on):
        """
        Run tests in parallel using multiprocessing.
        """
        print("Running tests in parallel...")
        with multiprocessing.Pool() as pool:
            results = [
                pool.apply_async(
                    TestVHAB._run_test,
                    (test, s_test_directory, s_folder_path, f_sim_time, True, b_debug_mode_on)
                )
                for test in t_tests
            ]
            for result in results:
                result.wait()

    @staticmethod
    def _run_serial_tests(t_tests, s_test_directory, s_folder_path, f_sim_time, b_debug_mode_on):
        """
        Run tests serially.
        """
        print("Running tests serially...")
        for test in t_tests:
            TestVHAB._run_test(test, s_test_directory, s_folder_path, f_sim_time, False, b_debug_mode_on)

    @staticmethod
    def _run_test(test, s_test_directory, s_folder_path, f_sim_time, b_parallel_execution, b_debug_mode_on):
        """
        Run a single test and update its status.
        """
        try:
            # Placeholder: Simulate running the test
            time.sleep(1)  # Simulate processing
            test["status"] = "Successful"
        except Exception as e:
            test["status"] = "Aborted"
            test["error_report"] = str(e)

    @staticmethod
    def _save_test_data(t_tests):
        """
        Save test results to a file.
        """
        output_path = Path("data/TestStatus.json")
        output_path.write_text(str(t_tests))

    @staticmethod
    def _display_summary(t_tests):
        """
        Display a summary of test results.
        """
        successful = sum(1 for test in t_tests if test["status"] == "Successful")
        aborted = sum(1 for test in t_tests if test["status"] == "Aborted")
        skipped = sum(1 for test in t_tests if test["status"] == "Skipped")

        print(f"Total Tests: {len(t_tests)}")
        print(f"Successful: {successful}")
        print(f"Aborted: {aborted}")
        print(f"Skipped: {skipped}")

    @staticmethod
    def _compare_to_previous_state(t_tests, s_compare_to_state):
        """
        Compare current test results to a previous state.
        """
        # Placeholder: Compare results and generate a report
        pass

    @staticmethod
    def _secs_to_hms(seconds):
        """
        Convert seconds to hours, minutes, and seconds.
        """
        h = int(seconds // 3600)
        m = int((seconds % 3600) // 60)
        s = seconds % 60
        return f"{h}h {m}m {s:.1f}s"

    @staticmethod
    def _has_parallel_support():
        """
        Check if parallel processing is supported.
        """
        return multiprocessing.cpu_count() > 1


# Example usage:
if __name__ == "__main__":
    TestVHAB.test_vhab()
