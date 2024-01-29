from optbinning import BinningProcess
from sklearn.linear_model import LogisticRegression
from optbinning import Scorecard
import pandas as pd
from typing import List, Tuple, Dict

from ml.utils.common_ops import identify_categorical_column_by_size


def process_bin_sequence_for_feature(features_bin: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Find continuous sequences of active rows
    active_sequences = (features_bin['Bin id'] - features_bin['Bin id'].shift(1) != 1).cumsum()
    # Identify isolated rows
    isolated_df = features_bin.groupby(active_sequences).filter(lambda group: len(group) == 1)
    continuous_df = features_bin.drop(isolated_df.index)
    return continuous_df, isolated_df


def ignore_non_impact_selected_feature(selected_features_impact_bin: pd.DataFrame, selected_features: pd.DataFrame) -> pd.DataFrame:
    # filtered the varaibles both exists in bin and features list
    selected_features_impact_bin = selected_features_impact_bin[
        selected_features_impact_bin['Variable'].isin(selected_features['name'])]
    return selected_features_impact_bin


def ignore_singular_matrix_features(scoredf: pd.DataFrame, selected_features_impact_bin: pd.DataFrame, selected_features: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    # Avoid the singular matrix features(No diffrences in row if all has same value then have to remove)
    selected_bins_per_features = selected_features_impact_bin.groupby(selected_features_impact_bin['Variable']).agg(
        {"Bin id": "count"}).reset_index()
    total_bins_per_features = scoredf.groupby(scoredf['Variable']).agg({"Bin id": "count"}).reset_index()
    singular_feature_df = pd.merge(total_bins_per_features, selected_bins_per_features, on=['Variable', 'Bin id'],
                                   how='inner')
    if not singular_feature_df.empty:
        selected_features_impact_bin = selected_features_impact_bin[
            ~selected_features_impact_bin['Variable'].isin(singular_feature_df['Variable'])]

    return selected_features_impact_bin, selected_features


def filter_bins(scoredf: pd.DataFrame, threshold: Dict[str, float], feature_details: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    selected_features_impact_bin = scoredf[
        (scoredf['Event rate'] >= threshold['Risk Average']) & (scoredf['IV'] >= 0.002)]
    selected_features = feature_details[feature_details['selected'] == True]
    processed_bin_df, selected_features = analyze_bin_sequence(selected_features, selected_features_impact_bin)
    selected_features_impact_bin, selected_features = ignore_singular_matrix_features(scoredf, processed_bin_df,
                                                                                      selected_features)
    selected_features_impact_bin = ignore_non_impact_selected_feature(selected_features_impact_bin, selected_features)

    return selected_features_impact_bin, selected_features


def analyze_bin_sequence(selected_features: pd.DataFrame, selected_features_impact_bin: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    processed_bin_df = pd.DataFrame()
    for i, data in selected_features.iterrows():
        column_name = data['name']
        temp_df = selected_features_impact_bin[selected_features_impact_bin['Variable'] == column_name]
        continuous_df, isolated_df = process_bin_sequence_for_feature(temp_df)
        if not continuous_df.empty and not isolated_df.empty:
            processed_bin_df = pd.concat([processed_bin_df, continuous_df], ignore_index=True)
        elif not continuous_df.empty and isolated_df.empty:
            processed_bin_df = pd.concat([processed_bin_df, continuous_df], ignore_index=True)
        else:
            processed_bin_df = pd.concat([processed_bin_df, isolated_df], ignore_index=True)
    return processed_bin_df, selected_features


def process_opt_bin(variable_names: List[str], traindf: pd.DataFrame, threshold: Dict[str, float], target: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    X = traindf[variable_names]

    y = traindf[target].values

    selection_criteria = {
        "iv": {"min": 0.01, "max": 1},
        "quality_score": {"min": 0.01},
        #     'Event rate':{"min":0.20}
    }
    categorical_variables = identify_categorical_column_by_size(traindf)
    binning_process = BinningProcess(variable_names,
                                     categorical_variables=categorical_variables,
                                     selection_criteria=selection_criteria)

    estimator = LogisticRegression(solver="lbfgs")

    scorecard = Scorecard(binning_process=binning_process,
                          estimator=estimator, scaling_method="min_max",
                          scaling_method_params={"min": 300, "max": 850})

    # fit
    binning_process.fit(traindf[variable_names], y)

    # feature details
    feature_details = binning_process.summary()

    scorecard.fit(X, y, show_digits=4)

    # scorecard df
    scoredf = scorecard.table(style="detailed")

    selected_features_bin, selected_features = filter_bins(scoredf, threshold, feature_details)

    return selected_features, selected_features_bin
