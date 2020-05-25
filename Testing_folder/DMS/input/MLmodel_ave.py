"""
This script is to define variables, models, and write out results.
It should be provided by the researcher and signed by all data parties
after checking the code. 

Until 23-04-2020, this script includes:
1. customize features (sum, avg, etc)
2. define what features will be used in the model
3. define models (linear/logistic regression, etc)
4. normalize features (max-min normalization, robust scaler)
5. write out the result 
"""
import os
import time
start_time0 = time.time()
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import redacted_logging as rlog
logger = rlog.get_logger(__name__)

from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import LinearRegression


###########################################
### Function for customizing new features #
###########################################

logger = rlog.get_logger(__name__)

def customize_features(input_dataframe):
    """ This function is to customize features such as calculate the sum, average of multiple features
        Please note there should not be any printing/writting out in this function
    Args:
        input_dataframe (Pandas.DataFrame): Dataframe of original data
    Returns:
        input_dataframe (Pandas.DataFrame): Dataframe of original + customized data.
    Example:
        If you need to add column_1 and column_2 as a new column:
            --> input_dataframe['new_column'] = input_dataframe['column_1'] + input_dataframe['column_2']
    Note:
        1. You have to use the exact names of columns.
        2. New columns (names) will be added to the dataframe.
    """
    ### input features which need to be operated ###
    ### Column names have to be accurate ###
    operated_feature = [
                    ["ZVWKHUISARTS_2010", "ZVWKHUISARTS_2011", "ZVWKHUISARTS_2012", "ZVWKHUISARTS_2013", 
                        "ZVWKHUISARTS_2014", "ZVWKHUISARTS_2015", "ZVWKHUISARTS_2016"],

                    ["ZVWKFARMACIE_2010", "ZVWKFARMACIE_2011", "ZVWKFARMACIE_2012", "ZVWKFARMACIE_2013",
                        "ZVWKFARMACIE_2014", "ZVWKFARMACIE_2015", "ZVWKFARMACIE_2016"],
                        
                    ["ZVWKZIEKENHUIS_2010", "ZVWKZIEKENHUIS_2011", "ZVWKZIEKENHUIS_2012", "ZVWKZIEKENHUIS_2013",
                        "ZVWKZIEKENHUIS_2014", "ZVWKZIEKENHUIS_2015", "ZVWKZIEKENHUIS_2016"],
                        
                    ["ZVWKPARAMEDISCH_2010", "ZVWKPARAMEDISCH_2011", "ZVWKPARAMEDISCH_2012", "ZVWKPARAMEDISCH_2013",
                        "ZVWKPARAMEDISCH_2014", "ZVWKPARAMEDISCH_2015", "ZVWKPARAMEDISCH_2016"],
                    
                    ["ZVWKHULPMIDDEL_2010", "ZVWKHULPMIDDEL_2011", "ZVWKHULPMIDDEL_2012", "ZVWKHULPMIDDEL_2013",
                        "ZVWKHULPMIDDEL_2014", "ZVWKHULPMIDDEL_2015", "ZVWKHULPMIDDEL_2016"],
                        
                    ["ZVWKZIEKENVERVOER_2010", "ZVWKZIEKENVERVOER_2011", "ZVWKZIEKENVERVOER_2012", "ZVWKZIEKENVERVOER_2013",
                        "ZVWKZIEKENVERVOER_2014", "ZVWKZIEKENVERVOER_2015", "ZVWKZIEKENVERVOER_2016"],
                        
                    ["ZVWKBUITENLAND_2010", "ZVWKBUITENLAND_2011", "ZVWKBUITENLAND_2012", "ZVWKBUITENLAND_2013",
                        "ZVWKBUITENLAND_2014", "ZVWKBUITENLAND_2015", "ZVWKBUITENLAND_2016"],
                        
                    ["ZVWKOVERIG_2010", "ZVWKOVERIG_2011", "ZVWKOVERIG_2012", "ZVWKOVERIG_2013",
                        "ZVWKOVERIG_2014", "ZVWKOVERIG_2015", "ZVWKOVERIG_2016"],
                        
                    ["ZVWKEERSTELIJNSPSYCHO_2010", "ZVWKEERSTELIJNSPSYCHO_2011", "ZVWKEERSTELIJNSPSYCHO_2012",
                        "ZVWKEERSTELIJNSPSYCHO_2013"],
                    
                    ["ZVWKGGZ_2010", "ZVWKGGZ_2011", "ZVWKGGZ_2012", "ZVWKGGZ_2013"],

                    ["ZVWKGENBASGGZ_2014", "ZVWKGENBASGGZ_2015", "ZVWKGENBASGGZ_2016"],

                    ["ZVWKSPECGGZ_2014", "ZVWKSPECGGZ_2015", "ZVWKSPECGGZ_2016"],

                    ["ZVWKGERIATRISCH_2013", "ZVWKGERIATRISCH_2014", "ZVWKGERIATRISCH_2015", "ZVWKGERIATRISCH_2016"],
                    
                    ["ZVWKWYKVERPLEGING_2014", "ZVWKWYKVERPLEGING_2015", "ZVWKWYKVERPLEGING_2016"],

                    ["ZVWKMULTIDISC_2015", "ZVWKMULTIDISC_2016"]
                ]

    ### Give names to new columns ###
    ### New columns names will be used ###
    customized_feature_names = ["Ave_ZVWKHUISARTS","Ave_ZVWKFARMACIE","Ave_ZVWKZIEKENHUIS","Ave_ZVWKPARAMEDISCH","Ave_ZVWKHULPMIDDEL",
                                    "Ave_ZVWKZIEKENVERVOER", "Ave_ZVWKBUITENLAND", "Ave_ZVWKOVERIG", "Ave_ZVWKEERSTELIJNSPSYCHO",
                                    "Ave_ZVWKGGZ", "Ave_ZVWKGENBASGGZ", "Ave_ZVWKSPECGGZ", "Ave_ZVWKGERIATRISCH", \
                                    "Ave_ZVWKWYKVERPLEGING", "Ave_ZVWKMULTIDISC"]

    ### Conduct operations on the exisitng columns  ###
    ### e.g., input_dataframe['new_column'] = input_dataframe['column_1'] + input_dataframe['column_2'] ###
    for i in range(0,len(operated_feature)):
        if customized_feature_names[i] == 'Ave_ZVWKEERSTELIJNSPSYCHO': # this feature is only available for 4 years #
            input_dataframe[customized_feature_names[i]] = (input_dataframe[operated_feature[i]].sum(axis=1)) / 4
        elif customized_feature_names[i] == 'Ave_ZVWKGGZ': # this feature is only available for 4 years #
            input_dataframe[customized_feature_names[i]] = (input_dataframe[operated_feature[i]].sum(axis=1)) / 4
        elif customized_feature_names[i] == 'Ave_ZVWKGENBASGGZ': # this feature is only available for 3 years #
            input_dataframe[customized_feature_names[i]] = (input_dataframe[operated_feature[i]].sum(axis=1)) / 3
        elif customized_feature_names[i] == 'Ave_ZVWKSPECGGZ': # this feature is only available for 3 years #
            input_dataframe[customized_feature_names[i]] = (input_dataframe[operated_feature[i]].sum(axis=1)) / 3
        elif customized_feature_names[i] == 'Ave_ZVWKGERIATRISCH': # this feature is only available for 4 years #
            input_dataframe[customized_feature_names[i]] = (input_dataframe[operated_feature[i]].sum(axis=1)) / 4
        elif customized_feature_names[i] == 'Ave_ZVWKWYKVERPLEGING': # this feature is only available for 3 years #
            input_dataframe[customized_feature_names[i]] = (input_dataframe[operated_feature[i]].sum(axis=1)) / 3
        elif customized_feature_names[i] == 'Ave_ZVWKMULTIDISC': # this feature is only available for 2 years #
            input_dataframe[customized_feature_names[i]] = (input_dataframe[operated_feature[i]].sum(axis=1)) / 2
        else:
            input_dataframe[customized_feature_names[i]] = (input_dataframe[operated_feature[i]].sum(axis=1)) / 7 

    return input_dataframe


