import os
import errno
import numpy as np
from math import pi
import pandas as pd
import seaborn as sns
from decimal import Decimal
from collections import Counter
# from bokeh.io import export_png
import matplotlib.pyplot as plt
from bokeh.transform import cumsum
from bokeh.io import output_file, show
from bokeh.core.properties import value
from bokeh.transform import factor_cmap, cumsum
from bokeh.models import HoverTool,ColumnDataSource
from bokeh.plotting import figure, show, output_file,save
from bokeh.palettes import Category10,Spectral10,Paired

import warnings
warnings.filterwarnings('ignore')


###########################################
### Function for checking missing values ##
###########################################
def check_missing(df, col, file):
    
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
        
        outputFile = 'output/%s_missings.csv' %file
        os.makedirs(os.path.dirname(outputFile), exist_ok=True)
        sort_table.to_csv(outputFile)
        print('Check missing outcome is saved to Output/%s_missings.csv' %file)
    print('Missing values check is done!')

def data_describe(df, col, file):
    outputFile = 'output/%s_describe.csv' %file
    os.makedirs(os.path.dirname(outputFile), exist_ok=True)
    df.describe().to_csv(outputFile)
    print('There is %d rows and %d columns' %(len(df), len(col)))
    print('Data description is done!')

###########################################
### Function for plot Correlation Matrix ##
###########################################
def corr_Matrix(df, file):
    sns.set(style="white")
    corr = df.corr() # [df_avg['SEX']=='M']
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
    plt.title('Correlation Matrix in %s' % file)

    filename = 'output/Output_CM/%s.png' %file
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename)
    print('Correlation Matrix plot is done')
    plt.clf()


#######################################
# Function for plotting cat features ##
#######################################
def cate_Dist(df,featureName, file):

    cnt = Counter(df[featureName].dropna())

    TOOLTIPS = [
        ("Counts", "$counts")
    ]
    
    feature = list(map(str,list(cnt.keys())))
    counts = list(map(str,list(cnt.values())))
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

    filename = "output/Output_categocial/%s_%s.html" %(file,featureName)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    save(p, filename=filename)
    print('%s - Distribution plot is done' %featureName)

##########################################
### Function for plotting Distribution ###
##########################################
def make_hist_plot(title, hist, edges, x, pdf,featureName):
    p = figure(title=title, toolbar_location='below', background_fill_color="#fafafa")
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], 
           fill_color="navy", line_color="white", alpha=0.5)
    p.line(x, pdf, line_color="#ff8888", line_width=4, alpha=0.7, legend="PDF")
#     p.line(x, cdf, line_color="orange", line_width=2, alpha=0.7, legend="CDF")

    # p.x_range.start = 0
    # p.x_range.end = 8000
    p.y_range.start = 0
    p.legend.location = "center_right"
    p.legend.background_fill_color = "#fefefe"
    p.xaxis.axis_label = featureName
    p.yaxis.axis_label = 'Pr(%s)' %featureName
    p.grid.grid_line_color="white"
    return p

def dist_Plot (df,featureName,file):
    F = featureName
    fea = df[F].dropna()
    mu = fea.mean()
    sigma = fea.std()

    hist, edges = np.histogram(fea, density=True) # bins=

    x = np.linspace(fea.min(), fea.max(), len(df))
    pdf = 1/(sigma * np.sqrt(2*np.pi)) * np.exp(-(x-mu)**2 / (2*sigma**2))
    #   cdf = (1+scipy.special.erf((x-mu)/np.sqrt(2*sigma**2)))/2
    p = make_hist_plot("Distribution of %s in %s (μ=%d, σ=%s)" %(featureName, file, mu, sigma), hist, edges, x, pdf,featureName)
#     show(p)
    filename = "output/Output_Dist/%s_%s.html" %(file,featureName)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    save(p, filename=filename)
    print('%s - Distribution plot is done' %featureName)

##########################################
######## Function for box plot ###########
##########################################
def box_Plot(df, featureSet, file):
    sns.set(style="ticks", palette="pastel")

    # Draw a nested boxplot to show bills by day and time
    p = sns.boxplot(x=featureSet[0], y=featureSet[1],
                hue=featureSet[2], palette=Spectral10, data=df)

    sns.despine(offset=10, trim=True)
    filename = "output/Output_BoxPlot/%s_%s_%s_%s.png" %(featureSet[0],featureSet[1],featureSet[2],file)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename)
    plt.clf()

##########################################
### Function for cat-num relation plot ###
##########################################
def plot_catNum(df,featureSet,file):
    cat_feature = featureSet[0]
    num_feature = featureSet[1]
    tar_feature = featureSet[2]
    
    sns.set()
    p = sns.catplot(x=cat_feature, y=num_feature, hue=tar_feature, kind="violin", data=df, palette = 'muted', aspect=2)

    filename = "output/Output_CatNum/%s_%s_%s_%s.png" %(featureSet[0],featureSet[1],featureSet[2],file)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    p.savefig(filename)
    print('Categorical-numerical features plot is done')
    plt.clf()
##########################################
### Function for num-num relation plot ###
##########################################
def plot_numNum(df,featureSet,file):
    num1_feature = featureSet[0]
    num2_feature = featureSet[1]
    tar_feature = featureSet[2]
    
    if tar_feature == 'None':
        sns.set(style="white")
        p = sns.jointplot(x=num1_feature, y=num2_feature, data = df, kind="kde", color="b")
        p.plot_joint(plt.scatter, c="r", s=30, linewidth=1, marker="+")
        
        filename = "output/Output_NumNum/%s_%s_%s.png" %(featureSet[0],featureSet[1],featureSet[2])
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        p.savefig(filename)
        
    else:
        p = sns.lmplot(x=num1_feature, y=num2_feature, hue=tar_feature, data=df, \
                   palette = 'magma', height = 6)
        filename = "output/Output_NumNum/%s_%s_%s_%s.png" %(featureSet[0],featureSet[1],featureSet[2],file)
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        p.savefig(filename)
    print('Numerical-numerical features plot is done')
    plt.clf()