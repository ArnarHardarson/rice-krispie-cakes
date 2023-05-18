import pandas as pd
import re

# Functions used in transformation of data to make it comparable

def convert_object_columns_to_numeric(df:pd.DataFrame):
    """
    Converts all columns in a dataframe to numeric if they are numerical
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError("df should be a Pandas dataframe")

    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_numeric(df[col])
            except ValueError:
                pass
    return df

def inch_to_cm(height):
    
    """
    Searches for 'in' in a string and converts the value to cm
    and strips 'in' and 'cm' from the value so that it is returned as a float.
    """
    
    if 'in' in height:
        height_in_inches = float(height.replace('in', '').strip())
        return round(height_in_inches * 2.54, 1)
    elif 'cm' in height:
        return float(height.replace('cm', '').strip())
    else:
        return None

def lb_to_kg(weight):
    
    """
    Searches for 'lb' in a string and converts the value to kg
    and strips 'lb' and 'kg' from the value so that it is returned as a float.
    """
    
    # check if "lb" and a number is in the string
    if 'lb' in weight:
        weight = re.findall(r'\d+', weight)
        if len(weight) > 0:
            weight = int(weight[0])
            return round(weight / 2.20462, 1)
    elif 'kg' in weight:
        return float(weight.re.findall(r'\d+', weight))
    else:
        return None