###############################
### Machine Learning Models ###
###############################

### Provide your Training and target features ###
def defineFeatures():
    """ This function is to define which features will be used as training features and target feature
        Please note there should not be any printing/writting out in this function
        Args:
            No inputs.

        Returns:
            model_name (list): a list of model names (used to label different models)
            training_features (list): a list of features for training the model (each model has a list of training features)
            target_feature (list): a list of features as target (each model has one target feature)
    """
    ### Give names to all models ###
    ### Length of model_name is equal to the length of training features (and the length of target features) ###
    model_name = ['model_0', 'model_1', 'model_2', 'model_3', 'model_4', 'model_5', 'model_6', 'model_7', 'model_8', 'model_9', 'model_10']

    ### training_features is a list of lists of features ###
    ### Template: [[training features in model_0],[training features in model_1],[training features in model_2]...]
    ### Please note the columns names (training features) you provide have to be correct ###
    training_features = [["N_Diabetes_WHO_2"],
                        ["SEX", "Age", "N_Education_3cat", "N_Diabetes_WHO_2"],
                        ["SEX", "Age", "height", "bmi", "N_Diabetes_WHO_2"],
                        ["SEX", "Age", "height", "waist", "hip", "N_Diabetes_WHO_2"],
                        ["SEX", "Age", "height", "bmi", "n_smokingcat4","N_ALCOHOL_CAT", "NIT_kcal", "medGRscore_TR", "N_Diabetes_WHO_2"],
                        ["SEX", "Age", "N_CVD", "N_HT",  "med_depression", "MINIlifedepr", "Mobility_lim", "N_Diabetes_WHO_2"],
                        ["SEX", "Age", "N_Education_3cat", "height", "bmi", "n_smokingcat4","N_ALCOHOL_CAT", "NIT_kcal", "medGRscore_TR", "N_Diabetes_WHO_2"],
                        ["SEX", "Age", "N_Education_3cat", "height", "bmi", "n_smokingcat4","N_ALCOHOL_CAT", "NIT_kcal", "medGRscore_TR", "N_Diabetes_WHO_2", 'MEAN_VALID_MIN_SLEEP_T', 'MEAN_SED_MIN_WAKE_T', 'MEAN_STAND_MIN_WAKE_T','MEAN_STEP_MIN_WAKE_T'],
                        ["SEX", "Age", "N_Education_3cat", "N_CVD", "N_HT",  "med_depression", "MINIlifedepr", "Mobility_lim", "N_Diabetes_WHO_2"],
                        ["SEX", "Age", "height", "bmi", "n_smokingcat4", "N_ALCOHOL_CAT", "NIT_kcal", "medGRscore_TR", "N_CVD", "N_HT",  "med_depression", "MINIlifedepr", "Mobility_lim", "N_Diabetes_WHO_2"],
                        ["SEX", "Age", "N_Education_3cat", "height", "bmi", "n_smokingcat4", "N_ALCOHOL_CAT", "NIT_kcal", "medGRscore_TR", "N_CVD", "N_HT",  "med_depression", "MINIlifedepr", "Mobility_lim", "N_Diabetes_WHO_2"]]

    target_feature = ["Ave_ZVWKHUISARTS","Ave_ZVWKFARMACIE","Ave_ZVWKZIEKENHUIS","Ave_ZVWKPARAMEDISCH","Ave_ZVWKHULPMIDDEL",
                    "Ave_ZVWKZIEKENVERVOER", "Ave_ZVWKBUITENLAND", "Ave_ZVWKOVERIG", "Ave_ZVWKEERSTELIJNSPSYCHO",
                    "Ave_ZVWKGGZ", "Ave_ZVWKWYKVERPLEGING", "Ave_ZVWKMULTIDISC"]

    return model_name, training_features, target_feature

