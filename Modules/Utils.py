import os
from PIL import Image
import zipfile
import subprocess
import shutil
import json
from Modules import FileHandling
from Modules import CsvHandling
from Modules import zipping

def divider(images,classifier,key,minimum):
    toret = []
    my_list = [x for i, x in enumerate(classifier[key]) if x not in classifier[key][:i]]
    if None in my_list:
        my_list.remove(None)

    for i in my_list:
        segment = []
        for j in range(len(classifier[key])):
            if classifier[key][j] == i:
                segment.extend([x for x in images if x[:-7]==classifier[minimum][j]])
        toret.append(segment)
    return toret

def create_cbz(images_folder, imagesList, output_cbz,temporalFolder = ".Temporal"):

    FileHandling.ensureExistance(temporalFolder)
    if sorted(imagesList) != imagesList:
        for image_file in imagesList: 
            FileHandling.copyFile(images_folder,image_file,temporalFolder,str(imagesList.index(image_file))+".jpg")
        images_folder = temporalFolder
        imagesList = FileHandling.findPatternFolder(temporalFolder,".jpg$")

    with zipfile.ZipFile(output_cbz, 'w', zipfile.ZIP_DEFLATED) as cbz:
        for image_file in imagesList:
            image_path = os.path.join(images_folder, image_file)
            with Image.open(image_path) as img: # Does this do anything?
                #rgb_image = img.convert("RGB")
                cbz.write(image_path, arcname=os.path.basename(image_path))

    FileHandling.deleteFolder(temporalFolder)


    print(output_cbz+" created successfully!")

def nameCreator(manga,division,name,inversion:bool,number,numeration:bool,format):
    if numeration:
        middle = division + " " + str(number)
    else:
        middle = division

    if inversion:
        middle = name + " " + middle
    else:
        middle = middle + " " + name

    return manga  + " " + middle + format
    
def preparationForCBZ(manga,minimum,callerDirectory,division,naming):
    image_folder = os.path.join(callerDirectory,"." + manga + "JPG")
    enumeration = os.path.join(callerDirectory,manga + "Numeration.csv")
    pdfFolder = os.path.join(callerDirectory,manga + " CBZ")

    FileHandling.ensureExistance(image_folder)
    FileHandling.ensureExistance(pdfFolder)

    enumeration = CsvHandling.openCsv(enumeration)
    images = FileHandling.findPatternFolder(image_folder,".jpg$")
    divide = divider(images,enumeration,division,minimum)

    names = []
    [names.append(x) for x in enumeration[division] if x not in names]

    for i in divide:
        name = nameCreator(manga,division,names[divide.index(i)],naming[division]["inversion"],divide.index(i)+1,naming[division]["numeration"],".cbz")
        create_cbz(image_folder, i[::-1], os.path.join(pdfFolder, name))

    zipping.zipAndDelete(image_folder)

def calculatePercentage(strings):
    counts = {}  # Dictionary to store string counts

    for s in strings:
        parts = s.split("-")

        before_dash = parts[0]
        if before_dash in counts:
            counts[before_dash] += 1
        else:
            counts[before_dash] = 1

    total_strings = len(strings)
    percentages = {}

    for key, value in counts.items():
        if value > 1:
            percentage = (value / total_strings) * 100
            percentages[key] = percentage
    percentages = {k: v for k, v in sorted(percentages.items(), key=lambda item: (-item[1], item[0]))}

    return percentages

def runTerminal(command):
    try:
        completed_process = subprocess.run(command, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if completed_process.returncode == 0:
            print("Command executed successfully!")
            print("Output:")
            print(completed_process.stdout)
        else:
            print("Command failed!")
            print("Error:")
            print(completed_process.stderr)
    except Exception as e:
        print("An error occurred:", e)

def copySongs(folder,outputFolder,randomizedList,widthNumber):
    for number,song in enumerate(randomizedList):
        newSong = "{:0>{}} ".format(number+1, widthNumber) + song
        print(newSong)
        origin = os.path.join(folder,song)
        destination = os.path.join(outputFolder,newSong)
        shutil.copy(origin, destination)

def saveList(list1,outputFile):
    list0 = list1.copy()
    with open(outputFile, "r") as file:
        oldList = file.readlines()
        oldList = [line.strip() for line in oldList]

    list0.extend([x for x in oldList if x not in list0])

    with open(outputFile, "w") as file:
        for song in sorted(list0):
            file.write(song + "\n")

def getSongs(folder,songNames):
    mp3List = FileHandling.findPatternFolder(folder,".mp3$")

    saveList(mp3List,songNames)

    percentageResults = calculatePercentage(mp3List)
    with open("Music/mp3Percents.json", "w") as jsonFile:
        json.dump(percentageResults, jsonFile)


    with open("Music/notExercise.txt", 'r') as file:
        elements = file.read().splitlines()

    # We eliminate all the songs in notExercise
    mp3List = [song for song in mp3List if song not in elements]

    return mp3List
