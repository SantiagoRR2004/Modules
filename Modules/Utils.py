import os
import subprocess
import shutil
import json
from Modules import FileHandling
import importlib.util


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
    percentages = {
        k: v
        for k, v in sorted(percentages.items(), key=lambda item: (-item[1], item[0]))
    }

    return percentages


def runTerminal(command):
    try:
        completed_process = subprocess.run(
            command,
            shell=True,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
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


def copySongs(folder, outputFolder, randomizedList, widthNumber):
    for number, song in enumerate(randomizedList):
        newSong = "{:0>{}} ".format(number + 1, widthNumber) + song
        print(newSong)
        origin = os.path.join(folder, song)
        destination = os.path.join(outputFolder, newSong)
        shutil.copy(origin, destination)


def saveList(list1, outputFile):
    list0 = list1.copy()
    with open(outputFile, "r") as file:
        oldList = file.readlines()
        oldList = [line.strip() for line in oldList]

    list0.extend([x for x in oldList if x not in list0])

    with open(outputFile, "w") as file:
        for song in sorted(list0):
            file.write(song + "\n")


def getSongs(folder, songNames):
    mp3List = FileHandling.findPatternFolder(folder, ".mp3$")

    saveList(mp3List, songNames)

    percentageResults = calculatePercentage(mp3List)
    with open("Music/mp3Percents.json", "w") as jsonFile:
        json.dump(percentageResults, jsonFile, indent=2, ensure_ascii=False)
        jsonFile.write("\n") # New line like Prettier

    with open("Music/notExercise.txt", "r") as file:
        elements = file.read().splitlines()

    # We eliminate all the songs in notExercise
    mp3List = [song for song in mp3List if song not in elements]

    return mp3List


def confirmImports(modules: dict) -> None:
    """
    This function will check if the modules are installed;
    if they are not it will try to install them.

    Might need to change this if pip stops working.
    Added --break-system-packages for newer ubuntu versions.

    Args:
        modules (dict): A dictionary with the module name in python as
        the key and the module name from pip as the value.

    Returns:
        None
    """
    for pythonName, module in modules.items():
        if not importlib.util.find_spec(pythonName):
            # Should try to use runTerminal

            try:
                process = subprocess.run(
                    f"pip install {module}", shell=True, text=True, capture_output=True
                )
                if process.returncode != 0:
                    raise Exception(process.stderr)
                else:
                    print(process.stdout)
            except Exception as e:
                process = subprocess.run(
                    f"pip install {module} --break-system-packages",
                    shell=True,
                    text=True,
                    capture_output=True,
                )
                if process.returncode != 0:
                    raise Exception(process.stderr)
                else:
                    print(process.stdout)


def addNewCronTasks(newTasks: list) -> None:
    """
    This function will add new tasks to the crontab
    without deleting the old ones.

    Args:
        newTasks (list): A list of strings with the new tasks.

    Returns:
        None
    """
    result = subprocess.run(
        ["crontab", "-l"], capture_output=True, text=True, check=True
    )

    if not result.stderr:
        oldTasks = result.stdout.split("\n")
        for task in newTasks:
            if task not in oldTasks:
                runTerminal(f"(crontab -l; echo '{task}') | crontab -")