def normalizeFeatures(combined_df, model_setting, model_name, training_features, target_feature):
    """ This function is to normalize training features
        Args:
            combined_df (Pandas.DataFrame): DataFrame of original + customized features
            model_setting (list): [index of which model, index of which target feature]
            model_name (list): a list of model name
            training_features(list): a list of column names of training features
            target_feature(list): a list of column names of target feature

        Returns:
            features (Pandas.DataFrame): Normalized training features
            target (list): normalized target feature
    """
    i_model = model_setting[0]
    i_training = model_setting[1]
    combined_df_selected = combined_df[training_features[i_model] + [target_feature[i_training]]]


    ### Removing missing values ###
    ### Normalization and model training will not work if missing values are not removed ###

    missing  = 0
    misVariables = []
    CheckNull = pd.isnull(combined_df_selected).sum()
    column_names = list(CheckNull.keys())
    for var in range(0, len(CheckNull)):
        if CheckNull[var] != 0:
            misVariables.append([column_names[var], CheckNull[var], round(CheckNull[var]/len(combined_df_selected ),3)])
            missing = missing + 1
    if missing != 0:
        df_misVariables = pd.DataFrame.from_records(misVariables)
        df_misVariables.columns = ['Variable', 'Missing', 'Percentage (%)']
        sort_table = df_misVariables.sort_values(by=['Percentage (%)'], ascending=False)
        
        outputFile = 'output/missings_in_models/%s_%s_summary.csv' %(model_name[i_model], target_feature[i_training])
        os.makedirs(os.path.dirname(outputFile), exist_ok=True)
        sort_table.to_csv(outputFile)

    combined_df_selected = combined_df_selected[np.invert(pd.isnull(combined_df_selected).any(axis=1))]
    logger.debug('After removing missings, {rows} rows left in training task of {model} {target}'.format(rows=len(combined_df_selected),model=model_name[i_model],target=target_feature[i_training]))

    ### If you don't want to remove missing values, please comment the above function (line 178 - line 199) ###
    ### Then, uncomment the following two lines.
    # combined_df_selected = combined_df_selected
    # logger.debug('You did not detect and remove missing values. The dataset might contain missing values which may cause errors in analysis.')


    ###### Normalization ######
    ### Scalers from Scikit learn are supported including Normalizer, MinMaxScaler, RobustScaler ###
    ### More scalers can be found here: https://scikit-learn.org/stable/modules/classes.html#module-sklearn.preprocessing ###
    logger.debug('Start Normalization ... ... ')
    scaler = RobustScaler(quantile_range=(15,85)) #MinMaxScaler(feature_range=(-1, 1)) RobustScaler
    scaled = scaler.fit_transform(combined_df_selected) # trans_features

    combined_df_scaled = pd.DataFrame.from_records(scaled)
    combined_df_scaled.columns = combined_df_selected.columns
    
    ##### Get training features and target #####
    features = combined_df_scaled[training_features[i_model]]
    target = combined_df_scaled[target_feature[i_training]]

    return features, target

