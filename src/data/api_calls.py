# for the data
import pandas as pd
import requests
import re
from transformation_functions import convert_object_columns_to_numeric, lb_to_kg, inch_to_cm


def games_json_dump(year=2022, division=1, page=1):
    """
    
    This function calls Crossfits api and returns json data on different years and divisions for the Crossfit Games
    Leaderboard.

    Parameters:
        - year from 2007 until most recent
        - division is either 1 for male or 2 for female
        - page is the number of page we are on the leaderboard

    """

    # error handling for function parameters
    if not isinstance(year, int):
        raise TypeError("year should be an integer")
    if not isinstance(division, int):
        raise TypeError("division should be an integer")
    if not isinstance(page, int):
        raise TypeError("page should be an integer")

    # url for api
    url = f"https://c3po.crossfit.com/api/leaderboards/v2/competitions/games/{year}/leaderboards?division={division}&sort=0&page={page}"
    # sending the request and reading the response.
    response = requests.get(url)
    # loading the response as json
    response = response.json()
    # returing the response as a json
    return(response)

def games_info(year=2022, division=1):
    """
    
    This function uses the json data from the api call in games_json_dump and parses
    the json to get information on the Crossfit Games for the specified year and division 
    returned as a Pandas Dataframe.

    Parameters:
        - year from 2007 until most recent
        - division is either 1 for male or 2 for female
        - page is the number of page we are on the leaderboard

    Returns:
        - competition_id for that specified year
        - total_pages for the leaderboard
        - total_competitors for that year and division
        - total_events for that years Games

    """

    # error handling for function parameters
    if not isinstance(year, int):
        raise TypeError("year should be an integer")
    if not isinstance(division, int):
        raise TypeError("division should be an integer")
    
    # get the json data from the web service
    response = games_json_dump(year=year, division=division)
    
    # collecting data on the specified games session
    total_pages = response['pagination']['totalPages']
    total_competitors = response['pagination']['totalCompetitors']
    competition_id = response['competition']['competitionId']
    total_events = len(response['ordinals'])
    # return a list of responses
    games_info_list = [competition_id, total_pages, total_competitors, total_events]

    return(games_info_list)

def games_info_multiple(year_from=2018, year_too=2022, division=1):
    
    """

    This function uses the games_info function to get information on multiple Crossfit Games 
    returned as a Pandas dataframe.

    Parameters:
        - year_xxx is from 2007 and to current
        - division is 1 for male, 2 for female and 0 for both

    Returns:
        - competition_id for that specified year
        - total_pages for the leaderboard
        - total_competitors for that year and division
        - total_events for that years Games
        - year of the Games
        - division of the specified Games

    """


    # error handling for function parameters
    if not isinstance(year_from, int):
        raise TypeError("year_from should be an integer")
    if not isinstance(year_too, int):
        raise TypeError("year_too should be an integer")
    if not isinstance(division, int):
        raise TypeError("division should be an integer")
    
    # create a dataframe to store results
    df_games_info_multiple = pd.DataFrame(columns=['competitionId', 'totalPages', 'totalCompetitors', 'totalEvents', 'year','division'])
    # determining what division value we need
    if division == 1:
        division_value = [1]
    elif division == 2:
        division_value = [2]
    # else we just take both divisions
    else:
        division_value = [1,2]
    # iterate over year_from and year_too
    for i in range(0, year_too - year_from + 1):
        for j in range(0,len(division_value)):
            # results form running games_info funcation
            result_list = games_info(year_from+i,division=division_value[j])
            # results from function
            result_list.append(year_from+i)
            result_list.append(division_value[j])
            # Convert the list to a DataFrame with a single row
            temp_df = pd.DataFrame([result_list], columns=['competitionId', 'totalPages', 'totalCompetitors', 'totalEvents', 'year','division'])
            # Concatenate the DataFrame with the existing DataFrame
            df_games_info_multiple = pd.concat([df_games_info_multiple, temp_df], ignore_index=True)
    
    # transform columns into integer when relevant
    df_games_info_multiple = convert_object_columns_to_numeric(df_games_info_multiple)

    return(df_games_info_multiple)

