import os
import errno
import numpy as np
from math import pi
import pandas as pd
import seaborn as sns
from decimal import Decimal
from collections import Counter
import matplotlib.pyplot as plt
from bokeh.transform import cumsum
from bokeh.io import output_file, show
from bokeh.core.properties import value
from bokeh.palettes import Category10,Spectral10,Paired,Category20
from bokeh.plotting import figure, show, output_file,save
from bokeh.models import HoverTool

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
        
        outputFile = 'output/%s_missings.csv' %file
        os.makedirs(os.path.dirname(outputFile), exist_ok=True)
        sort_table.to_csv(outputFile)
        print('Check missing outcome is saved to output/%s_missings.csv' %file)
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
def corr_Matrix(df, age_range, year):
    sns.set(style="white")
    corr = df.corr() # [df_avg['SEX']=='M']
    
    # Generate a mask for the upper triangle
    mask = np.zeros_like(corr, dtype=np.bool)
    mask[np.triu_indices_from(mask)] = True

    # Set up the matplotlib figure
    f, ax = plt.subplots(figsize=(15, 12))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(220, 10, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr,  cmap=cmap, annot=False, vmax=0.7, vmin=-0.7, #mask=mask,#center=0,
                square=True, linewidths=.2, cbar_kws={"shrink": 0.8})
    plt.title('Correlation Matrix (Age between %d to %d) in %s' %(age_range[0],age_range[1],year))

    filename = 'output/Output_CM/%s/CM_%dTo%d.png'%(year,age_range[0],age_range[1])
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename)
    print('Correlation Matrix plot is done')
    plt.clf()

#######################################
### Function for plotting Pie Chart ###
#######################################
def merge(df):
    ### Merge variables ###
    if 'SUM' in df.columns:
        df_merge = df.drop('SUM',axis=1)
     
    merged_col = df_merge.columns
    if 'SEX' in merged_col:
        df_merge = df_merge.drop('SEX',axis=1)
    
    if 'AGE' in merged_col:
        df_merge = df_merge.drop('AGE',axis=1)
        
    if 'GP_registration' in merged_col and 'GP_consult' in merged_col and 'GP_others' in merged_col:
        df_merge['GP'] = df['GP_registration']+df['GP_consult']+df['GP_others']
        df_merge = df_merge.drop(['GP_registration','GP_consult','GP_others'],axis=1)   
         
    if 'transport_seat' in merged_col and 'transport_land' in merged_col:
        df_merge['transport'] = df['transport_seat']+df['transport_land']
        df_merge = df_merge.drop(['transport_seat','transport_land'],axis=1)
        
    if 'basicGGZ' in merged_col and 'longGGZ' in merged_col:
        df_merge['GGZ'] = df['basicGGZ']+df['longGGZ']
        df_merge = df_merge.drop(['basicGGZ', 'longGGZ'],axis=1)
        
    if 'paramedical_phy' in merged_col and 'paramedical_others' in merged_col:
        df_merge['paramedical'] = df['paramedical_phy']+df['paramedical_others']
        df_merge = df_merge.drop(['paramedical_phy','paramedical_others'],axis=1)
    
    merged_col_new = list(df_merge.columns)
    full_col = ['medical_specialist','GP','pharmacy','dental','transport','abroad','paramedical', \
                 'others', 'firstLinePsy', 'GGZ','rehabilitation','nursing']
    order_col = []
    for i in full_col:
        if i in merged_col_new:
            order_col.append(merged_col_new[merged_col_new.index(i)])

    df_merge_ordered = df_merge[order_col]
    return df_merge_ordered 


def pie_Chart(df,age_range, year):

    ### Merge variables ###
    df_merge = merge(df)
    x = (df_merge.sum(axis=0)/len(df_merge)).to_dict()

    data = pd.Series(x).reset_index(name='value').rename(columns={'index':'Categories'})
    data['angle'] = data['value']/data['value'].sum() * 2*pi
    data['color'] = Paired[len(x)]
    data['percentage'] = data['value']/data['value'].sum()
    
    hover = HoverTool(tooltips=[("Categories","@label"),("percentage", "@percentage{%0.2f}")])
    
    p = figure(plot_height=400, title="Pie Chart on costs (Age between %d to %d) in %s" %(age_range[0],age_range[1],year), \
                tools=['save', hover], tooltips="@Categories: @value", x_range=(-0.5, 1.0))
    
    legend_new = []
    for i in range(0,len(data['percentage'])):
        legend_new.append(str(data['Categories'][i])+': '+ str(float(round(Decimal(data['percentage'][i]),4)*100))+"%")
    data['legend_new'] = legend_new
        
    p.wedge(x=0, y=1, radius=0.4, 
            start_angle=cumsum('angle', include_zero=True), end_angle=cumsum('angle'),
            line_color="white", fill_color='color', legend='legend_new', source=data)

    p.axis.axis_label=None
    p.axis.visible=False
    p.grid.grid_line_color = None

    filename = "output/Output_Pie/%s/Pie_%dTo%d.html"%(year,age_range[0],age_range[1])
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    save(p, filename=filename)

    print('Pie plot is done')

