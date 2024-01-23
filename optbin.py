from optbinning import BinningProcess
from sklearn.linear_model import LogisticRegression
from optbinning import Scorecard
from sklearn.model_selection import train_test_split
import statsmodels.formula.api as smf
import numpy as np
import pandas as pd
from sklearn.metrics import confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import joblib
import os

def parse_interval(interval_str):
    interval_str = interval_str.replace('(', '').replace(')', '').replace('[', '').replace(']', '')
    start, end = map(float, interval_str.split(','))
    return [start, end]


def generate_selected_features(selected_features, selected_features_bin):
    selected_features_and_bin_data_list = []
    for i, data in selected_features.iterrows():
        selected_features_and_bin_data = {}
        column_name = data['name']
        column_type = data['dtype']
        temp_df = selected_features_bin[selected_features_bin['Variable'] == column_name]
        selected_features_and_bin_data['name'] = column_name
        selected_features_and_bin_data['type'] = column_type
        if column_type == 'categorical':
            selected_bin_values = np.concatenate(temp_df['Bin'].values)
            selected_features_and_bin_data['criteria'] = list(selected_bin_values)
        if column_type == 'numerical':
            # temp_df['Bin']
            # Apply the function to the 'interval_column' and create a new column 'interval_list'
            temp_df['Bin_list'] = temp_df['Bin'].apply(parse_interval)
            # Convert the 'interval_list' column into a single flat list
            flat_list = [item for sublist in temp_df['Bin_list'] for item in sublist]
            data_range = [min(flat_list), max(flat_list)]
            selected_features_and_bin_data['criteria'] = data_range

        selected_features_and_bin_data_list.append(selected_features_and_bin_data)
    return selected_features_and_bin_data_list

def format_criteria_for_ui(selected_features_details_list):
    for lv in selected_features_details_list:
        column_name = lv['name']
        column_type = lv['type']
        criteria = lv['criteria']
        if column_type == 'categorical':
            lv['Impact Criteria'] = ','.join(criteria)
            format_list = criteria
        if column_type == 'numerical':
            if np.inf in criteria:
                string_value = 'greater than '+str( criteria[0])
                format_list = [ criteria[0],'Above' ]
            elif -np.inf in criteria:
                string_value = 'lesser than ' + str(criteria[1])
                format_list = [ 'Below',criteria[1]]
            else:
                string_value = 'between '+str(criteria[0]) +' to '+ str(criteria[1])
            lv['Impact Criteria']=string_value
            lv['criteria'] = format_list
        # del lv['criteria']
    return selected_features_details_list

def do_manual_optimal_binning(selected_features_and_bin_data_list, model_input_data):
    for lv in selected_features_and_bin_data_list:
        column_name = lv['name']
        column_type = lv['type']
        criteria = lv['criteria']
        if column_type == 'categorical':
            model_input_data[column_name] = [1 if x in criteria else 0 for x in model_input_data[column_name]]
        if column_type == 'numerical':
            if np.inf in criteria:
                model_input_data[column_name] = [1 if x >= criteria[0] else 0 for x in
                                                 model_input_data[column_name]]
            elif -np.inf in criteria:
                model_input_data[column_name] = [1 if x <= criteria[1] else 0 for x in
                                                 model_input_data[column_name]]
            else:
                model_input_data[column_name] = [1 if x>=criteria[0] and  x<=criteria[1] else 0 for x in
                                                 model_input_data[column_name]]
    return model_input_data

def performance_metrics(log_reg,X_test,y_test):
    y_pred = log_reg.predict(X_test)
    y_pred_binary = (y_pred >= 0.5).astype(int)
    # Compute confusion matrix
    cm = confusion_matrix(y_test, y_pred_binary)

    TN = cm[0][0]
    TP = cm[1][1]
    FP = cm[0][1]
    FN = cm[1][0]
    # print('TRUE Negative', TN)
    # print('TRUE Positive', TP)
    # print('False Positive', FP)
    # print('False Negative', FN)

    accuracy = (TP + TN) / (TP + TN + FP + FN)  # = (4 + 3200) / (4 + 3200 + 10 + 786) #≈ 0.8002
    # print("Accuracy:", accuracy)
    precision = TP / (TP + FP)  # = 4 / (4 + 10) #≈ 0.2857
    # print("Precision:", precision)
    recall = TP / (TP + FN)  # = 4 / (4 + 786) #≈ 0.0051
    # print("Recall (Sensitivity):", recall)
    f1_score = 2 * (precision * recall) / (precision + recall)  # = 2 * (0.2857 * 0.0051) / (0.2857 + 0.0051) ≈ 0.0101
    # print("F1 Score:", f1_score)
    y_pred_list = y_pred.tolist()

    # Calculate standard deviation
    std_dev = np.std(y_pred_list)

    low_risk_threshold = np.mean(y_pred_list) - 0.5 * std_dev
    high_risk_threshold = np.mean(y_pred_list) + 0.5 * std_dev

    performance_metrics_dict = {
        "accuracy":accuracy,
        "precision":precision,
        "recall":recall,
        "f1_score":f1_score,
        "cm":cm,
        "low_risk_threshold":low_risk_threshold,
        "high_risk_threshold":high_risk_threshold,
        "std_dev":std_dev
    }
    # Display confusion matrix using seaborn
    # plt.figure(figsize=(8, 6))
    # sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Predicted 0', 'Predicted 1'],
    #             yticklabels=['Actual 0', 'Actual 1'])
    # plt.xlabel('Predicted Label')
    # plt.ylabel('True Label')
    # plt.title('Confusion Matrix')
    # plt.show()std_dev
    return performance_metrics_dict