def games_info_competitors(year, division):
    
    """

    This function uses the functions games_json_dump and games_info to get competitor information for 
    the specified Crossfit Games year and division returned as a Pandas dataframe.

    It also does some transformation on the data from the api. It uses the inch_to_cm and lb_to_kg functions
    to create two new columns and transforms age to integer.

    Parameters:
        - year is from 2007 and to current
        - division is 1 for male, 2 for female and 0 for both

    This functions get's a bitt more complicated when there are more than one pages per call,
    e.g. in the year 2019 when there were 144 male competitors.
    """
        
    # create a dataframe to store info
    df_games_info_competitors = pd.DataFrame()

    # determining what division value we need
    if division == 1:
        division_value = [1]
    elif division == 2:
        division_value = [2]
    # else we just take both divisions
    else:
        division_value = [1,2]

    # iterate over division_value
    for current_division in range(0,len(division_value)):
        # collecting data on the specified games session
        info_response = games_info(year=year,division=division_value[current_division])
        # iterate to solve for when pages are more than 1
        if info_response[1] > 1:
            for page in range(1, info_response[1] + 1):
                response = games_json_dump(year=year,division=division_value[current_division],page=page)
                if page == info_response[1]: # if we are on the final page
                    # call webservice to get get the json
                    for competitors_on_last_page in range(0, info_response[2] - (info_response[1] - 1) * 50): # there are currently 50 results per page
                        # parse json to where we want to be
                        entrant_json = response['leaderboardRows'][competitors_on_last_page]['entrant']
                        # insert results in temporary dataframe
                        df_temp = pd.DataFrame([entrant_json])
                        # concatenate the DataFrame with the existing DataFrame
                        df_games_info_competitors = pd.concat([df_games_info_competitors, df_temp], ignore_index=True)
                else:
                    # call webservice to get get the json
                    #response = games_json_dump(year=year,division=division_value[current_division],page=page)
                    for competitor_not_on_last_page in range(0,50): # there are currently 50 results per page
                        # parse json to where we want to be
                        entrant_json = response['leaderboardRows'][competitor_not_on_last_page]['entrant']
                        # insert results in temporary dataframe
                        df_temp = pd.DataFrame([entrant_json])
                        # concatenate the DataFrame with the existing DataFrame
                        df_games_info_competitors = pd.concat([df_games_info_competitors, df_temp], ignore_index=True)
        # else when total_pages on the leaderbord is just one
        else:
            # call webservice to get get the json
            response = games_json_dump(year=year,division=division_value[current_division],page=1)
            for competitor in range(0,info_response[2]):
                # parse json to where we want to be
                entrant_json = response['leaderboardRows'][competitor]['entrant']
                # insert results in temporary dataframe
                df_temp = pd.DataFrame([entrant_json])
                # Concatenate the DataFrame with the existing DataFrame
                df_games_info_competitors = pd.concat([df_games_info_competitors, df_temp], ignore_index=True)
    
    # Some transfomration of the data in df_games_info_competitors
    
    # transform columns into numerical when relevant
    df_games_info_competitors = convert_object_columns_to_numeric(df_games_info_competitors)
    
    # apply the functions to the relevant columns and assign it back to the columns
    df_games_info_competitors['heightInCm'] = df_games_info_competitors['height'].apply(inch_to_cm)
    df_games_info_competitors['weightInKg'] = df_games_info_competitors['weight'].apply(lb_to_kg)
    

    return(df_games_info_competitors)


def games_info_competitor_multiple(year_from=2018, year_too=2022, division=1):
         
    """

        This function uses the games_info_competitors function to get information on Crossfit Games 
        competitors for multiple years returned as a Pandas dataframe.

        Parameters:
            - year is from 2007 and to current
            - division is 1 for male, 2 for female and 0 for both

    """   
            
    # create a dataframe to store info
    df_games_info_competitor_multiple = pd.DataFrame()
        
    # iterate over the selected years
    for year in range(year_from, year_too + 1):
        df_temp = games_info_competitors(year,division)
        df_temp['year'] = year
        df_games_info_competitor_multiple = pd.concat([df_games_info_competitor_multiple, df_temp], ignore_index=True)

    return(df_games_info_competitor_multiple)

