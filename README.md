## FAIRHealth Project: Privacy-Preserving Distributed Learning Infrastructure (PPDL)

### Introduction ###

[FAIRHealth project](https://www.maastrichtuniversity.nl/research/institutes/ids/research/research-projects/analyzing-partitioned-fair-health-data-0) is a collaboration between Maastricht University and Statistics Netherlands from Feb 2018 to Feb 2020. It is funded by Dutch National Research Agenda (NWA) under [VWData program](https://commit2data.nl/vwdata). In this project, we propose an innovative infrastructure for the secure and privacy-preserving analysis of personal health data from multiple providers with different governance policies. The approach involves distributed machine learning to analyze vertically partitioned data (different variables/attributes/features about a particular individual are distributed over a set of data sources). 

The main idea of our infrastructure is to send data-processing or analysis algorithms to data sources rather than transferring data to the researchers. Only the final (verified) results can be return to the researchers. Our infrastructure is an extension of [Personal Health Train Archtecture](https://www.dtls.nl/fair-data/personal-health-train/). The trains (applications) containing analytic algorithms are sent to the data stations (sources). The stations (sources) can inspect whether the train is allowed to execute the application on (a subset of) the available data.

Please find our publications: 

1. [Papar: A Privacy-Preserving Infrastructure for Analyzing Personal Health Data in a Vertically Partitioned Scenario](https://www.ncbi.nlm.nih.gov/pubmed/31437948) 
2. [Paper: Using the Personal Health Train for Automated and Privacy-Preserving Analytics on Vertically Partitioned Data](https://www.ncbi.nlm.nih.gov/pubmed/29678027)
3. Others: [Slides](https://docs.google.com/presentation/d/1_vzFc_wNMAxce3uXmRqob3LM0OjgLMCL8iImME_fXA4/edit?usp=sharing),  [Video Demo 1](https://youtu.be/zorPZ8Xg-r8),  [Video Demo 2](https://www.youtube.com/watch?v=Rqz5zfzEXRQ), [Video Demo 3](https://www.youtube.com/watch?v=04bJjSSjvg8&t=6s)

### Structure of PPDL

Until Feb 2020, PPDL infrastructure contains 5 components:

1. **Data transformation (Transform csv, sav data files to RDF data stored in graph database)**
2. Overview of Data (Visualize and obtain basic information/statistical summary of data)
3. Pseudonymization & Encryption (Pseudonymize personal identifiers(PI) and encrypt data files)
4. Matching & Merging (Match and merge multiple datasets on pseudonymized PI)
5. Analysis (Go through machine learning pipeline)
6. Logging all data processing history

### Prerequisites

Hardware:

- Windows 10 (fall creators update or higher)
- MacOS 10.13 (High Sierra)
- Ubuntu 16.04, 17.10 or 18.04
- Moderately recent CPU (minimum i5 processor)
- 8 GB of RAM (not occupied by many other applications/services)

Software:

- Docker Community Edition
  - native on Ubuntu [Install](https://docs.docker.com/install/linux/docker-ce/ubuntu/#set-up-the-repository)
  - for Windows [Install](https://hub.docker.com/editions/community/docker-ce-desktop-windows)
  - for Mac [Install](https://hub.docker.com/editions/community/docker-ce-desktop-mac)
- Python 3.6 (with pip as dependency manager)

### How to use it? (Test on your local laptop)

1. **Install base containers:** in all data stations (data parties and Trusted Secure Environment), a basic container needs to to installed. In your terminal: 

   ```shell
   docker pull sophia921025/datasharing_base:v1.0
   ```

   

2. **Get an overview of data:** At each data party (*/CBS/input/* or */DMS/input/*). Configure ***request.yaml*** based on the overview of data you need. In the folder which contains ***data file*** and ***request.yaml***, Mac/Linux run: (You can keep everything as default for testing purpose.)

   ```shell
   docker run --rm \
   -v "$(pwd)/input:/inputVolume" \
   -v "$(pwd)/input/20200308_cbs.csv:/data_file.csv" \
   -v "$(pwd)/output:/output" sophia921025/datasharing_overview:v1.0
   ```

   

3. All parties generate keys for communication and identification

   - At TSE side - Generate Quantum safe and Quantum vulnerable public-priate key pairs for each party:

     - Configure the *genKeys_input.yaml* *(./TSE/input/)*, set **party_name: cbs** and back to *TSE* folder run:

       ```shell
       docker run --rm -it \
       -v "$(pwd)/input:/inputVolume" \
       -v "$(pwd)/output:/output" sophia921025/datasharing_ppkeys:v1.0
       ```

     - Then, change the **party_name: dms**  in *genKeys_input.yaml* and run the command lines above again. 

     - You will get 8 key files in total in the */TSE/output* folder (4 key files for each party) (DO NOT CHANGE THE KEY FILE NAME!)

     

   - At data party - Generate Signing-verifying key pair and Quantum vulnerable public-private key pairs.

     - Configure the *genKeys_input.yaml* *(./CBS/input/)*, set **party_name: cbs** and back to *CBS* folder run:

       ```shell
       docker run --rm -it \
       -v "$(pwd)/input:/inputVolume" \
       -v "$(pwd)/output:/output" sophia921025/datasharing_svkeys:v1.0
       ```

       You will find 4 key files in the */CBS/output* folder

     - Configure the *genKeys_input.yaml* *(./DMS/input/)*, set **party_name: dms** and back to *DMS* folder and run the same command lines above. 

       You will find 4 keys files in the */DMS/output* folder



4. Key exchange - TSE needs to give Quantum Safe Public keys, Quantum vulnerable Public keys to each data party, and receive data parties' verifying keys and data parties' Quantum vulnerable public keys. So steps are below:
   - At TSE site: from */TSE/output* folder move all files starting with "*SECRET_xxxx.key*" (4 files)to */TSE/input* folder (this means keys will be used for next steps)
   - At TSE site: from */TSE/output* folder move "*Public_xxx_cbs*.key" (2 files) to */CBS/input/* folder
   - At TSE site: from */TSE/output* folder move "*Public_xxx_dms.key" (2 files) to */DMS/input/* folder
   - At CBS site: from */CBS/output* folder move "*SECRET_xxx_cbs.key" (2 files) to */CBS/input/* folder
   - At CBS site: from */CBS/output* folder move "*Public_xxx_cbs.key" (2 files) to */TSE/input/* folder
   - At DMS site: from */DMS/output* folder move "*SECRET_xxx_dms.key" (2 files) to */DMS/input/* folder
   - At DMS site: from */DMS/output* folder move "*Public_xxx_dms.key" (2 files) to */TSE/input/* folder



5. Pseudonymization and encryption of data: to pseudonymize the personal identifiers (PI) for linking multiple datasets, and encrypt the data files (pseudonymized PI + actual data). 

   - At CBS site: configure *encrypt_input.yaml* (./CBS/input/) (you can use the default setting) and then go back to *CBS* folder, run

     ```shell
     docker run --rm -it \
     -v "$(pwd)/input:/inputVolume" \
     -v "$(pwd)/input/20200312_simu_cbs.csv:/data_file.csv" \
     -v "$(pwd)/output:/output" sophia921025/datasharing_encdata:v1.0
     ```

     You will find one "xxxxx.enc" file and one *cbs_data_keys.json* file in */CBS/output* folder

   - Send/Move this "xxxxx.enc" file to */TSE/input/* folder

   - At DMS site: configure *encrypt_input.yaml* (./DMS/input/) (you can use the default setting) and then go back to *DMS* folder, run 

     ```shell
     docker run --rm -it \
     -v "$(pwd)/input:/inputVolume" \
     -v "$(pwd)/input/20200312_simu_dms.csv:/data_file.csv" \
     -v "$(pwd)/output:/output" sophia921025/datasharing_encdata:v1.0
     ```

     You will get one "xxxxx.enc" file and one *dms_data_keys.json* file in */DMS/output* folder

   - Send/Move this "xxxxx.enc" file to */TSE/input/* folder too

   

   6. Sign models: researchers should send their analysis model to all data parties. Data parties check the models and sign the models and send them to TSE. 

      - At CBS site: configure *sign_model_input.yaml* (./CBS/input/) (you can use the default setting) and then go back to *CBS* folder, run

        ```shell
        docker run --rm -it \
        -v "$(pwd)/input:/inputVolume" \
        -v "$(pwd)/output:/output" sophia921025/datasharing_signmodel:v1.0
        ```

        You will see two "cbs_xxxx.py.enc" files in the */CBS/output/* folder

      - Send/Move these two "cbs_xxxx.py.enc" files to */TSE/input/* folder

      - At DMS site: configure *sign_model_input.yaml* (./DMS/input/) (you can use the default setting) and then go back to *DMS* folder, run the command lines above. You will see two "dms_xxxx.py.enc" files in the */DMS/output/* folder

      - Send/Move these two "dms_xxxx.py.enc" files to */TSE/input/* folder

   

   7. Matching and analysis at TSE: at this moment, you should have 3 yaml files, 6 enc files, 8 key files in the */TSE/input/* folder. 

      - Configure *security_input.yaml* *(/TSE/input/)*: the things you need to change are:

        ```shell
        dmsfileUUID: "xxxxxx"
        dmsencryptKey: "yyyyyy"
        
        cbsfileUUID: "zzzzzzz"
        cbsencryptKey: "vvvvvvv"
        ```

      - You can find **dmsfileUUID** and **dmsencryptKey** in the */DMS/output/dms_data_keys.json*, **cbsfileUUID** and **cbsencryptKey** can be found in the */CBS/output/cbs_data_keys.json* You can leave the rest as default for testing purpose.

      - Configure *analysis_input.yaml* *(/TSE/input/)*: You can leave all inputs as default for testing purpose for now

      - In the TSE folder, run 

        ```shell
        docker run --rm -it \
        -v "$(pwd)/input:/inputVolume" \
        -v "$(pwd)/output:/output" sophia921025/datasharing_tse:v1.0
        ```

        

If Docker container runs properly, you will see execution logs as below. In the end, all results and logging histories (***ppds.log***) are stored in the ***output*** folder. To avoid data leakage from error shooting, if errors occur during executions, the error messages will saved in the ***ppds.log*** instead of printing out on the screen.

```powershell
INFO     ░ 2020-02-02 19:40:56,751 ░ verDec ░ verDec.py line 14 ▓ Reading request.yaml file...
INFO     ░ 2020-02-02 19:40:56,944 ░ verDec ░ verDec.py line 111 ▓ Signed models has been verified successfully!
INFO     ░ 2020-02-02 19:40:56,945 ░ verDec ░ verDec.py line 151 ▓ Verification and decryption took 0.3028s to run
... 
... ...
INFO     ░ 2020-01-19 10:25:05,619 ░ main ░ main.py line 272 ▓ In total, all models training took 16.6441 to run.
```