def process_train_data(traindf, target_column):
    # target_column = 'bad_loan'
    threshold = {"Total Records": len(traindf[target_column]),
                 "Target Count": len(traindf[traindf[target_column] == 1]),
                 "Risk Average": (len(traindf[traindf[target_column] == 1]) / len(traindf)),
                 "Risk Percentage": (len(traindf[traindf[target_column] == 1]) / len(traindf)) * 100
                 }

    # print(threshold)

    variable_names = list(traindf.columns[1:])
    X = traindf[variable_names]
    target = "bad_loan"
    y = traindf[target].values

    selection_criteria = {
        "iv": {"min": 0.01, "max": 1},
        "quality_score": {"min": 0.01},
        #     'Event rate':{"min":0.20}
    }
    binning_process = BinningProcess(variable_names,
                                     selection_criteria=selection_criteria)

    estimator = LogisticRegression(solver="lbfgs")

    scorecard = Scorecard(binning_process=binning_process,
                          estimator=estimator, scaling_method="min_max",
                          scaling_method_params={"min": 300, "max": 850})

    # fit
    binning_process.fit(traindf[variable_names], y)

    # feature details
    feature_details = binning_process.summary()
    # print(feature_details)
    # scorecard fit
    scorecard.fit(X, y, show_digits=4)

    # scorecard df
    scoredf = scorecard.table(style="detailed")
    # print(scoredf)
    # selected_features_bin = scoredf[(scoredf['Event rate']>=0.20) & (scoredf['IV']>0.01)]
    selected_features_bin = scoredf[(scoredf['Event rate'] >= threshold['Risk Average']) & (scoredf['WoE'] <= -0.20)]
    # print(selected_features_bin)

    selected_features = feature_details[feature_details['selected'] == True]
    # print(selected_features)

    selected_features_names = selected_features['name'].unique()

    selected_features_and_bin_data_list = generate_selected_features(selected_features, selected_features_bin)
    selected_features_names_with_target = np.append(selected_features_names, target)

    model_input_data = traindf[selected_features_names_with_target].copy()

    model_input_data = do_manual_optimal_binning(selected_features_and_bin_data_list, model_input_data)

    features_string = '+'.join(selected_features_names)

    # train_data, test_data = train_test_split(model_input_data, test_size=0.2, random_state=42)
    features = model_input_data.drop(target,
                                     axis=1)  # Adjust 'target_variable_name' to your actual target variable
    labels = model_input_data[target]

    # Split the dataset into training and testing sets (80% train, 20% test)
    X_train, X_test, y_train, y_test = train_test_split(features, labels, test_size=0.2, random_state=42)

    # model_train_data
    ipdata = X_train.copy()
    ipdata[target] = y_train
    ipdata = ipdata.dropna()

    logit_str = target + " ~ " + features_string


    log_reg = smf.logit(logit_str, data=ipdata).fit()
    performance_metrics_dict = performance_metrics(log_reg, X_test, y_test)
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    model_filename = f'model_{timestamp}.joblib'
    model_full_path = os.path.join('static', 'trained_model', model_filename)

    joblib.dump(log_reg, model_full_path)
    return (logit_str, log_reg, threshold, selected_features_names_with_target,selected_features_and_bin_data_list,
            performance_metrics_dict,model_full_path)

def get_model_file(model_path):
    return joblib.load(model_path)
def predict_score(json_data,selectedcriteria,model_full_path):
    input_dict ={}
    # print(json_data)
    for rj in selectedcriteria:
        cname= rj['name']
        ctype = rj['type']
        if ctype == 'numerical':
            input_dict[cname] = float(json_data[cname])
        else:
            input_dict[cname] = json_data[cname]

    input_df = pd.DataFrame([input_dict])
    for iv in selectedcriteria:
        if 'Above' in  iv['criteria']:
            updated_list = [np.inf if item == 'Above' else item for item in iv['criteria']]
            iv['criteria'] = updated_list
        elif 'Below' in iv['criteria']:
            updated_list = [-np.inf if item == 'Below' else item for item in iv['criteria']]
            iv['criteria']=updated_list
    # print(selectedcriteria)
    model_input_data = do_manual_optimal_binning(selectedcriteria, input_df)
    risk_model = get_model_file(model_full_path)
    Result = pd.DataFrame(risk_model.predict(model_input_data))
    score=Result[0][0]
    # print('predicted_score=prediction[0]*100',score)

    low_risk_threshold=json_data['low_risk_threshold']
    high_risk_threshold= json_data['high_risk_threshold']


    # Assign risk categories
    risk_cat = 'Green' if score < float(low_risk_threshold) else 'Yellow' if float(low_risk_threshold) <= score <= float(high_risk_threshold) else 'Red'
    score_percentage = score*100
    return score_percentage, risk_cat





