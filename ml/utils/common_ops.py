import os
from typing import List

import pandas as pd

from ml import app
from datetime import datetime
from ..config.config import Config


def assign_color(predicted_score: float, threshold_low: float, threshold_high: float) -> str:
    if threshold_low < predicted_score <= threshold_high:
        return "yellow"
    elif predicted_score >= threshold_high:
        return "red"
    else:
        return "green"


def identify_categorical_column_by_size(idf: pd.DataFrame) -> List:
    categorical_variables = []
    for cl in idf.columns:
        if len(idf[cl].unique()) <= Config.CATEGORICAL_COLUMN_UNIQUE_SIZE:
            categorical_variables.append(cl)
    return categorical_variables


def get_relative_path(filepath: str) -> str:
    relative_path = os.path.relpath(filepath, app.root_path)
    return relative_path


def get_save_path(filename: str, addtime: bool = False) -> str:
    if addtime:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    else:
        timestamp = ''
    file_full_path = os.path.join(app.static_folder, 'charts', str(timestamp) + filename)
    return file_full_path