##########################################
### Function for plotting Distribution ###
##########################################
def make_hist_plot(title, hist, edges, x, pdf):
    p = figure(title=title, toolbar_location='below', background_fill_color="#fafafa")
    p.quad(top=hist, bottom=0, left=edges[:-1], right=edges[1:], 
           fill_color="navy", line_color="white", alpha=0.5)
    p.line(x, pdf, line_color="#ff8888", line_width=4, alpha=0.7, legend="PDF")
#     p.line(x, cdf, line_color="orange", line_width=2, alpha=0.7, legend="CDF")

    p.x_range.start = 0
    p.x_range.end = 8000
    p.y_range.start = 0
    p.legend.location = "center_right"
    p.legend.background_fill_color = "#fefefe"
    p.xaxis.axis_label = 'Cost'
    p.yaxis.axis_label = 'Pr(cost)'
    p.grid.grid_line_color="white"
    return p

def dist_Plot (df,featureName,age_range,year):
    F = featureName
    fea = df[F].dropna()
    mu = fea.mean()
    sigma = fea.std()

    hist, edges = np.histogram(fea, density=True, bins=120)

    x = np.linspace(fea.min(), fea.max(), len(df))
    pdf = 1/(sigma * np.sqrt(2*np.pi)) * np.exp(-(x-mu)**2 / (2*sigma**2))
    #   cdf = (1+scipy.special.erf((x-mu)/np.sqrt(2*sigma**2)))/2
    p = make_hist_plot("Total healthcare cost in %s (Age between %d to %d)  (μ=%d, σ=%s)" \
                       %(year, age_range[0], age_range[1], mu, sigma), hist, edges, x, pdf)
#     show(p)
    filename = "output/Output_Dist/%s/Dist_%dTo%d.html"%(year,age_range[0],age_range[1])
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    save(p, filename=filename)
    print('Distribution plot is done')

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
### Function for plotting Stacked Area ###
##########################################
def stacked_Plot(df,year):
    N = len(df.columns)

    names = ["%s" % i for i in df.columns]

    p = figure(x_range=(0, len(df)-1), y_range=(0, 10000))
    p.grid.minor_grid_line_color = '#eeeeee'

    p.varea_stack(stackers=names, x='index', color=Category20[N], \
                  legend=[value(x) for x in names], source=df)

    p.legend.location = "top_left"
    p.x_range.start = 0
    p.x_range.end = 90
    p.xaxis.axis_label = 'Age'
    p.yaxis.axis_label = 'Total healthcare cost in %s' %year
    # reverse the legend entries to match the stacked order
    p.legend[0].items.reverse()

#     show(p)
    filename = "output/Output_Stacked/StackedArea_%s.html" %year
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    save(p, filename=filename)

### Give a age range (0-90) ###
def groupAgeRange(df_vektis, age_range, df_stack):
    if type(df_stack) == pd.DataFrame:
        df_vektis_aged = df_vektis[df_vektis['AGE']==age_range]
    else:
        df_vektis_aged = df_vektis[age_range[0]<=df_vektis['AGE']]
        df_vektis_aged = df_vektis_aged[df_vektis['AGE']<=age_range[1]]
        print("The number of insured people between %d to %d: " %(age_range[0],age_range[1]), len(df_vektis_aged))
#     print("The gender balance: ", Counter(df_vektis_aged['SEX']))

    ### As the original data is aggregated data 
    ### so we need to calculate the average costs for per insured person
    df_avg = df_vektis_aged[['SEX','AGE']]
    col = df_vektis_aged.columns
    for i in range(2, len(col)):
        df_avg[col[i]] = df_vektis_aged[col[i]]/df_vektis_aged['BSNs']

    ### Add one column - total healthcare costs ###
    df_avg['SUM'] = df_avg.drop(['SEX','AGE'],axis=1).sum(axis=1, skipna=True)
    
    return df_avg

  
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

    print('Numerical-numerical feature plot is done')
    plt.clf()