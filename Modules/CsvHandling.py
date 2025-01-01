import csv


def openCsv(pathTocsv):
    with open(pathTocsv, "r") as file:
        reader = csv.DictReader(file)
        toret = {x: [] for x in reader.fieldnames}
        for row in reader:
            for head in reader.fieldnames:
                toret[head].append(row[head])
        return toret


def saveCsv(pathTocsv, data):

    if type(data) == dict:
        saveCsvColumnBased(pathTocsv, data)

    elif type(data) == list:
        saveCsvRowBased(pathTocsv, data)


def saveCsvColumnBased(pathTocsv, dictWithColumnAsValues):
    with open(pathTocsv, "w", newline="") as csvfile:
        csvWriter = csv.DictWriter(csvfile, fieldnames=dictWithColumnAsValues.keys())

        # Write headers
        csvWriter.writeheader()

        # Write data
        for rowValues in zip(*dictWithColumnAsValues.values()):
            rowDict = dict(zip(dictWithColumnAsValues.keys(), rowValues))
            csvWriter.writerow(rowDict)


def saveCsvRowBased(pathTocsv, rowWithColumnAsValues):
    keys = list(rowWithColumnAsValues[0].keys())
    with open(pathTocsv, "w", newline="") as csvfile:
        csvWriter = csv.DictWriter(csvfile, fieldnames=keys)

        # Write headers
        csvWriter.writeheader()

        # Write data
        csvWriter.writerows(rowWithColumnAsValues)
