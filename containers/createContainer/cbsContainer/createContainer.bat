docker rm datasharing/cbs
docker build -t datasharing/cbs .\
docker run -it --rm --add-host dockerhost:10.0.75.1 datasharing/cbs /bin/bash
