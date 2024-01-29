from utils import custom_encoder
from .EDA.binning_algorithm import predict_score
from .EDA.generate_chart import identify_data_types
from flask import  request, jsonify
from . import app
import os
import pandas as pd
import json

@app.route('/upload', methods=['POST'])
def upload_file() -> dict:
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400

    file = request.files['file']

    if file.filename == '':
        return {'error': 'No selected file'}, 400

    try:
        file_full_path = os.path.join(app.static_folder, 'train_data', file.filename)
        file.save(file_full_path)
        # file.close()

        # Load the CSV file into a DataFrame
        df = pd.read_csv(file_full_path)

        # Process the DataFrame as needed
        # For example, get the first 10 records and column names
        tempdf=df.head(10)
        tempdf = tempdf.fillna('')
        first_10_records = tempdf.to_dict(orient='records')
        columns = list(df.columns)
        categorical_columns, numeric_columns = identify_data_types(tempdf)
        column_types = {}
        for cn in categorical_columns:
            column_types[cn] = 'categorical'
        for cn in numeric_columns:
            column_types[cn] = 'numeric'


        response ={'message': 'File uploaded successfully',
                'data': {'first_10_records': first_10_records, 'columns': columns,'file_path':file_full_path,
                         "column_types":column_types
                         }
                   }
        return response

    except Exception as e:
        return {'error': str(e)}, 500

@app.route('/model_test_with_user_input', methods=['POST'])
def model_test_with_user_input() -> str:
    if request.method == 'POST':
        request_json = request.json
        model_full_path = request_json['model_full_path']
        selectedcriteria = request_json['selectedcriteria']

        selectedcriteria = json.loads(selectedcriteria)

        score, risk_cat = predict_score(request_json,selectedcriteria,model_full_path)

        return json.dumps({"score":score, "risk_cat":risk_cat},default=custom_encoder)