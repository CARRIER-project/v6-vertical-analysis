docker rmi datasharing/ttp
docker build -t datasharing/ttp .\

# Uncomment lines below if you want to test execution    
#rm -R ./output/
#mkdir output
#docker run --rm --add-host dockerhost:10.0.75.1 -v %~dp0\output:/output -v %~dp0\input.json:/input.txt datasharing/ttp
