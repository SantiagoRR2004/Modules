from Modules import mangaUtils
from Modules import FileHandling
from Modules import CsvHandling
from Modules import zipping
from typing import List, Dict
import PyPDF2
from reportlab.pdfgen import canvas
from PIL import Image
import os
from collections import Counter
import zipfile


class MangaCreator:
    def __init__(self, mangaName: str, callerDirectory: str) -> None:
        """
        Initializes the MangaCreator with the name of the manga and the directory
        with all the data.

        Args:
            - mangaName (str): The name of the manga (no problem with spaces).
            - callerDirectory (str): The directory where the manga data is stored.

        Returns:
            - None
        """
        self.manga = mangaName
        self.callerDirectory = callerDirectory
        self.enumeration = self.getEnumeration()

        imageFolder = os.path.join(
            self.callerDirectory, "." + self.manga.replace(" ", "") + "JPG"
        )
        FileHandling.ensureExistance(imageFolder)
        self.images = FileHandling.findPatternFolder(imageFolder, ".jpg$")

    def getEnumeration(self) -> Dict[str, List[str]]:
        """
        Reads the enumeration file for the manga and returns its content as a dictionary.

        It also saves the minimum key for later use.

        Args:
            - None

        Returns:
            - Dict[str, List[str]]: The enumeration dictionary where keys are categories
              and values are lists of items in those categories.
        """
        enumerationFile = os.path.join(
            self.callerDirectory, self.manga.replace(" ", "") + "Numeration.csv"
        )
        if not os.path.exists(enumerationFile):
            Warning("Enumeration file not found.")
            return

        enumeration = CsvHandling.openCsv(enumerationFile)

        # Store the minimum for later use
        self.minimum = self.getMinimum(enumeration)

        return enumeration

    def getMinimum(self, enumeration: Dict[str, List[str]]) -> str:
        """
        Search for the first unique key in the enumeration dictionary.

        Args:
            - enumeration (Dict[str, List[str]]): The enumeration dictionary.

        Returns:
            - str: The first key with unique values in its list.
        """
        for key in enumeration:
            if len(set(enumeration[key])) == len(enumeration[key]):
                return key

    def createFiles(self, division: str) -> None:
        pass

    def divider(self, division: str) -> List[List[str]]:
        """
        Divides the images based on the unique values in the specified division.
        
        Args:
            - division (str): The key in the enumeration dictionary to divide the images by.
            
        Returns:
            - List[List[str]]: A list of lists, where each inner list contains images
              corresponding to a unique value in the specified division.
        """
        toret = []

        # This is like a set, but it keeps the order
        uniqueList = [
            name for i, name in enumerate(self.enumeration[division]) if name not in self.enumeration[division][:i]
        ]

        # Remove None values if they exist
        if None in uniqueList:
            uniqueList.remove(None)

        # Divide the files based on the unique values in the division
        for i in uniqueList:
            segment = []
            for j in range(len(self.enumeration[division])):
                if self.enumeration[division][j] == i:
                    segment.extend(
                        [x for x in self.images if x[:-7] == self.enumeration[self.minimum][j]]
                    )
            toret.append(segment)

        return toret

def preparationForPDF(
    manga,
    callerDirectory=os.path.join(os.getcwd(), "Manga"),
    division="",
    minimum="Title",
):
    mangaObject = MangaCreator(manga, callerDirectory)

    mangaSpaces = manga.replace(" ", "")
    mangaHyphens = manga.replace(" ", "-")

    infofile = os.path.join(callerDirectory, "Manga.json")
    mangaData = FileHandling.openJson(infofile)

    if mangaData.get(mangaHyphens) and mangaData.get(mangaHyphens).get("minimum"):
        minimum = mangaData[mangaHyphens]["minimum"]

    if division == "":
        division = minimum

    image_folder = os.path.join(callerDirectory, "." + mangaSpaces + "JPG")
    enumeration = os.path.join(callerDirectory, mangaSpaces + "Numeration.csv")
    pdfFolder = os.path.join(callerDirectory, mangaSpaces + " PDF")

    FileHandling.ensureExistance(image_folder)
    FileHandling.ensureExistance(pdfFolder)

    enumeration = CsvHandling.openCsv(enumeration)
    divide = mangaObject.divider(division)

    namesPdf = []
    [namesPdf.append(x) for x in enumeration[division] if x not in namesPdf]

    in_order = sum(
        1 for i in range(len(namesPdf) - 1) if namesPdf[i] <= namesPdf[i + 1]
    )
    total_pairs = len(namesPdf) - 1
    needNumberFlag = (in_order / total_pairs) < 0.9

    for i in divide:
        name = mangaUtils.nameCreator(
            manga,
            division,
            namesPdf[divide.index(i)],
            False,
            divide.index(i) + 1,
            needNumberFlag,
            ".pdf",
        )
        convertImagesToPDF(image_folder, i[::-1], os.path.join(pdfFolder, name))

    zipping.zipAndDelete(image_folder)


