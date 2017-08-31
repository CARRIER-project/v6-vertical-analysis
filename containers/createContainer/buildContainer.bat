xcopy ..\..\PQcrypto baseContainer\PQcrypto /e /i /h
docker rmi datasharing/base
docker build -t datasharing/base baseContainer/
rmdir /Q /S baseContainer\PQcrypto

rem if you want to run the container in a command line, and mount the PQcrypto to a local folder, use this line
rem docker run -it -v C:\Users\johan\Documents\Repositories\PHT\DataSharing\PQcrypto:/data datasharing/base /bin/bash

rem docker rmi jvsoest/analysis_r
rem docker build -t jvsoest/analysis_r:latest ./