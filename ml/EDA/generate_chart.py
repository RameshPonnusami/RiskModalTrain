import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import seaborn as sns
from ml.utils.common_ops import get_save_path, get_relative_path
from typing import Tuple, List, Dict, Any


def identify_data_types(df: pd.DataFrame) -> Tuple[List[str], List[str]]:
    # Selecting categorical columns
    categorical_columns = df.select_dtypes(include='object').columns.tolist()

    # Selecting numeric columns
    numeric_columns = df.select_dtypes(include=['int', 'float']).columns.tolist()

    return categorical_columns, numeric_columns


def plot_bar_chart(findf: pd.DataFrame, bin_column_name: str, target_percentage: str, target_label: str,
                   save_path: str) -> None:
    #     print('findf',findf)
    unique_values_count = len(findf[bin_column_name].unique())
    unique_values_count += 10
    # Adjust figure size based on the number of unique values
    figsize = (min(24, unique_values_count), 8)
    plt.figure(figsize=figsize)
    plt.ylabel(target_label)
    plt.xlabel(bin_column_name)
    plt.title(bin_column_name)
    bars = plt.bar(findf[bin_column_name].astype(str), findf[target_percentage], width=0.8)
    # Add values as text labels on each bar
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, yval, round(yval, 2), ha='center', va='bottom')
    plt.tight_layout()
    #     plt.xticks( findf[bin_column_name], findf.index.values ) # location, labels
    # Save the chart as an image with increased bottom margin

    plt.savefig(save_path, bbox_inches='tight', pad_inches=0.1)
    # plt.show()
    plt.close()


def plot_diagram(column_name: str, npa_df: pd.DataFrame, target: str, fig_size: Any = None) -> Tuple[str, pd.DataFrame]:
    mean_column_name = column_name + 'mean'

    # print(column_name)

    LapsUpdated = pd.DataFrame()

    target_sum = target + 'sum'
    target_count = target + 'count'
    target_percentage = target + '_Percentage'
    target_label = target + ' Percentage'

    bin_column_name = column_name + ''
    mean_bin_column_name = bin_column_name + 'mean'
    LapsUpdated[bin_column_name] = npa_df[column_name]

    LapsUpdated[target] = npa_df[target]
    FinalDataFrame = LapsUpdated.groupby(bin_column_name).agg({target: ['sum', 'count']})
    FinalDataFrame.columns = ["".join(j) for j in list(FinalDataFrame.columns)]
    FinalDataFrame.reset_index(inplace=True)

    FinalDataFrame[target_percentage] = FinalDataFrame[target_sum] / FinalDataFrame[target_count] * 100
    FinalDataFrame.sort_values(by=[target_percentage], ascending=False, inplace=True)
    FinalDataFrame.rename(columns={target_sum: target + ' total', target_count: 'Total Records'}, inplace=True)

    # display(FinalDataFrame)
    save_path = get_save_path(bin_column_name + '.png')
    # save_path = 'charts/' + bin_column_name + '.png'
    plot_bar_chart(FinalDataFrame, bin_column_name, target_percentage, target_label, save_path)
    save_path = get_relative_path(save_path)
    return save_path, FinalDataFrame


