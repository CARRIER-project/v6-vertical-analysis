docker rmi datasharing/base
docker build -t datasharing/base baseContainer/

# if you want to run the container in a command line, and mount the PQcrypto to a local folder, use this line
# docker run -it -v /home/johan/repos/DataSharing/PQcrypto:/data datasharing/base /bin/bash

docker rmi jvsoest/analysis_r
docker build -t jvsoest/analysis_r:latest ./