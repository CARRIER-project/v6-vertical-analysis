#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This script a sub-function file for requestBasicInfo.py script.
This script includes the implementation of the following functions
1. "data_describe": Basic description of data (from pandas.dataframe.desribe)
2. "check_missing": Missing values and percentage of each variables
3. "corr_Matrix": Correlation Matrix (plot)
4. "cate_Dist", "dist_Plot", "make_hist_plot": Histogram distributed plot
5. "box_Plot": Box distribution plot
6. "plot_numNum", "plot_catNum": Relations plot between different variables (numerical-numercial features, categorical-numerical features)

"""

import os
import sys
import numpy as np
import pandas as pd
import seaborn as sns
from collections import Counter
import matplotlib.pyplot as plt
from bokeh.transform import factor_cmap
from bokeh.models import ColumnDataSource
from bokeh.plotting import figure,save
from bokeh.palettes import Spectral10


import redacted_logging as rlog
logger = rlog.get_logger(__name__)

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
    for variable_item in range(0, len(CheckNull)):
        if CheckNull[variable_item] != 0:
            misVariables.append([column_names[variable_item], CheckNull[variable_item], round(CheckNull[variable_item]/len(data_frame),3)])
            missing = missing + 1

    if missing == 0:
        logger.info('Dataset is complete with no blanks.')
    else:
        logger.info('Totally, %d features have missing values (blanks).' %missing)
        df_misVariables = pd.DataFrame.from_records(misVariables)
        df_misVariables.columns = ['Variable', 'Missing', 'Percentage (%)']
        sort_table = df_misVariables.sort_values(by=['Percentage (%)'], ascending=False)
        # display(sort_table.style.bar(subset=['Percentage (%)'], color='#d65f5f'))
        
        outputFile = 'output/%s_missings.csv' %file_name
        os.makedirs(os.path.dirname(outputFile), exist_ok=True)
        sort_table.to_csv(outputFile)
        logger.info('Check missing outcome is saved to output/%s_missings.csv' %file_name)
    logger.debug('Missing values check is done!')

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
    logger.info('There is %d rows and %d columns' %(len(data_frame), len(column_names)))
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
    sns.set(style="white")
    corr = data_frame.corr() 
    # Generate a mask for the upper triangle
    mask = np.zeros_like(corr, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(15, 15))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(220, 10, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr,  cmap=cmap, annot=False, vmax=0.7, vmin=-0.7, #mask=mask,#center=0,
                square=True, linewidths=.2, cbar_kws={"shrink": 0.8})
    plt.title('Correlation Matrix in %s' % file_name)

    filename = 'output/Output_CM/%s.png' %file_name
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename)
    logger.debug('Correlation Matrix plot is done')
    plt.clf()


#######################################
# Function for plotting cat features ##
#######################################
def cate_Dist(data_frame, featureName, file_name):

    """Plot all categorical features and save them in PNG format

    Args:
        data_frame (pandas.DataFrame): the dataset with selected features.
        featureName (str): the columns name of one categorical feature.
        file_name(str): the name of the input data file.

    Returns:
        No return variables but generate the plot - "output/Output_categocial/*file_name*_*featureName*.html"
    """

    count_unique_values = Counter(data_frame[featureName].dropna())

    TOOLTIPS = [
        ("Counts", "$counts")
    ]
    
    feature = list(map(str,list(count_unique_values.keys())))
    counts = list(map(str,list(count_unique_values.values())))
    source = ColumnDataSource(data=dict(feature=feature, counts=counts))
    
    p = figure(x_range=feature, tools="hover", tooltips="@feature: @counts", \
            toolbar_location='below', title="%s Counts" %featureName)
    p.vbar(x='feature', top='counts', width=0.5, source=source, legend="feature",
        line_color='white', fill_color=factor_cmap('feature', palette=Spectral10, factors=feature))

    p.xgrid.grid_line_color = None
    p.y_range.start = 0
    # p.y_range.end = 9
    p.legend.orientation = "horizontal"
    p.legend.location = "top_center"

    filename = "output/Output_categocial/%s_%s.html" %(file_name,featureName)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    save(p, filename=filename)
    logger.debug('%s - Distribution plot is done' %featureName)

##########################################
### Function for plotting Distribution ###
##########################################
def make_hist_plot(title, hist, edges, x, pdf,featureName):
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
    p.y_range.start = 0
    p.legend.location = "center_right"
    p.legend.background_fill_color = "#fefefe"
    p.xaxis.axis_label = featureName
    p.yaxis.axis_label = 'Pr(%s)' %featureName
    p.grid.grid_line_color="white"
    return p

def dist_Plot (data_frame,featureName,file_name):
    """Plot all numerical features and save them in PNG format

    Args:
        data_frame (pandas.DataFrame): the dataset with selected features.
        featureName (str): the columns name of one numerical feature.
        file_name (str): the name of the input data file

    Returns:
        No return variables but save a plot as "output/Output_Dist/*file_name*_*featureName*.html"
    """
    try: 
        F = featureName
        fea = data_frame[F].dropna()
        mu = fea.mean()
        sigma = fea.std()

        hist, edges = np.histogram(fea, density=True) 

        x = np.linspace(fea.min(), fea.max(), len(data_frame))
        pdf = 1/(sigma * np.sqrt(2*np.pi)) * np.exp(-(x-mu)**2 / (2*sigma**2))
    except:
        logger.warning("%s has a wrong data type which cannot be plotted!" %featureName)
    else:    
        p = make_hist_plot("Distribution of %s in %s (μ=%d, σ=%s)" %(featureName, file_name, mu, sigma), hist, edges, x, pdf,featureName)

        filename = "output/Output_Dist/%s_%s.html" %(file_name,featureName)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        save(p, filename=filename)
        logger.debug('%s - Distribution plot is done' %featureName)
    

##########################################
######## Function for box plot ###########
##########################################
def box_Plot(data_frame, featureSet, file_name, catFea):
    """Plot a single variable distribution in a box style
    Args:
        data_frame (pandas.DataFrame): the dataset with selected features.
        featureSet (list) : a list (three) of features to plot the box distribution plot.
        catFea (list): a list of all categorical features in the dataset.
        file_name(str): the name of the input data file.

    Returns:
        No return variables but save a plot as output/Output_BoxPlot/*file_name*.png"
    """

    sns.set(style="ticks", palette="pastel")

    cat_feature = featureSet[0]
    num_feature = featureSet[1]

    if cat_feature not in catFea:
        logger.error("%s is not a categorical feature!" %cat_feature)
        sys.exit("Execution interrupted!")
    else:
        if len(featureSet) == 3:
            tar_feature = featureSet[2]
            if tar_feature not in catFea:
                logger.error("%s is not a categorical feature!" %tar_feature)
                sys.exit("Execution interrupted!")
            file_N = featureSet[0]+'_'+featureSet[1]+'_'+featureSet[2]+'_'+file_name
        elif len(featureSet) == 2:
            tar_feature = None
            file_N = featureSet[0]+'_'+featureSet[1]+'_'+file_name
        else:
            logger.error("3 features are the maximal we can plot.")
            sys.exit("Execution interrupted!")

        p = sns.boxplot(x=cat_feature, y=num_feature,
                    hue=tar_feature, palette=Spectral10, data=data_frame)

        sns.despine(offset=10, trim=True)
        filename = "output/Output_BoxPlot/%s.png" %(file_N)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        plt.savefig(filename)
        logger.debug('%s - box plot is done' %filename)
        plt.clf()

##########################################
### Function for cat-num relation plot ###
##########################################
def plot_catNum(data_frame,featureSet,file_name, catFea):
    """Plot a single numerical feature distribution indicating the relation of one categorical feature
    Args:
        data_frame (pandas.DataFrame): the dataset with selected features.
        featureSet (list) : a list (three) of features to plot the box distribution plot.
        catFea (list): a list of all categorical features in the dataset.
        file_name(str): the name of the input data file.

    Returns:
        No return variables but save a plot as output/Output_CatNum/*file_name*.png"
    """

    cat_feature = featureSet[0]
    num_feature = featureSet[1]

    if cat_feature not in catFea:
        logger.error("%s is not a categorical feature!" %cat_feature)
        sys.exit("Execution interrupted!")
    else:
        if len(featureSet) == 3:
            tar_feature = featureSet[2]
            if tar_feature not in catFea:
                logger.error("%s is not a categorical feature!" %tar_feature)
                sys.exit("Execution interrupted!")
            file_N = featureSet[0]+'_'+featureSet[1]+'_'+featureSet[2]+'_'+file_name
        elif len(featureSet) == 2:
            tar_feature = None
            file_N = featureSet[0]+'_'+featureSet[1]+'_'+file_name
        else:
            logger.error("3 features are the maximal we can plot.")
            sys.exit("Execution interrupted!")
        
        sns.set()
        p = sns.catplot(x=cat_feature, y=num_feature, hue=tar_feature, kind="violin", data=data_frame, palette = 'muted', aspect=2)

        filename = "output/Output_CatNum/%s.png" %(file_N)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        p.savefig(filename)
        logger.debug('Categorical-numerical features plot is done')
        plt.clf()


##########################################
### Function for num-num relation plot ###
##########################################
def plot_numNum(data_frame,featureSet,file_name, catFea):
    """Plot a single numerical feature distribution indicating the relation of another numerical feature
    Args:
        data_frame (pandas.DataFrame): the dataset with selected features.
        featureSet (list) : a list (three) of features to plot the box distribution plot.
        catFea (list): a list of all categorical features in the dataset.
        file_name(str): the name of the input data file.

    Returns:
        No return variables but save a plot as output/Output_NumNum/*file_name*.png"
    """

    num1_feature = featureSet[0]
    num2_feature = featureSet[1]
    if len(featureSet) == 3:
        tar_feature = featureSet[2]
        if tar_feature not in catFea:
                logger.error("%s is not a categorical feature!" %tar_feature)
                sys.exit("Execution interrupted!")
        file_N = featureSet[0]+'_'+featureSet[1]+'_'+featureSet[2]+'_'+file_name
    elif len(featureSet) == 2:
        tar_feature = None
        file_N = featureSet[0]+'_'+featureSet[1]+'_'+file_name
    else:
        logger.error("3 features are the maximal we can plot.")
        sys.exit("Execution interrupted!")

    if tar_feature == None:
        sns.set(style="white")
        p = sns.jointplot(x=num1_feature, y=num2_feature, data = data_frame, kind="kde", color="b")
        p.plot_joint(plt.scatter, c="r", s=30, linewidth=1, marker="+")
        
        filename = "output/Output_NumNum/%s.png" %(file_N)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        p.savefig(filename)
        
    else:
        p = sns.lmplot(x=num1_feature, y=num2_feature, hue=tar_feature, data=data_frame, \
                   palette = 'magma', height = 6)
        filename = "output/Output_NumNum/%s.png" %(file_N)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        p.savefig(filename)
    logger.debug('Numerical-numerical features plot is done')
    plt.clf()