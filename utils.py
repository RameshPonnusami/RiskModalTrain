import pandas as pd
import numpy as np
from typing import Union, List, Dict, Any, Tuple


def convert_to_numeric_or_str(value: Union[float, int, str]) -> Union[float, int, str]:
    try:
        return pd.to_numeric(value)
    except ValueError:
        return value


def get_column_info_for_ui(uidf: pd.DataFrame) -> Tuple[Dict[str, List[Any]], Dict[str, str]]:
    # Get column names and their data types
    column_info = {column: str(uidf[column].dtype) for column in uidf.columns}
    object_unique_values = {}
    for ci in column_info.keys():
        if column_info[ci] == 'object':
            unique_list = list(uidf[ci].unique())
            filtered_list = [x for x in unique_list if not (isinstance(x, float) and np.isnan(x)) and x != 'NaN']
            object_unique_values[ci] = filtered_list
    return object_unique_values, column_info


def custom_encoder(obj: Any) -> Any:
    def handle_item(item: Any) -> Any:
        if isinstance(item, (float, int,np.float64)):
            # Convert float, int, or float128 to string with a fixed number of decimal places
            return round(float(item), 2)
        elif isinstance(item, np.int64):
            # Convert numpy.int64 to Python int
            return int(item)

        elif isinstance(item, str):
            # Handle strings if needed
            return item
        elif isinstance(item, list):
            # Recursively encode elements in a list
            return [handle_item(sub_item) for sub_item in item]
        elif isinstance(item, dict):
            # Recursively encode values in a dictionary
            return {key: handle_item(value) for key, value in item.items()}
        else:
            raise TypeError(f"Object of type {type(item).__name__} is not JSON serializable")

    return handle_item(obj)


def fil_none_values(column_changes: List[Dict[str, Any]], df: pd.DataFrame) -> pd.DataFrame:
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
