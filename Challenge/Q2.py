#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

"""
Q2

(C) 2017 by Jay Kaiser <jayckaiser.github.io>
Updated Oct 26 by Jay Kaiser

 """

import pandas as pd
import numpy as np
import math
import matplotlib.pyplot as plt


def main():

    path_to_data = "C:/Users/jayka/Documents/Datasets/"

    accidents = pd.read_csv(path_to_data + "Accidents0514.csv", header=0)
    print("accidents loaded in")

    vehicles = pd.read_csv(path_to_data + "Vehicles0514.csv", header=0)
    print("vehicles loaded in")


    # what fraction of accidents occur in urban areas?
    # accidents:Urban_or_Rural_Area
    urban_accidents = accidents.loc[accidents['Urban_or_Rural_Area'] == 1]
    urban_vs_rural = len(urban_accidents.index) / len(accidents.index)
    print("The fraction of accidents that occurs in urban areas is {:.10f}.".format(urban_vs_rural))


    # when is the most dangerous hour to drive (based on fatal accidents)?
    # accidents:Time, accidents:Accident_Severity == 1
    accidents['Time'] = accidents['Time'].str[:2]

    twenty_four_hour_all = []
    twenty_four_hour_severe = []
    for i in range(24):
        twenty_four_hour_all.append(len(accidents.loc[accidents['Time'] == str(i).zfill(2)].index))
        twenty_four_hour_severe.append(len(accidents.loc[(accidents['Time'] == str(i).zfill(2)) &
                                                         (accidents['Accident_Severity'] == 1)].index))
    twenty_four_hour_proportions = [a / b for a, b in zip(twenty_four_hour_severe, twenty_four_hour_all)]

    most_dangerous_hour = max(twenty_four_hour_proportions)
    print("The most dangerous hour of the day has the proportion of accidents of {:.10f}.".format(most_dangerous_hour))


    # what is the trend of accidents per year?
    #accidents:Date
    accidents['Date'] = accidents['Date'].str[-4:]

    years = sorted(accidents['Date'].unique())
    accidents_per_year = {}
    for year in years:
        accidents_per_year[year] = len(accidents.loc[accidents['Date'] == year].index)

    least_squares = np.polyfit([int(year) for year in years],
                               [int(accidents_per_year[year]) for year in years],
                               deg=1)
    print("The slope of the line plotting the number of accidents per year is {:.10f}.".format(least_squares[0]))
    

    # do high-speed-limit accidents have more casualties?
    # accidents:Speed_limit, accidents:Number_of_Casualties
    speed_limits = sorted(accidents['Speed_limit'].unique())
    ratios = []
    for speed_limit in speed_limits:
        number_of_casualties = sum(accidents.loc[accidents['Speed_limit'] == speed_limit]['Number_of_Casualties'])
        number_of_accidents = len(accidents.loc[accidents['Speed_limit'] == speed_limit].index)
        ratios.append(number_of_casualties / number_of_accidents)
        #print("Speed Limit {}: {}".format(speed_limit, ratio_per_speed_limit[speed_limit]))

    pearsons = np.corrcoef(speed_limits, ratios)
    print("The Pearson correlation coefficient between speed limit and casualties to accidents is {:.10f}."
          .format(pearsons[0][1]))


    # how does weather influence skidding and/or overturning?
    # accidents:Weather_Conditions (2,3,5,6 vs 1), vehicles:Skidding_and_Overturning (1-5 vs 0)
    nonskidding_accidents = vehicles.loc[vehicles['Skidding_and_Overturning'] == 0]
    skidding_accidents = vehicles.loc[(vehicles['Skidding_and_Overturning'] == 1)
                                       | (vehicles['Skidding_and_Overturning'] == 2)
                                       | (vehicles['Skidding_and_Overturning'] == 3)
                                       | (vehicles['Skidding_and_Overturning'] == 4)
                                       | (vehicles['Skidding_and_Overturning'] == 5)]

    nice_weather_accidents = accidents.loc[accidents['Weather_Conditions'] == 1]
    snow_or_rain_accidents = accidents.loc[(accidents['Weather_Conditions'] == 2)
                                            | (accidents['Weather_Conditions'] == 3)
                                            | (accidents['Weather_Conditions'] == 5)
                                            | (accidents['Weather_Conditions'] == 6)]

    snow_or_rain_skidding_accidents = pd.Series(list(set(skidding_accidents['Accident_Index']) &
                                                     set(snow_or_rain_accidents['Accident_Index'])))
    nice_weather_skidding_accidents = pd.Series(list(set(skidding_accidents['Accident_Index']) &
                                                     set(snow_or_rain_accidents['Accident_Index'])))

    precipitation_vs_not_skidding_accidents = (len(snow_or_rain_skidding_accidents) / len(snow_or_rain_accidents)) \
                                              / (len(nice_weather_skidding_accidents) / len(nice_weather_accidents))
    print("The ratio of skidding accidents during precipitation vs not is {:.10f}"
          .format(precipitation_vs_not_skidding_accidents))



    # what is the ratio of fatal accidents from males vs females?
    # accidents: Accident_Severity == 1, vehicles:Sex_of_Driver (1=male, 2=female), vehicles:Vehicle_Type == 9
    fatal_accidents = accidents.loc[accidents['Accident_Severity'] == 1]
    car_accidents = vehicles.loc[vehicles['Vehicle_Type'] == 9]

    male_car_accidents = car_accidents.loc[car_accidents['Sex_of_Driver'] == 1]
    female_car_accidents = car_accidents.loc[car_accidents['Sex_of_Driver'] == 2]

    shared_fatal_males_accidents_between_csvs = pd.Series(list(set(fatal_accidents['Accident_Index']) &
                                                               set(male_car_accidents['Accident_Index'])))
    shared_fatal_female_accidents_between_csvs = pd.Series(list(set(fatal_accidents['Accident_Index']) &
                                                                set(female_car_accidents['Accident_Index'])))

    male_vs_female_fatalities = (len(shared_fatal_males_accidents_between_csvs) / len(male_car_accidents)) \
                                / (len(shared_fatal_female_accidents_between_csvs) / len(female_car_accidents))
    print("The ratio of male to female fatal car accidents is {:.10f}.".format(male_vs_female_fatalities))


    # estimate the areas of police districts.
    # accidents:Police_Force, accidents:Longitude, accidents:Latitude
    police_districts = list(accidents['Police_Force'].unique())
    districts_and_areas = {}
    for force in police_districts:
        accidents_in_district = accidents.loc[accidents['Police_Force'] == force]

        # By finding the mean Latitude, I can convert the distance of longitude from degrees to kilometers
        latitude_mean = accidents_in_district['Latitude'].mean()

        longitude_std = accidents_in_district['Longitude'].std()
        latitude_std = accidents_in_district['Latitude'].std()

        # the standard deviations are measured in degrees. They must be converted to kilometers.
        longitude_in_km = 111.320 * math.cos(math.radians(latitude_mean))
        latitude_in_km = 110.574 * latitude_std

        # area of an ellipse = pi * a * b
        district_area = math.pi * latitude_in_km * longitude_in_km

        districts_and_areas[force] = district_area

    max_district_area = max(districts_and_areas.values())
    print("The largest district measured from long/lat is {:.10f} kilometers squared.".format(max_district_area))
    
    
    # how fast do the number of car accidents drop off with age?
    # vehicles:Age_of_Driver
    vehicles = vehicles.loc[vehicles['Age_of_Driver'] >= 17]
    ages = sorted(vehicles['Age_of_Driver'].unique())

    accidents_per_age = [len(vehicles.loc[vehicles['Age_of_Driver'] == age].index) for age in ages]

    # I plot the graph just to confirm that yes, the decrease with age is exponential.
    plt.plot(ages, accidents_per_age)
    plt.show()

    best_fit_exponential = np.polyfit(ages,
                                      accidents_per_age,
                                      1)
    print("The exponential rate of decay of age vs accidents is {:.10f}.".format(best_fit_exponential[0]))


if __name__ == "__main__":
    main()