def plot_regression_decile(column: str, final_df: pd.DataFrame, target: str, additional_columns: List[str] = []) -> \
Tuple[str, pd.DataFrame]:
    tar_percentage = "Percentage_" + target
    label_plot = 'Percentage_of_' + target
    target_mean = target + 'mean'
    target_sum = target + 'sum'
    target_count = target + 'count'
    column_mean = column + 'mean'

    agg_condition = {target: ['sum', 'count'], column: ['min', 'max', 'mean']}

    for acl in additional_columns:
        agg_condition[acl] = ['sum', 'count']

    ContinousData = final_df
    GrandTotal_non_zero = ContinousData[ContinousData[column] != 0]
    GrandTotal_non_zero = GrandTotal_non_zero.sort_values(by=[column], ascending=False)
    GrandTotal_non_zero['Decile_rank'] = pd.qcut(GrandTotal_non_zero[column].rank(method='first'), 10, labels=False)
    # print("Unique Values {}".format(len(set(GrandTotal_non_zero[column].values))))
    Records, Columns = GrandTotal_non_zero.shape
    FinalDataFrame = GrandTotal_non_zero.groupby("Decile_rank").agg(agg_condition)
    FinalDataFrame.columns = ["".join(j) for j in list(FinalDataFrame.columns)]
    FinalDataFrame.reset_index(inplace=True)
    FinalDataFrame[tar_percentage] = FinalDataFrame[target_sum] / FinalDataFrame[target_count] * 100

    GrandTotal_zero = ContinousData[ContinousData[column] == 0]
    GrandTotal_zero = GrandTotal_zero.sort_values(by=[column], ascending=False)
    GrandTotal_zero['Decile_rank'] = 10
    Records, Columns = GrandTotal_zero.shape
    FinalDataFrame2 = GrandTotal_zero.groupby("Decile_rank").agg(agg_condition)
    FinalDataFrame2.columns = ["".join(j) for j in list(FinalDataFrame2.columns)]
    FinalDataFrame2.reset_index(inplace=True)
    FinalDataFrame2[tar_percentage] = FinalDataFrame2[target_sum] / FinalDataFrame2[target_count] * 100

    FinalDataFrame = pd.concat([FinalDataFrame, FinalDataFrame2], axis=0)
    FinalDataFrame.sort_values(by=[column_mean], ascending=False, inplace=True)

    FinalDataFrame[column_mean].fillna(0, inplace=True)
    FinalDataFrame[column_mean] = FinalDataFrame[column_mean].astype(np.float128)

    FinalDataFrame[tar_percentage] = FinalDataFrame[tar_percentage].astype(np.float128)
    #     FinalDataFrame.sort_values(by=[tar_percentage],ascending=False,inplace=True)

    for acl in additional_columns:
        ad_per = "Percentage_" + acl
        ad_sum = acl + 'sum'
        ad_count = acl + 'count'
        FinalDataFrame[ad_per] = FinalDataFrame[ad_sum] / FinalDataFrame[ad_count] * 100
        FinalDataFrame[ad_per] = FinalDataFrame[ad_per].astype(np.float128)

    FinalDataFrame.rename(columns={target_sum: target + ' total', target_count: 'Total Records'}, inplace=True)
    FinalDataFrame.sort_values(by=[tar_percentage], ascending=False, inplace=True)
    reg = LinearRegression()
    reg.fit(FinalDataFrame[[column_mean]], FinalDataFrame[tar_percentage])
    reg.predict(FinalDataFrame[[column_mean]])
    # print("Co-effictient {}".format(reg.coef_))
    # print("Intercept {}".format(reg.intercept_))
    plt.title(column)
    plt.xlabel(column_mean)
    # display(FinalDataFrame)
    plt.ylabel(label_plot)
    plt.scatter(FinalDataFrame[[column_mean]], FinalDataFrame[tar_percentage], color="red", marker="+")
    plt.plot(FinalDataFrame[[column_mean]], reg.predict(FinalDataFrame[[column_mean]]), color='blue')
    # save_path = 'charts/' + column_mean + '.png'
    save_path = get_save_path(column_mean + '.png')
    plt.savefig(save_path, bbox_inches='tight', pad_inches=0.1)
    # plt.show()
    plt.close()
    save_path = get_relative_path(save_path)
    # print('-------------------------------------------------------------------------------------------------------')
    return save_path, FinalDataFrame


def process_charts(df: pd.DataFrame, target_column: str) -> Dict[str, List[Dict[str, Any]]]:
    categorical_columns, numeric_columns = identify_data_types(df)

    bar_chart_details_list = []
    bar_chart_path_list = []
    for cl in categorical_columns:
        #     figsize=(24,8) if cl=='purpose' else None
        if cl not in ['id', target_column]:
            save_path, FinalDataFrame = plot_diagram(cl, df, target=target_column, fig_size=None)
            chart_details = {}
            chart_details['feature'] = cl
            chart_details['chart_path'] = save_path
            chart_details['table_data'] = FinalDataFrame.to_dict("records")
            bar_chart_details_list.append(chart_details)
            bar_chart_path_list.append(save_path)

    failed_columns = []
    line_chart_details_list = []
    line_chart_path_list = []
    all_continous_list = []
    for ac in df.columns:
        if ac not in categorical_columns and ac not in ['id', target_column]:
            try:
                save_path, FinalDataFrame = plot_regression_decile(ac, df, target=target_column)
                chart_details = {}
                chart_details['feature'] = ac
                chart_details['chart_path'] = save_path
                chart_details['table_data'] = FinalDataFrame.to_dict("records")
                line_chart_details_list.append(chart_details)
                line_chart_path_list.append(save_path)
                all_continous_list.append(ac)
            except Exception as e:
                print(e)
                # raise e
                failed_columns.append(ac)
                pass

    all_chart_details = {}
    all_chart_details['line_chart'] = line_chart_details_list
    all_chart_details['bar_chart'] = bar_chart_details_list
    all_chart_details['failed_features'] = failed_columns
    return all_chart_details


