cd C:\Users\johan\Documents\Repositories\PHT\DataSharing\containers\createContainer\cbsContainer
docker run --rm --add-host dockerhost:10.0.75.1 -v %~dp0\containers\createContainer\cbsContainer\output.txt:/output.txt datasharing/cbs

cd C:\Users\johan\Documents\Repositories\PHT\DataSharing\containers\createContainer\umContainer
docker run --rm --add-host dockerhost:10.0.75.1 -v %~dp0\containers\createContainer\umContainer\output.txt:/output.txt datasharing/um

cd C:\Users\johan\Documents\Repositories\PHT\DataSharing\containers\ttpImage
rmdir /Q /S output
mkdir output
docker run --rm --add-host dockerhost:10.0.75.1 -v %~dp0\containers\ttpImage\output:/output -v %~dp0\containers\ttpImage\input.json:/input.txt datasharing/ttp