import os
import csv
import re
import json
from Modules import zipping

def deleteFolder(path):
    emptyFolder(path)
    os.removedirs(path)

def emptyFolder(path):
    for filename in os.listdir(path):
        if os.path.isdir(os.path.join(path,filename)):
            deleteFolder(path)

        else:
            os.remove(os.path.join(path,filename))

def createFolder(folder):
    if not os.path.isdir(folder):
        os.mkdir(folder)
    else:
        emptyFolder(folder)

def findPatternFolder(folder, pattern):
    image_files = [f for f in os.listdir(folder) if re.search(pattern,f)]
    numbers = [x[:-4] for x in image_files]
    image_files = [x for _,x in sorted(zip(numbers,image_files))]
    return image_files

def openCsv(pathTocsv):
    with open(pathTocsv, 'r') as file:
        reader = csv.DictReader(file)
        toret = {x:[] for x in reader.fieldnames}
        for row in reader:
            for head in reader.fieldnames:
                toret[head].append(row[head])
        return toret

def ensureExistance(folder):
    if not os.path.exists(folder):
        zipFile = folder+".zip"
        if os.path.isfile(zipFile):
            zipping.decompressZip(folder)

        else:
            os.makedirs(folder)

def copyFile(sorceFolder,sourceFile,destinationFolder,destinationFile):
    with open(os.path.join(sorceFolder, sourceFile), 'rb') as source:
        with open(os.path.join(destinationFolder, destinationFile), 'wb') as destination:
            destination.write(source.read())

def openJson(pathTocsv):
    with open(pathTocsv, 'r') as jsonFile:
        return json.load(jsonFile)
