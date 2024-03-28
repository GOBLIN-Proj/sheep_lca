from sheep_lca.models import print_livestock_data, load_livestock_data
from sheep_lca.animal_data import AnimalData as ad
import pandas as pd 


def main():

        #Create some data to generate results 

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
    columns = ['ef_country', 'farm_id', 'year', 'cohort', 'pop', 'weight', 'daily_milk', 'forage', 'grazing',
                'con_type', 'con_amount', 't_outdoors', 't_indoors', 'wool', 't_stabled', 'mm_storage',
                'daily_spreading', 'n_sold', 'n_bought']
    
    livestock_data_frame = pd.DataFrame(livestock_data, columns=columns)

    animals = load_livestock_data(livestock_data_frame)

    print_livestock_data(animals)

    cohorts = livestock_data_frame.cohort.unique()

    print(cohorts)

    for cohort in cohorts:
        animal = getattr(animals[2018]["animals"], cohort)
        print(f"{cohort}: bought: {ad.get_animal_bought(animal)}")
        print(f"{cohort}: sold: {ad.get_animal_sold(animal)}")
        print(f"{cohort}: population: {ad.get_animal_population(animal)}")
        print(f"{cohort}: weight: {ad.get_animal_weight(animal)}")
        print(f"{cohort}: daily milk: {ad.get_animal_daily_milk(animal)}")
        print(f"{cohort}: grazing: {ad.get_animal_grazing(animal)}")
        print(f"{cohort}: t outdoors: {ad.get_animal_t_outdoors(animal)}")

        print(f"{cohort}: t indoors: {ad.get_animal_t_indoors(animal)}")
        print(f"{cohort}: t stabled: {ad.get_animal_t_stabled(animal)}")
        print(f"{cohort}: mm storage: {ad.get_animal_mm_storage(animal)}")
        print(f"{cohort}: forage: {ad.get_animal_forage(animal)}")
        print(f"{cohort}: concentrate type: {ad.get_animal_concentrate_type(animal)}")
        print(f"{cohort}: concentrate amount: {ad.get_animal_concentrate_amount(animal)}")
        print(f"{cohort}: year: {ad.get_animal_year(animal)}")
        print(f"{cohort}: cohort: {ad.get_animal_cohort(animal)}")
        

if __name__ == '__main__': 
    main()