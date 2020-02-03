
########## Simple Linear Regression ##########
import os
import time
start_time0 = time.time()
import json, sys, yaml
import numpy as np
import pandas as pd
from collections import Counter
import func
import MLmodel
import warnings
warnings.filterwarnings("ignore")
from sklearn.model_selection import cross_validate
import redacted_logging as rlog
logger = rlog.get_logger(__name__)

try:
    ### Load data from container ###
    df = pd.read_csv('/data/act_data.csv').drop('encString', axis=1)
    all_col = df.columns

except FileNotFoundError:
    logger.error("No combined dataset is available!!")


try:
    ### Read json file ###
    with open(r'/input/analysis_input.yaml') as file:
        inputYAML = yaml.load(file, Loader=yaml.FullLoader)
        logger.info("Reading analysis_input.yaml file...")
except FileNotFoundError:
    logger.error("Please provide your analysis input file and mount to the container. '-v $(pwd)/*YOURINPUT.yaml*:/analysis_input.yaml' ")

else:
    ### Select variables ###
    sel_col = inputYAML['variables']
    exl_col = inputYAML['exclude_variables']
    to_num = inputYAML['variables_to_numeric']
    
    if sel_col == "all":
        sel_df = df
        if exl_col != False:
            sel_df = sel_df.drop(exl_col, axis=1)
        col = sel_df.columns

    else:
        # check_contain = all(elem in all_col  for elem in sel_col)
        # if check_contain == True:
        try:
            sel_df = df[sel_col]
            col = sel_col
        # elif check_contain == False:
        except:
            logger.error('Mismatch between data columns and selected columns. Please make sure to only select columns that exist in the dataset!')
            sys.exit("Execution interrupted!")
        
        
    ### For checking data types ###
    sel_df.dtypes.to_csv('/output/dataType', header=False)

    # Convert to numeric, string will be converted to Nan
    if to_num == True:
        sel_df = sel_df.apply(pd.to_numeric,errors='coerce')
        logger.warning("All features are forced to numberic types. Strings become Nan. This might cause analysis mistakes.")


    ### Customize features (sum) ###
    customize_fea = inputYAML['customize_features']
    if customize_fea == True:
        try:
            combined_df = MLmodel.sum_features(sel_df)
        except KeyError:
            logger.error("Features you used in MLmodel.sum_features function are not in the dataset! ")
            sys.exit("Execution interrupted!")
    else:
        combined_df = sel_df


    ############# Main executions #############
    file_name = inputYAML['taskName']
    ctrl_var = inputYAML['control_var']


    ### 1.Overview on combined data ###
    #############################
    ### For checking missings ###
    #############################
    checkMissing = inputYAML['check_missing']
    if checkMissing == True:
        func.check_missing(combined_df, col, file_name)

    ###################################
    ### For getting some basic info ###
    ###################################
    basicInfo = inputYAML['basic_Information']
    if basicInfo == True:
        func.data_describe(combined_df, col, file_name)


    #######################################
    ### Function for correlation matrix ###
    #######################################
    CorrMatrix = inputYAML['correlation_matrix']
    if CorrMatrix == True:
        func.corr_Matrix(combined_df[col], file_name)

    existFile = "output/%s_Corr.csv" %file_name
    if os.path.exists(existFile):
        os.remove(existFile)

    ######################################
    ### Function for distribution plot ###
    ######################################
    dist_plot = inputYAML["Distribution_Plot"]
    if dist_plot == True:
        if ctrl_var == False:
            # ### Write to tables (generated too many numbers) ###
            # for c in range(0,len(col)):
            #     df_dist = func.dist_Plot(combined_df,col[c],ctrl_var)
            #     if c == 0:
            #         save_dist = df_dist
            #     else: 
            #         save_dist = pd.concat([save_dist,df_dist],axis=1, join='inner')

            # outputFile = "output/Dist_tables/%s_Dist.csv" %file_name
            # os.makedirs(os.path.dirname(outputFile), exist_ok=True)
            
            # if os.path.exists(outputFile) == False:
            #     with open(outputFile, 'w') as f:
            #         save_dist.to_csv(f)
            # elif os.path.exists(outputFile) == True:
            #     with open(outputFile, 'a') as f:
            #         save_dist.to_csv(f)
            # ##################### END  ########################
            for c in range(0,len(col)):
                func.dist_Plot(combined_df,col[c],ctrl_var)


        elif ctrl_var in col:
            list_value = list(Counter(combined_df[ctrl_var]).keys())
            if len(list_value) < 6:
                for i_value in list_value:
                    ctrl_combined_df = combined_df[combined_df[ctrl_var]==i_value]
                    for c in range(0,len(col)):
                        if ctrl_var != col[c]:
                            func.dist_Plot(ctrl_combined_df,col[c], str(ctrl_var+'_'+str(i_value)) )
            else: 
                logger.error("Sorry, control variable has too many different values! Please choose categorical variable as control")
                sys.exit("Execution interrupted!")
            
        else:
            logger.error("Please give one variable name or False to 'control_var'.")
            sys.exit("Execution interrupted!")
        
        logger.debug('Distribution plot is done')


    logger.info("Basic info took {runtime:.4f}s to run".format(runtime=(time.time() - start_time0)))


    ##### 2. Machine Learning Models #####
    task = inputYAML['task'].lower()
    logger.debug('Start training models ... ...')

    if task != False: 

        start_time1 = time.time()
        ### Get parameters users set ###
        kFold = inputYAML['k_fold/split_ratio']
        scoring = inputYAML['evaluation_methods']

        ### set up restrictions for inputs ###
        scoring_reg = ["neg_mean_absolute_error","neg_mean_squared_error","neg_mean_squared_log_error","r2"]
        scoring_cls = ['precision', 'recall', 'f1', 'roc_auc']

        ### Check inputed scoring  ### 
        if task == 'regression':
            if all(item in scoring_reg  for item in scoring):
                logger.debug("Regression evaluation metrics are fine!")
            else:
                logger.error("Sorry, so far we only support mean_absolute_error, mean_squared_error, mean_squared_log_error, r2 to evaluation regression models.")
                sys.exit("Execution interrupted!")

        elif task == 'classification':
            if all(item in scoring_cls  for item in scoring):
                logger.debug("Classification evaluation metrics are fine!")
            else:
                logger.error("Sorry, so far we only support Precision, Recall, F1-score, ROC to evaluation classification models.")
                sys.exit("Execution interrupted!")
        
        else:
            logger.error("Task needs to be either classification or regression")
            exit()


        logger.debug('Start checking if training and target features are in the dataset.')
        try: 
            model_name, training_features, target_feature = MLmodel.defineFeatures()
        except KeyError:
            logger.error("Some training and target features are in the dataset! Please check MLmodel.defineFeatures function!")
            sys.exit("Execution interrupted!")


        if len(model_name) != len(training_features):
            logger.error("Length of models names needs to match with length of training features.")
            sys.exit("Execution interrupted!")


        ### First, check if values are in the datasets before training models ###
        for set_f in training_features: 
            for each_f in set_f:
                if each_f not in combined_df.columns:
                    logger.debug("{feature} is not in the dataset".format(feature=each_f))
                    logger.error("Please provide existing training features from the dataset!")
                    sys.exit("Execution interrupted!")

        for each_t in target_feature: 
            if each_t not in combined_df.columns:
                logger.debug("{feature} is not in the dataset".format(feature=each_f))
                logger.error("Please provide existing target features from the dataset!")
                sys.exit("Execution interrupted!")

        logger.info('All training and target features are in the dataset.')


        #########################################
        ######### Choose and run models #########
        #########################################

        ### for save resutls ###
        result_list = [] 
        cnt = 0

        for m in range(0, len(model_name)): 
            logger.debug('Start training {model} ... ...'.format(model=model_name[m]))
            start_time_each = time.time()
            model = MLmodel.defineMLModels(model_name[m])

            model_name, training_features, target_feature = MLmodel.defineFeatures()
            num_training  = len(target_feature)

            for i_training in range(0, num_training):
                model_setting = [m, i_training]
                model_name, features, target, target_name = MLmodel.customizeFeatures(combined_df, model_setting, model_name, training_features, target_feature)


                ### If use cross validation ###
                if kFold <= 1 and kFold > 0:
                    results = func.splitDataTraining(task, model, features, target, kFold, scoring)
                    

                elif kFold > 2 and type(kFold)==int:
                    results = cross_validate(model, features, target, scoring=scoring, cv=kFold, error_score=np.nan, return_estimator=True, return_train_score=True)

                else:
                    logger.error("K-Fold has to be an integer (>=3) or 1 (the whole dataset will be training set) or 0-1 as a split ratio (testing/dataset)")
                    sys.exit("Execution interrupted!")

                ### Write output results ###
                if cnt == (len(model_name) * num_training) - 1:
                    save_file = True
                else:
                    save_file = False

                result_list = MLmodel.writeOutput(kFold, model_name, m, results, result_list, training_features, target_name, save_file)
                
                cnt = cnt + 1
            logger.info("{model} training took {runtime:.4f} to run.".format(model=model_name[m], runtime=(time.time() - start_time_each)))
        
        ### Write output results ###
        logger.info("In total, all models training took {runtime:.4f} to run. ".format(runtime=(time.time() - start_time1)))