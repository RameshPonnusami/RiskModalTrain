import json

from utils import fil_none_values, convert_to_numeric_or_str, get_column_info_for_ui, custom_encoder
from . import app
from flask import render_template, request, jsonify, redirect, url_for, Response
from flask import session
from functools import wraps
import pandas as pd
import joblib
from typing import Union, Any

from .config.config import Config

from .EDA.binning_algorithm import format_criteria_for_ui, process_train_data, process_EDA
from .EDA.generate_chart import process_charts
from .EDA.test_data import generate_predict_data
from .utils.common_ops import assign_color

VALID_USERNAME = Config.VALID_USERNAME
VALID_PASSWORD = Config.VALID_PASSWORD


def login_required(view_func) -> callable:
    @wraps(view_func)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or not session['username']:
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)

    return decorated_function


# Render the main page with the input form and charts
@app.route('/')
def index()-> Union[str, Response]:
    app.logger.debug('This is a debug message from the route')
    app.logger.info('This is an info message')
    app.logger.warning('This is a warning message')
    app.logger.error('This is an error message')
    app.logger.critical('This is a critical message')

    if 'username' in session:
        return render_template('index.html')
    else:
        return redirect(url_for('login'))
    # return render_template('index.html')


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login() -> Union[None, str]:
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == VALID_USERNAME and password == VALID_PASSWORD:
            session['username'] = username
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid username or password')
    return render_template('login.html')


# Logout route
@app.route('/logout')
def logout() -> Response:
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/EDA', methods=['GET', 'POST'])
@login_required
def EDA() -> Union[str, Response]:
    if request.method == 'POST':
        # Get the selected target column from the AJAX request
        target_column = request.json.get('target_column')
        file_path = request.json.get('file_path')
        column_changes = request.json.get('column_changes')

        traindf = pd.read_csv(file_path)
        traindf = fil_none_values(column_changes, traindf)
        # Process the target column as needed
        # For example, print or store the selected target column
        # print('Selected Target Column:', target_column)

        traindf = traindf.applymap(convert_to_numeric_or_str)

        all_chart_details = process_charts(traindf, target_column)

        selected_features_names_with_target, selected_features_and_bin_data_list, selected_features, selected_features_names, threshold = process_EDA(traindf,target_column)
        selected_features_details_list = format_criteria_for_ui(selected_features_and_bin_data_list)
        return json.dumps({'threshold': threshold,
                           "selected_features": list(selected_features),
                           "chartDetails": all_chart_details,
                           "selected_features_details": selected_features_details_list,

                           }, default=custom_encoder)


@app.route('/model_train', methods=['GET', 'POST'])
@login_required
def model_train() -> Union[str, Response]:
    if request.method == 'POST':
        # Get the selected target column from the AJAX request
        target_column = request.json.get('target_column')
        file_path = request.json.get('file_path')
        column_changes = request.json.get('column_changes')

        traindf = pd.read_csv(file_path)
        traindf = fil_none_values(column_changes, traindf)
        # Process the target column as needed
        # For example, print or store the selected target column
        # print('Selected Target Column:', target_column)

        traindf = traindf.applymap(convert_to_numeric_or_str)

        all_chart_details = process_charts(traindf, target_column)
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
                           "chartDetails": all_chart_details,
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

    else:
        return render_template('model_train.html')


@app.route('/model_details')
@login_required
def model_details() -> str:
    # check_login()
    # Add logic to gather and display model details
    log_reg = joblib.load('ml/log_reg_model')

    # Get the model summary
    model_summary = log_reg.summary()
    model_info = "Replace this with actual model details"
    coef_table_html = model_summary.tables[1].as_html(classes='table table-bordered table striped')
    pvalues_table_html = model_summary.tables[0].as_html()

    # Generate bivariate charts (replace this with actual chart generation logic)
    bivariate_charts = [

        'short_temp.png', 'term.png', 'emp_length_num.png', 'grade.png', 'purpose.png',
        'ruc.png'
    ]

    performance_charts = ['ruc.png', ]

    continous_charts = ['annual_inc.png', 'dti.png', 'revol_util.png', 'total_rec_flat.png', ]
    categorical_charts = ['short_temp.png', 'term.png', 'emp_length_num.png', 'grade.png', 'purpose.png']
    model_result = {"Accuracy": 0.80225 * 100,
                    "Precision": 0.4,
                    "Recall (Sensitivity)": 0.002531645569620253,
                    "F1 Score": 0.005031446540880503
                    }
    return render_template('model_details.html',
                           coef_table_html=coef_table_html,
                           pvalues_table_html=pvalues_table_html,
                           model_result=model_result,
                           bivariate_charts=bivariate_charts,
                           continous_charts=continous_charts,
                           categorical_charts=categorical_charts,
                           performance_charts=performance_charts)


def load_test_model() -> Any:
    with open('ml/log_reg_model', 'rb') as model_file:
        model = joblib.load(model_file)
    return model


@app.route('/predict', methods=['GET', 'POST'])
@login_required
def predict() -> Union[str, Response]:
    # check_login()
    try:
        if request.method == 'POST':
            # Get user input from the form
            annual_inc = float(request.form['annual_inc'])
            dti = float(request.form['dti'])
            revol_util = float(request.form['revol_util'])
            emp_length_num = int(request.form['emp_length_num'])
            grade = request.form['grade']
            purpose = request.form['purpose']
            term = request.form['term']
            annual_inc_lte_60000, dti_gte_18, revol_util_gt_60, emp_length_num_label, grade_label, purpose_label, term_label = generate_predict_data(
                annual_inc, dti, revol_util, emp_length_num, grade, purpose, term)
            # Create a DataFrame with the user input
            user_data = pd.DataFrame({
                'grade_label': [grade_label],
                'purpose_label': [purpose_label],
                'term_label': [term_label],
                'emp_length_num_label': [emp_length_num_label],
                'annual_inc_lte_60000': [annual_inc_lte_60000],
                'dti_gte_18': [dti_gte_18],
                'revol_util_gt_60': [revol_util_gt_60],
                # Include other input variables
            })

            # Use the model to predict
            # print(annual_inc,dti,revol_util,emp_length_num,grade,purpose,term)
            model = load_test_model()
            prediction = model.predict(user_data)  # Assuming a binary classification
            # print(prediction[0] )
            # Example usage
            average_score = 20  # Replace this with your average score from the trained model

            # Define thresholds based on your criteria
            threshold_low = average_score - 2
            threshold_high = average_score + 2
            predicted_score = prediction[0] * 100
            # Assign color based on predicted score
            color = assign_color(predicted_score, threshold_low, threshold_high)

            # Return the result to the user
            return render_template('predict.html', prediction_result=predicted_score,
                                   annual_inc=annual_inc, dti=dti, revol_util=revol_util,
                                   emp_length_num=emp_length_num, grade=grade, purpose=purpose, term=term,
                                   color=color)
        else:
            # Render the initial prediction form
            return render_template('predict.html')
    except Exception as e:
        return render_template('error.html', error_message=str(e))


@app.route('/testapi', methods=['POST','GET'])
def testapi():
    if request.method == 'POST':
        print(request.json)
        return {"msg":"hi"}
    return render_template('test1.html')