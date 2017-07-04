import csv
import random as rand

# todo: mistakes in bsn's and missing numbers.
with open("BSNs.txt", "rt") as bsn:
	with open("Maastricht.csv", "wb") as UM:
		mstricht = csv.writer(UM, delimiter=",");
		with open("CBS.csv", "wb") as CBS:
			hrlen = csv.writer(CBS,delimiter=",");
			i = 0;
			for text in bsn:
				x = text[0:-1]
				if i<1000:
					mstricht.writerow([x, str(rand.randint(18,65))]);
				if i<70000000:
					hrlen.writerow([x, str(rand.randint(1800,5000))]);
				else:
					break;		
						
		
