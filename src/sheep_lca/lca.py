# IMPORTS
from sheep_lca.data_loader import Loader
import copy


class Cohorts:
    def __init__(self) -> None:
        self.COHORTS = [
            "ewes",
            "lamb_less_1_yr",
            "lamb_more_1_yr",
            "male_less_1_yr",
            "ram",
        ]


###################################################################################################################
class Energy:
    def __init__(self, ef_country):
        self.loader_class = Loader(ef_country)

    def ratio_of_net_energy_maintenance(self, animal):
        """
            REM = Ratio of net energy maintenance to the amount of (DE) total energy
            consumed, minus poop

            DE = the digestible energy expressed as a percentage of gross energy
            (digestible dry matter )

        Parameters
        ----------

        animal: accepts the animal cohort type from the animal input data. For example,
        the input to calculate the REM for milking cows will be:
            for i in [data].values():
                print(lca.ratio_of_net_energy_maintenance(i.animals.ewes,grass))

        grass: accepts the grass database as a parameter, and utilises the digestible energy
        from the forage type that has been input into the animal and farm data.

        Returns
        -------
        The ratio of energy for maintenance as a float.

        See Also
        -------
        EQUATION 10.14 RATIO OF NET ENERGY AVAILABLE IN A DIET FOR MAINTENANCE TO DIGESTIBLE ENERGY
        2019 Refinement to the 2006 IPCC Guidelines for National Greenhouse Gas Inventories

        """
        # Raise errors for invalid input
        # if any(map((lambda value: type(value) != str), (animal, grass))):
        # raise ValueError("Input values must not be negative numbers")

        # if (type(animal) != models.AnimalCategory or type(grass) != models.Grass):
        #     raise TypeError("Animal and Grass inputs must be of be a 'models' Class")

        DE = self.loader_class.grass.get_forage_dry_matter_digestibility(animal.forage)

        # (1.123 - (4.092 * (10**-3) * DE) + (1.126 * (10**-5) * (DE ** 2)) - (25.4 / DE))

        return (
            1.123
            - (4.092 * (10**-3) * DE)
            + (1.126 * (10**-5) * (DE**2))
            - (25.4 / DE)
        )

        # 1.123-(4.092*(POWER(10,-3))*REFS!$Y$22)+
        # (1.126*(POWER(10,-5))*REFS!$Y$22)*(REFS!$Y$22))-(25.4/(IFERROR(VLOOKUP(CP!J2,REFS!X:Y,2,FALSE),REFS!$Y$22)))

    def ratio_of_net_energy_growth(self, animal):
        """
        REG = Ration of net energy for growth to total energy consumed, minus poop

            DE = the digestible energy expressed as a percentage of gross energy
            (digestible dry matter )

        Parameters
        ----------

        animal: accepts the animal cohort type from the animal input data. For example,
        the input to calculate the REM for milking cows will be:
            for i in [data].values():
                print(lca.ratio_of_net_energy_maintenance(i.animals.ewes,grass))

        grass: accepts the grass database as a parameter, and utilises the digestible energy
        from the forage type that has been input into the animal and farm data.

        Returns
        -------
        The ratio of energy for growth as a float.
        See Also
        -------
        EQUATION 10.15 RATIO OF NET ENERGY AVAILABLE FOR GROWTH IN A DIET TO DIGESTIBLE ENERGY CONSUMED
        2019 Refinement to the 2006 IPCC Guidelines for National Greenhouse Gas Inventories

        """

        DE = self.loader_class.grass.get_forage_dry_matter_digestibility(animal.forage)

        return (
            1.164
            - (5.160 * (10**-3) * DE)
            + (1.308 * (10**-5) * (DE**2))
            - (37.4 / DE)
        )

    #############################################################################################
    # Energy & Enteric Fermentation
    #############################################################################################

    def net_energy_for_maintenance(self, animal):
        """
        When this function is called, it returns the coefficient, which is the emisions factor for net energy
        for lactation, multiplied by the square root of animal weight to the power of 0.75.

        coefficient X (animal_weight^0.75)

        It utilises equation 10.3 from the IPCC 2006 guidelines (NEm)
        """

        coefficient = {
            "ewes": self.loader_class.emissions_factors.get_ef_net_energy_for_maintenance_sheep_more_than_a_year(),
            "lamb_less_1_yr": self.loader_class.emissions_factors.get_ef_net_energy_for_maintenance_sheep_up_to_a_year(),
            "lamb_more_1_yr": self.loader_class.emissions_factors.get_ef_net_energy_for_maintenance_sheep_more_than_a_year(),
            "male_less_1_yr": self.loader_class.emissions_factors.get_ef_net_energy_for_maintenance_intact_male_up_to_year(),
            "ram": self.loader_class.emissions_factors.get_ef_net_energy_for_maintenance_intact_male_more_than_a_year(),
        }

        cfi = coefficient.get(animal.cohort)

        return cfi * (animal.weight**0.75)

    def net_energy_for_activity(self, animal):
        """
        When this function is called it utilises the net_energy_for_maintenance eq multiplied by
        the coefficient for feed situation

        The equation is based on equation 10.4 from the IPCC 2006 guidelines.
        """

        grazing_type_coef = {
            "flat_pasture": self.loader_class.emissions_factors.get_ef_feeding_situation_grazing_flat_pasture(),
            "hilly_pasture": self.loader_class.emissions_factors.get_ef_feeding_situation_grazing_hilly_pasture(),
            "housed_ewe": self.loader_class.emissions_factors.get_ef_feeding_situation_housed_ewes(),
            "housed_lamb": self.loader_class.emissions_factors.get_ef_feeding_situation_housed_fattening_lambs(),
        }

        return grazing_type_coef.get(animal.grazing) * animal.weight

    def net_energy_for_weight_gain(self, animal):

        """
        This function is the net energy for growth, it is parameterised to the animals weight gain per day.
        It utilises equation 10.6 from the IPCC 2006 guidelines (NEg)

        """

        bwi = {
            "ewes": self.loader_class.animal_features.get_ewe_weight_after_weaning(),
            "lamb_less_1_yr": self.loader_class.animal_features.get_lamb_weight_gain(),
            "lamb_more_1_yr": self.loader_class.animal_features.get_lamb_weight_gain(),
            "male_less_1_yr": self.loader_class.animal_features.get_lamb_weight_gain(),
            "ram": self.loader_class.animal_features.get_ram_weight_after_weaning(),
        }

        bwf = {
            "ewes": self.loader_class.animal_features.get_ewe_weight_1_year_old(),
            "lamb_less_1_yr": self.loader_class.animal_features.get_lamb_less_1_yr_weight(),
            "lamb_more_1_yr": self.loader_class.animal_features.get_lamb_more_1_yr_weight(),
            "male_less_1_yr": self.loader_class.animal_features.get_lamb_less_1_yr_weight(),
            "ram": self.loader_class.animal_features.get_ram_weight_1_year_old(),
        }

        coef_a = {
            "ewes": self.loader_class.emissions_factors.get_ef_net_energy_for_growth_females_a(),
            "lamb_less_1_yr": self.loader_class.emissions_factors.get_ef_net_energy_for_growth_females_a(),
            "lamb_more_1_yr": self.loader_class.emissions_factors.get_ef_net_energy_for_growth_females_a(),
            "male_less_1_yr": self.loader_class.emissions_factors.get_ef_net_energy_for_growth_males_a(),
            "ram": self.loader_class.emissions_factors.get_ef_net_energy_for_growth_males_a(),
        }

        coef_b = {
            "ewes": self.loader_class.emissions_factors.get_ef_net_energy_for_growth_females_b(),
            "lamb_less_1_yr": self.loader_class.emissions_factors.get_ef_net_energy_for_growth_females_b(),
            "lamb_more_1_yr": self.loader_class.emissions_factors.get_ef_net_energy_for_growth_females_b(),
            "male_less_1_yr": self.loader_class.emissions_factors.get_ef_net_energy_for_growth_males_b(),
            "ram": self.loader_class.emissions_factors.get_ef_net_energy_for_growth_males_b(),
        }

        year = 365
        weight_gain = bwf.get(animal.cohort) - bwi.get(animal.cohort)

        a = coef_a.get(animal.cohort)
        b = coef_b.get(animal.cohort)

        bw_initial = bwi.get(animal.cohort)
        bw_finish = bwf.get(animal.cohort)

        return (weight_gain * (a + (0.5 * b) * (bw_initial + bw_finish))) / year

    def net_energy_for_lactation(self, animal):
        """
        This function utilised milk density and fat content to calculate the energy needed for milk production
        """
        milk_energy = 4.6
        weight_gain = (
            self.loader_class.animal_features.get_lamb_less_1_yr_weight()
            - self.loader_class.animal_features.get_lamb_weight_at_birth()
        )

        type = animal.cohort

        if type == "ewes":
            return ((5 * weight_gain) / 365) * milk_energy
        else:
            return 0

    def net_energy_for_wool(self, animal):

        energy_val_wool = 24

        wool_production = animal.wool

        return (energy_val_wool * wool_production) / 365

    def net_energy_for_pregnancy(self, animal):
        """
        This function utilised the net energy for maintenance by the emissions factor for preganancy to
        calculate energy required for pregnany

        Equation 10.13 from IPCC 2006 guidelines is utilised.
        """

        coef = self.loader_class.emissions_factors.get_ef_net_energy_for_pregnancy()
        nep = 0

        if animal.cohort == "ewes":
            nep = coef * self.net_energy_for_maintenance(animal)

        return nep

    def gross_energy_from_concentrate(self, animal):

        dm = self.loader_class.concentrates.get_con_dry_matter_digestibility(
            animal.con_type
        )
        mj = self.loader_class.concentrates.get_gross_energy_mje_dry_matter(
            animal.con_type
        )

        return (animal.con_amount * dm / 100) * mj

    ##REMI ADDED Functions
    def gross_amount_from_con_in_percent(self, animal, share_in_percent):

        """
        This function utilises all of the energy equations to estimate the total energy intake from grasses minus the
        energy intake from concentrates
        """

        REM = self.ratio_of_net_energy_maintenance(animal)
        REG = self.ratio_of_net_energy_growth(animal)
        NEM = self.net_energy_for_maintenance(animal)
        NEA = self.net_energy_for_activity(animal)
        NEL = self.net_energy_for_lactation(animal)
        NEP = self.net_energy_for_pregnancy(animal)
        NEG = self.net_energy_for_weight_gain(animal)
        dm = self.loader_class.concentrates.get_con_dry_matter_digestibility(
            animal.con_type
        )
        DMD = self.loader_class.grass.get_forage_dry_matter_digestibility(animal.forage)
        mj_con = self.loader_class.concentrates.get_gross_energy_mje_dry_matter(
            animal.con_type
        )
        mj_grass = self.loader_class.grass.get_gross_energy_mje_dry_matter(
            animal.forage
        )

        DMD_average = (
            share_in_percent / 100.0 * dm + (100.0 - share_in_percent) / 100 * DMD
        )
        mj_average = (
            share_in_percent / 100.0 * mj_con
            + (100.0 - share_in_percent) / 100.0 * mj_grass
        )

        return (
            ((((NEM + NEA + NEL + NEP) / REM) + (NEG / REG)) / (DMD_average / 100.0))
            / mj_average
            * (share_in_percent / (100.0))
        )

    def gross_energy_from_grass(self, animal):

        """
        This function utilises all of the energy equations to estimate the total energy intake from grasses minus the
        energy intake from concentrates
        """

        DMD = self.loader_class.grass.get_forage_dry_matter_digestibility(animal.forage)

        REM = self.ratio_of_net_energy_maintenance(animal)
        REG = self.ratio_of_net_energy_growth(animal)
        NEM = self.net_energy_for_maintenance(animal)
        NEA = self.net_energy_for_activity(animal)
        NEL = self.net_energy_for_lactation(animal)
        NEP = self.net_energy_for_pregnancy(animal)
        NEG = self.net_energy_for_weight_gain(animal)
        NEW = self.net_energy_for_wool(animal)
        con = self.gross_energy_from_concentrate(animal)

        return (
            (((NEM + NEA + NEL + NEP) / REM) + ((NEG + NEW) / REG)) / (DMD / 100.0)
        ) - con


