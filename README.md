# Configuration

An example of the configuration can be found in [app/config.yaml](app/config.yaml). Please edit the input, output and pythonFile parameters, especially the location on the docker host (indicated by the "host" variable).

## Running the web application

Please execute the two commands below to run the web-application.

1. **At data party side**, there are three functions: encrypt data, get data overview, and sign model code files. Run the following command in your terminal.

On Windows:
```powershell
docker volume create inputVolume

docker run -it --rm ^
    -p 80:80 ^
    -v /var/run/docker.sock:/var/run/docker.sock ^
    -v %cd%\app\config.yaml:/app/config.yaml ^
    -v inputVolume:/inputVolume sophia921025/datasharing_dataparty:0.1-web
```

On Linux/MacOS:
```powershell
docker volume create inputVolume

docker run -it --rm -p 80:80 \
-v "/var/run/docker.sock:/var/run/docker.sock" \
-v "$(pwd)/app/config.yaml:/app/config.yaml" \
-v "inputVolume:/inputVolume" sophia921025/datasharing_dataparty:0.1-web
```

Go to your browser: 

- 0.0.0.0/encdata - encrypt data
- 0.0.0.0/overview - get data overview
- 0.0.0.0/signmodel - sign model code files

After running at data party side, you are supposed to get encrypted data files, signed model files, and file UUID, encryption key, and verification keys. Please put encrypted data files, signed model files in a folder named as "input". Then put the path of this folder in the config.yaml file at TSE side. 

Then, **at TSE side**, run the following command 

On Windows:

```powershell
docker volume create inputVolume

docker run -it --rm ^
    -p 80:80 ^
    -v /var/run/docker.sock:/var/run/docker.sock ^
    -v %cd%\app\config.yaml:/app/config.yaml ^
    -v inputVolume:/inputVolume sophia921025/datasharing_tse:0.1-web
```

On Linux/MacOS:

```powershell
docker volume create inputVolume

docker run -it --rm -p 80:80 \
-v "/var/run/docker.sock:/var/run/docker.sock" \
-v "$(pwd)/app/config.yaml:/app/config.yaml" \
-v "inputVolume:/inputVolume" sophia921025/datasharing_tse:0.1-web
```

### Quickly test it by yourself (TSE as an example) ###

1. TSE_web/input folder contains two encrypted simulation datasets and two signed model files. 
2. Please configure the app/config.yaml file (input - host, output - host)
3. In TSE_web folder, run the above command lines.