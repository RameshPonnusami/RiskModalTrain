import json

from flask import Flask, render_template, request, jsonify, redirect, url_for
import joblib
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from flask import session
from functools import wraps
import logging
import numpy as np
import os

from optbin import process_train_data, format_criteria_for_ui
from generate_chart import process_charts
from optbin import predict_score
from utils import fil_none_values

app = Flask(__name__)



# Default log level
DEFAULT_LOG_LEVEL = logging.DEBUG

# Set the logger level based on the configuration or a default value
app.logger.setLevel(app.config.get('LOG_LEVEL', DEFAULT_LOG_LEVEL))

# Create a file handler and set the log level
file_handler = logging.FileHandler('app.log')
file_handler.setLevel(app.logger.level)

# Create a formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)

# Add the handler to the app logger
app.logger.addHandler(file_handler)


app.secret_key = "your_secret_key"  # Change this to a secure secret key

# Define static user credentials
VALID_USERNAME = "admin"
VALID_PASSWORD = "admin"

# Load your pre-trained model
with open('log_reg_model', 'rb') as model_file:
    model = joblib.load(model_file)

# Sample data for bivariate chart
# Replace this with your actual data and charting logic
# sample_data = pd.DataFrame({
#     'grade_label': [0, 1, 0, 1, 1],
#     'purpose_label': [1, 0, 1, 0, 1],
#     'bad_loan': [0, 1, 0, 1, 0]
# })

# Create a bivariate chart and convert it to a base64 encoded image
# plt.figure(figsize=(8, 6))
# sns.scatterplot(x='grade_label', y='purpose_label', hue='bad_loan', data=sample_data, palette='Set2')
# chart_image = BytesIO()
# plt.savefig(chart_image, format='png')
# chart_image.seek(0)
# chart_base64 = base64.b64encode(chart_image.read()).decode('utf-8')

# Check if the user is logged in for each route



def login_required(view_func):
    @wraps(view_func)
    def decorated_function(*args, **kwargs):
        if 'username' not in session or not session['username']:
            return redirect(url_for('login'))
        return view_func(*args, **kwargs)
    return decorated_function

# Render the main page with the input form and charts
@app.route('/')
def index():
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
def login():
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
def logout():
    session.pop('username', None)
    return redirect(url_for('login'))


from generate_chart import identify_data_types

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return {'error': 'No file part'}, 400

    file = request.files['file']

    if file.filename == '':
        return {'error': 'No selected file'}, 400

    try:

        file_full_path = os.path.join(app.root_path, 'static', 'train_data', file.filename)
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
        # print(response)
        return response

    except Exception as e:
        return {'error': str(e)}, 500



def custom_encoder(obj):
    def handle_item(item):
        if isinstance(item, (float, int, np.float128)):
            # Convert float, int, or float128 to string with a fixed number of decimal places
            return round(float(item), 2)
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


def get_column_info_for_ui(uidf):
    # Get column names and their data types
    column_info = {column: str(uidf[column].dtype) for column in uidf.columns}
    object_unique_values = {}
    for ci in column_info.keys():
        if column_info[ci] == 'object':
            unique_list = list(uidf[ci].unique())
            filtered_list = [x for x in unique_list if not (isinstance(x, float) and np.isnan(x)) and x != 'NaN']
            object_unique_values[ci] = filtered_list
    return object_unique_values,column_info


# Function to convert each element to numeric or keep as string
def convert_to_numeric_or_str(value):
    try:
        return pd.to_numeric(value)
    except ValueError:
        return value