class GrassFeed:
    def __init__(self, ef_country):
        self.energy_class = Energy(ef_country)
        self.cohorts_class = Cohorts()
        self.loader_class = Loader(ef_country)

    def dry_matter_from_grass(self, animal):

        """
        This function utilises all of the energy equations to estimate the total energy intake from grasses minus the
        energy intake from concentrates
        """

        DMD = self.loader_class.grass.get_forage_dry_matter_digestibility(animal.forage)

        REM = self.ratio_of_net_energy_maintenance(animal)
        REG = self.ratio_of_net_energy_growth(animal)
        NEM = self.net_energy_for_maintenance(animal)
        NEA = self.net_energy_for_activity(animal)
        NEL = self.net_energy_for_lactation(animal)
        NEP = self.net_energy_for_pregnancy(animal)
        NEG = self.net_energy_for_weight_gain(animal)
        con = self.gross_energy_from_concentrate(animal)
        GE = self.loader_class.grass.get_gross_energy_mje_dry_matter(animal.forage)
        dm = self.loader_class.concentrates.get_con_dry_matter_digestibility(
            animal.con_type
        )

        share_con = con / (((NEM + NEA + NEL + NEP) / REM) + (NEG / REG))

        DMD_average = share_con * dm + (1 - share_con) * DMD

        return (
            (
                (((NEM + NEA + NEL + NEP) / REM) + (NEG / REG)) / (DMD_average / 100.0)
                - con
            )
        ) / GE

    #########################################################################################################
    # CH4 CAlculations
    ########################################################################################################

    def ch4_emissions_factor(self, animal):
        """
        Function calculates the amount of methane emissions from feed intake utilising methane converstion
        factors

        IPCC 2019 EQUATION 10.21

        As per NIR 2020, lambs have an assumed Ym of 4.5 instead of 6.7 as per IPCC.

            GEC = Gross Energy from Concentrates
            GEG = Gross Energy from GE_grass
            GET = Gross Energy total
            Ym  = Methane conversion factor, percent of gross energy content of methane

            returns the emissions factor per cow per year
        """

        year = 365

        sheep_cohort = {"Sheep": ["lamb_less_1_yr", "male_less_1_yr"]}
        if animal.cohort in sheep_cohort["Sheep"]:
            Ym = (
                self.loader_class.emissions_factors.get_ef_methane_conversion_factor_lamb()
            )
        else:
            Ym = (
                self.loader_class.emissions_factors.get_ef_methane_conversion_factor_sheep()
            )

        # print(Ym)
        methane_energy = 55.65  # MJ/kg of CH4

        GEC = self.energy_class.gross_energy_from_concentrate(animal)
        GEG = self.energy_class.gross_energy_from_grass(animal)

        GET = GEC + GEG

        return (GET * Ym * year) / methane_energy


#############################################################################################
# Grazing Stage
#############################################################################################


