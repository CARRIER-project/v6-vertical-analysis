
########## Simple Linear Regression ##########
import time
start_time = time.time()
import json
import func
import pandas as pd
import numpy as np
from collections import Counter

combined_df = pd.read_csv('/data/act_data.csv').drop('encString', axis=1)
col = combined_df.columns

with open('analysis_input.json', 'r') as f:
    input = json.load(f)

### Separate features to numerical and categorical ###
catFea = []
numFea = []
for c in col:
    if len(Counter(combined_df[c].dropna())) > 10:
        numFea.append(c)
    else:
        catFea.append(c)


for i in range(0, len(input['taskName'])):
    file = input['taskName'][i]

    ###############################
    # 1.Overview on combined data #
    ###############################

    ### For checking missings ###
    checkMissing = input['check_missing'][i]
    if checkMissing == True:
        func.check_missing(combined_df, col, file)

    ### For getting some basic info ###
    basicInfo = input['basic_Information'][i]
    if basicInfo == True:
        func.data_describe(combined_df, col, file)


    ### Function for correlation matrix ###
    CorrMatrix = input['correlation_matrix'][i]
    if CorrMatrix == True:
        func.corr_Matrix(combined_df[col], file)

    ### Function for Cat-Num plot ###
    CN_plot = input["Cat_Num_plot"][i]
    if CN_plot == True:
        CN_feature = input["Cat_Num_feature"][i]
        if len(CN_feature) > 0:
            for f in CN_feature:
                print(f)
                func.plot_catNum(combined_df,f,file)

    ### Function for Box plot ###
    BoxPlot = input["Box_plot"]
    if BoxPlot == True:
        BoxPlot_feature = input["Box_plot_feature"]
        if len(BoxPlot_feature) > 0:
            for f in BoxPlot_feature:
                print(f)
                func.box_Plot(combined_df,f,file)

    ### Function for Num-Num plot ###
    NN_plot = input["Num_Num_Plot"][i]
    if NN_plot == True:
        NN_feature = input["Num_Num_feature"][i]
        if len(NN_feature) > 0:
            for f in NN_feature:
                print(f)
                func.plot_numNum(combined_df,f,file)


    ###############################
    # 2. Machine Learning Models ##
    ###############################

    ### Get parameters users set ###
    task = input['task'][i]
    print('\n\n')
    if task != False: 
        task = task.lower()
        model = input['model'][i].lower()
        scoring = input['evaluation_methods'][i]
        kFold = input['k_fold'][i]
        params = input['parameters'][i]
        customize_target = input['customize_target'][i]

        ### set up restrictions for inputs ###
        scoring_reg = ["neg_mean_absolute_error","neg_mean_squared_error","neg_mean_squared_log_error","r2"]
        scoring_cls = ['precision', 'recall', 'f1', 'roc_auc']

        ### Separate features and target class
        target_feature = input['target_feature'][i]
        training_features = input['training_features'][i]
        if type(target_feature) != str:
            print('Please provide the name of ONE target feature!')
        
        if target_feature not in combined_df.columns:
            print('Please provide target features from the dataset!')

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

        if customize_target == False:
            target = combined_df_selected[target_feature]
        elif customize_target == True:
            target = combined_df_selected[target_feature].sum(axis=1)
        features = combined_df_selected[training_features]


        ####################################
        ########## Choose models ###########
        ####################################
        if task == 'regression':
            if all(item in scoring_reg  for item in scoring):
                results = func.RegressionModel(model, params, features, target, scoring, kFold)
            else:
                print('Sorry, so far we only support mean_absolute_error, mean_squared_error, mean_squared_log_error, r2 to evaluation regression models.')
                
        elif task == 'classification':
            if all(item in scoring_cls  for item in scoring):
                results = func.ClassificationModel(model, params, features, target, scoring, kFold)
            else:
                print('Sorry, so far we only support Precision, Recall, F1-score, ROC to evaluation classification models.')

        else:
            print('Sorry! Only classification and regression can be handled so far. We are still developing other functions. Thanks! ')


        ####################################
        ########## Output restuls ##########
        ####################################

        # file = open('output/%s_%s_result.txt' %(file,input['model']), 'w')
        # file.write(results)
        # file.close()

        avgs = []
        values = []
        for key in results.keys():
            avg = results[key].mean()
            avgs.append(avg)

            value = results[key].tolist()
            values.append(value)
        save_keys = ['AVG_results'] + list(results.keys())   
        save_values = [avgs] + values 
        save_results = dict(zip(save_keys, save_values))

        with open('output/%s_%s_result.json' %(file, model), 'w') as fp:
            json.dump(save_results, fp)

        print("%s: Analysis took" %file, time.time() - start_time, "to run")
        print("%s: Result is generated at TSE!" %file)