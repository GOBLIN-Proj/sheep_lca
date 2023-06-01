import unittest
import pandas as pd
from sheep_lca.models import load_livestock_data, load_farm_data
from sheep_lca.lca import AirQualityTotals
import copy
import matplotlib.pyplot as plt
import os


class DatasetLoadingTestCase(unittest.TestCase):
    def setUp(self):
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

        farm_data = {
            "ef_country": ["ireland"],
            "farm_id": [2018],
            "year": [2018],
            "total_urea": [2072487.127],
            "total_urea_abated": [0],
            "total_n_fert": [17310655.18],
            "total_p_fert": [1615261.859],
            "total_k_fert": [3922778.8],
            "diesel_kg": [0],
            "elec_kwh": [0],
        }

        self.farm_dataframe = pd.DataFrame(farm_data)
        self.airquality = AirQualityTotals("ireland")
        self.baseline_index = -1
        self.emissions_dict = self.airquality.create_emissions_dictionary([self.baseline_index])

    def test_emissions(self):
        
        past_animals = load_livestock_data(self.data_frame)
        past_farms = load_farm_data(self.farm_dataframe)

        past_animals_loc = list(past_animals.keys())[0]
        past_farm_loc = list(past_farms.keys())[0]
        self.emissions_dict["manure_management"][
            self.baseline_index
        ] += self.airquality.total_manure_NH3_AQ(past_animals[past_animals_loc]["animals"])

        self.emissions_dict["soils"][
            self.baseline_index
        ] += self.airquality.total_grazing_soils_NH3_AQ(past_animals[past_animals_loc]["animals"])

        self.emissions_dict["soils"][
            self.baseline_index
        ] += self.airquality.total_fertiliser_soils_NH3_AQ(
            past_farms[past_farm_loc].total_urea,
            past_farms[past_farm_loc].total_urea_abated,
            past_farms[past_farm_loc].total_n_fert,
        )



        print(self.emissions_dict)


        path = "data"
        labels = self.emissions_dict.keys()
        values = [self.emissions_dict[label][self.baseline_index] for label in labels] 

        plt.bar(labels, values)
        plt.xticks(rotation=90)
        plt.ylabel('Values')
        plt.xlabel('Categories')
        plt.title('Bar Chart')
        plt.tight_layout()

        plt.savefig(os.path.join(path,"air_quality_emissions_test.png"))


if __name__ == "__main__":
    unittest.main()