class GrazingStage:
    def __init__(self, ef_country):
        self.loader_class = Loader(ef_country)
        self.energy_class = Energy(ef_country)
        self.grass_feed_class = GrassFeed(ef_country)

    def percent_outdoors(self, animal):
        hours = 24
        return animal.t_outdoors / hours

    def volatile_solids_excretion_rate_GRAZING(self, animal):
        """
        This function calculates Volitile Solids Excretion Rate (kg/day -1) to pasture

        GEC   = Gross Energy from Concentrates
        GEG   = Gross Energy from grass
        DE    = Percentage of Digestible Energy
        UE    = Urinary Energy
        ASH   = Ash content of manure
        18.45 = conversion factor for dietary GE per kg of dry matter, MJ kg-1.
        """

        DEC = self.loader_class.concentrates.get_con_digestible_energy(
            animal.con_type
        )  # Digestibility
        UE = 0.04
        ASH = 0.08
        DMD = self.loader_class.grass.get_forage_dry_matter_digestibility(animal.forage)
        GEC = self.energy_class.gross_energy_from_concentrate(animal)
        GEG = self.energy_class.gross_energy_from_grass(animal)
        OUT = self.percent_outdoors(animal)

        return (
            (((GEG * (1 - (DMD / 100))) + (UE * GEG)) * ((1 - ASH) / 18.45))
            + ((GEC * (1 - (DEC / 100)) + (UE * GEC)) * (((1 - ASH) / 18.45)))
        ) * OUT

    def net_excretion_GRAZING(self, animal):

        """
        This function calculates the net Nitrogen excretion (Nex) per kg to pasture

        EQUATION 10.31 & 10.32 N excretion and N retention
        """

        CP = self.loader_class.concentrates.get_con_crude_protein(
            animal.con_type
        )  # crude protein percentage (N contained in crude protein), apparently, 16% is the average N content; https://www.feedipedia.org/node/8329
        FCP = self.loader_class.grass.get_crude_protein(animal.forage)
        GEC = self.energy_class.gross_energy_from_concentrate(animal)
        GEG = self.energy_class.gross_energy_from_grass(animal)
        OUT = self.percent_outdoors(animal)
        N_retention_frac = 0.10

        return (
            (((GEC * 365) / 18.45) * ((CP / 100) / 6.25) * (1 - N_retention_frac))
            + ((((GEG * 365) / 18.45) * (FCP / 100.0) / 6.25) * (1 - N_retention_frac))
        ) * OUT

    def ch4_emissions_for_grazing(self, animal):

        """
        EQUATION 10.23 CH4 EMISSION FACTOR FROM MANURE MANAGEMENT. Values can be references in tables 10A onwards
        """
        year = 365
        return (
            (self.volatile_solids_excretion_rate_GRAZING(animal) * year)
            * 0.1
            * 0.67
            * 0.19
        )

    def nh3_emissions_per_year_GRAZING(self, animal):
        """
        This function returns total N-NH3 per year.
        EQUATION 10.26: N LOSSES DUE TO VOLATILISATION FROM MANURE MANAGEMENT
        Table 10.22
        """
        total_ammonia_nitrogen = {
            "ewes": self.loader_class.emissions_factors.get_ef_fracGASM_total_ammonia_nitrogen_pasture_range_paddock_deposition(),
            "lamb_less_1_yr": self.loader_class.emissions_factors.get_ef_fracGASM_total_ammonia_nitrogen_pasture_range_paddock_deposition(),
            "lamb_more_1_yr": self.loader_class.emissions_factors.get_ef_fracGASM_total_ammonia_nitrogen_pasture_range_paddock_deposition(),
            "male_less_1_yr": self.loader_class.emissions_factors.get_ef_fracGASM_total_ammonia_nitrogen_pasture_range_paddock_deposition(),
            "ram": self.loader_class.emissions_factors.get_ef_fracGASM_total_ammonia_nitrogen_pasture_range_paddock_deposition(),
        }

        TAN = total_ammonia_nitrogen.get(animal.cohort)

        return self.net_excretion_GRAZING(animal) * 0.6 * TAN

    def Nleach_GRAZING(self, animal):

        """
        This function returns the proportion of N leached from pasture
        """

        ten_percent_nex = 0.1

        return self.net_excretion_GRAZING(animal) * ten_percent_nex

    def PLeach_GRAZING(self, animal):

        """
        This function returns the proportion of P leached from pasture
        """

        return (self.net_excretion_GRAZING(animal) * (1.8 / 5)) * 0.03

    # direct and indirect (from leaching) N20 from PRP

    def PRP_N2O_direct(self, animal):

        """
        this function returns the direct n2o emissions from pasture, range and paddock

        EQUATION 10.25: DIRECT N2O EMISSIONS FROM MANURE MANAGEMENT

        EF3PRP, SO for sheep and ‘other animals’3 [kg N2O–N (kg N)-1] = 0.003

        """

        direct_n2o_emissions_factors = {
            "ewes": self.loader_class.emissions_factors.get_ef3__cpp_pasture_range_paddock_sheep_direct_n2o(),
            "lamb_less_1_yr": self.loader_class.emissions_factors.get_ef3__cpp_pasture_range_paddock_sheep_direct_n2o(),
            "lamb_more_1_yr": self.loader_class.emissions_factors.get_ef3__cpp_pasture_range_paddock_sheep_direct_n2o(),
            "male_less_1_yr": self.loader_class.emissions_factors.get_ef3__cpp_pasture_range_paddock_sheep_direct_n2o(),
            "ram": self.loader_class.emissions_factors.get_ef3__cpp_pasture_range_paddock_sheep_direct_n2o(),
        }

        EF = direct_n2o_emissions_factors.get(animal.cohort)
        return self.net_excretion_GRAZING(animal) * EF

    def PRP_N2O_indirect(self, animal):

        """
        This functions returns indirect n2o from atmospheric deposition and leaching related to pasture, range and paddock
        EQUATION 10.27: INDIRECT N2O EMISSIONS DUE TO VOLATILISATION OF N FROM MANURE MANAGEMENT
        EQUATION 10.29 INDIRECT N2O EMISSIONS DUE TO LEACHING FROM MANURE MANAGEMENT


        """

        atmospheric_deposition = {
            "ewes": self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water(),
            "lamb_less_1_yr": self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water(),
            "lamb_more_1_yr": self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water(),
            "male_less_1_yr": self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water(),
            "ram": self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water(),
        }

        leaching = {
            "ewes": self.loader_class.emissions_factors.get_ef_indirect_n2o_from_leaching_and_runoff(),
            "lamb_less_1_yr": self.loader_class.emissions_factors.get_ef_indirect_n2o_from_leaching_and_runoff(),
            "lamb_more_1_yr": self.loader_class.emissions_factors.get_ef_indirect_n2o_from_leaching_and_runoff(),
            "male_less_1_yr": self.loader_class.emissions_factors.get_ef_indirect_n2o_from_leaching_and_runoff(),
            "ram": self.loader_class.emissions_factors.get_ef_indirect_n2o_from_leaching_and_runoff(),
        }

        indirect_atmosphere = atmospheric_deposition.get(animal.cohort)
        indirect_leaching = leaching.get(animal.cohort)

        NH3 = self.nh3_emissions_per_year_GRAZING(animal)
        NL = self.Nleach_GRAZING(animal)

        return (NH3 * indirect_atmosphere) + (NL * indirect_leaching)


#############################################################################################
# Housing Stage
#############################################################################################


