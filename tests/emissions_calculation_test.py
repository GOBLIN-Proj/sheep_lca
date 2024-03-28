import unittest
import pandas as pd
from sheep_lca.models import load_livestock_data, load_farm_data
from sheep_lca.lca import ClimateChangeTotals
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
        self.climatechange = ClimateChangeTotals("ireland")
        self.baseline_index = -1
        self.emissions_dict = self.climatechange.create_expanded_emissions_dictionary([self.baseline_index])

    def test_emissions(self):
        
        past_animals = load_livestock_data(self.data_frame)
        past_farms = load_farm_data(self.farm_dataframe)

        past_animals_loc = list(past_animals.keys())[0]
        past_farm_loc = list(past_farms.keys())[0]

        self.emissions_dict["enteric_ch4"][
            self.baseline_index
        ] += self.climatechange.CH4_enteric_ch4(past_animals[past_animals_loc]["animals"]) * 28

        self.emissions_dict["manure_management_N2O"][
            self.baseline_index
        ] += self.climatechange.Total_storage_N2O(past_animals[past_animals_loc]["animals"]) * 298

        self.emissions_dict["manure_management_CH4"][
            self.baseline_index
        ] += self.climatechange.CH4_manure_management(
            past_animals[past_animals_loc]["animals"]
        ) * 28
        self.emissions_dict["manure_applied_N"][self.baseline_index] += 0

        self.emissions_dict["N_direct_PRP"][
            self.baseline_index
        ] += self.climatechange.N2O_total_PRP_N2O_direct(
            past_animals[past_animals_loc]["animals"]
        )* 298

        self.emissions_dict["N_indirect_PRP"][
            self.baseline_index
        ] += self.climatechange.N2O_total_PRP_N2O_indirect(
            past_animals[past_animals_loc]["animals"]
        ) *298

        self.emissions_dict["N_direct_fertiliser"][
            self.baseline_index
        ] = self.climatechange.N2O_direct_fertiliser(
            past_farms[past_farm_loc].total_urea,
            past_farms[past_farm_loc].total_urea_abated,
            past_farms[past_farm_loc].total_n_fert,
        )*298

        self.emissions_dict["N_indirect_fertiliser"][
            self.baseline_index
        ] += self.climatechange.N2O_fertiliser_indirect(
            past_farms[past_farm_loc].total_urea,
            past_farms[past_farm_loc].total_urea_abated,
            past_farms[past_farm_loc].total_n_fert,
        )* 298
        
        self.emissions_dict["soils_CO2"][
            self.baseline_index
        ] += self.climatechange.CO2_soils_GWP(
            past_farms[past_farm_loc].total_urea,
            past_farms[past_farm_loc].total_urea_abated,
        )

        self.emissions_dict["upstream_fuel_fert"][
            self.baseline_index
        ] += self.climatechange.upstream_and_inputs_and_fuel_co2(
            past_farms[past_farm_loc].diesel_kg,
            past_farms[past_farm_loc].elec_kwh,
            past_farms[past_farm_loc].total_n_fert,
            past_farms[past_farm_loc].total_urea,
            past_farms[past_farm_loc].total_urea_abated,
            past_farms[past_farm_loc].total_p_fert,
            past_farms[past_farm_loc].total_k_fert,
        )

        self.emissions_dict["upstream_feed"][
            self.baseline_index
        ] += self.climatechange.co2_from_concentrate_production(
            past_animals[past_animals_loc]["animals"]
        )

        # Totals
        self.emissions_dict["soil_organic_N_direct"][self.baseline_index] = (
            self.emissions_dict["manure_applied_N"][self.baseline_index]
            + self.emissions_dict["N_direct_PRP"][self.baseline_index]
        )
        self.emissions_dict["soil_organic_N_indirect"][
            self.baseline_index
        ] = self.emissions_dict["N_indirect_PRP"][self.baseline_index]

        self.emissions_dict["soil_inorganic_N_direct"][
            self.baseline_index
        ] = self.emissions_dict["N_direct_fertiliser"][self.baseline_index]
        self.emissions_dict["soil_inorganic_N_indirect"][
            self.baseline_index
        ] = self.emissions_dict["N_indirect_fertiliser"][self.baseline_index]

        self.emissions_dict["soil_N_direct"][self.baseline_index] = (
            self.emissions_dict["soil_organic_N_direct"][self.baseline_index]
            + self.emissions_dict["soil_inorganic_N_direct"][self.baseline_index]
        )

        self.emissions_dict["soil_N_indirect"][self.baseline_index] = (
            self.emissions_dict["soil_inorganic_N_indirect"][self.baseline_index]
            + self.emissions_dict["soil_organic_N_indirect"][self.baseline_index]
        )

        self.emissions_dict["soils_N2O"][self.baseline_index] = (
            self.emissions_dict["soil_N_direct"][self.baseline_index]
            + self.emissions_dict["soil_N_indirect"][self.baseline_index]
        )

        self.emissions_dict["upstream"][self.baseline_index]  = (
            self.emissions_dict["upstream_fuel_fert"][self.baseline_index] 
            + self.emissions_dict["upstream_feed"][self.baseline_index] 
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

        plt.savefig(os.path.join(path,"emissions_test.png"))

if __name__ == "__main__":
    unittest.main()
