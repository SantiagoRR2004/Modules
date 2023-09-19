import zipfile
import os
from Modules import FileHandling

def zipDir(path):
    zf = zipfile.ZipFile(path+".zip", "w")
    for dirname, subdirs, files in os.walk(path):
        directory = os.path.relpath(path,dirname)        
        for filename in files:
            zf.write(os.path.join(dirname, filename),os.path.join(directory, filename))
    zf.close()

def decompressZip(folder):
    with zipfile.ZipFile(folder+".zip","r") as zip:
        zip.extractall(folder)

def zipAndDelete(folder):
    zipDir(folder)
    FileHandling.deleteFolder(folder)
