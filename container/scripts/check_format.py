import time
start_time = time.time()

import redacted_logging as rlog
logger = rlog.get_logger(__name__)

def checking(df, PI):
    standardName = ['GBAGeboorteJaar', 'GBAGeboorteMaand', 'GBAGeboorteDag',
                    'GBAGeslacht', 'GBAPostcode', 'GBAHuisnummer', 'GBAToev']
    for var in standardName:
        if var in PI:
            if df[var].isnull().sum() > 0:
                logger.warning("%s has missing values. Missing in linking features will cause the instances not being matched" %var)
            
                
            if var == "GBAGeboorteJaar":
                df[var] = df[var].astype(str)
                for i in range(0, len(df)):
                    value = df.iloc[i][var]
                    if type(value) != str:
                        logger.warning("%s type has to be string" %var)
                        if len(value) != 4:
                            logger.warning("%s length has to be 4" %var)
                logger.debug("%s checking is done" %var)
                            
                
            if var == "GBAGeboorteMaand":
                df[var] = df[var].astype(str)
                for i in range(0, len(df)):
                    value = df.iloc[i][var]
                    if type(value) != str:
                        logger.warning("%s type has to be string" %var)
                        if len(value) != 2:
                            logger.warning("%s length has to be 2" %var)
                logger.debug("%s checking is done" %var)
                            
                
            if var == "GBAGeboorteDag":
                df[var] = df[var].astype(str)
                for i in range(0, len(df)):
                    value = df.iloc[i][var]
                    if type(value) != str:
                        logger.warning("%s type has to be string" %var)
                        if len(value) != 2:
                            logger.warning("%s length has to be 2" %var)
                logger.debug("%s checking is done" %var)
            
                            
            if var == "GBAGeslacht":
                df[var] = df[var].astype(str)
                for i in range(0, len(df)):
                    value = df.iloc[i][var]
                    if type(value) != str:
                        logger.warning("%s type has to be string" %var)
                        if value != 1 or value != 2:
                            logger.warning("%s has to be 1 or 2" %var)
                logger.debug("%s checking is done" %var)
            
                            
            if var == "GBAPostcode":
                df[var] = df[var].astype(str)
                for i in range(0, len(df)):
                    value = df.iloc[i][var]
                    if type(value) != str:
                        logger.warning("%s type has to be string" %var)
                        if len(value) != 6:
                            logger.warning("%s length has to be 6" %var)
                logger.debug("%s checking is done" %var)
            
                            
            if var == "GBAHuisnummer":
                df[var] = df[var].astype(str)
                for i in range(0, len(df)):
                    value = df.iloc[i][var]
                    if type(value) != str:
                        logger.warning("%s type has to be string" %var)
                        if len(value) < 5:
                            logger.warning("%s length has to be less 5" %var)
                logger.debug("%s checking is done" %var)
            
                            
            if var == "GBAToev":
                df[var] = df[var].astype(str)
                for i in range(0, len(df)):
                    value = df.iloc[i][var]
                    if type(value) != str:
                        logger.warning("%s type has to be string" %var)
                        if len(value) < 7:
                            logger.warning("%s length has to be less 7" %var)
                logger.debug("%s checking is done" %var)
            
                
        else:
            logger.error('Sorry, %s is not in the dataset.' %var)
