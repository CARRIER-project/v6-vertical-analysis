import os
import errno
import numpy as np
import json
from math import pi
import pandas as pd
import seaborn as sns
from scipy import stats
from decimal import Decimal
from collections import Counter
import matplotlib.pyplot as plt
from bokeh.plotting import figure, show, output_file,save
import redacted_logging as rlog
logger = rlog.get_logger(__name__)

import warnings
warnings.filterwarnings("ignore")

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
        logger.debug('Dataset is complete with no blanks.')
    else:
        logger.info('Totally, {number} features have missing values (blanks).'.format(number=missing))
        df_misVariables = pd.DataFrame.from_records(misVariables)
        df_misVariables.columns = ['Variable', 'Missing', 'Percentage (%)']
        sort_table = df_misVariables.sort_values(by=['Percentage (%)'], ascending=False)
        
        outputFile = 'output/%s_missings.csv'%file_name
        os.makedirs(os.path.dirname(outputFile), exist_ok=True)
        sort_table.to_csv(outputFile)
        logger.debug('Check missing outcome is saved to output/{file}_missings.csv'.format(file=file_name))


###########################################
# Function for variable basic information #
###########################################
def data_describe(df, col, file_name):
    outputFile = 'output/%s_describe.csv' %file_name
    os.makedirs(os.path.dirname(outputFile), exist_ok=True)
    df.describe().to_csv(outputFile)
    logger.info('There are {rows} rows and {columns} columns in the combined dataset'.format(rows=len(df), columns=len(col)))
    logger.debug('Data description is done!')

###########################################
### Function for plot Correlation Matrix ##
###########################################
def corr_Matrix(df, file_name):

    corr = df.corr() 

    outputFile = 'output/CM/%s.csv' %file_name
    os.makedirs(os.path.dirname(outputFile), exist_ok=True)
    corr.to_csv(outputFile)
    logger.debug("Correlation matrix table is done!")


    # Generate a mask for the upper triangle
    mask = np.zeros_like(corr, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(12, 12))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(220, 10, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr,  cmap=cmap, annot=False, mask=mask,#center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": 0.5})
    plt.title('Correlation Matrix in %s' % file_name)

    filename = 'output/CM/%s.png' %file_name
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename)
    logger.debug("Correlation matrix plot is done! \n")
    plt.clf()


##########################################
### Function for plotting Distribution ###
##########################################
def make_hist_plot(title, hist, edges, x, pdf):
    p = figure(title=title, toolbar_location='below', background_fill_color="#fafafa")
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], 
           fill_color="navy", line_color="white", alpha=0.5)
    p.line(x, pdf, line_color="#ff8888", line_width=4, alpha=0.7, legend="PDF")
#     p.line(x, cdf, line_color="orange", line_width=2, alpha=0.7, legend="CDF")

    # p.x_range.start = 0
    # p.x_range.end = 8000
    # p.y_range.start = 0
    p.legend.location = "center_right"
    p.legend.background_fill_color = "#fefefe"
    p.xaxis.axis_label = 'Cost'
    p.yaxis.axis_label = 'Pr(cost)'
    p.grid.grid_line_color="white"
    return p

