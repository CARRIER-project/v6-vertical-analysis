cbsSet <- read.csv("/input/cbs.csv")
dmsSet <- read.csv("/input/dms.csv")

#DMS set is subset of CBS
mergedSet <- sapply(dmsSet$id, function(x) {
    cbsIndex <- which(cbsSet$id==x)
    dmsIndex <- which(dmsSet$id==x)

    c(income=cbsSet$income[cbsIndex],
    age=dmsSet$age[dmsIndex])
})

mergedSet <- as.data.frame(t(mergedSet))
png(filename = "/output/myImage.png")
plot(mergedSet$age, mergedSet$income)
dev.off()