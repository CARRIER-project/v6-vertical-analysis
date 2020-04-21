#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
TODO: This script includes all sub-functions which are needed by the genenral analysis. 
Until 25-03-2020, the following functions has been implemented in this script:
1. Basic description of combined data (from pandas.dataframe.desribe)
2. Missing values and percentage of each variables
3. Correlation Matrix (plot)
4. Distributed plot
5. Split the dataset
6. Machine learning training
7. Evaluation

"""

import os
import numpy as np
import pandas as pd
import seaborn as sns
from scipy import stats
from collections import Counter
import matplotlib.pyplot as plt
from bokeh.plotting import figure, save
import redacted_logging as rlog
logger = rlog.get_logger(__name__)

from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_squared_log_error,r2_score, make_scorer
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score, roc_auc_score

###########################################
### Function for checking missing values ##
###########################################
def check_missing(data_frame, column_names, file_name):
    """check missing values in all variables, write the missing values table as an output file

    Args:
        data_frame (pandas.DataFrame): the dataset with selected features.
        column_names (list) : the column names of data_frame
        file_name(str): the name of the input data file

    Returns:
        No return variables but generate "output/*file_name*_missings.csv"
    """

    ##### Search missing valves #####
    missing  = 0
    misVariables = []
    CheckNull = data_frame.isnull().sum()
    for var in range(0, len(CheckNull)):
        if CheckNull[var] != 0:
            misVariables.append([column_names[var], CheckNull[var], round(CheckNull[var]/len(data_frame),3)])
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
def data_describe(data_frame, column_names, file_name):
    """Generate basic description table for the data set by using Pandas.DataFrame.describe(), write out the table to a file 

    Args:
        data_frame (pandas.DataFrame): the dataset with selected features.
        column_names (list) : the column names of data_frame
        file_name: the name of the input data file

    Returns:
        No return variables but generate "*file_name*/%s_describe.csv"
    """

    outputFile = 'output/%s_describe.csv' %file_name
    os.makedirs(os.path.dirname(outputFile), exist_ok=True)
    data_frame.describe().to_csv(outputFile)
    logger.info('There are {rows} rows and {columns} columns in the combined dataset'.format(rows=len(data_frame), columns=len(column_names)))
    logger.debug('Data description is done!')

###########################################
### Function for plot Correlation Matrix ##
###########################################
def corr_Matrix(data_frame, file_name):
    """Calculate the correlation matrix of all features and plot the matrix in a heatmap figure saved in PNG format

    Args:
        data_frame (pandas.DataFrame): the dataset with selected features.
        file_name: the name of the input data file

    Returns:
        No return variables but generate "output/Output_CM/*file_name*.png"
    """

    corr = data_frame.corr() 

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
    sns.heatmap(corr,  cmap=cmap, annot=False, #mask=mask,#center=0,
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
    """ Make the histogram plot for presenting the distribution of numerical features

    Args:
        title (str): the given title to the plot
        hist (float): calculated grids 
        edges (float): calcuated plot edges
        x (float): x-axis values
        pdf (float): calculated probability distribution function values
        featureName (str): the columns name of one numerical feature

    Returns:
        return plot figure
    """

    p = figure(title=title, toolbar_location='below', background_fill_color="#fafafa")
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], 
           fill_color="navy", line_color="white", alpha=0.5)
    p.line(x, pdf, line_color="#ff8888", line_width=4, alpha=0.7, legend="PDF")

    # p.x_range.start = 0
    # p.x_range.end = 8000
    # p.y_range.start = 0
    p.legend.location = "center_right"
    p.legend.background_fill_color = "#fefefe"
    p.xaxis.axis_label = 'Cost'
    p.yaxis.axis_label = 'Pr(cost)'
    p.grid.grid_line_color="white"
    return p

def dist_Plot (data_frame,featureName,ctrl_value):
    """Plot all numerical features and save them in PNG format

    Args:
        data_frame (pandas.DataFrame): the dataset with selected features.
        featureName (str): the columns name of one numerical feature.
        file_name (str): the name of the input data file

    Returns:
        No return variables but save a plot as "output/Output_Dist/*file_name*_*featureName*.html"
    """

    F = featureName
    fea = data_frame[F].dropna()
    mu = fea.mean()
    sigma = fea.std()

    hist, edges = np.histogram(fea, density=True)#, bins=120)
    x = np.linspace(fea.min(), fea.max(), len(data_frame))
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


############################################################
#### Train on the Splited training and testing dataset  ####
############################################################
def splitDataTraining (task, model, features, target, test_size, scoring):
    """ Split the dataset and train the machine leanring model

    Args:
        task (str): regression or classification
        model (str): machine learning model name
        features (list): the features are included in the training model
        target (str): the column name of the target feature
        test_size (float): the ratio of training and testing data
        scoring (str/list): the names of evaluation methods from Scikit Learn

    Returns:
        training results
    """

    if test_size == 1:
        logger.info("The whole dataset will be used for training!")
        try:
            model.fit(features,target)
            params = np.append(model.intercept_, model.coef_)
            predictions = model.predict(features)
        except:
            logger.error("Training model failed!")
            raise
        
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
        try:
            x_train,x_test,y_train,y_test = train_test_split(features, target, test_size=test_size,random_state = 1)
            model.fit(x_train,y_train)
            model_train_pred = model.predict(x_train)
            model_test_pred = model.predict(x_test)
        except:
            logger.error("Training model failed!")
            raise
        
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


###########################################
# Function for pairplot #
###########################################
def numeric_pairplot(data_frame, plot_feature_names, hue_feature_name, file_name):
    """Generate pairplot for the numeric features by using Seaborn

    Args:
        data_frame (pandas.DataFrame): the dataset with selected features.
        plot_feature_names (list) : the column names of features to be plotted
        hue_feature_name: the column name of controlled fetures
        file_name: the name of the input data file

    Returns:
        No return variables but generate "*file_name*/%s_pairplot.csv"
    """

    sns.pairplot(data_frame[plot_feature_names],hue=hue_feature_name)

    plt.title('Pairplot for selected numerical features')

    filename = 'output/%s_pairplot.png' %file_name
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename)
    logger.debug("Pairplot is done! \n")
    plt.clf()