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

The steps below make use of two parties, named **CBS** and **DMS**. If you want to use more parties - or change their names - then edit them in the shell scripts mentioned below before executing and change your folder paths accordingly.

The datasets used here are:

- For party **CBS**: `Testing_folder/CBS/input/20200511_sample_cbs.csv` is a random sample from Dutch Healthcare cost [open data](https://www.vektis.nl/open-data).

- For party **DMS**: `Testing_folder/DMS/input/20200402_random_dms.csv` is perturbed data - added randoms to all values and shuffle the datasets - from the Maastricht Study.

When following these steps you will be asked to

```
execute commands in the terminal
```
or

> perform other actions.

#### 1. Build container
In all data stations (data parties and Trusted Secure Environment), a container needs to to installed/built. It includes all basic libraries such as python-3.6, Pandas, Numpy, Scikit Learn, as well as python scripts for key generations, data encryption, matching, analysis etc. Build the container in the `container` folder: 

```shell
cd container
./build_container.sh
cd -
```

#### 2. Get an overview of data
From this step on, all actions will happen in the `Testing_folder`.

```shell
cd Testing_folder
```

> If needed, configure the `request.yaml` in each data party's `input` folder and/or edit `overview.sh` in the folders `CBS` and `DMS` and change the `DATA_FILE` to point to your sample files.

For a simple test run, you can leave both `request.yaml` files and `overview.sh` files at their default. 

```shell
cd CBS
./overview.sh
cd -
```

```shell
cd DMS
./overview.sh
cd -
```

#### 3. All parties generate keys for communication and identification
##### TSE side
Generate *quantum-safe* and *classic* public-priate key pairs for each party. Creating, exporting and importing of secret keys requires a password. An example password for copy&pasting can be `DataSharing!!!20200202`.


```shell
cd TSE
./gen_receiver_keys.sh
cd -
```

You will get a number of key files in the `./TSE/output` folder - 4 key files per party. Do not change the key file name!

##### Data party
Generate *Signing-verifying key pair* and *Classic public-private key pairs*.

```shell
cd CBS
./gen_sender_keys.sh
cd -
```

```shell
cd DMS
./gen_sender_keys.sh
cd -
```

You will find 4 key files in each `output` folder.

#### 4. Key exchange
TSE needs to give *Quantum Safe Public keys*, *Classic Public keys* to each data party, and receive data parties' *Verifying Keys* and data parties' *Classic Public Keys*.

```shell
cd TSE
./move_keys.sh
cd -
```

This executes the steps below:

- **TSE**: from `TSE/output` move all files named `SECRET*.key` (4 files) to `TSE/input`
- **TSE**: from `TSE/output` move `Public*CBS.key` (2 files) to `CBS/input/`
- **TSE**: from `TSE/output` move `Public*DMS.key` (2 files) to `DMS/input/`
- **CBS**: from `CBS/output` move `SECRET*CBS.key` (2 files) to `CBS/input/`
- **CBS**: from `CBS/output` move `Public*CBS.key` (2 files) to `TSE/input/`
- **DMS**: from `DMS/output` move `SECRET*DMS.key` (2 files) to `DMS/input/`
- **DMS**: from `DMS/output` move `Public*DMS.key` (2 files) to `TSE/input/`


#### 5. Pseudonymization and encryption of data
To pseudonymize the personal identifiers (PI) for linking multiple datasets, and encrypt the data files (pseudonymized PI + actual data). 

##### CBS site
> If needed, configure `CBS/input/encrypt_input.yaml` and edit the script `CBS/hash_encrypt.sh` to have `DATA_FILE` point to your data file.

For a quick test, just keep the defaults.

```shell
cd CBS
./hash_encrypt.sh
cd -
```

You will find one `*.enc` file and one `CBS_data_keys.json` file in `CBS/output`. 

> Send/Move this `*.enc` file to `TSE/input/`.

##### DMS site
> If needed, configure `DMS/input/encrypt_input.yaml` and edit the script `DMS/hash_encrypt.sh` to have `DATA_FILE` point to your data file.

For a quick test, just keep the defaults.

```shell
cd DMS
./hash_encrypt.sh
cd -
```

You will get one `*.enc` file and one `DMS_data_keys.json` file in `/DMS/output`

> Send/Move this `*.enc` file to `TSE/input/` as well.


#### 6. Sign models
Researchers should send their analysis model to all data parties. Data parties check the models and sign the models and send them to TSE. 

##### CBS site
> If needed supply your own model and configure `CBS/input/sign_model_input.yaml`.

```shell
cd CBS
./sign_model.sh
cd -
```

You will see one or more `CBS_*.py.enc` files in `/CBS/output/`.

> Send/Move these `CBS_*.py.enc` file(s) to `TSE/input/`.

##### DMS site
> If needed supply your own model and configure `DMS/input/sign_model_input.yaml`.

```shell
cd DMS
./sign_model.sh
cd -
```

You will see one or more `DMS*.py.enc` files in `/DMS/output/`.

> Send/Move these `DMS*.py.enc` file(s) to `TSE/input/` as well.


#### 7. Matching and analysis at TSE
At this moment, you should have 3 `*.yaml` files, 3 `*.enc` files per data party and 4 `*.key` files per data party in `TSE/input/`. 

> **Not optional!**
> Look up `DMSfileUUID` and `DMSencryptKey` in `DMS/output/DMS_data_keys.json`. `CBSfileUUID` and `CBSencryptKey` can be found in `CBS/output/CBS_data_keys.json`. Enter these in `TSE/input/security_input.yaml` **without quotation marks**. You can leave the rest of the file as default for testing purpose.

> If necessary, configure `TSE/input/analysis_input.yaml`. You can leave all inputs as default for testing purposes.

```shell
cd TSE
./analyze.sh
cd -
```

If the Docker container runs properly, you will see execution logs as below. In the end, all results and logging histories are stored in `TSE/output/`. Uncaught exceptions as well as more verbose logging will not show up on screen, but are logged to `TSE/output/ppds.log` instead. Parts of datasets *can* show up in uncaught exceptions, so make sure the data party's researchers can only see the on-screen logging.

Example of a successful run:

```shell
INFO     ░ 2020-03-27 10:40:31,359 ░ verify_decrypt ░ verify_decrypt.py line 184 ▓ Signed models has been verified successfully!
INFO     ░ 2020-03-27 10:40:31,363 ░ verify_decrypt ░ verify_decrypt.py line 184 ▓ Signed models has been verified successfully!
INFO     ░ 2020-03-27 10:40:31,366 ░ verify_decrypt ░ verify_decrypt.py line 275 ▓ Your model is verified successfully.
INFO     ░ 2020-03-27 10:40:31,368 ░ verify_decrypt ░ verify_decrypt.py line 280 ▓ Verification and decryption took 7.4462s to run
[...]
INFO     ░ 2020-04-02 14:25:23,010 ░ analysis_main ░ analysis_main.py line 394 ▓ In total, all models training took 10.5484 to run. 
INFO     ░ 2020-04-02 14:25:23,010 ░ analysis_main ░ analysis_main.py line 395 ▓ The whole analysis process took 13.0924 to run.
```
