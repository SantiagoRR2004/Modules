from Modules import FileHandling, CsvHandling, zipping
from typing import List, Dict
import PyPDF2
from reportlab.pdfgen import canvas
from PIL import Image
import os
from collections import Counter
import zipfile


class MangaCreator:
    temporalFolder = ".Temporal"

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
        self.imageFolder = imageFolder
        FileHandling.ensureExistance(imageFolder)
        self.images = sorted(os.listdir(imageFolder))

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

    def createFiles(self, division: str, extension: str) -> None:
        methodName = f"create{extension.upper()}"
        method = getattr(self, methodName, None)

        # Check if the method exists and is callable
        if not callable(method):
            print(f"Unsupported extension: {extension}")
            return

        finalFolder = os.path.join(
            self.callerDirectory, self.manga.replace(" ", "") + " " + extension.upper()
        )
        FileHandling.ensureExistance(finalFolder)

        dividedImages = self.divider(division)
        names = [n + "." + extension.lower() for n in self.getNames(division)]

        # Create the temporal folder if it doesn't exist
        FileHandling.ensureExistance(self.temporalFolder)

        for i, segment in enumerate(dividedImages):

            # Check if the segment is empty
            if not segment:
                print(f"No images found for '{names[i]}'.")
            else:
                fileName = os.path.join(finalFolder, names[i])

                try:
                    method(segment, fileName)
                    print(f"{fileName} created successfully!")
                except Exception as e:
                    print(f"Error creating {names[i]}: {e}")

        # Clean up
        zipping.zipAndDelete(self.imageFolder)
        FileHandling.deleteFolder(self.temporalFolder)

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
            name
            for i, name in enumerate(self.enumeration[division])
            if name not in self.enumeration[division][:i]
        ]

        # Remove None values if they exist
        if None in uniqueList:
            uniqueList.remove(None)

        # Divide the files based on the unique values in the division
        for i in uniqueList:
            segment = []
            for j in range(len(self.enumeration[division])):
                if self.enumeration[division][j] == i:

                    for image in self.images:
                        marker = "".join(image.split(".")[:-1])  # Remove the extension
                        marker = marker[:-3]  # No more than 999 images
                        if marker == self.enumeration[self.minimum][j]:
                            segment.append(image)

            toret.append(segment)

        return toret

    def getNames(self, division: str) -> List[str]:
        """
        Returns the names of the manga based on the specified division.

        Args:
            - division (str): The key in the enumeration dictionary to get names from.

        Returns:
            - List[str]: A list of names corresponding to the unique values in the division.
        """
        uniqueList = []

        # This is like a set, but it keeps the order
        [
            uniqueList.append(x)
            for x in self.enumeration[division]
            if x not in uniqueList
        ]

        in_order = sum(
            1 for i in range(len(uniqueList) - 1) if uniqueList[i] <= uniqueList[i + 1]
        )
        total_pairs = len(uniqueList) - 1
        needNumberFlag = (in_order / total_pairs) < 0.9

        names = []

        for i in range(len(uniqueList)):
            if needNumberFlag:
                middle = division + " " + str(i + 1)
            else:
                middle = division

            middle = middle + " " + uniqueList[i]

            name = self.manga + " " + middle

            names.append(name)

        return names

    def createPDF(self, imageList: List[str], outputFile: str) -> None:
        """
        Creates a PDF file from a list of images.

        THIS IS DEPRECATED BECAUSE CALIBRE HANDLES ZIPS BETTER.

        Args:
            - imageList (List[str]): List of image filenames to include in the PDF.
            - outputFile (str): The path where the output PDF will be saved.

        Returns:
            - None
        """
        # https://stackoverflow.com/questions/44375872/pypdf2-returning-blank-pdf-after-copy

        pdf_writer = PyPDF2.PdfWriter()
        smallerPdfs = []

        cover = Image.open(os.path.join(self.imageFolder, imageList[0]))
        width = cover.width
        width = Counter(
            [Image.open(os.path.join(self.imageFolder, x)).width for x in imageList]
        ).most_common(1)[0][0]

        for image_file in imageList:
            image_path = os.path.join(self.imageFolder, image_file)

            # Open each image file using PIL
            image = Image.open(image_path)
            pageNumber = round(image.width / width)

            for i in range(pageNumber):  # Number of pages in width

                fileName = self.temporalFolder + "/" + image_file[:-4] + str(i) + ".pdf"

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
        with open(outputFile, "wb") as output:
            pdf_writer.write(output)

    def createCBZ(self, imagesList: List[str], outputFile: str) -> None:
        """
        Creates a CBZ (Comic Book Zip) file from a list of images.

        THIS IS DEPRECATED BECAUSE CALIBRE HANDLES ZIPS BETTER.

        Args:
            - imagesList (List[str]): List of image filenames to include in the CBZ.
            - outputFile (str): The path where the output CBZ will be saved.

        Returns:
            - None
        """
        for image_file in imagesList:
            FileHandling.copyFile(
                self.imageFolder,
                image_file,
                self.temporalFolder,
                str(imagesList.index(image_file)) + ".jpg",
            )
        imagesList = FileHandling.findPatternFolder(self.temporalFolder, ".jpg$")

        with zipfile.ZipFile(outputFile, "w", zipfile.ZIP_DEFLATED) as cbz:
            for image_file in imagesList:
                image_path = os.path.join(self.temporalFolder, image_file)
                with Image.open(image_path) as img:  # Does this do anything?
                    # rgb_image = img.convert("RGB")
                    cbz.write(image_path, arcname=os.path.basename(image_path))

    def createZIP(self, imagesList: List[str], outputFile: str) -> None:
        """
        Creates a ZIP file from a list of images.

        Args:
            - imagesList (List[str]): List of image filenames to include in the ZIP.
            - outputFile (str): The path where the output ZIP will be saved.

        Returns:
            - None
        """
        # First we create the folder
        FileHandling.ensureExistance(outputFile[: -len(".zip")])

        # Then we copy the images
        for image_file in imagesList:
            FileHandling.copyFile(
                self.imageFolder,
                image_file,
                outputFile[: -len(".zip")],
                image_file,
            )

        # Finally we zip the folder
        zipping.zipAndDelete(outputFile[: -len(".zip")])