######################################
### Define Machine learning Models ###
######################################
def defineMLModels(model_name, kFold):
    """ This function is to define training models using either Scikit learn(KFold!=False) 
        or Statsmodels (KFold==False)
        Args:
            model_name (list): a list of model name
            KFold(number): 
                - False: The whole dataset will be trained to learn associations using Statsmodels
                - 0-1: The whole dataset will be split into training and testing data (test_data_size this value)
                - > 1: The whole dataset will use cross-validation with KFold

        Returns:
            model (list): a list of defined models
    """

    ### Define_models is a dict which should indicate which model uses which analysis algorithms ###
    ### when the goal of execution is prediciton, kFold will be a real number. ###
    ### In this case, we recommend to use Skicit learn models e.g., linear regress, SVM regression, etc ###
    ### More models can be found: https://scikit-learn.org/stable/supervised_learning.html ###
    if kFold:
        define_models = {
            'model_0': LinearRegression(normalize=True), ### Define models names and parameters ###
            'model_1': LinearRegression(normalize=True),
            'model_2': LinearRegression(normalize=True),
            'model_3': LinearRegression(normalize=True),
            'model_4': LinearRegression(normalize=True),
            'model_5': LinearRegression(normalize=True),
            'model_6': LinearRegression(normalize=True),
            'model_7': LinearRegression(normalize=True),
            'model_8': LinearRegression(normalize=True),
            'model_9': LinearRegression(normalize=True),
            'model_10': LinearRegression(normalize=True)
        }

    else:
        ### when the goal of execution is learning association, kFold will be a False. ###
        ### We support statsmodels to learn associations https://www.statsmodels.org/stable/index.html ###
        define_models = {
            'model_0': ['OLS', 'add_constant'], ### Define models names and parameters ###
            'model_1': ['OLS', 'add_constant'],
            'model_2': ['OLS', 'add_constant'],
            'model_3': ['OLS', 'add_constant'],
            'model_4': ['OLS', 'add_constant'],
            'model_5': ['OLS', 'add_constant'],
            'model_6': ['OLS', 'add_constant'],
            'model_7': ['OLS', 'add_constant'],
            'model_8': ['OLS', 'add_constant'],
            'model_9': ['OLS', 'add_constant'],
            'model_10': ['OLS', 'add_constant']
        }

    model = define_models[model_name]
    try:
        logger.debug('Model parameters (Scikit Learnt): {param}'.format(param=model.get_params()))
    except:
        logger.debug('Model parameters (Statmodel): %s' %model[0])

    return model