@app.route('/model_train', methods=['GET','POST'])
@login_required
def model_train():
    if request.method == 'POST':
        # Get the selected target column from the AJAX request
        target_column = request.json.get('target_column')
        file_path = request.json.get('file_path')
        column_changes = request.json.get('column_changes')

        app.logger.debug(column_changes)

        traindf = pd.read_csv(file_path)
        traindf = fil_none_values(column_changes, traindf)
        # Process the target column as needed
        # For example, print or store the selected target column
        # print('Selected Target Column:', target_column)


        traindf = traindf.applymap(convert_to_numeric_or_str)

        all_chart_details = process_charts(traindf,target_column)
        logit_str,log_reg,threshold,selected_features,selected_features_and_bin_data_list,performance_metrics_dict,model_full_path=process_train_data(traindf,target_column)

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

        object_unique_values, column_info =get_column_info_for_ui(traindf[list(selected_features)])

        column_info.pop(target_column, None)

        return json.dumps({"coef":coef_records,"pvalue":pvalue_records,'threshold':threshold,
                           "selected_features":list(selected_features),
                           "chartDetails":all_chart_details,
                           "selected_features_details": selected_features_details_list,
                           "column_info":column_info,
                            "object_unique_values":object_unique_values,
                           "model_full_path":model_full_path,
                           "low_risk_threshold":performance_metrics_dict['low_risk_threshold'],
                            "high_risk_threshold":performance_metrics_dict['high_risk_threshold'],
                            "std_dev":performance_metrics_dict['std_dev'],
                           },default=custom_encoder)

    else:
        return render_template('model_train.html')



@app.route('/model_test_with_user_input', methods=['POST'])
def model_test_with_user_input():
    if request.method == 'POST':
        request_json = request.json
        model_full_path = request_json['model_full_path']
        selectedcriteria = request_json['selectedcriteria']

        selectedcriteria = json.loads(selectedcriteria)

        score, risk_cat = predict_score(request_json,selectedcriteria,model_full_path)

        return json.dumps({"score":score, "risk_cat":risk_cat},default=custom_encoder)

@app.route('/model_details')
@login_required
def model_details():
    # check_login()
    # Add logic to gather and display model details
    log_reg = joblib.load('log_reg_model')

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

    performance_charts=['ruc.png',]

    continous_charts=[ 'annual_inc.png', 'dti.png', 'revol_util.png', 'total_rec_flat.png', ]
    categorical_charts=[  'short_temp.png', 'term.png', 'emp_length_num.png', 'grade.png', 'purpose.png' ]
    model_result={"Accuracy": 0.80225*100,
                    "Precision": 0.4,
                    "Recall (Sensitivity)": 0.002531645569620253,
                    "F1 Score": 0.005031446540880503
                  }
    print(performance_charts)
    return render_template('model_details.html',
                           coef_table_html=coef_table_html,
                           pvalues_table_html=pvalues_table_html,
                           model_result=model_result,
                             bivariate_charts=bivariate_charts,
                             continous_charts=continous_charts,
                             categorical_charts=categorical_charts,
                             performance_charts=performance_charts)


def generate_predict_data(annual_inc,dti,revol_util,emp_length_num,grade,purpose,term):
    # Assuming you have individual variables

    # Grade label
    grade_label = 1 if grade in ['C', 'D', 'E', 'F', 'G'] else 0
    # Purpose label
    purpose_label = 1 if purpose in ['small_business', 'other', 'moving', 'vacation', 'major_purchase', 'medical',
                                   'wedding', 'debt_consolidation'] else 0
    # Term label
    term_label = 1 if term in [' 60 months'] else 0
    # Emp length num label
    emp_length_num_label = 1 if emp_length_num in [0, 1, 2, 10] else 0
    # Annual income label
    annual_inc_lte_60000 = 1 if annual_inc <= 60000 else 0
    # Short emp label
    # short_emp_eq_1 = 1 if short_emp == 1 else 0
    # DTI label
    dti_gte_18 = 1 if dti >= 18 else 0
    # Revol util label
    revol_util_gt_60 = 1 if revol_util > 60 else 0
    return annual_inc_lte_60000,dti_gte_18,revol_util_gt_60,emp_length_num_label,grade_label,purpose_label,term_label

def assign_color(predicted_score, threshold_low, threshold_high):

    if threshold_low < predicted_score <= threshold_high:
        return "yellow"
    elif predicted_score >= threshold_high:
        return "red"
    else:
        return "green"




