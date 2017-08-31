rmdir /Q /S output
mkdir output
docker run --rm -v %~dp0\output:/output -v %~dp0\run.r:/run.r jvsoest/analysis_r:latest