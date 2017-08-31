#create a normal distribution of income (assume a normal distribution :)
incomeVector = rnorm(n=500, m=30000, sd=7000)

cbsSet <- data.frame(id = c(1:length(incomeVector)),
                    income = incomeVector)
cbsSet$id <- cbsSet$id + 100000
cbsSet$id <- as.character(cbsSet$id)

#write the CBS set into a CSV
write.csv(cbsSet, file = "/data/cbs.csv")