class HousingStage:
    def __init__(self, ef_country):
        self.loader_class = Loader(ef_country)
        self.energy_class = Energy(ef_country)

    def percent_indoors(self, animal):
        hours = 24
        return (animal.t_indoors + animal.t_stabled) / hours

    def VS_HOUSED(self, animal):
        """
        This function returns the volatile solids excreted per day for the period animals are
        housed.

        # Volitile Solids Excretion Rate (kg/day -1)
        # GEcon = Gross Energy from Concentrates
        # GEgrass = Gross Energy from grass
        # DE= Percentage of Digestible Energy
        # UE = Urinary Energy
        # ASH = Ash content of manure
        # 18.45 = conversion factor for dietary GE per kg of dry matter, MJ kg-1.
        """
        DEC = self.loader_class.concentrates.get_con_digestible_energy(
            animal.con_type
        )  # Digestibility of concentrate
        UE = 0.04
        ASH = 0.08
        DMD = self.loader_class.grass.get_forage_dry_matter_digestibility(animal.forage)
        GEC = self.energy_class.gross_energy_from_concentrate(animal)
        GEG = self.energy_class.gross_energy_from_grass(animal)
        IN = self.percent_indoors(animal)

        # The second instance of GEG in part 2 of equation may need to be changed to GEC

        return (
            (((GEC * (1 - (DEC / 100))) + (UE * GEC)) * ((1 - ASH) / 18.45))
            + ((GEG * (1 - (DMD / 100)) + (UE * GEG)) * ((1 - ASH) / 18.45))
        ) * IN

    def net_excretion_HOUSED(self, animal):
        """
        This function returns kg of nitrogen excreted per year while animals are housed

        - this function is a produces a rate that is a little higher than the costa rica model,
        however, this is likley due to the higher energy ratios resulting from the use of IPCC equations.
        """

        CP = self.loader_class.concentrates.get_con_crude_protein(
            animal.con_type
        )  # crude protein percentage (N contained in crude protein), apparently, 16% is the average N content; https://www.feedipedia.org/node/8329
        FCP = self.loader_class.grass.get_crude_protein(animal.forage)
        GEC = self.energy_class.gross_energy_from_concentrate(animal)
        GEG = self.energy_class.gross_energy_from_grass(animal)

        N_retention_frac = 0.10

        IN = self.percent_indoors(animal)

        return (
            (((GEC * 365) / 18.45) * ((CP / 100) / 6.25) * (1 - N_retention_frac))
            + ((((GEG * 365) / 18.45) * (FCP / 100.0) / 6.25) * (1 - N_retention_frac))
        ) * IN

    def total_ammonia_nitrogen_nh4_HOUSED(self, animal):
        """
        This function returns the total ammonia nitrate (TAN) NH4 per year

        TAN is 60% of Nex
        """
        percentage_nex = 0.6

        return self.net_excretion_HOUSED(animal) * percentage_nex

    def nh3_emissions_per_year_HOUSED(self, animal):

        """
        This function returns the total nh3 emissions per year for housing


        EQUATION 10.26: N LOSSES DUE TO VOLATILISATION FROM MANURE MANAGEMENT

        Table 10.22

        In the case of bio digesters, table 10.17 in IPCC 2019 is utilised to produce the MCF factor.

        NIR 2020 states that 89% of sheep manure on grass, the rest in deep bedding. The "solid" category represents emissions factors for deep bedding

        IPCC 2019 Table 10.22 FracGas_ms used for deep bedding
        """

        storage_TAN = {
            "tank solid": self.loader_class.emissions_factors.get_ef_TAN_house_liquid(),
            "tank liquid": self.loader_class.emissions_factors.get_ef_TAN_house_liquid(),
            "solid": self.loader_class.emissions_factors.get_ef_TAN_house_solid_deep_bedding(),
            "biodigester": self.loader_class.emissions_factors.get_ef_TAN_house_liquid(),
        }

        return (
            self.total_ammonia_nitrogen_nh4_HOUSED(animal)
            * storage_TAN[animal.mm_storage]
        )

    def HOUSING_N2O_indirect(self, animal):

        """
        this function returns the indirect emissions from the housing Stage
        """
        ef = (
            self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water()
        )

        indirect_n2o = self.nh3_emissions_per_year_HOUSED(animal) * ef

        return indirect_n2o


#############################################################################################
# Storage Stage
#############################################################################################
class StorageStage:
    def __init__(self, ef_country):
        self.loader_class = Loader(ef_country)
        self.housing_class = HousingStage(ef_country)

    def net_excretion_STORAGE(self, animal):

        """
        This function returns kg of Nex per year from storage
        """

        return self.housing_class.net_excretion_HOUSED(
            animal
        ) - self.housing_class.nh3_emissions_per_year_HOUSED(animal)

    def total_ammonia_nitrogen_nh4_STORAGE(self, animal):

        """
        this function returns the total ammonia nitrogen (TAN) NH4 per year

        TAN is 60% of Nex
        """
        percentage_nex = 0.6

        return self.net_excretion_STORAGE(animal) * percentage_nex

    def CH4_STORAGE(self, animal):

        """
        This function returns the total CH4 per year from storage.

        EQUATION 10.23: CH4 EMISSION FACTOR FROM MANURE MANAGEMENT

        Bo (max methane of manure) seems to be 0.1, however the percentages in IPCC 2006 seem to be much larger.

        NIR 2020 states that 89% of sheep manure on grass, the rest in deep bedding. The "solid" category represents emissions factors for deep bedding
        IPCC 2019 values used for deep bedding (2.75%).
        """

        storage_MCF = {
            "tank solid": self.loader_class.emissions_factors.get_ef_mcf_liquid_tank(),
            "tank liquid": self.loader_class.emissions_factors.get_ef_mcf_liquid_tank(),
            "solid": self.loader_class.emissions_factors.get_ef_mcf_solid_storage_deep_bedding(),
            "biodigester": self.loader_class.emissions_factors.get_ef_mcf_anaerobic_digestion(),
        }

        return (self.housing_class.VS_HOUSED(animal) * 365) * (
            0.1 * 0.67 * storage_MCF[animal.mm_storage]
        )

    def STORAGE_N2O_direct(self, animal):

        """
        This functions returns direct N2O emissions from manure storage


        NIR 2020 states that 89% of sheep manure on grass, the rest in deep bedding. The "solid" category represents emissions factors for deep bedding

        """

        storage_N2O = {
            "tank solid": self.loader_class.emissions_factors.get_ef_n2o_direct_storage_tank_solid(),  # crust cover for ireland
            "tank liquid": self.loader_class.emissions_factors.get_ef_n2o_direct_storage_tank_liquid(),
            "solid": self.loader_class.emissions_factors.get_ef_n2o_direct_storage_solid_deep_bedding(),
            "biodigester": self.loader_class.emissions_factors.get_ef_n2o_direct_storage_tank_anaerobic_digestion(),
        }

        return self.net_excretion_STORAGE(animal) * storage_N2O[animal.mm_storage]

    def nh3_emissions_per_year_STORAGE(self, animal):
        """
        This function returns the total nh3 emissions per year for storage


        NIR 2020 states that 89% of sheep manure on grass, the rest in deep bedding. The "solid" category represents emissions factors for deep bedding

        IPCC 2019 Table 10.22 FracGas_ms used for deep bedding
        """

        storage_TAN = {
            "tank solid": self.loader_class.emissions_factors.get_ef_TAN_storage_tank(),
            "tank liquid": self.loader_class.emissions_factors.get_ef_TAN_storage_tank(),
            "solid": self.loader_class.emissions_factors.get_ef_TAN_storage_solid_deep_bedding(),
            "biodigester": self.loader_class.emissions_factors.get_ef_TAN_storage_tank(),
        }

        return (
            self.total_ammonia_nitrogen_nh4_STORAGE(animal)
            * storage_TAN[animal.mm_storage]
        )

    def STORAGE_N2O_indirect(self, animal):

        """
        This functions returns indirect n2o from atmospheric deposition and leaching related to storage
        """

        atmospheric_deposition = {
            "ewes": self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water(),
            "lamb_less_1_yr": self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water(),
            "lamb_more_1_yr": self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water(),
            "male_less_1_yr": self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water(),
            "ram": self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water(),
        }

        indirect_atmosphere = atmospheric_deposition.get(animal.cohort)

        NH3 = self.nh3_emissions_per_year_STORAGE(animal)

        return NH3 * indirect_atmosphere


