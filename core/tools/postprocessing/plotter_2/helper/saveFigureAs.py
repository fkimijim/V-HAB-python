import os
import tkinter as tk
from tkinter import filedialog, simpledialog
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

# Global variables for previous path and format
previous_path = ""
previous_format = ""

# Fixed file types
file_types = [
    ("MATLAB Figure", "*.fig"),
    ("PDF", "*.pdf"),
    ("PNG", "*.png"),
    ("JPEG", "*.jpg"),
    ("SVG", "*.svg"),
    ("EMF", "*.emf"),
]

def save_figure_as():
    global previous_path, previous_format

    # Default save location
    initial_dir = previous_path if os.path.isdir(previous_path) else os.getcwd()

    # Open file dialog to get the save path and file type
    root = tk.Tk()
    root.withdraw()
    file_path = filedialog.asksaveasfilename(
        initialdir=initial_dir,
        title="Save as",
        filetypes=file_types
    )

    if not file_path:
        print("Save operation canceled.")
        return

    # Save the selected path for future use
    previous_path = os.path.dirname(file_path)

    # Determine file format from file extension
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension == ".pdf":
        format_flag = "pdf"
    elif file_extension == ".png":
        format_flag = "png"
    elif file_extension == ".jpg":
        format_flag = "jpeg"
    elif file_extension == ".svg":
        format_flag = "svg"
    elif file_extension == ".emf":
        format_flag = "emf"
    else:
        print("Unsupported file format.")
        return

    # Ask for additional settings using a simple dialog
    figure_width = simpledialog.askfloat("Figure Width", "Enter figure width in cm:", minvalue=5.0, maxvalue=50.0, initialvalue=16.0)
    figure_height = simpledialog.askfloat("Figure Height", "Enter figure height in cm:", minvalue=5.0, maxvalue=50.0, initialvalue=10.0)
    font_name = simpledialog.askstring("Font Name", "Enter font name:", initialvalue="Arial")
    font_size = simpledialog.askinteger("Font Size", "Enter font size (pt):", minvalue=6, maxvalue=36, initialvalue=8)

    if None in [figure_width, figure_height, font_name, font_size]:
        print("Settings dialog canceled.")
        return

    # Adjust figure size and font
    fig = plt.gcf()
    fig.set_size_inches(figure_width / 2.54, figure_height / 2.54)  # cm to inches
    plt.rcParams.update({"font.size": font_size, "font.family": font_name})

    # Save figure based on selected format
    if format_flag == "pdf":
        with PdfPages(file_path) as pdf:
            pdf.savefig(fig, bbox_inches='tight')
    else:
        fig.savefig(file_path, format=format_flag, bbox_inches='tight', dpi=300)

    print(f"Figure saved to {file_path}")

# Example usage
if __name__ == "__main__":
    # Create a sample plot for testing
    plt.figure()
    plt.plot([0, 1, 2, 3], [10, 20, 25, 30])
    plt.title("Sample Plot")
    plt.xlabel("X Axis")
    plt.ylabel("Y Axis")

    save_figure_as()
