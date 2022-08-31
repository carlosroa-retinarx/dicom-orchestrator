import os
import numpy as np
import pydicom
from PIL import Image
import tempfile
from pydicom.filewriter import dcmwrite
from pydicom.filereader import dcmread
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import UID
from datetime import date, datetime
from dotenv import load_dotenv
import cv2


load_dotenv()


def dcm_format_to(img_path: str, format='png'):
    """
    Convert a dcm image
    Example: file_name = dcm_format('my_dicom_file.dcm', 'png')
    :param img_path: str with the image path
    :param format: format to convert
    :returns: Filename
    :exception: Image not found
    :exception: Format must be a string
    """
    # Reading the file.dcm
    try:
        # windows
        im = dcmread(img_path)
    except:
        try:
            # linux
            im = dcmread(img_path.replace('/', '\\'))
        except:
            raise Exception("Image not found")
    filename = im.filename
    # Convert into a pixel array
    im = im.pixel_array.astype(float)

    # Rescaling pixel array (0-1)*255 (0-255)
    rescaled_image = (np.maximum(im, 0) / im.max()) * 255  # float pixels
    final_image = np.uint8(rescaled_image)  # integer pixels

    # Create the image
    final_image = Image.fromarray(final_image)
    # final_image.show())

    if isinstance(format, str):
        # Save the image.format Images/UID_date/original/SerieInstanceUID.format 0020,000e
        file_name = f'{filename.replace(".dcm", "")}_{str(date.today())}.{format}'
        final_image.save(f'{file_name}', format='png')
    else:
        raise Exception("Format must be a string")

    return file_name


# x = dcm_format_to("RG1_JLSN.dcm")
# print(x)


def format_to_dcm(img_path: str, img_name: str, fileid: str):
    """
        Convert an image to dcm
        Example: file_name = dcm_format('my_dicom_file.dcm', 'png')
        :param img_name: str with file's name
        :param img_path: str with the image path
        :returns: Filename
        :exception: Image not found
        :exception: Format must be a string
        """

    # Create some temporary filenames
    suffix = '.dcm'
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix).name

    indexnumbertemp = fileid.split('_')
    print(indexnumbertemp)
    indexnumber = indexnumbertemp[len(indexnumbertemp) - 1]

    sop_instance_uid = "1.2.826.0.1.3680043.10.1026.1." + indexnumber

    # Populate required values for file meta information
    file_meta = FileMetaDataset()
    file_meta.FileMetaInformationGroupLength = 190
    file_meta.FileMetaInformationVersion = b'\x00\x01'
    file_meta.MediaStorageSOPClassUID = UID('1.2.840.10008.5.1.4.1.1.1')  # ComputedRadiographyImageStorage
    file_meta.MediaStorageSOPInstanceUID = UID(sop_instance_uid)
    file_meta.TransferSyntaxUID = UID('1.2.840.10008.1.2.1')  # Explicit VR Little Endian
    file_meta.ImplementationClassUID = UID("1.2.826.0.1.3680043.10.1026")
    file_meta.ImplementationVersionName = "retinarx-1.0"

    # Create the FileDataset instance (initially no data elements, but file_meta supplied)
    ds = FileDataset(temp_file, {}, file_meta=file_meta, preamble=b"\0" * 128)
    print("DS", ds)

    # Add the data elements -- not trying to set all required here. Check DICOM standard
    ####### Aquí van valores pasados a la funcion con la metadata relacionada a la imagen #######
    patient_name = "RetinaRX^Dataset01-" + fileid
    ds.PatientName = patient_name
    patient_id = fileid + indexnumber
    ds.PatientID = patient_id
    ds.Modality = "CR"
    ds.StudyInstanceUID = UID("1.2.826.0.1.3680043.10.1026.2." + indexnumber)
    ds.SeriesInstanceUID = UID("1.2.826.0.1.3680043.10.1026.2.1." + indexnumber)
    ds.SOPInstanceUID = UID(sop_instance_uid)
    ds.SOPClassUID = UID("1.2.840.10008.5.1.4.1.1.1")
    ds.StudyDate = "20220827"
    ds.AccessionNumber = "100" + indexnumber
    ds.StudyID = indexnumber
    ds.SeriesNumber = "1"
    ds.InstanceNumber = "1"
    ds.BodyPartExamined = "CHEST"
    ds.PixelSpacing = [1, 1]
    ds.PatientBirthDate = "19720827"
    ds.PatientSex = "M"
    ds.StudyDescription = "Test"
    ds.PatientAge = "050Y"

    # Set the transfer syntax
    ds.is_little_endian = True
    ds.is_implicit_VR = False

    # Set creation date/time
    dt = datetime.now()
    ds.ContentDate = dt.strftime('%Y%m%d')
    timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds
    # ds.ContentTime = timeStr
    date_to_filename = dt.strftime("%m-%d-%Y_%H-%M-%S")

    # Image Pgn Info
    try:
        # windows
        cv2img = cv2.imread(f'{img_path}//{img_name}', -1)  # the PNG or JPG file to be transformed

    except:
        # linux
        cv2img = cv2.imread(f'{img_path}', -1)  # the PNG or JPG file to be transformed

    cv2img = cv2.resize(cv2img, (512, 512))
    # cv2.imshow("cv2img", cv2img)
    # cv2.waitKey()

    ds.Rows = cv2img.shape[0]
    ds.Columns = cv2img.shape[1]
    ds.PhotometricInterpretation = "MONOCHROME2"
    ds.SamplesPerPixel = 1
    ds.BitsStored = 16
    ds.BitsAllocated = 16
    ds.HighBit = 15
    ds.PixelRepresentation = 0
    ds.PixelData = cv2img.tobytes()

    pydicom.dataset.validate_file_meta(ds.file_meta, enforce_standard=True)

    # Create the dicom file
    dcmwrite(filename=f'./inDICOM_padchest_sample2/{patient_id}{suffix}', dataset=ds)

    print('Load file {} ...'.format(temp_file))
    print(ds)


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print(os.getcwd())
    names = set()
    i = 0
    for f in os.listdir('./padchest_sample2'):
        i = i + 1
        name = f.split('.')[0].split("_")[1]
        if name not in names:
            name = name + "_" + str(i)
            names.add(name)
            format_to_dcm("./padchest_sample2", f, name)
        else:
            name = name + "_" + f.split('.')[0].split("_")[2]
            name = name + "_" + str(i)
            names.add(name)
            format_to_dcm("./padchest_sample2", f, name)