###############################################################################
# Daily Spread
###############################################################################


class DailySpread:
    def __init__(self, ef_country):
        self.loader_class = Loader(ef_country)
        self.storage_class = StorageStage(ef_country)

    def net_excretion_SPREAD(self, animal):

        """
        This function returns Nex from daily spread
        """

        nex_storage = self.net_excretion_STORAGE(animal)
        direct_n2o = self.STORAGE_N2O_direct(animal)
        nh3_emissions = self.nh3_emissions_per_year_STORAGE(animal)
        indirect_n2o = self.STORAGE_N2O_indirect(animal)

        return nex_storage - direct_n2o - nh3_emissions - indirect_n2o

    def total_ammonia_nitrogen_nh4_SPREAD(self, animal):
        """
        this function returns the total ammonia nitrogen (TAN) NH4 per year from daily spread
        """
        percentage_nex = 0.6

        return self.net_excretion_SPREAD(animal) * percentage_nex

    def SPREAD_N2O_direct(self, animal):

        """
        This function returns the proportion of N direct emissions from daily spread
        """

        n2o_direct = {
            "ewes": self.loader_class.emissions_factors.get_ef_direct_n2o_emissions_soils(),
            "lamb_less_1_yr": self.loader_class.emissions_factors.get_ef_direct_n2o_emissions_soils(),
            "lamb_more_1_yr": self.loader_class.emissions_factors.get_ef_direct_n2o_emissions_soils(),
            "male_less_1_yr": self.loader_class.emissions_factors.get_ef_direct_n2o_emissions_soils(),
            "ram": self.loader_class.emissions_factors.get_ef_direct_n2o_emissions_soils(),
        }

        return self.net_excretion_SPREAD(animal) * n2o_direct.get(animal.cohort)

    def nh3_emissions_per_year_SPREAD(self, animal):

        """
        this function returns nh3 emmissions per year from daily spreading
        """

        nh4 = self.total_ammonia_nitrogen_nh4_SPREAD(animal)

        daily_spreading = {
            "none": self.loader_class.emissions_factors.get_ef_nh3_daily_spreading_none(),
            "manure": self.loader_class.emissions_factors.get_ef_nh3_daily_spreading_manure(),
            "broadcast": self.loader_class.emissions_factors.get_ef_nh3_daily_spreading_broadcast(),
            "injection": self.loader_class.emissions_factors.get_ef_nh3_daily_spreading_injection(),
            "trailing hose": self.loader_class.emissions_factors.get_ef_nh3_daily_spreading_traling_hose(),
        }

        return nh4 * daily_spreading[animal.daily_spreading]

    def leach_nitrogen_SPREAD(self, animal):

        """
        This function returns the proportion of nitrogen leached from spreading

        """

        ten_percent_nex = 0.1

        return self.net_excretion_SPREAD(animal) * ten_percent_nex

    def leach_phospherous_SPREAD(self, animal):

        """
        This function returns the proportion of kg P leach per year *(1.8/5))*0.03

        """

        return (self.net_excretion_SPREAD(animal) * (1.8 / 5)) * 0.03

    def SPREAD_N2O_indirect(self, animal):

        """
        This functions returns indirect n2o from atmospheric deposition and leaching related to daily spread
        """

        atmospheric_deposition = {
            "ewes": self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water(),
            "lamb_less_1_yr": self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water(),
            "lamb_more_1_yr": self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water(),
            "male_less_1_yr": self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water(),
            "ram": self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water(),
        }

        leaching = {
            "ewes": self.loader_class.emissions_factors.get_ef_indirect_n2o_from_leaching_and_runoff(),
            "lamb_less_1_yr": self.loader_class.emissions_factors.get_ef_indirect_n2o_from_leaching_and_runoff(),
            "lamb_more_1_yr": self.loader_class.emissions_factors.get_ef_indirect_n2o_from_leaching_and_runoff(),
            "male_less_1_yr": self.loader_class.emissions_factors.get_ef_indirect_n2o_from_leaching_and_runoff(),
            "ram": self.loader_class.emissions_factors.get_ef_indirect_n2o_from_leaching_and_runoff(),
        }

        indirect_atmosphere = atmospheric_deposition.get(animal.cohort)
        indirect_leaching = leaching.get(animal.cohort)

        NH3 = self.nh3_emissions_per_year_SPREAD(animal)
        NL = self.leach_nitrogen_SPREAD(animal)

        return (NH3 * indirect_atmosphere) + (NL * indirect_leaching)


###############################################################################
# Farm & Upstream Emissions
###############################################################################
class FertiliserInputs:
    def __init__(self, ef_country):
        self.loader_class = Loader(ef_country)

    # Urea Fertiliser
    def urea_N2O_direct(self, total_urea, total_urea_abated):

        """
        this function returns the total emissions from urea and abated urea applied to soils
        """

        ef_urea = self.loader_class.emissions_factors.get_ef_urea()
        ef_urea_abated = self.loader_class.emissions_factors.get_ef_urea_and_nbpt()

        return (total_urea * ef_urea) + (total_urea_abated * ef_urea_abated)

    def urea_NH3(self, total_urea, total_urea_abated):

        """
        This function returns  the amount of urea and abated urea volatised.
        Below is the original fraction used in the Costa Rica version, however this seems to be incorrect.
        FRAC=0.02 #FracGASF ammoinium-fertilisers [fraction of synthetic fertiliser N that volatilises as NH3 and NOx under different conditions]
        """
        ef_urea = (
            self.loader_class.emissions_factors.get_ef_fracGASF_urea_fertilisers_to_nh3_and_nox()
        )
        ef_urea_abated = (
            self.loader_class.emissions_factors.get_ef_fracGASF_urea_and_nbpt_to_nh3_and_nox()
        )

        return (total_urea * ef_urea) + (total_urea_abated * ef_urea_abated)

    def urea_nleach(self, total_urea, total_urea_abated):

        """
        This function returns  the amount of urea and abated urea leached from soils.

        Below is the original fraction used in the Costa Rica version, however this seems to be incorrect.
        FRAC=0.02 #FracGASF ammoinium-fertilisers [fraction of synthetic fertiliser N that volatilises as NH3 and NOx under different conditions]
        """

        leach = self.loader_class.emissions_factors.get_ef_frac_leach_runoff()

        return (total_urea + total_urea_abated) * leach

    def urea_N2O_indirect(self, total_urea, total_urea_abated):
        """
        this function returns the idirect emissions from urea
        """
        indirect_atmosphere = (
            self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water()
        )
        indirect_leaching = (
            self.loader_class.emissions_factors.get_ef_indirect_n2o_from_leaching_and_runoff()
        )

        return (self.urea_NH3(total_urea, total_urea_abated) * indirect_atmosphere) + (
            self.urea_nleach(total_urea, total_urea_abated) * indirect_leaching
        )

    def urea_co2(self, total_urea, total_urea_abated):
        """
        returns the total CO2 from urea application
        """

        # return ((total_urea+total_urea_abated)/47) * (44/12)
        return ((total_urea + total_urea_abated) * 0.2) * (
            44 / 12
        )  # adjusted to the NIR version of this calculation

    def urea_P_leach(self, total_urea, total_urea_abated):
        """
        this function returns the idirect emissions from urea
        """
        frac_leach = float(self.loader_class.emissions_factors.get_ef_Frac_P_Leach())

        return (total_urea + total_urea_abated) * frac_leach

    # Nitrogen Fertiliser Emissions

    def n_fertiliser_P_leach(self, total_n_fert):
        """
        this function returns the idirect emissions from urea
        """
        frac_leach = float(self.loader_class.emissions_factors.get_ef_Frac_P_Leach())

        return total_n_fert * frac_leach

    def n_fertiliser_direct(self, total_n_fert):

        """
        This function returns total direct emissions from ammonium nitrate application at field level
        """
        ef = self.loader_class.emissions_factors.get_ef_ammonium_nitrate()
        return total_n_fert * ef

    def n_fertiliser_NH3(self, total_n_fert):

        """
        This function returns total NH3 emissions from ammonium nitrate application at field level
        """
        ef = (
            self.loader_class.emissions_factors.get_ef_fracGASF_ammonium_fertilisers_to_nh3_and_nox()
        )
        return total_n_fert * ef

    def n_fertiliser_nleach(self, total_n_fert):
        """
        This function returns total leached emissions from ammonium nitrate application at field level
        """

        ef = self.loader_class.emissions_factors.get_ef_frac_leach_runoff()

        return total_n_fert * ef

    def n_fertiliser_indirect(self, total_n_fert):

        """
        this function returns the indirect emissions from ammonium nitrate fertiliser
        """

        indirect_atmosphere = (
            self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water()
        )
        indirect_leaching = (
            self.loader_class.emissions_factors.get_ef_indirect_n2o_from_leaching_and_runoff()
        )

        return (self.n_fertiliser_NH3(total_n_fert) * indirect_atmosphere) + (
            self.n_fertiliser_nleach(total_n_fert) * indirect_leaching
        )

    def p_fertiliser_P_leach(self, total_p_fert):
        """
        this function returns the idirect emissions from urea
        """
        frac_leach = float(self.loader_class.emissions_factors.get_ef_Frac_P_Leach())

        return total_p_fert * frac_leach