def games_info_scores(year=2022, division=1):
    
    """

        This function uses the functions games_json_dump and games_info to get events score information for 
        the specified Crossfit Games year and division returned as a Pandas dataframe.
            
        Parameters:
            - year is from 2007 and to current
            - division is 1 for male, 2 for female and 0 for both

    """   
    
    # create a dataframe to store the scores
    df_games_info_scores = pd.DataFrame()
    # collecting data on the specified games session
    #game_info_call = games_info(year=year,division=division)
    # determining what division value we need
    if division == 1:
        division_value = [1]
    elif division == 2:
        division_value = [2]
    # else we just take both divisions
    else:
        division_value = [1,2]

    # iterate over division_value
    for current_division in range(0,len(division_value)):
        # collecting data on the specified games session
        info_response = games_info(year=year,division=division_value[current_division])
        # iterate to solve for when pages are more than 1
        if info_response[1] > 1:
            for page in range(1, info_response[1] + 1):
                # call webservice to get get the json
                response = games_json_dump(year=year,division=division_value[current_division],page=page)
                if page == info_response[1]: # if we are on the final page
                    for competitors_on_last_page in range(0, info_response[2] - (info_response[1] - 1) * 50): # there are currently 50 results per page
                        # parse json to where we want to be 
                        scores_json = response['leaderboardRows'][competitors_on_last_page]['scores']
                        df_temp = pd.json_normalize(scores_json)
                        # adding columns to dataframe so other data can be joined in a relational model
                        df_temp['competitorId'] = response['leaderboardRows'][competitors_on_last_page]['entrant']['competitorId']
                        df_temp['year'] = year
                        df_temp['division'] = division_value[current_division]
                        # Concatenate the DataFrame with the existing DataFrame
                        df_games_info_scores = pd.concat([df_games_info_scores, df_temp], ignore_index=True)
                else:
                    for competitor_not_on_last_page in range(0,50): # there are currently 50 results per page
                        # parse json to where we want to be
                        scores_json = response['leaderboardRows'][competitor_not_on_last_page]['scores']
                        df_temp = pd.json_normalize(scores_json)
                        # adding columns to dataframe so other data can be joined in a relational model
                        df_temp['competitorId'] = response['leaderboardRows'][competitor_not_on_last_page]['entrant']['competitorId']
                        df_temp['year'] = year
                        df_temp['division'] = division_value[current_division]
                        # Concatenate the DataFrame with the existing DataFrame
                        df_games_info_scores = pd.concat([df_games_info_scores, df_temp], ignore_index=True)
        # else when total_pages on the leaderbord is just one
        else:
        # call webservice to get get the json
            response = games_json_dump(year=year,division=division_value[current_division],page=1)
            for competitor in range(0,info_response[2]):
                # parse json to where we want to be
                scores_json = response['leaderboardRows'][competitor]['scores']
                df_temp = pd.json_normalize(scores_json)
                # adding columns to dataframe so other data can be joined in a relational model
                df_temp['competitorId'] = response['leaderboardRows'][competitor]['entrant']['competitorId']
                df_temp['year'] = year
                df_temp['division'] = division_value[current_division]
                # Concatenate the DataFrame with the existing DataFrame
                df_games_info_scores = pd.concat([df_games_info_scores, df_temp], ignore_index=True)

    # A lot of transformation of the data in df_games_info_competitors is needed
     
    # transforming the rank column so we can change rank to a numerical column
    df_games_info_scores.loc[df_games_info_scores['rank'] == 'CUT', 'rankReason'] = 'CUT'
    df_games_info_scores.loc[df_games_info_scores['rank'] == 'WD', 'rankReason'] = 'WD'
    df_games_info_scores.loc[df_games_info_scores['rank'] == 'DNF', 'rankReason'] = 'DNF'
    new_rank = 0
    df_games_info_scores.loc[df_games_info_scores['rank'].isin(['CUT', 'WD', 'DNF']), 'rank'] = new_rank

    # transform columns into numerical when relevant
    df_games_info_scores = convert_object_columns_to_numeric(df_games_info_scores)

    # new column to get the weight in kg of the event is a weighlifting event
    df_games_info_scores['scoreIsWeightInKg'] = df_games_info_scores['scoreDisplay'].apply(lb_to_kg)
    
    # return the final dataframe
    return(df_games_info_scores)

def games_info_scores_multiple(year_from=2021, year_too=2022, division=1):
             
    """

        This function uses the games_info_scores function to get information on Crossfit Games 
        scores for multiple years returned as a Pandas dataframe.

        Parameters:
            - year is from 2007 and to current
            - division is 1 for male, 2 for female and 0 for both

    """   

    # error handling for function parameters
    if not isinstance(year_from, int):
        raise TypeError("year_from should be an integer")
    # error handling for function parameters
    if not isinstance(year_too, int):
        raise TypeError("year_too should be an integer")
    if not isinstance(division, int):
        raise TypeError("division should be an integer")
            
    # create a dataframe to store info
    df_games_info_scores_multiple = pd.DataFrame()
        
    # iterate over the selected years
    for year in range(year_from, year_too + 1):
        df_temp = games_info_scores(year,division)
        df_temp['year'] = year
        df_games_info_scores_multiple = pd.concat([df_games_info_scores_multiple, df_temp], ignore_index=True)

    return(df_games_info_scores_multiple)