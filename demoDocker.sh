cd containers/createContainer/cbsContainer
docker run --rm --add-host dockerhost:10.0.75.1 -v ./output.txt:/output.txt datasharing/cbs

cd ../umContainer
docker run --rm --add-host dockerhost:10.0.75.1 -v ./output.txt:/output.txt datasharing/um

cd ../../ttpImage
rm -R output/
mkdir output
# Commented for now, needs to be executed based on output of containers above, and implemented in input.txt
#docker run --rm --add-host dockerhost:10.0.75.1 -v ./output:/output -v ./input.json:/input.txt datasharing/ttp
