rm -R output/
mkdir output
docker run --name myTest -v %~dp0/output:/output -v %~dp0/run.r:/run.r jvsoest/analysis_r:latest
docker rm myTest