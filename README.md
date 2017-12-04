# UM-CBS DataSharing repository
This repository contains the encryption libraries, and the base docker containers and examples. For additions/changes, please make branches, and send pull requests (with review option). For more information, check [git workflow](https://www.atlassian.com/git/tutorials/comparing-workflows).

## Building Docker containers
Before building the Docker containers, please make sure you have installed docker from [here](https://www.docker.com).
Afterwards, perform the steps below. All code blocks are executed from the root of this repository.

### 1: Build the base container
We are not using the DockerHub at the moment. Please execute the following commands to build a base container where Python, R and the [PQcrypto](PQcrypto/) packages are installed.
```
cd containers/createContainer
sh buildContainer.sh
```

### 2: Build containers for data extraction
After building the base container, we can build specific containers for UM and CBS to extract data, and send this data to the trusted third party (TTP).
```
cd containers/createContainer/cbsContainer
sh createContainer.sh

cd ../umContainer
sh createContainer.sh
```

### 3: Build container for Trusted Third Party
As mentioned before, we need an additional container for the TTP. This container will retrieve the data, decrypt, verify, and execute the analysis. An example analysis is given in this repository. To build the TTP container, execute the commands below.
```
cd containers/ttpImage
sh runContainer.sh
```