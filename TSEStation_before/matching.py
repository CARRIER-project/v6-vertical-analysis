import time
start_time = time.time()

import json, yaml
import pandas as pd
import numpy as np
import redacted_logging as rlog
logger = rlog.get_logger(__name__)

#read input file
try:
    with open(r'security_input.yaml') as file:
        inputYAML = yaml.load(file, Loader=yaml.FullLoader)
        logger.info("Reading request.yaml file...")
except FileNotFoundError:
    logger.error("Cannot find security_input.yaml file!")

else:
    parties = inputYAML['parties']

    # Read all encrypted datasets into a list #
    try:
        smallest = 0
        dataset_list = []
        for p in parties: 
            df_eachParty = pd.read_csv('/data/encrypted_%s.csv' %(p)).set_index('encString')
            dataset_list.append(df_eachParty)
    except:
        logger.error("Verification and decrption failed! No files are able to be executed. Please check your keys.")
    else:
        for i in range(0, len(parties)):
            logger.info('{dataparty} has {datasize} rows'.format(dataparty=parties[i], datasize=len(dataset_list[i])))

        # Order the size of datasets from small to large #
        sizes = []
        for dataset in dataset_list:
            sizes.append(len(dataset))
        order = np.argsort(sizes)

        # Find match records #

        for item in range(0, len(order)): 
            multi_match = []
            multi_match_number = []
            exact_match = []
            no_match = []

            if item == 0:
                combined_df = dataset_list[order[item]]
            else:
                for i in combined_df.index:
                    try:
                        pair = dataset_list[order[item]].loc[i]
                        if type(pair) == pd.DataFrame:
                            multi_match.append(i)
                            multi_match_number.append(len(pair))
                        elif type(pair) == pd.Series:
                            exact_match.append(i)
                    except:
                        no_match.append(i)

                # Report matches #   
                logger.info('Matching result - Exact {exNum}'.format(exNum=len(exact_match)))
                logger.info('Matching result - Multi {mulNum}'.format(mulNum=len(multi_match)))
                logger.info('Matching result - None {noNum}'.format(noNum=len(no_match)))
                logger.info("Multi-matching array: {array} ".format(array=str(multi_match_number)))

                # Link and combine actual data with person identifiers #
                combined_df = pd.concat([combined_df.loc[exact_match], dataset_list[order[item]].loc[exact_match]], axis=1, join='inner')
        if len(exact_match) > 0:
            logger.debug('Features in combined dataset are saved locally')
            cmb_col = list(combined_df.columns)
            with open('/output/CombinedFeatures.txt', 'w') as f:
                for item in cmb_col:
                    f.write("%s\n" % item)

            # Save file #
            combined_df.to_csv('/data/act_data.csv')
            logger.info("Matching and linking took {runtime:.4f}s to run.".format(runtime=(time.time() - start_time)))
            
        else:
            logger.info('No records have been exactly matched so that no combined dataset is generated!!')