def change_type_to_int(base_df: pd.DataFrame) -> pd.DataFrame:
    cls = ['balance probability min',
           'balance probability max',
           'balance probability mean',
           'balance min',
           'balance max',
           'balance mean']
    for cl in cls:
        base_df[cl] = base_df[cl].astype(int)
    return base_df


def format_the_column(ip_df: pd.DataFrame) -> pd.DataFrame:
    f_columns = []
    for ip in ip_df.columns:
        v = ip.replace('-', '').replace(' ', '').replace('(', '').replace(')', '').replace('/', '_').replace('%',
                                                                                                             ')'
                                                                                                             ).replace(
            '_ ', '').replace('.', '_')
        v = v.replace('min', ' min').replace('max', ' max').replace('mean', ' mean').replace('PredictionProbability',
                                                                                             'Prediction Probability')
        f_columns.append(v)
    return ip_df.rename(columns={ip: v for ip, v in zip(ip_df.columns, f_columns)})


def round_df_value(FinalDataFrame: pd.DataFrame) -> pd.DataFrame:
    for cl in list(FinalDataFrame.columns):
        try:
            if FinalDataFrame[cl].dtype == 'float64':
                FinalDataFrame[cl] = FinalDataFrame[cl].round(2)
        except:
            pass
    return FinalDataFrame


def plot_test_decile(rawdata: pd.DataFrame, selected_columns: List[str], target_column: str, orderby_field: str = 'PredictionProbability') -> Tuple[str, pd.DataFrame]:
    orderby_feild_mean = orderby_field + 'mean'
    target_cl = target_column
    target_mean = target_cl + 'mean'
    condition_dict = {target_cl: ['sum', 'count', 'mean'], 'PredictionProbability': ['min', 'max', 'mean']
                      }
    for sc in selected_columns:
        if sc not in [target_cl]:
            condition_dict[sc] = ['mean']
    GrandTotal = rawdata.sort_values(by=[orderby_field], ascending=False)
    GrandTotal['Decile_rank'] = pd.qcut(GrandTotal[orderby_field].rank(method='first'), 10, labels=False)
    FinalDataFrame = GrandTotal.groupby("Decile_rank").agg(condition_dict)
    FinalDataFrame.columns = ["".join(j) for j in list(FinalDataFrame.columns)]
    FinalDataFrame.reset_index(inplace=True)
    # print (FinalDataFrame.columns)
    # FinalDataFrame["Percentage"]=FinalDataFrame["StarLabelsum"]/FinalDataFrame["StarLabelcount"]*100
    FinalDataFrame[target_mean] = FinalDataFrame[target_mean] * 100
    FinalDataFrame.sort_values(by=[orderby_feild_mean], ascending=False, inplace=True)

    reg = LinearRegression()
    reg.fit(FinalDataFrame[["PredictionProbabilitymean"]], FinalDataFrame[target_mean])
    reg.predict(FinalDataFrame[["PredictionProbabilitymean"]])
    plt.title("PredictionProbability")
    plt.xlabel("PredictionProbabilitymean")
    plt.ylabel(target_mean)

    plt.scatter(FinalDataFrame[["PredictionProbabilitymean"]], FinalDataFrame[target_mean], color="red", marker="+")
    plt.plot(FinalDataFrame[["PredictionProbabilitymean"]], reg.predict(FinalDataFrame[["PredictionProbabilitymean"]]),
             color='blue')
    save_path = get_save_path(str(target_mean) + '.png')
    plt.savefig(save_path, bbox_inches='tight', pad_inches=0.1)
    # FinalDataFrame.columns=total_mean_list
    FinalDataFrame_ = format_the_column(FinalDataFrame.copy())
    # FinalDataFrame = change_type_to_int (FinalDataFrame_)
    plt.close()
    FinalDataFrame_ = round_df_value(FinalDataFrame_)
    save_path = get_relative_path(save_path)
    return save_path, FinalDataFrame_


def get_corr(df: pd.DataFrame) -> pd.DataFrame:
    numeric_columns = df.select_dtypes(include='number').columns
    categorical_columns = df.select_dtypes(exclude='number').columns
    df.fillna(0, inplace=True)
    # Encode categorical variables (convert them to numerical values)
    df_encoded = pd.get_dummies(df, columns=categorical_columns)
    # Calculate the correlation matrix
    corr_matrix = df_encoded.corr()
    return corr_matrix


def plot_heat_map(cm_df: pd.DataFrame) -> str:
    plt.figure(figsize=(5, 4))
    sns.heatmap(cm_df, annot=True)
    plt.title('Correlation')
    save_path = get_save_path(str('correlation') + '.png', addtime=True)
    plt.savefig(save_path, bbox_inches='tight', pad_inches=0.1)
    plt.close()
    save_path = get_relative_path(save_path)
    return save_path