################################################################################
# Total Global Warming Potential of whole farms (Upstream Processes & Fossil Fuel Energy)
################################################################################

# Emissions from on Farm Fossil Fuels


class Upstream:
    def __init__(self, ef_country):
        self.loader_class = Loader(ef_country)
        self.cohorts_class = Cohorts()

    def co2_from_concentrate_production(self, animal):
        concentrate_co2 = 0

        for key in animal.__dict__.keys():
            if (
                key in self.cohorts_class.COHORTS
                and animal.__getattribute__(key).pop != 0
            ):
                concentrate_co2 += (
                    animal.__getattribute__(key).con_amount
                    * self.loader_class.concentrates.get_con_co2_e(
                        animal.__getattribute__(key).con_type
                    )
                ) * animal.__getattribute__(key).pop

        return concentrate_co2 * 365

    def diesel_CO2(self, diesel_kg):

        """
        this function returns the direct and indirect upstream CO2 emmisions from diesel
        """

        Diesel_indir = self.loader_class.upstream.get_upstream_kg_co2e(
            "diesel_indirect"
        )
        Diest_dir = self.loader_class.upstream.get_upstream_kg_co2e("diesel_direct")

        return diesel_kg * (Diest_dir + Diesel_indir)

    def elec_CO2(self, elec_kwh):

        """
        this functino returns the upstream CO2 emissions from electricity consumption
        """

        elec_consumption = self.loader_class.upstream.get_upstream_kg_co2e(
            "electricity_consumed"
        )  # based on Norway hydropower
        return elec_kwh * elec_consumption

    # Emissions from upstream fertiliser production
    def fert_upstream_CO2(
        self, total_n_fert, total_urea, total_urea_abated, total_p_fert, total_k_fert
    ):

        """
        this function returns the upstream emissions from urea and ammonium fertiliser manufature
        """
        AN_fert_CO2 = self.loader_class.upstream.get_upstream_kg_co2e(
            "ammonium_nitrate_fertiliser"
        )  # Ammonium Nitrate Fertiliser
        Urea_fert_CO2 = self.loader_class.upstream.get_upstream_kg_co2e("urea_fert")
        Triple_superphosphate = self.loader_class.upstream.get_upstream_kg_co2e(
            "triple_superphosphate"
        )
        Potassium_chloride = self.loader_class.upstream.get_upstream_kg_co2e(
            "potassium_chloride"
        )

        return (
            (total_n_fert * AN_fert_CO2)
            + (total_urea * Urea_fert_CO2)
            + (total_urea_abated * Urea_fert_CO2)
            + (total_p_fert * Triple_superphosphate)
            + (total_k_fert * Potassium_chloride)
        )

    def fert_upstream_EP(
        self, total_n_fert, total_urea, total_urea_abated, total_p_fert, total_k_fert
    ):

        """
        this function returns the upstream emissions from urea and ammonium fertiliser manufature
        """
        AN_fert_PO4 = self.loader_class.upstream.get_upstream_kg_po4e(
            "ammonium_nitrate_fertiliser"
        )  # Ammonium Nitrate Fertiliser
        Urea_fert_PO4 = self.loader_class.upstream.get_upstream_kg_po4e("urea_fert")
        Triple_superphosphate = self.loader_class.upstream.get_upstream_kg_po4e(
            "triple_superphosphate"
        )
        Potassium_chloride = self.loader_class.upstream.get_upstream_kg_po4e(
            "potassium_chloride"
        )

        return (
            (total_n_fert * AN_fert_PO4)
            + (total_urea * Urea_fert_PO4)
            + (total_urea_abated * Urea_fert_PO4)
            + (total_p_fert * Triple_superphosphate)
            + (total_k_fert * Potassium_chloride)
        )


################################################################################
# Allocation
################################################################################
class Allocation:
    def lamb_live_weight_output_value(self, animal):

        return (
            (
                (animal.lamb_less_1_yr.weight * animal.lamb_less_1_yr.n_sold)
                * animal.lamb_less_1_yr.meat_price_kg
            )
            + (
                (animal.lamb_more_1_yr.weight * animal.lamb_more_1_yr.n_sold)
                * animal.lamb_more_1_yr.meat_price_kg
            )
            + (
                (animal.male_less_1_yr.weight * animal.male_less_1_yr.n_sold)
                * animal.male_less_1_yr.meat_price_kg
            )
        )

    def sheep_live_weight_output_value(self, animal):

        return (
            (animal.ewes.weight * animal.ewes.n_sold) * animal.ewes.meat_price_kg
        ) + ((animal.ram.weight * animal.ram.n_sold) * animal.ram.meat_price_kg)

    def wool_output_value(self, animal):

        return (
            (
                (animal.lamb_less_1_yr.wool * animal.lamb_less_1_yr.wool_price_kg)
                * (animal.lamb_less_1_yr.pop - animal.lamb_less_1_yr.n_sold)
            )
            + (
                (animal.lamb_more_1_yr.wool * animal.lamb_more_1_yr.wool_price_kg)
                * (animal.lamb_more_1_yr.pop - animal.lamb_more_1_yr.n_sold)
            )
            + (
                (animal.male_less_1_yr.wool * animal.male_less_1_yr.wool_price_kg)
                * (animal.male_less_1_yr.pop - animal.male_less_1_yr.n_sold)
            )
            + (
                (animal.ewes.wool * animal.ewes.wool_price_kg)
                * (animal.ewes.pop - animal.ewes.n_sold)
            )
            + (
                (animal.ram.wool * animal.ram.wool_price_kg)
                * (animal.ram.pop - animal.ram.n_sold)
            )
        )

    def live_weight_bought(self, animal):

        return (
            (animal.ewes.weight * animal.ewes.n_bought)
            + (animal.lamb_less_1_yr.weight * animal.lamb_less_1_yr.n_bought)
            + (animal.lamb_more_1_yr.weight * animal.lamb_more_1_yr.n_bought)
            + (animal.male_less_1_yr.weight * animal.male_less_1_yr.n_bought)
            + (animal.ram.weight * animal.ram.n_bought)
        )

    def total_lamb_live_weight_kg(self, animal):

        return (
            (animal.lamb_less_1_yr.weight * animal.lamb_less_1_yr.n_sold)
            + (animal.lamb_more_1_yr.weight * animal.lamb_more_1_yr.n_sold)
            + (animal.male_less_1_yr.weight * animal.male_less_1_yr.n_sold)
        )

    def total_sheep_live_weight_kg(self, animal):

        return (animal.ewes.weight * animal.ewes.n_sold) + (
            animal.ram.weight * animal.ram.n_sold
        )

    def total_wool_weight_kg(self, animal):

        return (
            (
                animal.lamb_less_1_yr.wool
                * (animal.lamb_less_1_yr.pop - animal.lamb_less_1_yr.n_sold)
            )
            + (
                animal.lamb_more_1_yr.wool
                * (animal.lamb_more_1_yr.pop - animal.lamb_more_1_yr.n_sold)
            )
            + (
                animal.male_less_1_yr.wool
                * (animal.male_less_1_yr.pop - animal.male_less_1_yr.n_sold)
            )
            + (animal.ewes.wool * (animal.ewes.pop - animal.ewes.n_sold))
            + (animal.ram.wool * (animal.ram.pop - animal.ram.n_sold))
        )

    def lamb_allocation_factor(self, animal):
        total = (
            self.lamb_live_weight_output_value(animal)
            + self.sheep_live_weight_output_value(animal)
            + self.wool_output_value(animal)
        )
        return self.lamb_live_weight_output_value(animal) / total

    def sheep_allocation_factor(self, animal):
        total = (
            self.lamb_live_weight_output_value(animal)
            + self.sheep_live_weight_output_value(animal)
            + self.wool_output_value(animal)
        )
        return self.sheep_live_weight_output_value(animal) / total

    def wool_allocation_factor(self, animal):
        total = (
            self.lamb_live_weight_output_value(animal)
            + self.sheep_live_weight_output_value(animal)
            + self.wool_output_value(animal)
        )
        return self.wool_output_value(animal) / total


