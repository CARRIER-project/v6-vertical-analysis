
########## Simple Linear Regression ##########
import time
start_time0 = time.time()
import json
import func
import pandas as pd
import numpy as np
from collections import Counter

import warnings
warnings.filterwarnings("ignore")

### Load data from container ###
df = pd.read_csv('/data/act_data.csv').drop('encString', axis=1)
# df = pd.read_csv('actualTestingData.csv')
all_col = df.columns

### Read json file ###
with open('analysis_input.json', 'r') as f:
    input_json = json.load(f)

### Select variables ###
sel_col = input_json['variables']
exl_col = input_json['exclude_variables']
if sel_col == "all":
    sel_df = df
    if exl_col != False:
        sel_df = sel_df.drop(exl_col, axis=1)
    col = sel_df.columns
else:
    check_contain = all(elem in all_col  for elem in sel_col)
    if check_contain == True:
        sel_df = df[sel_col]
        col = sel_col
    elif check_contain == False:
        raise LookupError('Mismatch between data columns and selected columns. Please make sure to only select columns that exist in the dataset!') 


### Customize features (sum) ###
feature_sum = input_json['feature_sum']
sum_name = input_json['sum_name']
replace = input_json['replace?']

if feature_sum == False:
    print("No customized features.")
elif len(feature_sum) > 0:
    if type(feature_sum[0]) == str:
        sel_df[sum_name] = sel_df[feature_sum].sum(axis=1)
        if replace == True:
            sel_df = sel_df.drop([feature_sum], axis=1)

    elif type(feature_sum[0]) == list:
        for i in range(0,len(feature_sum)):
            sel_df[sum_name[i]] = sel_df[feature_sum[i]].sum(axis=1)
            if replace == True:
                sel_df = sel_df.drop([feature_sum[i]], axis=1)


### Separate features to numerical and categorical ###
catFea = []
numFea = []
for c in col:
    if len(Counter(sel_df[c].dropna())) > 10:
        numFea.append(c)
    else:
        catFea.append(c)


########## Main executions ##########

def main(input_json, combined_df, col, file_name, ctrl_values):
    ###############################
    # 1.Overview on combined data #
    ###############################

    ### For checking missings ###
    checkMissing = input_json['check_missing'][i]
    if checkMissing == True:
        func.check_missing(combined_df, col, file_name)

    ### For getting some basic info ###
    basicInfo = input_json['basic_Information'][i]
    if basicInfo == True:
        func.data_describe(combined_df, col, file_name)


    ### Function for correlation matrix ###
    CorrMatrix = input_json['correlation_matrix'][i]
    if CorrMatrix == True:
        func.corr_Matrix(combined_df[col], file_name)

    ### Function for distribution plot ###
    dist_plot = input_json["Distribution_Plot"][i]
    if dist_plot == True:
        for c in col:
            func.dist_Plot(combined_df,c,ctrl_values,file_name)


    print("Basic info took", time.time() - start_time0, "to run")
    
    ###############################
    # 2. Machine Learning Models ##
    ###############################

    ### Get parameters users set ###
    task = input_json['task'][i]
    print('\n\n')
    if task != False: 
        start_time1 = time.time()
        task = task.lower()
        model = input_json['model'][i].lower()
        scoring = input_json['evaluation_methods'][i]
        kFold = input_json['k_fold'][i]
        params = input_json['parameters'][i]


        ### set up restrictions for inputs ###
        scoring_reg = ["neg_mean_absolute_error","neg_mean_squared_error","neg_mean_squared_log_error","r2"]
        scoring_cls = ['precision', 'recall', 'f1', 'roc_auc']

        ### Separate features and target class
        target_feature = input_json['target_feature'][i]
        training_features = input_json['training_features'][i]
        if type(target_feature) != str:
            raise ValueError('Please provide the name of ONE target feature!')
        
        if target_feature not in combined_df.columns:
            raise ValueError('Please provide target features from the dataset!')

        ####################################
        ### Training and target features ###
        ####################################
        print('*************************************************')
        print('Missing values in training and target features:')
        combined_df_selected = combined_df[training_features+ [target_feature]]
        print(pd.isnull(combined_df_selected).sum())
        combined_df_selected = combined_df_selected[np.invert(pd.isnull(combined_df_selected).any(axis=1))]
        print('Missing values are removed by default if you did not provide replacing value.')
        print("The number of instances(rows): ", len(combined_df_selected))
        print('*************************************************')

        features = combined_df_selected[training_features]
        target = combined_df_selected[target_feature]

        ####################################
        ########## Choose models ###########
        ####################################
        if task == 'regression':
            if all(item in scoring_reg  for item in scoring):
                results = func.RegressionModel(model, params, features, target, scoring, kFold)
            else:
                raise LookupError('Sorry, so far we only support mean_absolute_error, mean_squared_error, mean_squared_log_error, r2 to evaluation regression models.')
                
        elif task == 'classification':
            if all(item in scoring_cls  for item in scoring):
                results = func.ClassificationModel(model, params, features, target, scoring, kFold)
            else:
                raise LookupError('Sorry, so far we only support Precision, Recall, F1-score, ROC to evaluation classification models.')

        else:
            raise LookupError('Sorry! Only classification and regression can be handled so far. We are still developing other functions. Thanks! ')


        ####################################
        ########## Output restuls ##########
        ####################################

        # file = open('output/%s_%s_result.txt' %(file,input_json['model']), 'w')
        # file.write(results)
        # file.close()


        avgs = []
        values = []
        coef_list = []
        for key in results.keys():
            if key == 'estimator':
                for model in results[key]:
                    coef_list.append(list(model.coef_))
            else:
                avg = results[key].mean()
                avgs.append(avg)

                value = results[key].tolist()
                values.append(value)
        save_keys = ['coef_'] + ['AVG_results'] + list(results.keys())   
        save_values = [coef_list] + [avgs] + values 
        save_results = dict(zip(save_keys, save_values))

        with open('output/%s_result.json' %(file_name), 'w') as fp:
            json.dump(save_results, fp)

        print("%s: Analysis took" %file_name, time.time() - start_time1, "to run")
        print("%s: Result is generated at TSE!" %file_name)


for i in range(0, len(input_json['taskName'])):
    ctrl_var = input_json['control_var'][i]
    taskName = input_json['taskName'][i]

    if ctrl_var == False:
        file_name = taskName
        combined_df = sel_df
        ### Main functions ###
        main(input_json, combined_df, col, file_name, 0)

    else:
        for c in catFea:
            if c != ctrl_var:
                func.plot_catCat(combined_df, ctrl_var, c, file_name)
    
        ctrl_values = input_json['control_values'][i]
        for j in ctrl_values:
            file_name = taskName + '_' + ctrl_var + '_' + str(j)
            if type(j) != list:
                combined_df = sel_df[sel_df[ctrl_var]==j]
            elif type(j) == list:
                combined_df = sel_df[ (j[0]<=sel_df[ctrl_var]) & (sel_df[ctrl_var]<j[1])]
            ### Main functions ###
            main(input_json, combined_df, col, file_name, j)


