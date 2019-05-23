rm %~dp0\output\*
mkdir %~dp0\tmp\

copy %~dp0\..\createContainer\umContainer\tmp\* %~dp0\tmp\
copy %~dp0\..\createContainer\cbsContainer\tmp\* %~dp0\tmp\

docker rm datasharing/tse
docker build -t datasharing/tse .\

docker run --rm --add-host dockerhost:10.0.75.1 -v %~dp0\output:/output -v %~dp0\tmp:/temp -v %~dp0\input.json:/input.txt datasharing/tse

docker push datasharing/tse