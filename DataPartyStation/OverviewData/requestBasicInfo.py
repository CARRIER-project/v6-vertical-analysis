#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script is to generate an (statistical) overview about the data.
Users need to configure the request.yaml to indicate what basic information they want to know about the data.
Until 25-03-2020, the following functions has been implemented in this script:
1. Basic description of data (from pandas.dataframe.desribe)
2. Missing values and percentage of each variables
3. Correlation Matrix (plot)
4. Histogram distributed plot
5. Box distribution plot
6. Relations plot between different variables (numerical-numercial features, categorical-numerical features)

"""

import ntpath
from collections import Counter
import yaml
import pyreadstat
import pandas as pd
import BasicInfo_Subfunctions
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

    The main function will read the configuration file (request.yaml) and obtain the requeired parameters. 
    After reading the data file, the varilables will be selected by users input.
    Execute the functions of generating basic description of data, checking cokpleteness, plotting correlation metrix, distribution plots.
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
        BasicInfo_Subfunctions.check_missing(data_frame, column_names, file_name)

    # Get the basic description about the dataset
    if input_yaml['data_description']:
        BasicInfo_Subfunctions.data_describe(data_frame, column_names, file_name)

    # Function for correlation matrix
    if input_yaml['correlation_matrix']:
        BasicInfo_Subfunctions.corr_Matrix(data_frame[column_names], file_name)

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
                    BasicInfo_Subfunctions.dist_Plot(data_frame[numerical_features],
                                   numerical_feature, file_name)
                except: 
                    if numerical_feature not in categorical_features:
                        logger.error(numerical_feature, " -- Data type " +
                                     "does not support numerical " +
                                     "distribution plot")
                    raise


            for categorical_feature in categorical_features:
                try:
                    BasicInfo_Subfunctions.cate_Dist(data_frame[categorical_features],
                                   categorical_feature, file_name)
                except:
                    if categorical_feature not in numerical_features:
                        logger.error(categorical_feature, " -- Data type " +
                                     "does not support categorical " +
                                     "distribution plot")
                    raise

        else:
            for distribution_feature in input_yaml['distribution_feature']:
                if distribution_feature in numerical_features:
                    try:
                        BasicInfo_Subfunctions.dist_Plot(data_frame[numerical_features],
                                       distribution_feature, file_name)
                    except:
                        logger.error(distribution_feature, " -- Data type " +
                                     "does not support numerical " +
                                     "distribution plot")
                        raise

                elif distribution_feature in categorical_features:
                    try:
                        BasicInfo_Subfunctions.cate_Dist(data_frame[categorical_features],
                                       distribution_feature, file_name)
                    except:
                        logger.error(distribution_feature, " -- Data type " +
                                     "does not support categorical " +
                                     "distribution plot")
                        raise

    # Function for Cat-Num plot
    if input_yaml["Cat_Num_plot"] and input_yaml["Cat_Num_feature"]:
        for categorical_numerical_feature in input_yaml['Cat_Num_feature']:
            BasicInfo_Subfunctions.plot_catNum(data_frame, categorical_numerical_feature,
                             file_name, categorical_features)

    # Function for Box plot
    if input_yaml["Box_plot"] and input_yaml["Box_plot_feature"]:
        for box_plot_feature in input_yaml['Box_plot_feature']:
            try:
                BasicInfo_Subfunctions.box_Plot(data_frame, box_plot_feature,
                            file_name, categorical_features)
            except: ############
                logger.error(box_plot_feature, " -- Data type " +
                                     "does not support categorical " +
                                     "distribution plot")
                raise

    # Function for Num-Num plot
    if input_yaml["Num_Num_Plot"] and input_yaml["Num_Num_feature"]:
        for numerical_numerical_feature in input_yaml['Num_Num_feature']:
            try:
                BasicInfo_Subfunctions.plot_numNum(data_frame, numerical_numerical_feature,
                                file_name, categorical_features)
            except:############
                logger.error(box_plot_feature, " -- Data type " +
                                     "does not support categorical " +
                                     "distribution plot")
                raise


if __name__ == "__main__":
    main()