def dist_Plot (df,featureName,ctrl_value):

    F = featureName
    fea = df[F].dropna()
    mu = fea.mean()
    sigma = fea.std()

    hist, edges = np.histogram(fea, density=True)#, bins=120)
    x = np.linspace(fea.min(), fea.max(), len(df))
    pdf = 1/(sigma * np.sqrt(2*np.pi)) * np.exp(-(x-mu)**2 / (2*sigma**2))

    if ctrl_value == False:
        p = make_hist_plot("Distribution Plot - %s (μ=%d, σ=%s)" \
                        %(F, mu, sigma), hist, edges, x, pdf)
        filename = "output/Dist/%s.html"%(F)
    else:
        p = make_hist_plot("Distribution Plot - %s (%s)  (μ=%d, σ=%s)" \
                        %(F, ctrl_value, mu, sigma), hist, edges, x, pdf)
        filename = "output/Dist/%s_%s.html"%(F,ctrl_value)

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    save(p, filename=filename)

    # ### Write to tables (generated too many numbers) ###
    # df_dist = pd.DataFrame.from_records([hist, edges, x, pdf]).transpose()
    # df_dist.columns = ['%s_%s_hist'%(F,str(ctrl_var)), \
    #                     '%s_%s_edges'%(F,str(ctrl_var)), \
    #                     '%s_%s_x'%(F,str(ctrl_var)), \
    #                     '%s_%s_pdf'%(F,str(ctrl_var))]
    # return df_dist
    # ##################### END  ########################



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

    logger.debug("Categorical-Categorical feature plot is done!")



############################################################
#### Train on the Splited training and testing dataset  ####
############################################################
def splitDataTraining (task, model, features, target, test_size, scoring):
    if test_size == 1:
        logger.info("The whole dataset will be used for training!")
        model.fit(features,target)
        params = np.append(model.intercept_, model.coef_)
        predictions = model.predict(features)
        
        newX = pd.DataFrame({"Constant":np.ones(len(features))}).join(pd.DataFrame(features))
        MSE = (sum((target-predictions)**2))/(len(newX)-len(newX.columns))

        var_b = MSE*(np.linalg.inv(np.dot(newX.T,newX)).diagonal())
        sd_b = np.sqrt(var_b)
        ts_b = params/ sd_b

        p_values =[2*(1-stats.t.cdf(np.abs(i),(len(newX)-1))) for i in ts_b]

        sd_b = np.round(sd_b,3)
        ts_b = np.round(ts_b,3)
        p_values = np.round(p_values,3)
        params = np.round(params,4)

        results = pd.DataFrame()
        results["Coefficients"],results["Standard Errors"],results["t values"],results["Probabilites"] = [params,sd_b,ts_b,p_values]
        
        return results

    elif test_size < 1: 
        x_train,x_test,y_train,y_test = train_test_split(features, target, test_size=test_size,random_state = 1)
        model.fit(x_train,y_train)
        model_train_pred = model.predict(x_train)
        model_test_pred = model.predict(x_test)
        results = pd.DataFrame()

        if task == "regression":
            if "neg_mean_absolute_error" in scoring: 
                results['MAE_train'], results['MAE_test'] = [[mean_absolute_error(y_train,model_train_pred)],[mean_absolute_error(y_test,model_test_pred)]]
            if "neg_mean_squared_error" in scoring: 
                results['MSE_train'], results['MSE_test'] = [[mean_squared_error(y_train,model_train_pred)], [mean_squared_error(y_test,model_test_pred)]]
            if "neg_mean_squared_log_error" in scoring: 
                results['MSLE_train'], results['MSLE_test'] = [[mean_squared_log_error(y_train,model_train_pred)], [mean_squared_log_error(y_test,model_test_pred)]]
            if "r2" in scoring: 
                results['r2_train'], results['r2_test'] = [[r2_score(y_train,model_train_pred)], [r2_score(y_test,model_test_pred)]]
            return results

        elif task == "classification":
            if "precision" in scoring: 
                results['precision_train'], results['precision_test'] = [[precision_score(y_train,model_train_pred)], [precision_score(y_test,model_test_pred)]]
            if "recall" in scoring: 
                results['recall_train'], results['recall_test'] = [[recall_score(y_train,model_train_pred)], [recall_score(y_test,model_test_pred)]]
            if "f1" in scoring: 
                results['f1_train'], results['f1_test'] = [[f1_score(y_train,model_train_pred)], [f1_score(y_test,model_test_pred)]]
            if "roc_auc" in scoring: 
                results['roc_auc_train'], results['roc_auc_test'] = [[roc_auc_score(y_train,model_train_pred)], [roc_auc_score(y_test,model_test_pred)]]

            return results
