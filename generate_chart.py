import matplotlib.pyplot as plt
import pandas as pd
from sklearn.linear_model import LinearRegression
import os
import numpy as np


def identify_data_types(df):
    # Selecting categorical columns
    categorical_columns = df.select_dtypes(include='object').columns.tolist()

    # Selecting numeric columns
    numeric_columns = df.select_dtypes(include=['int', 'float']).columns.tolist()

    return categorical_columns, numeric_columns


def get_save_path(filename):
    file_full_path = os.path.join('static', 'charts', filename)
    return file_full_path


def plot_bar_chart(findf, bin_column_name, target_percentage, target_label, save_path):
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


def plot_diagram(column_name, npa_df, target, fig_size=None):
    mean_column_name = column_name + 'mean'

    print(column_name)

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
    return save_path, FinalDataFrame

    #     if fig_size:
    #         plt.figure(figsize=fig_size)
    #     plt.ylabel(target_label)
    #     plt.xlabel(bin_column_name)
    #     plt.title(bin_column_name)
    #     plt.bar(FinalDataFrame[bin_column_name].astype(str),FinalDataFrame[target_percentage],width=0.8)
    #     plt.show()
    # print('-----------------------------------------------------------------------------------------------------')


def plot_regression_decile(column, final_df, target, additional_columns=[]):
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
    # print('-------------------------------------------------------------------------------------------------------')
    return save_path, FinalDataFrame


def process_charts(df, target_column):
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
                chart_details['feature'] = cl
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
