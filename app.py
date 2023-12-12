from flask import Flask, render_template, request, jsonify, redirect, url_for
import joblib
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from io import BytesIO
import base64
from flask import session
from functools import wraps

app = Flask(__name__)

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

if __name__ == '__main__':
    app.run(debug=True)
