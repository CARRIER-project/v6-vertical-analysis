## FAIRHealth Project: Privacy-Preserving Distributed Learning Infrastructure (PPDL)

### Introduction ###

[FAIRHealth project](https://www.maastrichtuniversity.nl/research/institutes/ids/research/research-projects/analyzing-partitioned-fair-health-data-0) is a collaboration between Maastricht University and Statistics Netherlands from Feb 2018 to Feb 2020. It is funded by Dutch National Research Agenda (NWA) under [VWData program](https://commit2data.nl/vwdata). In this project, we propose an innovative infrastructure for the secure and privacy-preserving analysis of personal health data from multiple providers with different governance policies. The approach involves distributed machine learning to analyze vertically partitioned data (different variables/attributes/features about a particular individual are distributed over a set of data sources). 

The main idea of our infrastructure is to send data-processing or analysis algorithms to data sources rather than transferring data to the researchers. Only the final (verified) results can be return to the researchers. Our infrastructure is an extension of [Personal Health Train Archtecture](https://www.dtls.nl/fair-data/personal-health-train/). The trains (applications) containing analytic algorithms are sent to the data stations (sources). The stations (sources) can inspect whether the train is allowed to execute the application on (a subset of) the available data.

### Structure of PPDL

Until Feb 2020, PPDL infrastructure contains 5 components:

1. Data transformation (Transform csv, sav data files to RDF data stored in graph database)
2. Overview of Data (Visualize and obtain basic information/statistical summary of data)
3. Pseudonymization & Encryption (Pseudonymize personal identifiers(PI) and encrypt data files)
4. Matching & Merging (Match and merge multiple datasets on pseudonymized PI)
5. Analysis (Go through machine learning pipeline)
6. Logging all data processing history

### Diagram of PPDL ###

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

### Pull Docker images from Docker Hub

In your terminal: 

``` powershell
docker pull sophia921025/datasharing/base:2020-01-15 #base image contains needed libraries
docker pull sophia921025/datasharing/dataparty:2020-01-15 #at each data party station
docker pull sophia921025/datasharing/tse:2020-01-15 #at TSE station
```

At each data party station, create a folder, put ***data file*** and ***input.json*** into this folder. Configure ***input.json*** based on data requirements and salt (agreed by all data parties). In your terminal:

Mac/Linux:

```powershell
docker run --rm -v "$(pwd)/input.json:/input.json" datasharing/dataparty:2020-01-15
```

Windows:

```powershell
docker run --rm -v "%cd%/input.json:/input.json" datasharing/tse:2020-01-15
```

At TSE station, create a folder, put ***encrypted data files*** from data parties, ***security_input.json***, and ***analysis_input.json***, and your ***analysis python scrip***t (ML models) into this folder. Configure ***security_input.json*** based on the keys from data parties, and ***analysis_input.json*** based on your analysis requirements. In your terminal:

Mac/Linux:

```powershell
docker run --rm \
-v "$(pwd)/input:/input" \
-v "$(pwd)/output:/output" \
-v "$(pwd)/MLmodel_ave.py:/MLmodel.py" \
-v "$(pwd)/analysis_input.json:/analysis_input.json" \
-v "$(pwd)/security_input.json:/security_input.json" datasharing/tse:2020-01-15
```

Windows:

```powershell
docker run --rm \
-v "%cd%/input:/input" \
-v "%cd%/output:/output" \
-v "%cd%/MLmodel_ave.py:/MLmodel.py" \
-v "%cd%/analysis_input.json:/analysis_input.json" \
-v "%cd%/security_input.json:/security_input.json" datasharing/tse:2020-01-15
```

If Docker container runs properly, you will see execution logs as below. In the end, all results and logging histories (***ppds.log***) are stored in the ***output*** folder. To avoid data leakage from error shooting, if errors occur during executions, the error messages will saved in the ***ppds.log*** instead of printing out on the screen.

```powershell
INFO     ░ 2020-01-19 10:24:33,292 ░ verDec ░ verDec.py line 77 ▓ Verification and decryption took 1.2064s to run
INFO     ░ 2020-01-19 10:24:35,093 ░ matching ░ matching.py line 26 ▓ dms has 3285 rows
INFO     ░ 2020-01-19 10:24:35,094 ░ matching ░ matching.py line 26 ▓ cbs has 5000 rows
... 
... ...
INFO     ░ 2020-01-19 10:25:05,619 ░ main ░ main.py line 272 ▓ In total, all models training took 16.6441 to run.
```