cbsSet <- read.csv("/data/cbsData.csv")
dmsSet <- read.csv("/data/umData.csv")

#DMS set is subset of CBS
mergedSet <- sapply(dmsSet$id, function(x) {
    cbsIndex <- which(cbsSet$id==x)
    dmsIndex <- which(dmsSet$id==x)

    c(income=cbsSet$income[cbsIndex],
    age=dmsSet$age[dmsIndex])
})

mergedSet <- as.data.frame(t(mergedSet))
png(filename = "/temp/myImage.png")
plot(mergedSet$age, mergedSet$income)
dev.off()