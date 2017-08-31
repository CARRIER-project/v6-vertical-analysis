rm -R output/
mkdir output
docker run --name myTest -v $(pwd)/output:/output -v $(pwd)/run.r:/run.r jvsoest/analysis_r:latest
docker rm myTest