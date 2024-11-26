import os
import re
import json

class Table:
    """
    MatterTable contains all matter-related data and some functions.

    This class mimics the behavior of MATLAB's `table` class from V-HAB.
    """

    # Class constants
    CONST = {
        'fUniversalGas': 8.314472,
        'fGravitation': 6.67384e-11,
        'fAvogadro': 6.02214129e23,
        'fBoltzmann': 1.3806488e-23,
        'fStefanBoltzmann': 5.670373e-8,
        'fLightSpeed': 2.998e8,
        'fPlanck': 6.626e-34,
        'fFaraday': 96485.3365,
    }

    STANDARD = {
        'Temperature': 288.15,  # K (15 deg C)
        'Pressure': 101325,  # Pa (sea-level pressure)
    }

    def __init__(self):
        """
        Class constructor to initialize the matter table.
        """
        print("Checking for changes regarding the matter table source data.")

        # Placeholder for loaded or initialized data
        self.ttxMatter = {}
        self.afMolarMass = []
        self.aiCharge = []
        self.afNutritionalEnergy = []
        self.afDissociationConstant = []
        self.tiN2I = {}
        self.csSubstances = []
        self.iSubstances = 0
        self.csI2N = []
        self.abCompound = []
        self.abEdibleSubstances = []
        self.csEdibleSubstances = []

        # Attempt to load existing matter data
        self.load_matter_data()

    def load_matter_data(self):
        """
        Load matter data or initialize from scratch if not available.
        """
        data_file = os.path.join("data", "MatterData.json")

        if os.path.exists(data_file):
            with open(data_file, 'r') as file:
                print("Loading MatterData from stored file.")
                data = json.load(file)
                self.ttxMatter = data['ttxMatter']
                self.afMolarMass = data['afMolarMass']
                self.aiCharge = data['aiCharge']
                self.afNutritionalEnergy = data['afNutritionalEnergy']
                self.afDissociationConstant = data['afDissociationConstant']
                self.tiN2I = data['tiN2I']
                self.csSubstances = data['csSubstances']
                self.iSubstances = len(self.csSubstances)
                self.csI2N = data['csI2N']
                self.abCompound = data['abCompound']
                self.abEdibleSubstances = data['abEdibleSubstances']
                self.csEdibleSubstances = data['csEdibleSubstances']
        else:
            print("Regenerating matter table from scratch.")
            self.initialize_matter_table()

    def initialize_matter_table(self):
        """
        Initialize the matter table from raw data sources.
        """
        # Placeholder: Load the necessary data
        # For simplicity, these should be replaced with actual data import logic.
        self.ttxMatter = self.import_matter_data("MatterData.csv")
        self.csSubstances = list(self.ttxMatter.keys())
        self.iSubstances = len(self.csSubstances)
        self.afMolarMass = [0] * self.iSubstances
        self.aiCharge = [0] * self.iSubstances
        self.afNutritionalEnergy = [0] * self.iSubstances
        self.abCompound = [False] * self.iSubstances
        self.abEdibleSubstances = [False] * self.iSubstances
        self.csI2N = self.csSubstances[:]

        for i, substance in enumerate(self.csSubstances):
            self.tiN2I[substance] = i

        # Save initialized data
        self.save_matter_data()

    def save_matter_data(self):
        """
        Save the initialized matter table to a file for future use.
        """
        data = {
            'ttxMatter': self.ttxMatter,
            'afMolarMass': self.afMolarMass,
            'aiCharge': self.aiCharge,
            'afNutritionalEnergy': self.afNutritionalEnergy,
            'afDissociationConstant': self.afDissociationConstant,
            'tiN2I': self.tiN2I,
            'csSubstances': self.csSubstances,
            'csI2N': self.csI2N,
            'abCompound': self.abCompound,
            'abEdibleSubstances': self.abEdibleSubstances,
            'csEdibleSubstances': self.csEdibleSubstances,
        }

        data_file = os.path.join("data", "MatterData.json")
        os.makedirs(os.path.dirname(data_file), exist_ok=True)

        with open(data_file, 'w') as file:
            json.dump(data, file)
        print("MatterData saved successfully.")

    @staticmethod
    def import_matter_data(filename):
        """
        Placeholder for importing matter data from a CSV file.
        """
        # Example data, replace with real data parsing logic
        print(f"Importing data from {filename}")
        return {
            "H2O": {"fMolarMass": 18.015, "iCharge": 0, "fNutritionalEnergy": 0},
            "CO2": {"fMolarMass": 44.01, "iCharge": 0, "fNutritionalEnergy": 0},
        }

    @staticmethod
    def extract_atomic_types(s_molecule):
        """
        Extract the single atoms out of a molecule string, e.g. CO2
        leads to {'C': 1, 'O': 2}.
        """
        elements = {}
        current_element = ""
        atom_count = ""

        # Remove ion denominators from the molecule name
        s_molecule = re.sub(r'plus|minus', '', s_molecule)

        for char in s_molecule:
            if char.isdigit():
                atom_count += char
            elif char.isupper():
                if current_element:
                    elements[current_element] = int(atom_count) if atom_count else 1
                current_element = char
                atom_count = ""
            elif char.islower():
                current_element += char

        if current_element:
            elements[current_element] = int(atom_count) if atom_count else 1

        return elements
