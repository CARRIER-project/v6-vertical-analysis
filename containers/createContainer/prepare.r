dir.create("/input")
dir.create("/output")

#create a normal distribution of income (assume a normal distribution :)
incomeVector = rnorm(n=500, m=30000, sd=7000)

cbsSet <- data.frame(id = c(1:length(incomeVector)),
                    income = incomeVector)
cbsSet$id <- cbsSet$id + 100000
cbsSet$id <- as.character(cbsSet$id)

#write the CBS set into a CSV
write.csv(cbsSet, file = "/input/cbs.csv")

#create a normal distribution of ages
ageVector <- rnorm(n=500, m=45, sd=20)

#create the matrix with fake IDs
dmsSet <- data.frame(id = c(1:length(ageVector)),
                    age = ageVector)
dmsSet$id <- dmsSet$id + 100000
dmsSet$id <- as.character(dmsSet$id)

dmsSet <- dmsSet[sample(1:nrow(dmsSet), size=200),]

#write the CBS set into a CSV
write.csv(dmsSet, file = "/input/dms.csv")