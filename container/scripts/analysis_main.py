#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script is to analyze the combined dataset from all parties.
Until 25-03-2020, the analysis process includes:
1. Overview of combined data
2. Check if the model parameters are valid
3. customize features (remove missing values, normalization)
4. Train the analysis model (regression or classification)
"""


########## Simple Linear Regression ##########
import os
import time
import sys, yaml
import numpy as np
import pandas as pd
from collections import Counter
from scripts import analysis_subfunctions
from sklearn.model_selection import cross_validate
import redacted_logging as rlog

import warnings
warnings.filterwarnings('ignore')


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
            inputYAML = yaml.load(file, Loader=yaml.FullLoader)
            logger.debug("Reading analysis_input.yaml file...")
    except yaml.parser.ParserError:
        logger.error(f"File {file} is not valid YAML.")
        raise
    except FileNotFoundError:
        logger.error(f"Trying to read file '{file}', but it does not exist.")
        raise

    return inputYAML


def select_features(data_frame, selected_variables, excluded_variables, logger):
    """ generated a new DataFrame only including selected features

    Args:
        data_frame (Pandas.DataFrame): the original dataframe
        selected_variables (str/list): a list of features will be trained in the model. "all" will include all features.
        excluded_variables (boolean/list): a list of features will be excluded in the model. "False" no features will be excluded.
        logger (logging.Logger): Logger class handling log messages.

    Raises:
        KeyError: If selected/excluded features are not in the dataframe

    Returns:
        selected_data_frame (Pandas.DataFrame): a new DataFrame only including the selected features
        selected_columns (list): a list of names of selected features
    """

    ### For checking data types ###
    if type(selected_variables) == str:
        if selected_variables.lower() == "all":
            selected_data_frame = data_frame
            if excluded_variables:
                try:
                    selected_data_frame = selected_data_frame.drop(excluded_variables, axis=1)
                except KeyError:
                    logger.error(f"One or more excluded features '{excluded_variables}' are not" +
                                "found in the data.")
            selected_columns = list(selected_data_frame.columns)
        else:
            logger.debug("Please input 'all' or a list of feature names! ")

    else:
        try:
            selected_data_frame = data_frame[selected_variables]
            selected_columns = selected_variables
        except KeyError:
            logger.error(f"One or more selected features '{selected_variables}' are not" +
                               "found in the data.")
    
    return selected_data_frame, selected_columns

        
### 1.Overview on combined data ###
def overview_combined_data (combined_df, selected_columns, plotting_features, file_name, checkMissing, basicInfo, 
                            CorrMatrix, dist_plot, dist_table, category_threshold, pairplot_plot, pairplot_features, pairplot_hue, control_variable, logger):
    """ Generate basic information of the dataset including basic statistics, missing values,
        correlation matrix, distribution plot.

    Args:
        combined_df (Pandas.DataFrame): dataframe with selected features.
        selected_columns (list): a list of names of selected features.
        file_name: output file name (suffix).
        checkMissing (boolean): if check missing values.
        basicInfo (boolean): if generate basic statistics table.
        CorrMatrix (boolean): if plot correlation matrix.
        dist_plot (boolean): if make distribution plots.
        control_variable (str): the name of the control variable.
        logger (logging.Logger): Logger class handling log messages.

    Returns:
        No return.
    """

    ### For checking missings ###
    if checkMissing:
        try: 
            analysis_subfunctions.check_missing(combined_df, selected_columns, file_name)
        except:
            logger.warning("Failed to check missing values, but the execution will be continued!")

    ### For getting some basic info ###
    if basicInfo:
        try:
            analysis_subfunctions.data_describe(combined_df, selected_columns, file_name)
        except:
            logger.warning("Failed to generate data basic info table, but the execution will be continued!")

    ### Features to be plotted ###
    if plotting_features == 'all':
        plotting_features = selected_columns
    elif plotting_features == False:
        CorrMatrix = False
        dist_plot = False
    
    ### Function for correlation matrix ###
    if CorrMatrix:

        try:
            analysis_subfunctions.corr_Matrix(combined_df[plotting_features], file_name)

            existFile = "output/%s_Corr.csv" %file_name
            if os.path.exists(existFile):
                os.remove(existFile)
        except IndexError:
            logger.error("Plotting_features are not in the dataset. Please provide valid feature names!")
        except:
            logger.warning("Failed to plot correlation matrix, but the execution will be continued!")


    ### Function for distribution plot and table ###
    if dist_plot:
        if not control_variable:
            for column_item in range(0,len(plotting_features)):
                try:
                    analysis_subfunctions.dist_Plot(combined_df,plotting_features[column_item],control_variable)
                except ValueError:
                    logger.debug("%s - Calculated values for plotting contains errors!" %plotting_features[column_item])
            logger.debug('Distribution plot is done')

        elif control_variable in selected_columns:
            list_value = list(Counter(combined_df[control_variable]).keys())

            if len(list_value) < category_threshold:
                for i_value in list_value:
                    ctrl_combined_df = combined_df[combined_df[control_variable]==i_value]
                    for column_item in range(0,len(plotting_features)):
                        if control_variable != plotting_features[column_item]:
                            try:
                                analysis_subfunctions.dist_Plot(ctrl_combined_df,plotting_features[column_item], str(control_variable+'_'+str(i_value)) )
                            except ValueError:
                                logger.debug("%s - Calculated values for plotting contains errors!" %plotting_features[column_item])
            
                logger.debug('Distribution plot is done')
            else: 
                logger.error("Sorry, control variable has too many different values! Please choose categorical variable as control")
            
        else:
            logger.error("Please give one valid variable name or False to 'control_var'.")
            sys.exit("Execution interrupted!")
        
    if dist_table:
        ### Generate the data distribution parameters on the entire dataset ###
        analysis_subfunctions.dist_table_function(combined_df, category_threshold, file_name, 'entire', 'dataset')

        if control_variable:
            if control_variable in selected_columns:
                list_value = list(Counter(combined_df[control_variable]).keys())
                if len(list_value) < category_threshold:
                    for i_value in list_value:
                        ctrl_combined_df = combined_df[combined_df[control_variable]==i_value]
                        analysis_subfunctions.dist_table_function(ctrl_combined_df, category_threshold, file_name, control_variable, i_value)
                else: 
                    logger.error("Sorry, control variable has too many different values! Please choose categorical variable as control")
            
            else:
                logger.error("Please give one valid variable name or False to 'control_var'.")
                sys.exit("Execution interrupted!")
                
        logger.debug('Distribution table is done')


    ### Function for pairplot ###
    if pairplot_plot:
        try:
            analysis_subfunctions.numeric_pairplot(combined_df, pairplot_features, pairplot_hue, file_name)
        except IndexError:
            logger.error("Pairplot_features are not in the dataset. Please provide valid feature names!")
        except:
            logger.warning("Failed to plot Pairplot, but the execution will be continued!")

        


### 2. Check if features, evaluaton methods are valid ###
def check_model_inputs(ml_model, task, scoring, combined_df, logger):
    """ Check if the model parameters are valid

    Args:
        ml_model (module): model to use
        task (str): regression or classification.
        scoring (str/list): evaluation methods from Scikit Learn.
        combined_df (Pandas.DataFrame): the dataframe with selected features.
        logger (logging.Logger): Logger class handling log messages.

    Returns:
        model_name (list/str): a list of model file names.
        training_features (list): a list of selected features which will be trained in the model.
        target_feature (str): the column name of target features.
    """

    logger.debug('Start training models ... ...')

    if task in ['regression', 'classification']: 

        ### set up restrictions for inputs ###
        scoring_reg = ["neg_mean_absolute_error","neg_mean_squared_error","neg_mean_squared_log_error","r2"]
        scoring_cls = ['precision', 'recall', 'f1', 'roc_auc']

        ### Check inputed scoring  ### 
        if task == 'regression':
            if all(item in scoring_reg  for item in scoring):
                logger.debug("Regression evaluation metrics are fine!")
            else:
                logger.error("Sorry, so far we only support mean_absolute_error, mean_squared_error, mean_squared_log_error, r2 to evaluation regression models.")
                sys.exit("Execution interrupted!")

        elif task == 'classification':
            if all(item in scoring_cls  for item in scoring):
                logger.debug("Classification evaluation metrics are fine!")
            else:
                logger.error("Sorry, so far we only support Precision, Recall, F1-score, ROC to evaluation classification models.")
                sys.exit("Execution interrupted!")
        
    else:
        logger.error("Task needs to be either classification or regression")
        sys.exit("Execution interrupted!")


    logger.debug('Start checking if training and target features are in the dataset.')

    model_name, training_features, target_feature = ml_model.defineFeatures()

    if len(model_name) != len(training_features):
        logger.error("The number of sets of training features needs to be the same as the number of analysis models.")
        sys.exit("Execution interrupted!")


    ### First, check if values are in the datasets before training models ###
    for set_of_features in training_features: 
        for each_feature in set_of_features:
            if each_feature not in combined_df.columns:
                logger.debug("{feature} is not in the dataset".format(feature=each_feature))
                logger.error("Please provide existing training features from the dataset!")
                sys.exit("Execution interrupted!")

    for each_target_feature in target_feature: 
        if each_target_feature not in combined_df.columns:
            logger.debug("{feature} is not in the dataset".format(feature=each_target_feature))
            logger.error("Please provide existing target features from the dataset!")
            sys.exit("Execution interrupted!")

    logger.info('All training and target features are in the dataset.')
 
    return model_name, training_features, target_feature



def training_process(ml_model, combined_df, task, kFold, scoring, 
                    model_name, training_features, target_feature, logger):

    """ Train and evaluate the analysis model 

    Args:
        ml_model (module): model to use
        combined_df (Pandas.DataFrame): the dataframe with selected features.
        task (str): regression or classification.
        kFold (int/float): K-fold cross-validation or dataset slipting ratio
        scoring (str/list): evaluation methods from Scikit Learn.
        model_name (list/str): a list of model file names.
        training_features (list): a list of selected features which will be trained in the model.
        target_feature (str): the column name of target features.
        logger (logging.Logger): Logger class handling log messages.

    Returns:
        No returns.
    """

    result_list = [] 
    count = 0

    for each_model in range(0, len(model_name)): 
        logger.debug('Start training {model} ... ...'.format(model=model_name[each_model]))
        start_time_each = time.time()

            ### read model parameter setting from the analysis model code file ###
        try:
            model = ml_model.defineMLModels(model_name[each_model], kFold)
        except:
            logger.error("Errors occur in the defineMLModels function in the analysis model. ")
            raise

        num_training  = len(target_feature)

        ### Normalize training features ###
        for i_training in range(0, num_training):
            model_setting = [each_model, i_training]
            try: 
                features, target = ml_model.normalizeFeatures(combined_df, model_setting, model_name, training_features, target_feature)
            except:
                logger.error("Error occurs in the normalizeFeatures(...) function in the analysis code!")
                raise

            ### If use cross validation ###
            if kFold:
                if (kFold <= 1 and kFold > 0):
                    results = analysis_subfunctions.splitDataTraining(task, model, features, target, kFold, scoring)

                elif kFold > 2 and type(kFold)==int:
                    results = cross_validate(model, features, target, scoring=scoring, cv=kFold, error_score=np.nan, return_estimator=True, return_train_score=True)

                else:
                    logger.error("K-Fold has to be an integer (>=3) or 0-1 as a split ratio (testing/dataset) or False (the whole dataset will be trained by statmodels)")
                    sys.exit("Execution interrupted!")
            else:
                results = analysis_subfunctions.splitDataTraining(task, model, features, target, kFold, scoring)

            ### Write output results ###
            if (count == (len(model_name) * num_training) - 1):
                save_file = True
            else:
                save_file = False
                
            try:
                result_list = ml_model.writeOutput(kFold, model_name[each_model], results, result_list, training_features[each_model], target_feature[i_training], save_file)
            except:
                logger.error("Error occurs in the writeOutput(...) function in the analysis code!")
                raise



            ###

            count = count + 1

        logger.info("{model} training took {runtime:.4f} to run.".format(model=model_name[each_model], runtime=(time.time() - start_time_each)))
    


def main():
    """
    main function: read values from yaml file, check if the model parameters are valid in this case,
    execute the functions from the analysis model file, then generate the fail results. 
    
    """

    # We have to import MLmodel in the main function at runtime, because when
    # this script is imported, MLmodel.py does not exist yet.
    start_time_step_0 = time.time()
    from models import MLmodel

    ### Read analysis yaml file ###
    logger = rlog.get_logger(__name__)
    input_analysis_yaml_file_name = r'/inputVolume/analysis_input.yaml'
    inputYAML = load_yaml_file(input_analysis_yaml_file_name, logger)

    ### Load data from container ###
    try:
        data_frame = pd.read_csv('/data/act_data.csv').drop('encString', axis=1)
    except FileNotFoundError:
        logger.error("No combined dataset is available!! Please check step1: verification-decrption and step2: matching.")


    ### Read values from yaml file ###
    try:
        selected_variables = inputYAML['variables']
        excluded_variables = inputYAML['exclude_variables']
        categorical_to_numerical = inputYAML['variables_to_numeric']
        customize_feature = inputYAML['customize_features']
        file_name = inputYAML['taskName']
        checkMissing = inputYAML['check_missing']
        basicInfo = inputYAML['basic_Information']
        plotting_features = inputYAML['plotting_features']
        CorrMatrix = inputYAML['correlation_matrix']
        dist_plot = inputYAML["distribution_plot"]
        dist_table = inputYAML["distribution_table"]
        control_variable = inputYAML['control_var']
        category_threshold = inputYAML['category_threshold']
        pairplot_plot = inputYAML["pairplot_plot"]
        pairplot_features = inputYAML["pairplot_features"]
        pairplot_hue = inputYAML["pairplot_hue"]
        task = inputYAML['task'].lower()
        kFold = inputYAML['k_fold/split_ratio']
        scoring = inputYAML['evaluation_methods']
    except KeyError:
        logger.error("YAML file not valid. Please consult the example " +
                        "'analysis_input.yaml' file and edit in your settings.")

    ### Include selected features based on the yaml file ###
    selected_data_frame, selected_columns = select_features(data_frame, selected_variables, excluded_variables, logger)
    
    ### For checking data types ###
    selected_data_frame.dtypes.to_csv('/output/dataType.csv', header=False)

    ### Customize features ###
    if customize_feature:
        try:
            combined_df = MLmodel.customize_features(selected_data_frame)
            selected_columns = list(combined_df.columns)
        except:
            logger.error("Errors occur from customize_features function of the analysis model (from the reseacher). ")
            raise
    else:
        combined_df = selected_data_frame

    # Convert to numeric, string will be converted to Nan
    if categorical_to_numerical:
        combined_df = combined_df.apply(pd.to_numeric, errors='coerce')
        logger.warning("All features are forced to numberic types. Strings become Nan. This might cause analysis mistakes.")


    ### Main executions ###############
    ### 1. Check if features, evaluaton methods are valid ###
    model_name, training_features, target_feature = check_model_inputs(MLmodel, task, scoring, combined_df, logger)
    logger.info("Pre-processing data took {runtime:.4f}s to run".format(runtime=(time.time() - start_time_step_0)))

    ### 2.Overview on combined data ###
    start_time_step_1 = time.time()
    overview_combined_data (combined_df, selected_columns, plotting_features, file_name, checkMissing, basicInfo, 
                            CorrMatrix, dist_plot, dist_table, category_threshold, pairplot_plot, pairplot_features, pairplot_hue, control_variable, logger)
    logger.info("Basic info took {runtime:.4f}s to run".format(runtime=(time.time() - start_time_step_1)))


    ### 3. Run the model ###
    start_time_step_2 = time.time()
    training_process(MLmodel, combined_df, task, kFold, scoring, model_name, training_features, target_feature, logger)

    logger.info("In total, all models training took {runtime:.4f} to run. ".format(runtime=(time.time() - start_time_step_2)))
    logger.info("The whole analysis process took {runtime:.4f} to run. ".format(runtime=(time.time() - start_time_step_0)))


if __name__ == "__main__":
    main()
