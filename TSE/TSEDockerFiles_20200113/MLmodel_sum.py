
########## Simple Linear Regression ##########
import os
import time
start_time0 = time.time()
import json
import func
import numpy as np
import pandas as pd
from collections import Counter

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

def sum_features(sel_df):

    ### input features which need to be operated ###
    feature_sum = [
                    ["ZVWKHUISARTS_2011", "ZVWKHUISARTS_2012", "ZVWKHUISARTS_2013", 
                        "ZVWKHUISARTS_2014", "ZVWKHUISARTS_2015", "ZVWKHUISARTS_2016"],

                    ["ZVWKFARMACIE_2011", "ZVWKFARMACIE_2012", "ZVWKFARMACIE_2013",
                        "ZVWKFARMACIE_2014", "ZVWKFARMACIE_2015", "ZVWKFARMACIE_2016"],
                        
                    ["ZVWKZIEKENHUIS_2011", "ZVWKZIEKENHUIS_2012", "ZVWKZIEKENHUIS_2013",
                        "ZVWKZIEKENHUIS_2014", "ZVWKZIEKENHUIS_2015", "ZVWKZIEKENHUIS_2016"],
                        
                    ["ZVWKPARAMEDISCH_2011", "ZVWKPARAMEDISCH_2012", "ZVWKPARAMEDISCH_2013",
                        "ZVWKPARAMEDISCH_2014", "ZVWKPARAMEDISCH_2015", "ZVWKPARAMEDISCH_2016"],
                    
                    ["ZVWKHULPMIDDEL_2011", "ZVWKHULPMIDDEL_2012", "ZVWKHULPMIDDEL_2013",
                        "ZVWKHULPMIDDEL_2014", "ZVWKHULPMIDDEL_2015", "ZVWKHULPMIDDEL_2016"],
                        
                    ["ZVWKZIEKENVERVOER_2011", "ZVWKZIEKENVERVOER_2012", "ZVWKZIEKENVERVOER_2013",
                        "ZVWKZIEKENVERVOER_2014", "ZVWKZIEKENVERVOER_2015", "ZVWKZIEKENVERVOER_2016"],
                        
                    ["ZVWKBUITENLAND_2011", "ZVWKBUITENLAND_2012", "ZVWKBUITENLAND_2013",
                        "ZVWKBUITENLAND_2014", "ZVWKBUITENLAND_2015", "ZVWKBUITENLAND_2016"],
                        
                    ["ZVWKOVERIG_2011", "ZVWKOVERIG_2012", "ZVWKOVERIG_2013",
                        "ZVWKOVERIG_2014", "ZVWKOVERIG_2015", "ZVWKOVERIG_2016"],
                        
                    ["ZVWKEERSTELIJNSPSYCHO_2011", "ZVWKEERSTELIJNSPSYCHO_2012",
                        "ZVWKEERSTELIJNSPSYCHO_2013"],
                    
                    ["ZVWKGGZ_2011", "ZVWKGGZ_2012", "ZVWKGGZ_2013"],
                    
                    ["ZVWKWYKVERPLEGING_2014", "ZVWKWYKVERPLEGING_2015", "ZVWKWYKVERPLEGING_2016"],

                    ["ZVWKMULTIDISC_2015", "ZVWKMULTIDISC_2016"]
                ]

    ### Give names to new features ###
    sum_name = ["Sum_ZVWKHUISARTS","Sum_ZVWKFARMACIE","Sum_ZVWKZIEKENHUIS","Sum_ZVWKPARAMEDISCH","Sum_ZVWKHULPMIDDEL",
                    "Sum_ZVWKZIEKENVERVOER", "Sum_ZVWKBUITENLAND", "Sum_ZVWKOVERIG", "Sum_ZVWKEERSTELIJNSPSYCHO",
                    "Sum_ZVWKGGZ", "Sum_ZVWKWYKVERPLEGING", "Sum_ZVWKMULTIDISC"]

    ### Sum up features ###
    for i in range(0,len(feature_sum)):
        
        sel_df[sum_name[i]] = (sel_df[feature_sum[i]].sum(axis=1)) / 7 

    return sel_df



###############################
### Machine Learning Models ###
###############################

### Provide your Training and target features ###
def defineFeatures(combined_df, model_setting):
    model_name = ['model_1', 'model_2', 'model_3', 'model_4', 'model_5', 'model_6', 'model_7', 'model_8', 'model_9', 'model_10']

    training_features = [["SEX", "Age", "N_Education_3cat", "N_Diabetes_WHO_2"],
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

    if model_setting == 'checking':
        features = training_features
        target = target_feature
        return model_name, features, target

    elif type(model_setting) == list:
        i_model = model_setting[0]
        i_training = model_setting[1]

        ###### Remove missing values ######
        print('*************************************************')
        print('Missing values in training and target features:')
        combined_df_selected = combined_df[training_features[i_model] + [target_feature[i_training]]]
        print(pd.isnull(combined_df_selected).sum())
        combined_df_selected = combined_df_selected[np.invert(pd.isnull(combined_df_selected).any(axis=1))]

        print('Missing values are removed by default.')
        print("The number of instances(rows): ", len(combined_df_selected))

        ###### Normalization ######
        print('\n*************************************************')
        print('***** Normalization *****')
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
def defineMLModels(model_name):
    ### Configure models ###
    define_models = {
        'model_1': LinearRegression(normalize=True),
        'model_2': LinearRegression(normalize=True),
        'model_3': LinearRegression(normalize=True),
        'model_4': LinearRegression(normalize=True),
        'model_5': LinearRegression(normalize=True),
        'model_6': LinearRegression(normalize=True),
        'model_7': LinearRegression(normalize=True),
        'model_8': LinearRegression(normalize=True)
    }

    print('************* Model parameters *****************')
    model = define_models[model_name]
    print(model.get_params())
    print('************************************************')

    return model


####################################
########## Output restuls ##########
####################################
def writeOutput(kFold, model_name, m, results, model, target_name):
    if kFold == 0:
        with open('output/%s_%s_result.json' %(model_name[m], target_name), 'w') as fp:
            json.dump(results, fp)
    
    elif kFold > 2: 
        coef_ = []
        for kfold_model in results['estimator']:
            coef_.append(kfold_model.coef_.tolist())
        results.update({'coef_':coef_}) 

        new_results = dict()
        for key in results.keys():
            if key != 'estimator': 
                if type(results[key])!= list:
                    value = results[key].tolist()
                    new_results.update({key:value}) 
                else: 
                    new_results.update({key:results[key]})

        with open('output/%s_%s_result.json' %(model_name[m], target_name), 'w') as fp:
            json.dump(new_results, fp) 

        if m == len(model_name)-1:
            combined_outFile = dict()
            for n in model_name:
                fileName = str(n)+'_'+str(target_name)
                with open('output/%s_result.json' %fileName, 'r') as fp:
                    temp = json.load(fp)
                combined_outFile.update({fileName:temp})

            with open('output/combined_%s_result.json' %target_name, 'w') as fp:
                json.dump(combined_outFile, fp) 

        print("%s: Result is generated at TSE!" %model_name[m])