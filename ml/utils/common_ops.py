import os

from ml import app
from datetime import datetime

def assign_color(predicted_score, threshold_low, threshold_high):

    if threshold_low < predicted_score <= threshold_high:
        return "yellow"
    elif predicted_score >= threshold_high:
        return "red"
    else:
        return "green"

def get_relative_path(filepath):
    relative_path = os.path.relpath(filepath, app.root_path)
    return relative_path


def get_save_path(filename,addtime=False):
    if addtime:
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    else:
        timestamp=''
    file_full_path = os.path.join(app.static_folder, 'charts', str(timestamp)+filename)
    return file_full_path