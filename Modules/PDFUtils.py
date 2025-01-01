from Modules import Utils
from Modules import FileHandling
from Modules import CsvHandling
from Modules import zipping
import PyPDF2
from reportlab.pdfgen import canvas
from PIL import Image
import os
from collections import Counter

# https://stackoverflow.com/questions/44375872/pypdf2-returning-blank-pdf-after-copy


def preparationForPDF(
    manga,
    callerDirectory=os.path.join(os.getcwd(), "Manga"),
    division="",
    minimum="Title",
    inversion=False,
    numeration=False,
):
    mangaSpaces = manga.replace(" ", "")
    mangaHyphens = manga.replace(" ", "-")

    infofile = os.path.join(callerDirectory, "Manga.json")
    mangaData = FileHandling.openJson(infofile)

    if mangaData.get(mangaHyphens) and mangaData.get(mangaHyphens).get("minimum"):
        minimum = mangaData[mangaHyphens]["minimum"]

    if division == "":
        division = minimum

    if mangaData.get("naming").get(division):
        inversion = mangaData["naming"][division]["inversion"]
        numeration = mangaData["naming"][division]["numeration"]

    image_folder = os.path.join(callerDirectory, "." + mangaSpaces + "JPG")
    enumeration = os.path.join(callerDirectory, mangaSpaces + "Numeration.csv")
    pdfFolder = os.path.join(callerDirectory, mangaSpaces + " PDF")

    FileHandling.ensureExistance(image_folder)
    FileHandling.ensureExistance(pdfFolder)

    enumeration = CsvHandling.openCsv(enumeration)
    images = FileHandling.findPatternFolder(image_folder, ".jpg$")
    divide = Utils.divider(images, enumeration, division, minimum)

    namesPdf = []
    [namesPdf.append(x) for x in enumeration[division] if x not in namesPdf]

    for i in divide:
        name = Utils.nameCreator(
            manga,
            division,
            namesPdf[divide.index(i)],
            inversion,
            divide.index(i) + 1,
            numeration,
            ".pdf",
        )
        convertImagesToPDF(image_folder, i[::-1], os.path.join(pdfFolder, name))

    zipping.zipAndDelete(image_folder)


def convertImagesToPDF(image_folder, imageList, output_pdf, temporalFolder=".Temporal"):
    FileHandling.ensureExistance(temporalFolder)

    pdf_writer = PyPDF2.PdfWriter()
    smallerPdfs = []

    if not imageList:
        FileHandling.deleteFolder(temporalFolder)
        print("Can't create " + output_pdf)
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