# Handle the form submission
@app.route('/predict', methods=['GET','POST'])
@login_required
def predict():
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
            annual_inc_lte_60000,dti_gte_18,revol_util_gt_60,emp_length_num_label,grade_label,purpose_label,term_label = generate_predict_data(annual_inc,dti,revol_util,emp_length_num,grade,purpose,term)
            # Create a DataFrame with the user input
            user_data = pd.DataFrame({
                'grade_label': [grade_label],
                'purpose_label': [purpose_label],
                'term_label': [term_label],
                'emp_length_num_label': [emp_length_num_label],
                'annual_inc_lte_60000':[annual_inc_lte_60000],
                'dti_gte_18':[dti_gte_18],
                'revol_util_gt_60':[revol_util_gt_60],
                # Include other input variables
            })

            # Use the model to predict
            # print(annual_inc,dti,revol_util,emp_length_num,grade,purpose,term)
            prediction = model.predict(user_data)  # Assuming a binary classification
            # print(prediction[0] )
            # Example usage
            average_score = 20  # Replace this with your average score from the trained model
 
            # Define thresholds based on your criteria
            threshold_low = average_score - 2
            threshold_high = average_score + 2
            predicted_score=prediction[0]*100
            # Assign color based on predicted score
            color = assign_color(predicted_score, threshold_low, threshold_high)
            print(f"Predicted Score: {prediction[0]}, Color: {color}")
 

            # Return the result to the user
            return render_template('predict.html', prediction_result=predicted_score,
                                   annual_inc=annual_inc, dti=dti, revol_util=revol_util,
                                   emp_length_num=emp_length_num, grade=grade, purpose=purpose, term=term,
                                    color=color)
        else:
            # Render the initial prediction form
            return render_template('predict.html')
    except Exception as e:
        raise e
        return render_template('error.html', error_message=str(e))

@app.route('/set_log_level', methods=['POST'])
def set_log_level():
    new_log_level_str = request.form.get('log_level', '').upper()

    # Check if the provided log level is valid
    if new_log_level_str not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        return jsonify({'error': 'Invalid log level'}), 400

    new_log_level = getattr(logging, new_log_level_str, DEFAULT_LOG_LEVEL)

    # Set the log level for the application's logger and file handler
    app.config['LOG_LEVEL'] = new_log_level
    app.logger.setLevel(new_log_level)
    file_handler.setLevel(new_log_level)

    return jsonify({'message': f'Log level set to {new_log_level_str}'}), 200


from celery import Celery

# Create Celery instances
celery_instance_1 = Celery('celery_instance_1')
celery_instance_2 = Celery('celery_instance_2')
celery_instance_3 = Celery('celery_instance_3')

# Function to set log level for a Celery instance
def set_celery_log_level(celery_instance, new_log_level_str):
    new_log_level = getattr(logging, new_log_level_str, DEFAULT_LOG_LEVEL)
    celery_instance.conf['LOG_LEVEL'] = new_log_level
    celery_instance.log.setLevel(new_log_level)

# Define Celery tasks for each instance
@celery_instance_1.task
def example_task_1():
    celery_instance_1.log.debug('This is a debug message from task in instance 1')

@celery_instance_2.task
def example_task_2():
    celery_instance_2.log.debug('This is a debug message from task in instance 2')

@celery_instance_3.task
def example_task_3():
    celery_instance_3.log.debug('This is a debug message from task in instance 3')


# Flask endpoint to set Celery log level dynamically for all instances
@app.route('/set_celery_log_level', methods=['POST'])
def set_celery_log_level():
    new_log_level_str = request.form.get('log_level', '').upper()

    # Check if the provided log level is valid
    if new_log_level_str not in ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']:
        return jsonify({'error': 'Invalid log level'}), 400

    # Set the log level for each Celery instance
    set_celery_log_level(celery_instance_1, new_log_level_str)
    set_celery_log_level(celery_instance_2, new_log_level_str)
    set_celery_log_level(celery_instance_3, new_log_level_str)

    return jsonify({'message': f'Celery log level set to {new_log_level_str} for all instances'}), 200

@app.route('/testapi', methods=['POST','GET'])
def testapi():
    if request.method == 'POST':
        print(request.json)
        return {"msg":"hi"}
    return render_template('test1.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000,debug=True)
