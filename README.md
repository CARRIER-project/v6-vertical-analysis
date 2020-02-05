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

``` powershell
docker pull sophia921025/datasharing_base:v0.1
```

2. **Get an overview of data:** At each data party station, create a folder, put ***data file*** and ***request.yaml*** into this folder. Configure ***request.yaml*** based on the overview of data you need. In your terminal, 

```powershell
docker pull sophia921025/datasharing_overview:v0.1
docker pull sophia921025/datasharing_overview_web:v0.1
```

​		In the folder which contains ***data file*** and ***request.yaml***, Mac/Linux run: (please change the third line "data_party_1.csv" to the name of your own data file.)

```powershell
docker run -it --rm -p 80:80 \
-v "/var/run/docker.sock":"/var/run/docker.sock" \
-v "$(pwd)/app/config.yaml":"/app/config.yaml" \
-v "inputVolume:/inputVolume" sophia921025/datasharing_overview_web:v0.1
```

​		Windows run (please change the third line "data_party_1.csv" to the name of your own data file.)

```powershell
docker run -it --rm -p 80:80 \
-v "/var/run/docker.sock":"/var/run/docker.sock" \
-v "%cd%/app/config.yaml":"/app/config.yaml" \
-v "inputVolume:/inputVolume" sophia921025/datasharing_overview_web:v0.1
```

3. **Pseudonymization and encryption**: to pseudonymize the personal identifiers (PI) for linking multiple datasets, and encrypt the data files (pseudonymized PI + actual data). Go to the folder which contains ***data file*** and ***encrypt_input.yaml***. Please configure ***encrypt_input.yaml*** first. Then in the terminal 

```powershell
docker pull sophia921025/datasharing_encdata:v0.1
docker pull sophia921025/datasharing_enc_web:v0.1
```

Mac/Linux: (please change the second line "data_party_1.csv" to the name of your own data file.)

```powershell
docker run -it --rm -p 80:80 \
-v "/var/run/docker.sock":"/var/run/docker.sock" \
-v "$(pwd)/app/config.yaml":"/app/config.yaml" \
-v "inputVolume:/inputVolume" sophia921025/datasharing_enc_web:v0.1
```

Windows (please change the second line "data_party_1.csv" to the name of your own data file.):

```powershell
docker run -it --rm -p 80:80 \
-v "var/run/docker.sock":"/var/run/docker.sock" \
-v "%cd%/app/config.yaml":"/app/config.yaml" \
-v "inputVolume:/inputVolume" sophia921025/datasharing_enc_web:v0.1
```

After successful execution, your encrypted data file and key file (keys.json) will be stored locally/to the server (e.g., trusted third party, trusted secure environment).

4. Sign your model file (python script) by all data parties. Create a folder where contains ***your_model.py*** and ***encrypt_input.yaml*** (need to be configured). Then in the terminal, Mac/Linux (please change the second line "your_model.py" to the name of your own model file): 

```powershell
docker run -it --rm -p 80:80 \
-v "/var/run/docker.sock":"/var/run/docker.sock" \
-v "$(pwd)/app/config.yaml":"/app/config.yaml" \
-v "inputVolume:/inputVolume" sophia921025/datasharing_signmodel_web:v0.1
```

Windows (please change the second line "your_model.py" to the name of your own model file): 

```powershell
docker run -it --rm -p 80:80 \
-v "/var/run/docker.sock":"/var/run/docker.sock" \
-v "%cd%/app/config.yaml":"/app/config.yaml" \
-v "inputVolume:/inputVolume" sophia921025/datasharing_signmodel_web:v0.1
```



5. At **Trusted Secure Environment (TSE)**, create a folder, put ***encrypted data files*** from data parties, ***security_input.yaml***, and ***analysis_input.yaml***, and your ***analysis python script*** (ML models) into this folder. Configure ***security_input.yaml*** based on the keys from data parties, and ***analysis_input.yaml*** based on your analysis requirements. In your terminal:

```powershell
docker pull sophia921025/datasharing_tse:v0.1
docker pull sophia921025/datasharing_tse_web:v0.1
```

Mac/Linux:

```powershell
docker run --rm \
-v "$(pwd)/input:/input" \
-v "$(pwd)/output:/output" \
-v "$(pwd)/analysis_input.yaml:/analysis_input.yaml" \
-v "$(pwd)/security_input.yaml:/security_input.yaml" sophia921025/datasharing_tse:v0.1
```

Windows:

```powershell
docker run --rm \
-v "%cd%/input:/input" \
-v "%cd%/output:/output" \
-v "%cd%/analysis_input.json:/analysis_input.json" \
-v "%cd%/security_input.json:/security_input.json" sophia921025/datasharing_tse:v0.1
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

