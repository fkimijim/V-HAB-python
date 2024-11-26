import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "matter", "data")))
import AntoineData

AntoineData = AntoineData()

def import_antoine_data(self):
    """
    Imports data for the Antoine equation for vapor pressure.
    This function manipulates the `ttxMatter` property of the matter table
    class and adds properties to several substances required in the Antoine equation.
    """
    # Retrieve the list of substances from the AntoineData class
    cs_substances = dir(AntoineData)

    # Loop through each substance and add the Antoine parameters to the matter table
    for substance in cs_substances:
        if not substance.startswith('_'):  # Ignore built-in attributes
            self.ttxMatter[substance]["cxAntoineParameters"] = getattr(AntoineData, substance)
