rmdir /Q /S output
mkdir output
docker run -it --rm --add-host dockerhost:10.0.75.1 -v %~dp0\output:/output -v %~dp0\run.r:/run.r -v %~dp0\run.py:/run.py -v %~dp0\input.json:/input.txt -v %~dp0\run.sh:/run.sh datasharing/base /bin/bash