def convertImagesToPDF(image_folder, imageList, output_pdf, temporalFolder=".Temporal"):
    # https://stackoverflow.com/questions/44375872/pypdf2-returning-blank-pdf-after-copy

    FileHandling.ensureExistance(temporalFolder)

    pdf_writer = PyPDF2.PdfWriter()
    smallerPdfs = []

    if not imageList:
        FileHandling.deleteFolder(temporalFolder)
        # print("Can't create " + output_pdf)
        return False

    cover = Image.open(os.path.join(image_folder, imageList[0]))
    width = cover.width
    width = Counter(
        [Image.open(os.path.join(image_folder, x)).width for x in imageList]
    ).most_common(1)[0][0]

    for image_file in imageList:
        image_path = os.path.join(image_folder, image_file)

        # Open each image file using PIL
        image = Image.open(image_path)
        pageNumber = round(image.width / width)

        for i in range(pageNumber):  # Number of pages in width

            fileName = temporalFolder + "/" + image_file[:-4] + str(i) + ".pdf"

            pdf_page = canvas.Canvas(fileName, pagesize=(width, image.height))
            pdf_page.drawImage(
                image_path, -i * width, 0, width=image.width, height=image.height
            )
            pdf_page.showPage()
            pdf_page.save()

            # We open the pdfs manually so empty pages don't appear
            smallerPdfs.append(PyPDF2.PdfReader(open(fileName, "rb")))
            # We don't close the pdfs manually

    for pdf in smallerPdfs:
        pdf_writer.add_page(pdf.pages[0])

    # Save the resulting PDF to the specified output path
    with open(output_pdf, "wb") as output:
        pdf_writer.write(output)

    FileHandling.deleteFolder(temporalFolder)

    print(output_pdf + " created successfully!")



def create_cbz(images_folder, imagesList, output_cbz, temporalFolder=".Temporal"):

    FileHandling.ensureExistance(temporalFolder)
    if sorted(imagesList) != imagesList:
        for image_file in imagesList:
            FileHandling.copyFile(
                images_folder,
                image_file,
                temporalFolder,
                str(imagesList.index(image_file)) + ".jpg",
            )
        images_folder = temporalFolder
        imagesList = FileHandling.findPatternFolder(temporalFolder, ".jpg$")

    with zipfile.ZipFile(output_cbz, "w", zipfile.ZIP_DEFLATED) as cbz:
        for image_file in imagesList:
            image_path = os.path.join(images_folder, image_file)
            with Image.open(image_path) as img:  # Does this do anything?
                # rgb_image = img.convert("RGB")
                cbz.write(image_path, arcname=os.path.basename(image_path))

    FileHandling.deleteFolder(temporalFolder)

    print(output_cbz + " created successfully!")


def nameCreator(
    manga, division, name, inversion: bool, number, numeration: bool, format
):
    if numeration:
        middle = division + " " + str(number)
    else:
        middle = division

    if inversion:
        middle = name + " " + middle
    else:
        middle = middle + " " + name

    return manga + " " + middle + format


def preparationForCBZ(manga, minimum, callerDirectory, division):
    mangaObject = MangaCreator(manga, callerDirectory)


    image_folder = os.path.join(callerDirectory, "." + manga + "JPG")
    enumeration = os.path.join(callerDirectory, manga + "Numeration.csv")
    pdfFolder = os.path.join(callerDirectory, manga + " CBZ")

    FileHandling.ensureExistance(image_folder)
    FileHandling.ensureExistance(pdfFolder)

    enumeration = CsvHandling.openCsv(enumeration)
    divide = mangaObject.divider(division)

    names = []
    [names.append(x) for x in enumeration[division] if x not in names]

    in_order = sum(1 for i in range(len(names) - 1) if names[i] <= names[i + 1])
    total_pairs = len(names) - 1
    needNumberFlag = (in_order / total_pairs) < 0.9

    for i in divide:
        name = nameCreator(
            manga,
            division,
            names[divide.index(i)],
            False,
            divide.index(i) + 1,
            needNumberFlag,
            ".cbz",
        )
        create_cbz(image_folder, i[::-1], os.path.join(pdfFolder, name))

    zipping.zipAndDelete(image_folder)
