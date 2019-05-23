rm %~dp0\output\*
copy %~dp0\..\createContainer\umContainer\tmp\* %~dp0\output\
copy %~dp0\..\createContainer\cbsContainer\tmp\* %~dp0\output\

docker rm datasharing/tse
docker build -t datasharing/tse .\

docker run --rm --add-host dockerhost:10.0.75.1 -v %~dp0\output:/temp -v %~dp0\input.json:/input.txt datasharing/tse

rem docker push datasharing/tse