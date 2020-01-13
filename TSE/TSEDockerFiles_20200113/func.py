import os
import errno
import numpy as np
import json
from math import pi
import pandas as pd
import seaborn as sns
from decimal import Decimal
from collections import Counter
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_squared_log_error,r2_score, make_scorer
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score, roc_auc_score

###########################################
### Function for checking missing values ##
###########################################
def check_missing(df, col, file_name):
    
    ##### Replace customized missing valve #####
    mis_value_code = None  # Input #
    if mis_value_code != None :
        df = df.replace({mis_value_code : np.nan})
    
    ##### Search missing valves #####
    missing  = 0
    misVariables = []
    CheckNull = df.isnull().sum()
    for var in range(0, len(CheckNull)):
        if CheckNull[var] != 0:
            misVariables.append([col[var], CheckNull[var], round(CheckNull[var]/len(df),3)])
            missing = missing + 1

    if missing == 0:
        print('Dataset is complete with no blanks.')
    else:
        print('Totally, %d features have missing values (blanks).' %missing)
        df_misVariables = pd.DataFrame.from_records(misVariables)
        df_misVariables.columns = ['Variable', 'Missing', 'Percentage (%)']
        sort_table = df_misVariables.sort_values(by=['Percentage (%)'], ascending=False)
        # display(sort_table.style.bar(subset=['Percentage (%)'], color='#d65f5f'))
        
        outputFile = 'output/%s_missings.csv'%file_name
        os.makedirs(os.path.dirname(outputFile), exist_ok=True)
        sort_table.to_csv(outputFile)
        print('************************************************')
        print('Check missing outcome is saved to output/%s_missings.csv' %file_name)


###########################################
# Function for variable basic information #
###########################################
def data_describe(df, col, file_name):
    outputFile = 'output/%s_describe.csv' %file_name
    os.makedirs(os.path.dirname(outputFile), exist_ok=True)
    df.describe().to_csv(outputFile)
    print('There is %d rows and %d columns' %(len(df), len(col)))
    print('Data description is done!')

###########################################
### Function for plot Correlation Matrix ##
###########################################
def corr_Matrix(df, file_name):

    corr = df.corr() 

    outputFile = 'output/Output_CM/%s.csv' %file_name
    os.makedirs(os.path.dirname(outputFile), exist_ok=True)
    corr.to_csv(outputFile)
    print('************************************************')
    print("Correlation matrix table is done!")


##########################################
### Function for plotting Distribution ###
##########################################

def dist_Plot (df,featureName,age_range,file_name):
    F = featureName
    fea = df[F].dropna()
    mu = fea.mean()
    sigma = fea.std()

    hist, edges = np.histogram(fea, density=True)#, bins=120)
    x = np.linspace(fea.min(), fea.max(), len(df))
    pdf = 1/(sigma * np.sqrt(2*np.pi)) * np.exp(-(x-mu)**2 / (2*sigma**2))
    df_dist = pd.DataFrame.from_records([hist, edges, x, pdf]).transpose()
    df_dist.columns = ['%s_%s_hist'%(F,str(age_range)), \
                        '%s_%s_edges'%(F,str(age_range)), \
                        '%s_%s_x'%(F,str(age_range)), \
                        '%s_%s_pdf'%(F,str(age_range))]
    return df_dist


###############################
#### Plot Categorical vars ####
###############################
def plot_catCat(df, fea_1, fea_2, file_name):
    print(fea_1, fea_2)
    temp = df[[fea_1,fea_2]] ###
    temp = temp.replace(np.nan, -9999, regex=True)
    var_1_keys = sorted(list(Counter(temp[fea_1].tolist()).keys()),reverse=True)
    var_2_keys = sorted(list(Counter(temp[fea_2].tolist()).keys()))
    var_list = []
    for i in var_1_keys:
        var2_list = []
        cnt_var = Counter(temp[temp[fea_1]==i][fea_2])
        for k in var_2_keys:
            if k in sorted(cnt_var.keys()):
                var2_list.append(cnt_var[k])
            else:
                var2_list.append(0)
        var_list.append(var2_list)

    var_df = pd.DataFrame.from_records(var_list,columns=var_2_keys)
    var_df.index=var_1_keys

    outputFile = "output/%s_CatCat.csv" %file_name
    os.makedirs(os.path.dirname(outputFile), exist_ok=True)
    # var_df.to_csv(outputFile)

    if os.path.exists(outputFile) == False:
        with open(outputFile, 'w') as f:
            f.write("Table for %s - %s \n" %(fea_1,fea_2))
            var_df.to_csv(f)
    elif os.path.exists(outputFile) == True:
        with open(outputFile, 'a') as f:
            f.write("Table for %s - %s \n" %(fea_1,fea_2))
            var_df.to_csv(f)

    print('************************************************')
    print("Categorical-Categorical feature plot is done!")



############################################################
#### Train on the Splited training and testing dataset  ####
############################################################
def splitDataTraining (task, model, features, target, scoring):
    x_train,x_test,y_train,y_test = train_test_split(features, target, random_state = 1)
    model.fit(x_train,y_train)
    model_train_pred = model.predict(x_train)
    model_test_pred = model.predict(x_test)
    results = str()

    if task == "regression":
        if "neg_mean_absolute_error" in scoring: 
            results = 'MAE train data: %.3f, MAE test data: %.3f' % (
            mean_absolute_error(y_train,model_train_pred),
            mean_absolute_error(y_test,model_test_pred)) 
        if "neg_mean_squared_error" in scoring: 
            results = results + '\n' + 'MSE train data: %.3f, MSE test data: %.3f' % (
            mean_squared_error(y_train,model_train_pred),
            mean_squared_error(y_test,model_test_pred)) 
        if "neg_mean_squared_log_error" in scoring: 
            results = results + '\n' + 'MSLE train data: %.3f, MSLE test data: %.3f' % (
            mean_squared_log_error(y_train,model_train_pred),
            mean_squared_log_error(y_test,model_test_pred)) 
        if "r2" in scoring: 
            results = results + '\n' +'R2 train data: %.3f, R2 test data: %.3f' % (
            r2_score(y_train,model_train_pred),
            r2_score(y_test,model_test_pred))

        return results, model

    elif task == "classification":
        if "precision" in scoring: 
            results = 'Precision train data: %.3f, Precision test data: %.3f' % (
            precision_score(y_train,model_train_pred),
            precision_score(y_test,model_test_pred)) 
        if "recall" in scoring: 
            results = results + '\n' +'Recall train data: %.3f, Recall test data: %.3f' % (
            recall_score(y_train,model_train_pred),
            recall_score(y_test,model_test_pred)) 
        if "f1" in scoring: 
            results = results + '\n' +'F1-score train data: %.3f, F1-score test data: %.3f' % (
            f1_score(y_train,model_train_pred),
            f1_score(y_test,model_test_pred)) 
        if "roc_auc" in scoring: 
            results = results + '\n' +'ROC train data: %.3f, ROC test data: %.3f' % (
            roc_auc_score(y_train,model_train_pred),
            roc_auc_score(y_test,model_test_pred))

        return results, model
