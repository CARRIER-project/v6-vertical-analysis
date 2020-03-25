#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TODO: Maybe more description what happens in this script.

Read healthcare cost data from vektis
https://www.vektis.nl/intelligence/open-data
Please read the data description before using the data.
"""

import ntpath
from collections import Counter
import yaml
import pyreadstat
import pandas as pd
import func
import redacted_logging as rlog


def load_yaml_file(file_name, logger):
    """loads a yaml file, logs to logger if errors occur

    Args:
        file_name (str): File name of the YAML file to be loaded.
        logger (logging.Logger): Logger class handling log messages.

    Returns:
        dict: yaml file content as a dictionary.
    """
    try:
        with open(file_name) as file:
            input_yaml = yaml.load(file, Loader=yaml.FullLoader)
            logger.debug("Reading request.yaml file...")
    except yaml.parser.ParserError:
        logger.error(f"File {file} is not valid YAML.")
        raise
    except FileNotFoundError:
        logger.error(f"Trying to read file '{file}', but it does not exist.")
        raise

    return input_yaml


def get_data_from_file(file_path, file_sep, logger):
    """Read data from a '.csv' file, or load it from a '.sav' file.

    Args:
        file_path (str): Path of the data file.
        file_sep (str): Separator for the '.csv' file.
        logger (logging.Logger): Logger class handling log messages.

    Raises:
        FileNotFoundError: If the data file can not be found.

    Returns:
        pandas.core.frame.DataFrame: Data in a data frame.
    """
    try:
        if '.csv' in file_path:
            data_frame = pd.read_csv(file_path, sep=file_sep)
        elif '.sav' in file_path:
            data_frame, _ = pyreadstat.read_sav(file_path)
    except FileNotFoundError:
        logger.error("The data file does not exist!")
        raise

    return data_frame


def main():
    """main function

    [TODO:description]
    """
    logger = rlog.get_logger(__name__)
    input_yaml_file_name = "/inputVolume/request.yaml"
    input_yaml = load_yaml_file(input_yaml_file_name, logger)

    # Read data path and delimiter from configuration file
    try:
        file_path = input_yaml['data_file']
        file_sep = input_yaml['delimiter']
        selected_features = input_yaml['selected_features']
        excluded_features = input_yaml['excluded_features']
    except KeyError:
        logger.error("YAML file not valid. Please consult the example " +
                     "'request.yaml' file and edit in your settings.")

    # Read data (csv or sav)
    file_name = ntpath.basename(file_path).split('.')[0]

    data_frame = get_data_from_file(file_path, file_sep, logger)

    # Select features you are interested in
    if selected_features in ("all", "All", "ALL"):
        for excluded_feature in excluded_features:
            try:
                data_frame = data_frame.drop(excluded_feature, axis=1)
            except KeyError:
                logger.warning(f"Excluded feature '{excluded_feature}' not" +
                               "found in the data.")
        column_names = data_frame.columns
    else:
        column_names = selected_features

    # Check missing values in the dataset
    if input_yaml['check_missing']:
        func.check_missing(data_frame, column_names, file_name)

    # Get the basic description about the dataset
    if input_yaml['data_description']:
        func.data_describe(data_frame, column_names, file_name)

    # Function for correlation matrix
    if input_yaml['correlation_matrix']:
        func.corr_Matrix(data_frame[column_names], file_name)

    # Separate features to numerical and categorical
    numerical_features = []
    categorical_features = []
    for column_item in column_names:
        if len(Counter(data_frame[column_item].dropna())) > 20:
            numerical_features.append(column_item)
        else:
            categorical_features.append(column_item)

    # Function for distribution plot
    if input_yaml['distribution_plot']:
        if input_yaml['distribution_feature'] == 'ALL':
            for numerical_feature in numerical_features:
                try:
                    func.dist_Plot(data_frame[numerical_features],
                                   numerical_feature, file_name)
                except ???:  # TODO: what error is this
                    if numerical_feature not in categorical_features:
                        logger.error(numerical_feature, " -- Data type " +
                                     "does not support numerical " +
                                     "distribution plot")

            for categorical_feature in categorical_features:
                try:
                    func.cate_Dist(data_frame[categorical_features],
                                   categorical_feature, file_name)
                except ???:  # TODO: what error is this
                    if categorical_feature not in numerical_features:
                        logger.error(categorical_feature, " -- Data type " +
                                     "does not support categorical " +
                                     "distribution plot")

        else:
            for distribution_feature in input_yaml['distribution_feature']:
                if distribution_feature in numerical_features:
                    try:
                        func.dist_Plot(data_frame[numerical_features],
                                       distribution_feature, file_name)
                    except ???:  # TODO: what error is this
                        logger.error(distribution_feature, " -- Data type " +
                                     "does not support numerical " +
                                     "distribution plot")

                elif distribution_feature in categorical_features:
                    try:
                        func.cate_Dist(data_frame[categorical_features],
                                       distribution_feature, file_name)
                    except ???:  # TODO: what error is this
                        logger.error(distribution_feature, " -- Data type " +
                                     "does not support categorical " +
                                     "distribution plot")

    # Function for Cat-Num plot
    if input_yaml["Cat_Num_plot"] and input_yaml["Cat_Num_feature"]:
        # print(input_yaml['Cat_Num_feature'])
        # TODO: Logging instead of print? Or leave out completely?
        for categorical_numerical_feature in input_yaml['Cat_Num_feature']:
            func.plot_catNum(data_frame, categorical_numerical_feature,
                             file_name, categorical_features)

    # Function for Box plot
    # TODO: Can these go wrong? Do we need try except?
    if input_yaml["Box_plot"] and input_yaml["Box_plot_feature"]:
        for box_plot_feature in input_yaml['Box_plot_feature']:
            func.box_Plot(data_frame, box_plot_feature,
                          file_name, categorical_features)

    # Function for Num-Num plot
    # TODO: Can these go wrong? Do we need try except?
    if input_yaml["Num_Num_Plot"] and input_yaml["Num_Num_feature"]:
        for numerical_numerical_feature in input_yaml['Num_Num_feature']:
            func.plot_numNum(data_frame, numerical_numerical_feature,
                             file_name, categorical_features)


if __name__ == "__main__":
    main()