################################################################################
# Total Global Warming Potential of whole farms
################################################################################


class ClimateChangeTotals:
    def __init__(self, ef_country):
        self.cohorts_class = Cohorts()
        self.grass_feed_class = GrassFeed(ef_country)
        self.grazing_class = GrazingStage(ef_country)
        self.spread_class = DailySpread(ef_country)
        self.housing_class = HousingStage(ef_country)
        self.storage_class = StorageStage(ef_country)
        self.fertiliser_class = FertiliserInputs(ef_country)
        self.upstream_class = Upstream(ef_country)

    def create_emissions_dictionary(self, keys):
        key_list = [
            "enteric_ch4",
            "manure_management_N2O",
            "manure_management_CH4",
            "manure_applied_N",
            "N_direct_PRP",
            "N_direct_PRP",
            "N_indirect_PRP",
            "N_direct_fertiliser",
            "N_indirect_fertiliser",
            "soils_CO2",
            "soil_organic_N_direct",
            "soil_organic_N_indirect",
            "soil_inorganic_N_direct",
            "soil_inorganic_N_indirect",
            "soil_N_direct",
            "soil_N_indirect",
            "soils_N2O",
        ]

        keys_dict = dict.fromkeys(keys)

        emissions_dict = dict.fromkeys(key_list)

        for key in emissions_dict.keys():
            emissions_dict[key] = copy.deepcopy(keys_dict)
            for inner_k in keys_dict.keys():
                emissions_dict[key][inner_k] = 0

        return emissions_dict

    def Enteric_CH4(self, animal):

        return self.grass_feed_class.ch4_emissions_factor(animal)

    def CH4_enteric_ch4(self, animal):

        Enteric = 0

        for key in animal.__dict__.keys():

            if (
                key in self.cohorts_class.COHORTS
                and animal.__getattribute__(key).pop != 0
            ):

                Enteric += (
                    self.Enteric_CH4(animal.__getattribute__(key))
                    * animal.__getattribute__(key).pop
                )

        return Enteric

    def CH4_manure_management(self, animal):

        result = 0

        for key in animal.__dict__.keys():

            if (
                key in self.cohorts_class.COHORTS
                and animal.__getattribute__(key).pop != 0
            ):

                result += (
                    self.Total_manure_ch4(animal.__getattribute__(key))
                    * animal.__getattribute__(key).pop
                )

        return result

    def PRP_Total(self, animal):

        """
        this function returns the emissions total (N20-N) related to Pature, Range and Paddock
        Unconverted
        """

        return self.grazing_class.PRP_N2O_direct(
            animal
        ) + self.grazing_class.PRP_N2O_indirect(animal)

    def Total_storage_N2O(self, animal):

        """
        This function returns the total N20 related to manure storage, no spreading included


        """
        mole_weight = 44.0 / 28.0

        n2o_direct = 0
        n2o_indirect_storage = 0
        n2o_indirect_housing = 0

        for key in animal.__dict__.keys():

            if (
                key in self.cohorts_class.COHORTS
                and animal.__getattribute__(key).pop != 0
            ):

                n2o_direct += (
                    self.storage_class.STORAGE_N2O_direct(animal.__getattribute__(key))
                    * animal.__getattribute__(key).pop
                )
                n2o_indirect_storage += (
                    self.storage_class.STORAGE_N2O_indirect(
                        animal.__getattribute__(key)
                    )
                    * animal.__getattribute__(key).pop
                )
                n2o_indirect_housing += (
                    self.housing_class.HOUSING_N2O_indirect(
                        animal.__getattribute__(key)
                    )
                    * animal.__getattribute__(key).pop
                )

        return (n2o_direct + n2o_indirect_storage + n2o_indirect_housing) * mole_weight

    def N2O_total_PRP_N2O_direct(self, animal):

        """
        this function returns the direct n2o emissions from pasture, range and paddock

        "Fertiliser is excluded at the moment"
        """

        mole_weight = 44.0 / 28.0

        PRP_direct = 0

        for key in animal.__dict__.keys():

            if (
                key in self.cohorts_class.COHORTS
                and animal.__getattribute__(key).pop != 0
            ):

                PRP_direct += (
                    self.grazing_class.PRP_N2O_direct(animal.__getattribute__(key))
                    * animal.__getattribute__(key).pop
                )

        return PRP_direct * mole_weight

    def N2O_total_PRP_N2O_indirect(self, animal):

        mole_weight = 44.0 / 28.0

        PRP_indirect = 0

        for key in animal.__dict__.keys():

            if (
                key in self.cohorts_class.COHORTS
                and animal.__getattribute__(key).pop != 0
            ):

                PRP_indirect += (
                    self.grazing_class.PRP_N2O_indirect(animal.__getattribute__(key))
                    * animal.__getattribute__(key).pop
                )

        return PRP_indirect * mole_weight

    def Total_manure_ch4(self, animal):

        """
        this function returns the total ch4 related to manure storage
        """

        return self.grazing_class.ch4_emissions_for_grazing(
            animal
        ) + self.storage_class.CH4_STORAGE(animal)

    def CO2_soils_GWP(self, total_urea, total_urea_abated):
        return self.fertiliser_class.urea_co2(total_urea, total_urea_abated)

    def N2O_direct_fertiliser(self, total_urea, total_urea_abated, total_n_fert):
        """
        This function returns the total direct and indirect emissions from urea and ammonium fertilisers
        """

        result = (
            (
                self.fertiliser_class.urea_N2O_direct(total_urea, total_urea_abated)
                + self.fertiliser_class.n_fertiliser_direct(total_n_fert)
            )
            * 44.0
            / 28.0
        )

        return result

    def N2O_fertiliser_indirect(self, total_urea, total_urea_abated, total_n_fert):
        """
        This function returns the total direct and indirect emissions from urea and ammonium fertilisers
        """

        result = (
            (
                self.fertiliser_class.urea_N2O_indirect(total_urea, total_urea_abated)
                + self.fertiliser_class.n_fertiliser_indirect(total_n_fert)
            )
            * 44.0
            / 28.0
        )

        return result

    def upstream_and_inputs_and_fuel_co2(
        self,
        diesel_kg,
        elec_kwh,
        total_n_fert,
        total_urea,
        total_urea_abated,
        total_p_fert,
        total_k_fert,
        animal,
    ):
        return (
            self.upstream_class.diesel_CO2(diesel_kg)
            + self.upstream_class.elec_CO2(elec_kwh)
            + self.upstream_class.fert_upstream_CO2(
                total_n_fert,
                total_urea,
                total_urea_abated,
                total_p_fert,
                total_k_fert,
            )
            + self.upstream_class.co2_from_concentrate_production(animal)
        )


