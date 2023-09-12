from datetime import datetime, date, timedelta
import smtplib
from email.message import EmailMessage
import requests
import os
from PIL import Image
import PyPDF2
from reportlab.pdfgen import canvas
import csv
import zipfile
import subprocess
import shutil
import os
import json
from Modules import FileHandling
#https://stackoverflow.com/questions/44375872/pypdf2-returning-blank-pdf-after-copy

def is_month(string):
    try:
        datetime.strptime(string, "%B")
        return True
    except ValueError:
        return False

def find_next_month(current_month):
    # Parsing the input month string to a datetime object
    current_date = datetime.strptime(current_month, "%B")

    # Adding one month to the current date
    next_month_date = current_date + timedelta(days=31)

    # Formatting the next month as a string
    next_month = next_month_date.strftime("%B")

    return next_month

def find_last_month(current_month):
    # Parsing the input month string to a datetime object
    current_date = datetime.strptime(current_month, "%B")

    # Subtracting one month from the current date
    last_month_date = current_date - timedelta(days=31)

    # Formatting the last month as a string
    last_month = last_month_date.strftime("%B")

    return last_month

def eliminateSufixes(dates):
    for sufix in ["st","nd","th","rd"]:
        for date in range(len(dates)):
            dateParts = dates[date].split()
            for unit in range(len(dateParts)):
                if dateParts[unit][0].isdigit():
                    dateParts[unit] = dateParts[unit].replace(sufix,"")
            dates[date] = " ".join(dateParts)
    return dates

def parseDate(date):
    date = date.split(" ")
    toret = {}

    for i in date:
        if i.isnumeric() and int(i) <= 31:
            toret["day"] = int(i)
            
        elif is_month(i):
            toret["month"] = i

        elif i.isnumeric() and int(i) >= 2021:
            toret["year"] = int(i)
    return toret

def filldates(start,end):

    if "day" not in start and "day" not in end:
        print("Problem; no days")
    
    if "month" not in start or "month" not in end:

        if "month" not in start and "month" not in end:
            print("Problem; no months")

        elif "month" not in start:
            if end["day"] >= start["day"]:
                start["month"] = end["month"]
            else:
                start["month"] = find_last_month(end["month"])


        elif "month" not in end:
            if end["day"] >= start["day"]:
                end["month"] = start["month"]
            else:
                end["month"] = find_next_month(end["month"])


                
    if "year" not in start or "year" not in end:
        monthStart = datetime.strptime(start["month"], "%B").month
        monthEnd = datetime.strptime(end["month"], "%B").month

        if "year" not in start and "year" not in end:
            # We have to put something so it doesn"t fail
            start["year"] = 2000
            end["year"] = 2000
            print("Problem; no year")

        elif "year" not in start:
            if monthEnd >= monthStart:
                start["year"] = end["year"]
            else:
                start["year"] = end["year"]-1

        elif "year" not in end:
            if monthEnd >= monthStart:
                end["year"] = start["year"]
            else:
                end["year"] = start["year"]+1

    return start,end

def send_notification(subject, body):
    sender = "???@????"
    receiver = ""

    msg = EmailMessage()
    msg.set_content(body)
    msg["Subject"] = subject
    msg["From"] = sender
    msg["To"] = receiver

    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    with open("Password.json", "r") as jsonFile:
        data = json.load(jsonFile)
    username = data["username"]
    password = data["password"]
    

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.ehlo()
        server.starttls()
        server.login(username, password)
        server.send_message(msg)
        print("Mail sent")

def formattingDates(release_dates):
    formattedDates = []
    for date_range in release_dates:

        if len(date_range.split(" - ")) == 1:
            start = date_range.split(" - ")[0]
            formattedStart = datetime.strptime(start, "%B %d %Y")
            formattedStart = formattedStart.strftime("%Y-%m-%d")
            formattedEnd = formattedStart
            
        else:
            start = date_range.split(" - ")[0]
            end = date_range.split(" - ")[1]
            
            start = parseDate(start)
            end = parseDate(end)

            start,end = filldates(start,end)

            formattedStart = "{month} {day} {year}".format(year=start["year"], month=start["month"], day=start["day"])
            formattedStart = datetime.strptime(formattedStart, "%B %d %Y")
            formattedStart = formattedStart.strftime("%Y-%m-%d")

            formattedEnd = "{month} {day} {year}".format(year=end["year"], month=end["month"], day=end["day"])
            formattedEnd = datetime.strptime(formattedEnd, "%B %d %Y")
            formattedEnd = formattedEnd.strftime("%Y-%m-%d")

        formattedDates.append({"start":formattedStart,"end":formattedEnd})

    return formattedDates


def zipdir(path):
    zf = zipfile.ZipFile(path+".zip", "w")
    for dirname, subdirs, files in os.walk(path):
        zf.write(dirname)
        for filename in files:
            zf.write(os.path.join(dirname, filename))
    zf.close()

