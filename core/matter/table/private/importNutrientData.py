import os
import re

class NutrientImporter:
    def __init__(self):
        self.ttxNutrientData = {}
        self.csEdibleSubstances = []
        self.ttxMatter = {
            "C4H5ON": {"fNutritionalEnergy": 10},
            "C6H12O6": {"fNutritionalEnergy": 10},
            "C16H32O2": {"fNutritionalEnergy": 10},
        }  # Example placeholder data

    def normalize_path(self, path):
        """Replace non-standard characters in food names with underscores."""
        return re.sub(r'[^\w]', '_', path)

    def import_nutrient_data(self):
        data_dir = 'core/+matter/+data/+NutrientData'
        csv_files = [
            f for f in os.listdir(data_dir)
            if f.endswith('.csv')
        ]

        tConversion = {
            'g': 1e-3,
            'mg': 1e-6,
            'microg': 1e-9,
            'kcal': 4184,
            'kJ': 1000,
            'IU': 1
        }

        csCustomFoodNames = [
            ('Beans, snap', 'SnapBeans'),
            ('Onions, young green', 'GreenOnions'),
            ('ORGANIC WHOLE GROUND TIGERNUT', 'Chufa'),
            ('Beans, kidney', 'Drybean'),
            ('Potatoes', 'Whitepotato'),
            ('Soybeans', 'Soybean'),
            ('Tomatoes', 'Tomato'),
            ('Peanuts', 'Peanut'),
            ('Wild rice', 'Rice'),
            ('Sweet potato', 'Sweetpotato')
        ]

        for csv_file in csv_files:
            file_path = os.path.join(data_dir, csv_file)
            with open(file_path, 'r') as file:
                lines = file.readlines()

            acData = []
            sFoodName = ""
            iHeaderRows = None
            iDataColumn = None

            for i, line in enumerate(lines):
                if "Nutrient data for:" in line:
                    split_line = re.split(r': ', line)
                    sFoodName = split_line[1].strip()
                    for custom_name, replacement in csCustomFoodNames:
                        if custom_name in sFoodName:
                            sFoodName = replacement
                            break
                    sFoodName = self.normalize_path(sFoodName)

                elif "per 100 g" in line:
                    columns = line.split(',')
                    iDataColumn = next(
                        i for i, col in enumerate(columns) if "per 100 g" in col
                    )

                elif "Proximates" in line:
                    iHeaderRows = i

                elif iHeaderRows and i > iHeaderRows:
                    if 'Sources of Data' in line or line.strip() == "":
                        break
                    acData.append(re.split(r',(?=(?:[^\"]*\"[^\"]*\")*[^\"]*$)', line))

            self.ttxNutrientData[sFoodName] = {}
            sSubHeader = None

            for row in acData:
                row_name = row[0].strip().strip('"')
                if len(row) == 1:
                    sSubHeader = row_name
                else:
                    sUnit = row[1].strip()
                    sUnit = sUnit.replace('�g', 'microg')
                    fData = tConversion[sUnit] * 10 * float(row[iDataColumn])

                    sUnitHeader = 'Mass' if sUnit not in ('IU', 'kcal', 'kJ') else 'Energy'
                    if sUnitHeader not in self.ttxNutrientData[sFoodName]:
                        self.ttxNutrientData[sFoodName][sUnitHeader] = {}

                    if sSubHeader:
                        if sSubHeader not in self.ttxNutrientData[sFoodName][sUnitHeader]:
                            self.ttxNutrientData[sFoodName][sUnitHeader][sSubHeader] = {}
                        self.ttxNutrientData[sFoodName][sUnitHeader][sSubHeader][row_name] = fData
                    else:
                        self.ttxNutrientData[sFoodName][sUnitHeader][row_name] = fData

        # Example of adding a generic "Food" entry with predefined values
        self.ttxNutrientData['Food'] = {
            "Mass": {
                "Water": 0.4636,
                "Protein": 0.175,
                "Carbohydrate_by_difference": 0.525,
                "Total_lipid_fat": 0.3,
                "Ash": 0.001,
                "Fiber_total_dietary": 0.012
            }
        }

        # Example of using the data to define compound masses
        self.csEdibleSubstances = list(self.ttxNutrientData.keys())
        for substance in self.csEdibleSubstances:
            mass_data = self.ttxNutrientData[substance].get("Mass", {})
            # Here you would define compound masses using the imported data
            # Example: self.define_compound_mass(substance, mass_data)

    def define_compound_mass(self, substance_name, composition):
        """
        Example placeholder for defining compound masses.
        """
        print(f"Defining compound mass for {substance_name}: {composition}")


# Example usage
nutrient_importer = NutrientImporter()
nutrient_importer.import_nutrient_data()
