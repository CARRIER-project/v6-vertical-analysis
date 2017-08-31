docker rm datasharing/cbs
docker build -t datasharing/cbs .\
docker run -it --rm datasharing/cbs /bin/bash
