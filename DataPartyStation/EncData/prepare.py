import time, json, sys, yaml
start_time = time.time()
import pyreadstat
import pandas as pd
import checkFormat
from PQencryption.hashing import sha_512_PyNaCl

import redacted_logging as rlog
logger = rlog.get_logger(__name__)

try:
    with open(r'encrypt_input.yaml') as file:
        inputYAML = yaml.load(file, Loader=yaml.FullLoader)
        logger.info("Reading encrypt_input.yaml file...")
except FileNotFoundError:
    logger.error("Cannot find the encrypt_input.yaml! ")
else:
    file_path = inputYAML['data_file']
    file_sep = inputYAML['delimiter']

    try:
        if '.csv' in file_path:
            df =  pd.read_csv(file_path, sep=file_sep)
        elif '.sav' in file_path:
            df, meta = pyreadstat.read_sav(file_path)
    except FileNotFoundError:
        logger.error("The data file does not exist!")
    except: 
        logger.error("Errors occur when reading the data file!")

    else:
        # Salt must be 128 bytes in hex.
        ### 18-08-2019 ###
        salt_text = inputYAML['salt_text']
        salt_missing = 128 - len(salt_text)
        if salt_missing > 0:
            salt_text = salt_text + ("a" * salt_missing)
        if salt_missing < 0:
            salt_text = salt_text[:salt_missing]
        salt = salt_text.encode('UTF-8')

        # Input names of PI columns
        PI = inputYAML['linking_features'] 
        act_data = df.drop(PI, axis=1)


        ########################################
        ### Check formats of linking features###
        ########################################
        if inputYAML['check_format'] == True:
            checkFormat.checking(df, PI)
        else:
            logger.info("You did not check format of linking features which might cause mis-matchings!")

        try:
            hashedPI = []
            if df[PI].isnull().sum().sum() == 0:
                for i in range(0, len(df)):
                    combine_PI = str()
                    for j in range(0, len(PI)):
                        id_feature =  df.iloc[i][PI[j]]
                        combine_PI = combine_PI + str(id_feature)
                    
                    # Remove space from strings #
                    combine_PI =  combine_PI.replace(' ', '')
                    hashed = sha_512_PyNaCl.sha512_hash(salt, combine_PI.encode('UTF-8'))
                    hashedPI.append(hashed)
            else:
                logger.error("Work cannot be done because missing values are in personal identifiers!")
                logger.info(df.isnull().sum())
                sys.exit("Execution interrupted!")
        except:
            logger.error("Failed to pseudonymize and encrypt the data file.")

        else:
            hashedPI_df = pd.DataFrame(hashedPI, columns=['encString'])
            hashedData_df = pd.concat([hashedPI_df, act_data], axis=1, join='inner')
            logger.info("Pseudonymized data has %s rows" %str(len(hashedData_df)))

            hashedData_df.to_csv("/data/encrypted_%s.csv" %(inputYAML['party_name']), index=None, sep=',', encoding='utf-8') #2.4 Output file name

            logger.info("My program took {runtime:.4f}s to run".format(runtime=time.time() - start_time)) 