###############################################################################
# Water Quality EP PO4e
###############################################################################


class EutrophicationTotals:
    def __init__(self, ef_country):
        self.loader_class = Loader(ef_country)
        self.cohorts_class = Cohorts()
        self.grazing_class = GrazingStage(ef_country)
        self.housing_class = HousingStage(ef_country)
        self.storage_class = StorageStage(ef_country)
        self.spread_class = DailySpread(ef_country)
        self.fertiliser_class = FertiliserInputs(ef_country)

    # Manure Management
    def total_manure_NH3_EP(self, animal):
        """
        Convert N to PO4  = 0.42

        """

        indirect_atmosphere = (
            self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water()
        )

        NH3N = 0

        for key in animal.__dict__.keys():
            if (
                key in self.cohorts_class.COHORTS
                and animal.__getattribute__(key).pop != 0
            ):

                NH3N += (
                    self.storage_class.nh3_emissions_per_year_STORAGE(
                        animal.__getattribute__(key)
                    )
                    + self.housing_class.nh3_emissions_per_year_HOUSED(
                        animal.__getattribute__(key)
                    )
                ) * animal.__getattribute__(key).pop

        return (NH3N * indirect_atmosphere) * 0.42

    # SOILS
    def total_fertiliser_soils_NH3_and_LEACH_EP(
        self, total_urea, total_urea_abated, total_n_fert
    ):
        """
        Convert N to PO4  = 0.42

        """
        LEACH = 0
        NH3N = 0

        indirect_atmosphere = (
            self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water()
        )

        if total_urea != None or total_urea_abated != None or total_n_fert != None:
            LEACH = self.fertiliser_class.urea_nleach(
                total_urea, total_urea_abated
            ) + self.fertiliser_class.n_fertiliser_nleach(total_n_fert)
            NH3N = self.fertiliser_class.urea_NH3(
                total_urea, total_urea_abated
            ) + self.fertiliser_class.n_fertiliser_NH3(total_n_fert)

        return (NH3N * indirect_atmosphere) + LEACH * 0.42

    def total_grazing_soils_NH3_and_LEACH_EP(self, animal):
        # No spreading for sheep
        LEACH = 0
        NH3N = 0

        indirect_atmosphere = (
            self.loader_class.emissions_factors.get_ef_indirect_n2o_atmospheric_deposition_to_soils_and_water()
        )

        for key in animal.__dict__.keys():
            if (
                key in self.cohorts_class.COHORTS
                and animal.__getattribute__(key).pop != 0
            ):
                NH3N += (
                    self.grazing_class.nh3_emissions_per_year_GRAZING(
                        animal.__getattribute__(key)
                    )
                    * animal.__getattribute__(key).pop
                )

                # Leach from grazing, none from spread for sheep

                LEACH += (
                    self.grazing_class.Nleach_GRAZING(animal.__getattribute__(key))
                    * animal.__getattribute__(key).pop
                )

        return (NH3N * indirect_atmosphere) + LEACH * 0.42

    def fertiliser_soils_P_LEACH_EP(
        self, total_urea, total_urea_abated, total_n_fert, total_p_fert
    ):
        PLEACH = 0

        PLEACH = (
            self.fertiliser_class.urea_P_leach(total_urea, total_urea_abated)
            + self.fertiliser_class.n_fertiliser_P_leach(total_n_fert)
            + self.fertiliser_class.p_fertiliser_P_leach(total_p_fert)
        )

        return PLEACH * 3.06

    def grazing_soils_P_LEACH_EP(self, animal):

        PLEACH = 0

        for key in animal.__dict__.keys():
            if (
                key in self.cohorts_class.COHORTS
                and animal.__getattribute__(key).pop != 0
            ):

                # Just leach from grazing, not from manure application
                PLEACH += (
                    self.grazing_class.PLeach_GRAZING(animal.__getattribute__(key))
                    * animal.__getattribute__(key).pop
                )

        return PLEACH * 3.06

    def total_fertilser_soils_EP(
        self,
        total_urea,
        total_urea_abated,
        total_n_fert,
        total_p_fert,
    ):

        return self.total_fertiliser_soils_NH3_and_LEACH_EP(
            total_urea, total_urea_abated, total_n_fert
        ) + self.fertiliser_soils_P_LEACH_EP(
            total_urea, total_urea_abated, total_n_fert, total_p_fert
        )

    def total_grazing_soils_EP(self, animal):

        return self.total_grazing_soils_NH3_and_LEACH_EP(
            animal
        ) + self.grazing_soils_P_LEACH_EP(animal)

    # Imported Feeds
    def EP_from_concentrate_production(self, animal):

        concentrate_p = 0

        for key in animal.__dict__.keys():

            if (
                key in self.cohorts_class.COHORTS
                and animal.__getattribute__(key).pop != 0
            ):

                concentrate_p += (
                    animal.__getattribute__(key).con_amount
                    * self.loader_class.concentrates.get_con_po4_e(
                        animal.__getattribute__(key).con_type
                    )
                ) * animal.__getattribute__(key).pop

        return concentrate_p * 365


###############################################################################
# Air Quality Ammonia
###############################################################################


class AirQualityTotals:
    def __init__(self, ef_country):
        self.loader_class = Loader(ef_country)
        self.cohorts_class = Cohorts()
        self.grazing_class = GrazingStage(ef_country)
        self.housing_class = HousingStage(ef_country)
        self.storage_class = StorageStage(ef_country)
        self.spread_class = DailySpread(ef_country)
        self.fertiliser_class = FertiliserInputs(ef_country)
        self.upstream_class = Upstream(ef_country)

    # Manure Management
    def total_manure_NH3_AQ(self, animal):

        NH3N = 0

        for key in animal.__dict__.keys():
            if (
                key in self.cohorts_class.COHORTS
                and animal.__getattribute__(key).pop != 0
            ):

                NH3N += (
                    self.storage_class.nh3_emissions_per_year_STORAGE(
                        animal.__getattribute__(key),
                    )
                    + self.housing_class.nh3_emissions_per_year_HOUSED(
                        animal.__getattribute__(key),
                    )
                ) * animal.__getattribute__(key).pop

        return NH3N

    # SOILS
    def total_fertiliser_soils_NH3_AQ(
        self, total_urea, total_urea_abated, total_n_fert
    ):

        NH3N = self.fertiliser_class.urea_NH3(
            total_urea, total_urea_abated
        ) + self.fertiliser_class.n_fertiliser_NH3(total_n_fert)

        return NH3N

    def total_grazing_soils_NH3_AQ(self, animal):

        # No emissions from spreading for sheep

        NH3N = 0

        for key in animal.__dict__.keys():
            if (
                key in self.cohorts_class.COHORTS
                and animal.__getattribute__(key).pop != 0
            ):
                NH3N += (
                    self.grazing_class.nh3_emissions_per_year_GRAZING(
                        animal.__getattribute__(key)
                    )
                    * animal.__getattribute__(key).pop
                )

        return NH3N