####################################
########## Output restuls ##########
####################################
def writeOutput(kFold, single_model_name, results, result_list, single_training_feature_set, target_name, save_file):
    """ This function is to write the result to files. Based on the different values of KFold, 
        we write out different results

        Args:
            kFold (False or numbers): 
                - False: results from statsmodel are stored as pictures
                - 0-1: results are generated in one csv file 
                - > 1: results are generated in multiple csv files cuz multiple evaluation methods
            single_model_name (string): the given name of the model
            results (list): the set of result from one single model
            result_list (list): a list of sets of results from all models
            single_training_feature_set (list): training features for this single model
            target_name (string): target feature for this single model 
            save_file (Boolean): if write the results to files (when all models are done, save_file will be True)
            
            KFold(number): 
               

        Returns:
            result_list (list): a list of results (each model generates one set of results)
    """

    ### Output for Statsmodels ### 
    if not kFold:
        ### Write results out to a png file ###
        plt.rc('figure', figsize=(12, 7))
        plt.text(0.01, 0.05, str(results), {'fontsize': 10}, fontproperties = 'monospace')
        plt.axis('off')
        plt.tight_layout()

        filename = 'output/statmodels/%s_%s.png' %(target_name, single_model_name)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        plt.savefig(filename)
        logger.debug("%s - Statmodels result plot is done!" %single_model_name)
        plt.clf()
    ### Output for Scikit Learn ### 
    elif len(result_list) == 0:
        mean_scores = {}
        std_scores = {}
        mean_coef_ = {}
        std_coef_ = {}
        mean_intercept = {}
        general_re = pd.DataFrame()
        result_list = [mean_scores, std_scores, mean_coef_, std_coef_, mean_intercept, general_re]
    else:
        if kFold == 1:
            index_name = ['_Intercept'] + single_training_feature_set
            index_name = [single_model_name+'_'+target_name+'_'+x for x in index_name]
            results.index = index_name
            result_list[5] = pd.concat([result_list[5], results])
            if save_file == True:
                result_list[5].to_csv('output/onlyTraining_results.csv')
        
        elif kFold < 1:
            results.index = [single_model_name+'_'+target_name]
            result_list[5] = pd.concat([result_list[5], results])
            if save_file == True:
                result_list[5].to_csv('output/sliptTraining_results.csv')
        
        elif kFold > 2: 
            ### Save the scores ####
            temp_df = pd.DataFrame.from_dict(results)
            temp_mean = temp_df.mean()
            temp_std = temp_df.std()
            ### mean and STD of the evaluation scores ###
            result_list[0].update({single_model_name+'_'+target_name:temp_mean}) # mean_scores
            result_list[1].update({single_model_name+'_'+target_name:temp_std})  # std_scores

            ### Save the coef_ and intercept ###

            coef_ = []
            intercept_ = []
            for kfold_model in results['estimator']:
                coef_.append(kfold_model.coef_.tolist())
                intercept_.append(kfold_model.intercept_.tolist())
            
            ### mean and STD of Coef_ ###
            coef_df = pd.DataFrame.from_dict(coef_)
            coef_df.columns = single_training_feature_set
            mean_coef_ = coef_df.mean()
            std_coef_ = coef_df.std()
            result_list[2].update({single_model_name+'_'+target_name:mean_coef_}) # mean_coef_
            result_list[3].update({single_model_name+'_'+target_name:std_coef_})  # std_coef_

            ### mean and STD of Intercept ###
            intercept_df = pd.DataFrame.from_dict(intercept_)
            meanSTD_intercept_ = pd.concat([intercept_df.mean(), intercept_df.std()],axis=1)
            meanSTD_intercept_.columns = ['mean_intercept','STD_intercept']
            result_list[4].update({single_model_name+'_'+target_name:meanSTD_intercept_}) # mean_coef_

            if save_file == True:
                mean_score_df = pd.DataFrame.from_dict(result_list[0]).transpose() # mean_scores
                mean_score_df.to_csv("output/mean_scores.csv")
                std_score_df = pd.DataFrame.from_dict(result_list[1]).transpose() # std_scores
                std_score_df.to_csv("output/STD_scores.csv")

                mean_coef_df = pd.DataFrame.from_dict(result_list[2]).transpose() # mean_coef_
                mean_coef_df.to_csv("output/mean_coef_.csv")
                std_coef_df = pd.DataFrame.from_dict(result_list[3]).transpose() # STD_coef_
                std_coef_df.to_csv("output/STD_coef_.csv")

        logger.debug("All Results are generated at TSE!\n")

    return result_list
