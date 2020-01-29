
########## Simple Linear Regression ##########
import os
import time
start_time0 = time.time()
import func
import numpy as np
import pandas as pd
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

def sum_features(sel_df):

    return sel_df


###############################
### Machine Learning Models ###
###############################

### Provide your Training and target features ###
def defineFeatures():
    model_name = ['model_0', 'model_1', 'model_2']

    training_features = [["var1"],
                        ["var1", "var2", "var3", "var8"],
                        ["var1", "var10", "var11", "var12"]]

    target_feature = ["var13","var14"]

    return model_name, training_features, target_feature

def customizeFeatures(combined_df, model_setting, model_name, training_features, target_feature):

    i_model = model_setting[0]
    i_training = model_setting[1]

    ###### Remove missing values ######
    combined_df_selected = combined_df[training_features[i_model] + [target_feature[i_training]]]
    miss_sum = pd.isnull(combined_df_selected).sum()
    combined_df_selected = combined_df_selected[np.invert(pd.isnull(combined_df_selected).any(axis=1))]

    outputFile = 'output/missing_values/%s_%s_summary.csv' %(model_name[i_model], target_feature[i_training])
    os.makedirs(os.path.dirname(outputFile), exist_ok=True)
    miss_sum.to_csv(outputFile)

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
def defineMLModels(model_name):
    ### Configure models ###
    define_models = {
        'model_0': LinearRegression(normalize=True),
        'model_1': LinearRegression(normalize=True),
        'model_2': LinearRegression(normalize=True)
    }

    model = define_models[model_name]
    logger.info('Model parameters: {param}'.format(param=model.get_params()))

    return model


####################################
########## Output restuls ##########
####################################
def writeOutput(kFold, model_name, m, results, result_list, training_features, target_name, save_file):
    if len(result_list) == 0:
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
        
        if kFold < 1:
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