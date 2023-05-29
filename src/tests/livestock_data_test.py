import unittest
import pandas as pd
import os
from sheep_lca.models import load_livestock_data, print_livestock_data
import io
from contextlib import redirect_stdout


def capture_stdout(function, *args, **kwargs):
    f = io.StringIO()
    with redirect_stdout(f):
        function(*args, **kwargs)

    return f.getvalue()


def read_expected_output(filename, path):
    with open(os.path.join(path, filename), "r") as file:
        return file.read()


class DatasetLoadingTestCase(unittest.TestCase):
    def setUp(self):
        self.txt_path = "./data"
        # Create the DataFrame with the provided data

        data = {
            "ef_country": [
                "ireland",
                "ireland",
                "ireland",
                "ireland",
                "ireland",
                "ireland",
                "ireland",
                "ireland",
                "ireland",
                "ireland",
            ],
            "farm_id": [2018, 2018, 2018, 2018, 2018, 2018, 2018, 2018, 2018, 2018],
            "year": [2018, 2018, 2018, 2018, 2018, 2018, 2018, 2018, 2018, 2018],
            "cohort": [
                "ewes",
                "ewes",
                "ram",
                "ram",
                "lamb_more_1_yr",
                "lamb_more_1_yr",
                "lamb_less_1_yr",
                "lamb_less_1_yr",
                "male_less_1_yr",
                "male_less_1_yr",
            ],
            "pop": [
                37812.8,
                9453.199999,
                1146.402738,
                295.9906066,
                2237.334377,
                554.9823874,
                17417.92548,
                4365.861448,
                10891.89346,
                7628.877455,
            ],
            "weight": [68, 68, 86, 86, 68, 68, 33, 33, 33, 33],
            "daily_milk": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "forage": [
                "average",
                "average",
                "average",
                "average",
                "average",
                "average",
                "average",
                "average",
                "average",
                "average",
            ],
            "grazing": [
                "flat_pasture",
                "hilly_pasture",
                "flat_pasture",
                "hilly_pasture",
                "flat_pasture",
                "hilly_pasture",
                "flat_pasture",
                "hilly_pasture",
                "flat_pasture",
                "hilly_pasture",
            ],
            "con_type": [
                "concentrate",
                "concentrate",
                "concentrate",
                "concentrate",
                "concentrate",
                "concentrate",
                "concentrate",
                "concentrate",
                "concentrate",
                "concentrate",
            ],
            "con_amount": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "t_outdoors": [
                21.36,
                21.36,
                21.36,
                21.36,
                21.36,
                21.36,
                21.36,
                21.36,
                21.36,
                21.36,
            ],
            "t_indoors": [2.64, 2.64, 2.64, 2.64, 2.64, 2.64, 2.64, 2.64, 2.64, 2.64],
            "wool": [4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5, 4.5],
            "t_stabled": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "mm_storage": [
                "solid",
                "solid",
                "solid",
                "solid",
                "solid",
                "solid",
                "solid",
                "solid",
                "solid",
                "solid",
            ],
            "daily_spreading": [
                "broadcast",
                "broadcast",
                "broadcast",
                "broadcast",
                "broadcast",
                "broadcast",
                "broadcast",
                "broadcast",
                "broadcast",
                "broadcast",
            ],
            "n_sold": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            "n_bought": [0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        }
        self.data_frame = pd.DataFrame(data)

    def test_data_set_creation(self):
        # Perform assertions or tests on the loaded DataFrame
        self.assertEqual(len(self.data_frame), 10)  # Example assertion

    def test_output_livestock(self):
        data = load_livestock_data(self.data_frame)
        print(print_livestock_data(data))
        output = capture_stdout(print_livestock_data, data)

        # Validate the output
        expected_output = read_expected_output("livestock.txt", self.txt_path)
        self.assertEqual(output.strip(), expected_output.strip())


if __name__ == "__main__":
    unittest.main()
