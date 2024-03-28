import pandas as pd
from sheep_lca.resource_manager.models import load_livestock_data, load_farm_data
from sheep_lca.lca import ClimateChangeTotals


def main():
    # Instantiate ClimateChange Totals Class, passing Ireland as the emissions factor country
    climatechange = ClimateChangeTotals("ireland")

    # Create a dictionary to store results
    index = -1
    emissions_dict = climatechange.create_emissions_dictionary([index])

    # Create some data to generate results

    livestock_data = {
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

    livestock_data_frame = pd.DataFrame(livestock_data)

    farm_data = {
        'ef_country': ['ireland'],
        'farm_id': [2018],
        'year': [2018],
        'total_urea_kg': [2072487.127],
        'total_lime_kg': [2072487.127],
        'an_n_fert': [2072487.127],
        'urea_n_fert': [2072487],
        'total_urea_abated': [17310655.18],
        'total_p_fert': [1615261.859],
        'total_k_fert': [3922778.8],
        'diesel_kg': [0],
        'elec_kwh': [0]
    }

    farm_dataframe = pd.DataFrame(farm_data)

    # load the dataframes
    animals = load_livestock_data(livestock_data_frame)
    farms = load_farm_data(farm_dataframe)

    animals_loc = list(animals.keys())[0]
    farm_loc = list(farms.keys())[0]

    # generate results and store them in the dictionary

    emissions_dict["enteric_ch4"][index] += climatechange.CH4_enteric_ch4(
        animals[animals_loc]["animals"]
    )
    emissions_dict["manure_management_N2O"][index] += climatechange.Total_storage_N2O(
        animals[animals_loc]["animals"]
    )
    emissions_dict["manure_management_CH4"][
        index
    ] += climatechange.CH4_manure_management(animals[animals_loc]["animals"])
    emissions_dict["manure_applied_N"][index] += 0

    emissions_dict["N_direct_PRP"][index] += climatechange.N2O_total_PRP_N2O_direct(
        animals[animals_loc]["animals"]
    )

    emissions_dict["N_indirect_PRP"][index] += climatechange.N2O_total_PRP_N2O_indirect(
        animals[animals_loc]["animals"]
    )
    emissions_dict["N_direct_fertiliser"][index] = climatechange.N2O_direct_fertiliser(
        farms[farm_loc].urea_n_fert,
        farms[farm_loc].total_urea_abated,
        farms[farm_loc].an_n_fert,
    )

    emissions_dict["N_indirect_fertiliser"][
        index
    ] += climatechange.N2O_fertiliser_indirect(
        farms[farm_loc].urea_n_fert,
        farms[farm_loc].total_urea_abated,
        farms[farm_loc].an_n_fert,
    )
    emissions_dict["soils_CO2"][index] += climatechange.CO2_soils_GWP(
        farms[farm_loc].total_urea_kg,
        farms[farm_loc].total_lime_kg,
    )

    # Add the totals
    emissions_dict["soil_organic_N_direct"][index] = (
        emissions_dict["manure_applied_N"][index]
        + emissions_dict["N_direct_PRP"][index]
    )
    emissions_dict["soil_organic_N_indirect"][index] = emissions_dict["N_indirect_PRP"][
        index
    ]

    emissions_dict["soil_inorganic_N_direct"][index] = emissions_dict[
        "N_direct_fertiliser"
    ][index]
    emissions_dict["soil_inorganic_N_indirect"][index] = emissions_dict[
        "N_indirect_fertiliser"
    ][index]

    emissions_dict["soil_N_direct"][index] = (
        emissions_dict["soil_organic_N_direct"][index]
        + emissions_dict["soil_inorganic_N_direct"][index]
    )

    emissions_dict["soil_N_indirect"][index] = (
        emissions_dict["soil_inorganic_N_indirect"][index]
        + emissions_dict["soil_organic_N_indirect"][index]
    )

    emissions_dict["soils_N2O"][index] = (
        emissions_dict["soil_N_direct"][index]
        + emissions_dict["soil_N_indirect"][index]
    )

    # Print the emission results dictionary
    print(emissions_dict)


if __name__ == "__main__":
    main()
