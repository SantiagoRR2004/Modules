import smtplib
from email.message import EmailMessage
import os
import subprocess
import shutil
import json

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
    percentages = {k: v for k, v in sorted(percentages.items(), key=lambda item: item[1], reverse=True)}

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
    with open("Music/mp3Percents.json", "w") as jsonFile:
        json.dump(percentageResults, jsonFile)


    with open("Music/notExercise.txt", 'r') as file:
        elements = file.read().splitlines()

    # We eliminate all the songs in notExercise
    mp3List = [song for song in mp3List if song not in elements]

    return mp3List
