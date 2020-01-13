
########## Simple Linear Regression ##########
import os
import time
import json
import numpy as np
import pandas as pd
from collections import Counter
import func
import MLmodel
import warnings
warnings.filterwarnings("ignore")
from sklearn.model_selection import cross_validate

start_time0 = time.time()

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


### For checking data types ###
sel_df.dtypes.to_csv('/output/dataType', header=False)
# Convert to numeric, string will be converted to Nan
sel_df = sel_df.apply(pd.to_numeric,errors='coerce')


### Customize features (sum) ###
customize_fea = input_json['customize_features']
if customize_fea == True:
    combined_df = MLmodel.sum_features(sel_df)
else:
    combined_df = sel_df


### Separate features to numerical and categorical ###
catFea = []
numFea = []
col = sel_df.columns
for c in col:
    if len(Counter(sel_df[c].dropna())) > 10:
        numFea.append(c)
    else:
        catFea.append(c)


############# Main executions #############
file_name = input_json['taskName']
ctrl_values = input_json['control_values']


### 1.Overview on combined data ###
#############################
### For checking missings ###
#############################
checkMissing = input_json['check_missing']
if checkMissing == True:
    func.check_missing(combined_df, col, file_name)

###################################
### For getting some basic info ###
###################################
basicInfo = input_json['basic_Information']
if basicInfo == True:
    func.data_describe(combined_df, col, file_name)

#######################################
### Function for correlation matrix ###
#######################################
CorrMatrix = input_json['correlation_matrix']
if CorrMatrix == True:
    func.corr_Matrix(combined_df[col], file_name)

existFile = "output/%s_CatCat.csv" %file_name
if os.path.exists(existFile):
    os.remove(existFile)

######################################
### Function for distribution plot ###
######################################
dist_plot = input_json["Distribution_Plot"]
if dist_plot == True:
    for c in range(0,len(col)):
        df_dist = func.dist_Plot(combined_df,col[c],ctrl_values,file_name)
        if c == 0:
            save_dist = df_dist
        else: 
            save_dist = pd.concat([save_dist,df_dist],axis=1, join='inner')
    outputFile = "output/%s_Dist.csv" %file_name
    os.makedirs(os.path.dirname(outputFile), exist_ok=True)
    # df_dist.to_csv(outputFile)
    
    if os.path.exists(outputFile) == False:
        with open(outputFile, 'w') as f:
            save_dist.to_csv(f)
    elif os.path.exists(outputFile) == True:
        with open(outputFile, 'a') as f:
            save_dist.to_csv(f)

    print('************************************************')
    print('Distribution plot is done')


print("Basic info took", time.time() - start_time0, "to run")


##### 2. Machine Learning Models #####
task = input_json['task'].lower()
print('\n***** Start training models *****\n')

if task != False: 

    start_time1 = time.time()
    ### Get parameters users set ###
    kFold = input_json['k_fold']
    scoring = input_json['evaluation_methods']

    ### set up restrictions for inputs ###
    scoring_reg = ["neg_mean_absolute_error","neg_mean_squared_error","neg_mean_squared_log_error","r2"]
    scoring_cls = ['precision', 'recall', 'f1', 'roc_auc']

    ### Check inputed scoring  ### 
    if task == 'regression':
        if all(item in scoring_reg  for item in scoring):
            print("Regression evaluation metrics are fine!")
        else:
            raise LookupError('Sorry, so far we only support mean_absolute_error, mean_squared_error, mean_squared_log_error, r2 to evaluation regression models.')
    
    elif task == 'classification':
        if all(item in scoring_cls  for item in scoring):
            print("Classification evaluation metrics are fine!")
        else:
            raise LookupError('Sorry, so far we only support Precision, Recall, F1-score, ROC to evaluation classification models.')
    
    else:
        raise LookupError("K-Fold has to be an integer (>=3) or 0 (No cross validation)")


    num_models = input_json['num_models']    
    num_training = input_json['num_training']

    print('Start checking if training and target features are in the dataset.')
    print('... ...')

    ### Define training and target features ###
    mode = 'checking'
    model_name, features, target = MLmodel.defineFeatures(combined_df, mode)

    if len(model_name) != len(features):
        raise ValueError("Length of models names needs to match with length of training features.")


    ### First, check if values are in the datasets before training models ###
    for set_f in features: 
        for each_f in set_f:
            if each_f not in combined_df.columns:
                print(each_f, " is not in the dataset")
                raise ValueError('Please provide existing training features from the dataset!')

    for each_t in target: 
        if each_t not in combined_df.columns:
            print(each_t, " is not in the dataset")
            raise ValueError('Please provide existing target features from the dataset!')
    print('All training and target features are in the dataset.')


    #########################################
    ######### Choose and run models #########
    #########################################

    for m in range(0, len(model_name)): 
        print('Start training %s' %m)
        start_time_each = time.time()
        model = MLmodel.defineMLModels(model_name[m])
        
        for i_training in range(0, num_training-1):
            model_setting = [m, i_training]
            model_name, features, target, target_name = MLmodel.defineFeatures(combined_df, model_setting)

            ### If use cross validation ###
            if kFold == 0:
                results, model = func.splitDataTraining(task, model, features, target, scoring)

            elif kFold > 2:
                results = cross_validate(model, features, target, scoring=scoring, cv=kFold, error_score=np.nan, return_estimator=True, return_train_score=True)

            else:
                raise LookupError("K-Fold has to be an integer (>=3) or 0 (No cross validation)")

            ### Write output results ###
            MLmodel.writeOutput(kFold, model_name, m, results, model, target_name)
        print("%s Model training took" %model_name[m], time.time() - start_time_each, "to run")
    
    ### Write output results ###
    print("\nIn total, Machine Learning models training took", time.time() - start_time1, "to run")



