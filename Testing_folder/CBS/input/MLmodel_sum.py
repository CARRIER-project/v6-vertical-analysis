########## Simple Linear Regression ##########
import os
import time
start_time0 = time.time()
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import Counter
import redacted_logging as rlog
logger = rlog.get_logger(__name__)

from sklearn import svm
from sklearn.preprocessing import MinMaxScaler, RobustScaler
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB, BernoulliNB
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.linear_model import LinearRegression,LogisticRegression
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_squared_log_error,r2_score, make_scorer
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score, roc_auc_score


###########################################
### Function for customizing new features #
###########################################

logger = rlog.get_logger(__name__)

def customize_features(sel_df):

    ### input features which need to be operated ###
    feature_sum = [
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
                    
                    ["ZVWKWYKVERPLEGING_2014", "ZVWKWYKVERPLEGING_2015", "ZVWKWYKVERPLEGING_2016"],

                    ["ZVWKMULTIDISC_2015", "ZVWKMULTIDISC_2016"]
                ]

    ### Give names to new features ###
    sum_name = ["Sum_ZVWKHUISARTS","Sum_ZVWKFARMACIE","Sum_ZVWKZIEKENHUIS","Sum_ZVWKPARAMEDISCH","Sum_ZVWKHULPMIDDEL",
                    "Sum_ZVWKZIEKENVERVOER", "Sum_ZVWKBUITENLAND", "Sum_ZVWKOVERIG", "Sum_ZVWKEERSTELIJNSPSYCHO",
                    "Sum_ZVWKGGZ", "Sum_ZVWKWYKVERPLEGING", "Sum_ZVWKMULTIDISC"]

    ### Sum up features ###
    for i in range(0,len(feature_sum)):
        
        sel_df[sum_name[i]] = (sel_df[feature_sum[i]].sum(axis=1)) 

    return sel_df



###############################
### Machine Learning Models ###
###############################

### Provide your Training and target features ###
def defineFeatures():
    model_name = ['model_0', 'model_1', 'model_2', 'model_3', 'model_4', 'model_5', 'model_6', 'model_7', 'model_8', 'model_9', 'model_10']

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

    target_feature = ["Sum_ZVWKHUISARTS","Sum_ZVWKFARMACIE","Sum_ZVWKZIEKENHUIS","Sum_ZVWKPARAMEDISCH","Sum_ZVWKHULPMIDDEL",
                    "Sum_ZVWKZIEKENVERVOER", "Sum_ZVWKBUITENLAND", "Sum_ZVWKOVERIG", "Sum_ZVWKEERSTELIJNSPSYCHO",
                    "Sum_ZVWKGGZ", "Sum_ZVWKWYKVERPLEGING", "Sum_ZVWKMULTIDISC"]

    return model_name, training_features, target_feature

def normalizeFeatures(combined_df, model_setting, model_name, training_features, target_feature):

    i_model = model_setting[0]
    i_training = model_setting[1]

    ###### Remove missing values ######
    combined_df_selected = combined_df[training_features[i_model] + [target_feature[i_training]]]
    
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
    logger.info('After removing missings, {rows} rows left in training task of {model} {target}'.format(rows=len(combined_df_selected),model=model_name[i_model],target=target_feature[i_training]))

    ###### Normalization ######
    logger.debug('Start Normalization ... ... ')
    scaler = RobustScaler(quantile_range=(15,85)) #MinMaxScaler(feature_range=(-1, 1)) RobustScaler
    scaled = scaler.fit_transform(combined_df_selected) # trans_features

    combined_df_scaled = pd.DataFrame.from_records(scaled)
    combined_df_scaled.columns = combined_df_selected.columns
    
    ##### Get training features and target #####
    features = combined_df_scaled[training_features[i_model]]
    target = combined_df_scaled[target_feature[i_training]]
    target_name = target_feature[i_training]


    return model_name, features, target, target_name

######################################
### Define Machine learning Models ###
######################################
def defineMLModels(model_name, kFold):
    ## Configure models when kFold is not False ###
    if kFold:
        define_models = {
            'model_0': LinearRegression(normalize=True),
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
        ### If you wanna use statmodels to learn associations (kFold is False)
        define_models = {
            'model_0': ['OLS', 'add_constant'],
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
        logger.info('Model parameters (Scikit Learnt): {param}'.format(param=model.get_params()))
    except:
        logger.info('Model parameters (Statmodel): %s' %model[0])

    return model


####################################
########## Output restuls ##########
####################################
def writeOutput(kFold, model_name, m, results, result_list, training_features, target_name, save_file):
    if not kFold:
        ### Write results out to a png file ###
        plt.rc('figure', figsize=(12, 7))
        plt.text(0.01, 0.05, str(results), {'fontsize': 10}, fontproperties = 'monospace')
        plt.axis('off')
        plt.tight_layout()

        filename = 'output/statmodels/%s_%s.png' %(target_name, model_name[m])
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        plt.savefig(filename)
        logger.debug("%s - Statmodels result plot is done!" %model_name[m])
        plt.clf()
    
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
            index_name = ['_Intercept'] + training_features[m]
            index_name = [model_name[m]+'_'+target_name+'_'+x for x in index_name]
            results.index = index_name
            result_list[5] = pd.concat([result_list[5], results])
            if save_file == True:
                result_list[5].to_csv('output/onlyTraining_results.csv')
        
        elif kFold < 1:
            results.index = [model_name[m]+'_'+target_name]
            result_list[5] = pd.concat([result_list[5], results])
            if save_file == True:
                result_list[5].to_csv('output/sliptTraining_results.csv')
        
        elif kFold > 2: 
            ### Save the scores ####
            temp_df = pd.DataFrame.from_dict(results)
            temp_mean = temp_df.mean()
            temp_std = temp_df.std()
            ### mean and STD of the evaluation scores ###
            result_list[0].update({model_name[m]+'_'+target_name:temp_mean}) # mean_scores
            result_list[1].update({model_name[m]+'_'+target_name:temp_std})  # std_scores

            ### Save the coef_ and intercept ###

            coef_ = []
            intercept_ = []
            for kfold_model in results['estimator']:
                coef_.append(kfold_model.coef_.tolist())
                intercept_.append(kfold_model.intercept_.tolist())
            
            ### mean and STD of Coef_ ###
            coef_df = pd.DataFrame.from_dict(coef_)
            coef_df.columns = training_features[m]
            mean_coef_ = coef_df.mean()
            std_coef_ = coef_df.std()
            result_list[2].update({model_name[m]+'_'+target_name:mean_coef_}) # mean_coef_
            result_list[3].update({model_name[m]+'_'+target_name:std_coef_})  # std_coef_

            ### mean and STD of Intercept ###
            intercept_df = pd.DataFrame.from_dict(intercept_)
            meanSTD_intercept_ = pd.concat([intercept_df.mean(), intercept_df.std()],axis=1)
            meanSTD_intercept_.columns = ['mean_intercept','STD_intercept']
            result_list[4].update({model_name[m]+'_'+target_name:meanSTD_intercept_}) # mean_coef_

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