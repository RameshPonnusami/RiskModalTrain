import pandas as pd
import numpy as np

def fil_none_values(column_changes,df):
    for cc in column_changes:
        cname = cc['columnName']
        selected_option = cc['selectedOption']
        if selected_option == 'manual':
            given_value = cc['textInput']
            df[cname].fillna(given_value, inplace=True)
        elif selected_option == 'mean' and cc['columnType'] == 'numeric':
            try:
                pd.to_numeric(df[cname], errors='raise', downcast='float')
                #             print(f"{column} contains only int or float values.")
                is_int_float = True
            except ValueError:
                is_int_float = False
            #             print(f"{column} contains non-numeric values or mixed types.")
            if is_int_float:
                c_mean_value = df[cname].mean()
                df[cname].fillna(c_mean_value, inplace=True)
        elif selected_option == 'zero':
            df[cname].fillna(0, inplace=True)
        else:
            pass
    return df