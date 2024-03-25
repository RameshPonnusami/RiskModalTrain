from utils import custom_encoder, fil_none_values, convert_to_numeric_or_str, get_column_info_for_ui
from .EDA.binning_algorithm import predict_score, process_train_data, format_criteria_for_ui
from .EDA.generate_chart import identify_data_types, process_charts
from flask import  request, jsonify, Response
from . import app
import os
import pandas as pd
import json
from .custom_annotations import login_required
from typing import Union, Any

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

@app.route('/model_train_n', methods=['POST'])
@login_required
def model_train_n() -> Union[str, Response]:
    if request.method == 'POST':
        # Get the selected target column from the AJAX request
        target_column = request.json.get('target_column')
        file_path = request.json.get('file_path')
        column_changes = request.json.get('column_changes')
        updated_criteria = request.json.get('updated_criteria')

        traindf = pd.read_csv(file_path)
        traindf = fil_none_values(column_changes, traindf)


        traindf = traindf.applymap(convert_to_numeric_or_str)

        # all_chart_details = process_charts(traindf, target_column)
        logit_str, log_reg, threshold, selected_features, selected_features_and_bin_data_list, performance_metrics_dict, model_full_path = process_train_data(
            traindf, target_column)

        model_summary = log_reg.summary()
        model_info = "Replace this with actual model details"

        # Extract the first table from model_summary
        coef_table_data = model_summary.tables[1]
        pvalue_table_data = model_summary.tables[0]

        # Convert the table data to a DataFrame
        tempdf = pd.DataFrame(pvalue_table_data.data)
        first_row_list = tempdf.iloc[0].tolist()
        tempdf = tempdf.drop(index=tempdf.index[0])
        tempdf.columns = first_row_list
        pvalue_records = tempdf.to_dict(orient='records')
        # print('pvalue_records',pvalue_records)

        tempdf = pd.DataFrame(coef_table_data.data)
        first_row_list = tempdf.iloc[0].tolist()
        tempdf = tempdf.drop(index=tempdf.index[0])
        tempdf.columns = first_row_list
        coef_records = tempdf.to_dict(orient='records')
        # print('coef_records',coef_records)

        coef_table_html = model_summary.tables[1].as_html()
        pvalues_table_html = model_summary.tables[0].as_html()

        # print(({"coef":coef_table_html,"pvalue":pvalues_table_html,'threshold':threshold,"selected_features":selected_features}))
        # print("pvalue",pvalue_records,)

        selected_features_details_list = format_criteria_for_ui(selected_features_and_bin_data_list)

        object_unique_values, column_info = get_column_info_for_ui(traindf[list(selected_features)])

        column_info.pop(target_column, None)



        return json.dumps({"coef": coef_records, "pvalue": pvalue_records, 'threshold': threshold,
                           "selected_features": list(selected_features),
                           "selected_features_details": selected_features_details_list,
                           "column_info": column_info,
                           "object_unique_values": object_unique_values,
                           "model_full_path": model_full_path,
                           "low_risk_threshold": performance_metrics_dict['low_risk_threshold'],
                           "high_risk_threshold": performance_metrics_dict['high_risk_threshold'],
                           "std_dev": performance_metrics_dict['std_dev'],
                           "testdecile": performance_metrics_dict['testdecile'].to_dict(orient='records'),
                           "decile_chart": performance_metrics_dict['decile_chart'],
                           "trainDecileWithScore": performance_metrics_dict['trainDecileWithScore'].to_dict(
                               orient='records'),
                           "trainDecileChart": performance_metrics_dict['trainDecileChart'],
                           "dsa_dict": performance_metrics_dict['dsa_dict'],
                           "corr_df_after_bin": performance_metrics_dict['corr_df_after_bin'].to_dict(orient='records'),
                           "corr_df_before_bin": performance_metrics_dict['corr_df_before_bin'].to_dict(
                               orient='records'),
                           }, default=custom_encoder)