def deleteFolder(path):
    emptyFolder(path)
    os.removedirs(path)

def emptyFolder(path):
    for filename in os.listdir(path):
            if os.path.isdir(os.path.join(path,filename)):
                deleteFolder(path)
            else:
                os.remove(os.path.join(path,filename))

def download_image(url, dest_file):
    if not os.path.isfile(dest_file):
        response = requests.get(url)
        if response.status_code == 200:
            with open(dest_file, 'wb') as f:
                f.write(response.content)

def get_images(image_folder):
    # Get a list of all JPEG files in the specified folder
    image_files = [f for f in os.listdir(image_folder) if f.endswith(".jpg")]
    numbers = [int(x[:-4]) for x in image_files]
    image_files = [x for _,x in sorted(zip(numbers,image_files))]
    return image_files

def open_csv(pathTocsv):
    with open(pathTocsv, 'r') as file:
        reader = csv.DictReader(file)
        toret = {x:[] for x in reader.fieldnames}
        for row in reader:
            for head in reader.fieldnames:
                toret[head].append(row[head])
        return toret


def divider(images,classifier,key,minimum):
    toret = []
    my_list = [x for i, x in enumerate(classifier[key]) if x not in classifier[key][:i]]
    for i in my_list:
        segment = []
        for j in range(len(classifier[key])):
            if classifier[key][j] == i:
                segment.extend([x for x in images if x[:-7]==classifier[minimum][j]])
        toret.append(segment)
    return toret

def convert_images_to_pdf(image_folder,imageList, output_pdf,temporalFolder = ".Temporal"):
    FileHandling.ensureExistance(temporalFolder)

    pdf_writer = PyPDF2.PdfWriter()
    smallerPdfs = []


    if not imageList:
        FileHandling.deleteFolder(temporalFolder)
        print("Can't create "+output_pdf) 
        return False

    cover = Image.open(os.path.join(image_folder, imageList[0]))
    width =  cover.width

    for image_file in imageList:
        image_path = os.path.join(image_folder, image_file)

        # Open each image file using PIL
        image = Image.open(image_path)
        pageNumber = round(image.width/width)

        for i in range(pageNumber): # Number of pages in width
            
            fileName = temporalFolder+"/"+image_file[:-4]+str(i)+".pdf"
            
            pdf_page = canvas.Canvas(fileName, pagesize=(width, image.height))
            pdf_page.drawImage(image_path, -i*width, 0, width=image.width, height=image.height)
            pdf_page.showPage()
            pdf_page.save()
            
            # We open the pdfs manually so empty pages don't appear
            smallerPdfs.append(PyPDF2.PdfReader(open(fileName,"rb")))
            # We don't close the pdfs manually

    for pdf in smallerPdfs:
       pdf_writer.add_page(pdf.pages[0])
       
    # Save the resulting PDF to the specified output path
    with open(output_pdf, 'wb') as output:
        pdf_writer.write(output)

    FileHandling.deleteFolder(temporalFolder)

    print(output_pdf+" created successfully!")

def create_cbz(images_folder, imagesList, output_cbz,temporalFolder = ".Temporal"):

    FileHandling.ensureExistance(temporalFolder)
    if sorted(imagesList) != imagesList:
        for image_file in imagesList: 
            FileHandling.copyFile(images_folder,image_file,temporalFolder,str(imagesList.index(image_file))+".jpg")
        images_folder = temporalFolder
        imagesList = FileHandling.getImages(temporalFolder)

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

    enumeration = FileHandling.openCsv(enumeration)
    images = FileHandling.getImages(image_folder)
    divide = divider(images,enumeration,division,minimum)

    names = []
    [names.append(x) for x in enumeration[division] if x not in names]

    for i in divide:
        name = nameCreator(manga,division,names[divide.index(i)],naming[division]["inversion"],divide.index(i)+1,naming[division]["numeration"],".cbz")
        create_cbz(image_folder, i[::-1], os.path.join(pdfFolder, name))

    FileHandling.zipAndDelete(image_folder)

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

def saveList(list0,outputFile):
    with open(outputFile, "w") as file:
        for song in sorted(list0):
            file.write(song + "\n")


def getSongs(folder,songNames):
    mp3List = [file for file in os.listdir(folder) if file.endswith(".mp3")]

    saveList(mp3List,songNames)

    percentageResults = calculatePercentage(mp3List)
    with open("mp3Percents.json", "w") as jsonFile:
        json.dump(percentageResults, jsonFile)


    with open("notExercise.txt", 'r') as file:
        elements = file.read().splitlines()

    # We eliminate all the songs in notExercise
    mp3List = [song for song in mp3List if song not in elements]

    return mp3List
