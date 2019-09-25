import os
import errno
import numpy as np
from math import pi
import pandas as pd
import seaborn as sns
from decimal import Decimal
from collections import Counter
from bokeh.io import export_png
import matplotlib.pyplot as plt
from bokeh.transform import cumsum
from bokeh.io import output_file, show
from bokeh.core.properties import value
from bokeh.transform import factor_cmap, cumsum
from bokeh.models import HoverTool,ColumnDataSource
from bokeh.plotting import figure, show, output_file
from bokeh.palettes import Category10,Spectral10,Paired

from sklearn import svm
from sklearn.tree import DecisionTreeClassifier
from sklearn.naive_bayes import GaussianNB, BernoulliNB
from sklearn.model_selection import train_test_split, cross_validate
from sklearn.linear_model import LinearRegression,LogisticRegression
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_squared_log_error,r2_score
from sklearn.metrics import classification_report, f1_score, precision_score, recall_score, roc_auc_score

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
        print('************************************************')
        print('Check missing outcome is saved to output/%s_missings.csv' %file)


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
    f, ax = plt.subplots(figsize=(12, 12))

    # Generate a custom diverging colormap
    cmap = sns.diverging_palette(220, 10, as_cmap=True)

    # Draw the heatmap with the mask and correct aspect ratio
    sns.heatmap(corr,  cmap=cmap, annot=False, vmax=0.7, vmin=-0.7, mask=mask,#center=0,
                square=True, linewidths=.5, cbar_kws={"shrink": 0.5})
    plt.title('Correlation Matrix in %s' % file)

    filename = 'output/Output_CM/%s.png' %file
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename)
    print('************************************************')
    print("Correlation matrix is done!")
    plt.clf()
    
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
    plt = sns.catplot(x=cat_feature, y=num_feature, hue=tar_feature, kind="violin", data=df, palette = 'muted', aspect=2)

    filename = "output/Output_CatNum/%s_%s_%s_%s.png" %(featureSet[0],featureSet[1],featureSet[2],file)
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    plt.savefig(filename)
    print('************************************************')
    print("Categorical-numerical feature plot is done!")


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
    print('************************************************')
    print("Numerical-numerical feature plot is done!")
    plt.clf()

###############################
## Linear Regression ######
###############################
def RegressionModel(model, params, features, target, scoring, kFold):
    if model == "linear regression":
        model = LinearRegression(fit_intercept=params['fit_intercept'], \
            normalize=params['normalize'], copy_X=params['copy_X'])
        print('************************************************')
        print(model.get_params())
        print('************************************************')
    else:
        print('Sorry, we are still developing other regression methods.')

    if kFold == 0:
        x_train,x_test,y_train,y_test = train_test_split(features,target, random_state = 1)
        model.fit(x_train,y_train)

        model_train_pred = model.predict(x_train)
        model_test_pred = model.predict(x_test)

        results = str()
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

        return results

    elif kFold > 2:
        results = cross_validate(model, features, target, scoring=scoring, cv=kFold,error_score=np.nan)
        return results

    else:
        print("K-Fold has to be an integer (>=3) or 0 (No cross validation)")



def ClassificationModel(model, params, features, target, scoring, kFold):

    ### Configure models ###
    if model == "logistic regression":
        model = LogisticRegression(class_weight=params['class_weight'], solver=params['solver'], max_iter=params['max_iter'])
    elif model == "SVM":
        model = svm.SVC(kernel=params['kernel'], class_weight=params['class_weight'], verbose=params['verbose'], 
        probability=params['probability'], random_state=params['random_state']) # linear, rbf, poly
    elif model == "gradient boosting":
        model = GradientBoostingClassifier(loss=params['loss'], learning_rate=params['learning_rate'], 
        n_estimators=params['n_estimators'], max_depth=params['max_depth'])
    elif model == "decision tree":
        model = DecisionTreeClassifier(class_weight=params['class_weight'])
    elif model == "random forest":
        model = RandomForestClassifier(n_estimators=params['n_estimators'], max_leaf_nodes=params['max_leaf_nodes'], random_state=params['random_state'],
        class_weight=params['class_weight'],criterion=params['criterion'], max_features = params['max_features']) #entropy gini
    elif model == "bernoulli naive bayes":
        model = BernoulliNB(class_prior=params['class_prior'])  # GaussianNB(priors=[0.5,0.5]) BernoulliNB(class_prior=[1,2]) 
    elif model == "gaussian naive bayes":
        model = GaussianNB(priors=params['priors']) #('SVM', SVM)

    else:
        print('Sorry, we are still developing other classification methods.')

    if kFold == 0:
        x_train,x_test,y_train,y_test = train_test_split(features,target, random_state = 1)
        model.fit(x_train,y_train)

        model_train_pred = model.predict(x_train)
        model_test_pred = model.predict(x_test)

        results = str()
        if "precision" in scoring: 
            results = 'Precision train data: %.3f, Precision test data: %.3f' % (
            precision(y_train,model_train_pred),
            precision(y_test,model_test_pred)) 
        if "recall" in scoring: 
            results = results + '\n' +'Recall train data: %.3f, Recall test data: %.3f' % (
            recall(y_train,model_train_pred),
            recall(y_test,model_test_pred)) 
        if "f1" in scoring: 
            results = results + '\n' +'F1-score train data: %.3f, F1-score test data: %.3f' % (
            f1(y_train,model_train_pred),
            f1(y_test,model_test_pred)) 
        if "roc_auc" in scoring: 
            results = results + '\n' +'ROC train data: %.3f, ROC test data: %.3f' % (
            roc_auc(y_train,model_train_pred),
            roc_auc(y_test,model_test_pred))

        return results

    elif kFold > 2:
        results = cross_validate(model, features, target, scoring=scoring, cv=kFold, error_score=np.nan)
        return results

    else:
        print("K-Fold has to be an integer (>=3) or 0 (No cross validation)")