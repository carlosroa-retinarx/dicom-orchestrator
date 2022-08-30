import os
import numpy as np
from PIL import Image
import tempfile
from pydicom.filewriter import dcmwrite
from pydicom.filereader import dcmread
from pydicom.dataset import FileDataset, FileMetaDataset
from pydicom.uid import UID
from datetime import date, datetime
from dotenv import load_dotenv
import base64

load_dotenv()


def to_binary(img_path):
    """
    Transform a file to binary
    :param img_path: str with img path
    :return: binary file
    """
    with open(img_path, 'rb') as f:
        return f.read()


def base64_encode(img_path):
    with open(img_path, "rb") as f:
        return base64.b64encode(f.read())
    # with open(img_path, "rb") as f:
    #     return base64.b64encode(f.read())


def base64_decode(b64_string):
    return b64_string.decode('utf-8')


def dcm_format_to(img_path: str, format='png', output: bool = False):
    """
    Convert a dcm image
    Example: file_name = dcm_format('my_dicom_file.dcm', 'png')
    :param output: if True return img file converted
    :param img_path: str with the image path
    :param format: format to convert
    :returns: img file converted
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

    if output is True:
        return final_image


# x = dcm_format_to("RG1_JLSN.dcm")
# print(x)


def format_to_dcm(img_path: str, img_name: str, output: bool = False):
    """
        Convert an image to dcm
        Example: file_name = dcm_format('my_dicom_file.dcm', 'png')
        :param output: if True return img file converted
        :param img_name: str with file's name
        :param img_path: str with the image path
        :returns: img file converted into dcm format
        :exception: Image not found
        :exception: Format must be a string
        """

    # Create some temporary filenames
    suffix = '.dcm'
    temp_file = tempfile.NamedTemporaryFile(suffix=suffix).name

    # Populate required values for file meta information
    file_meta = FileMetaDataset()
    file_meta.MediaStorageSOPClassUID = UID('1.2.840.10008.5.1.4.1.1.1')  # ComputedRadiographyImageStorage
    file_meta.MediaStorageSOPInstanceUID = UID("1.2.3")
    file_meta.ImplementationClassUID = UID("1.2.3.4")

    # Create the FileDataset instance (initially no data elements, but file_meta supplied)
    ds = FileDataset(temp_file, {}, file_meta=file_meta, preamble=b"\0" * 128)

    # Add the data elements -- not trying to set all required here. Check DICOM standard
    ####### Aquí van valores pasados a la funcion con la metadata relacionada a la imagen #######
    patient_name = "Test^Firstname"
    ds.PatientName = patient_name
    patient_id = "123456"
    ds.PatientID = patient_id

    # Set the transfer syntax
    ds.is_little_endian = True
    ds.is_implicit_VR = True

    # Set creation date/time
    dt = datetime.now()
    ds.ContentDate = dt.strftime('%Y%m%d')
    timeStr = dt.strftime('%H%M%S.%f')  # long format with micro seconds
    ds.ContentTime = timeStr
    date_to_filename = dt.strftime("%m-%d-%Y_%H-%M-%S")

    # Image Pgn Info
    try:
        # windows
        img = Image.open(f'{img_path}//{img_name}')  # the PNG or JPG file to be replace
    except:
        # linux
        img = Image.open(f'{img_path}\\{img_name}')  # the PNG or JPG file to be replace

    if img.mode == 'L':
        np_image = np.array(img.getdata(), dtype=np.uint8)
        ds.Rows = img.height
        ds.Columns = img.width
        ds.PhotometricInterpretation = "MONOCHROME1"
        ds.SamplesPerPixel = 1
        ds.BitsStored = 8
        ds.BitsAllocated = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0
        ds.PixelData = np_image.tobytes()
        ds.is_little_endian = True
        ds.is_implicit_VR = True

    elif img.mode == 'RGBA':
        np_image = np.array(img.getdata(), dtype=np.uint8)[:, :3]
        ds.Rows = img.height
        ds.Columns = img.width
        ds.PhotometricInterpretation = "RGB"
        ds.SamplesPerPixel = 3
        ds.BitsStored = 8
        ds.BitsAllocated = 8
        ds.HighBit = 7
        ds.PixelRepresentation = 0
        ds.PixelData = np_image.tobytes()
        ds.is_little_endian = True
        ds.is_implicit_VR = True

    print("Writing test file", temp_file)
    ds.save_as(temp_file)
    print("File saved.")

    # Create the dicom file
    file_name = f'{patient_name}_{patient_id}_{date_to_filename}{suffix}'
    dcmwrite(filename=file_name, dataset=ds)

    print('Load file {} ...'.format(temp_file))
    ds = dcmread(temp_file)
    # print(ds)

    # Remove the created file
    print('Remove file {} ...'.format(temp_file))
    os.remove(temp_file)

    if output is True:
        return ds


# x = format_to_dcm('.', 'RG1_JLSN_2022-08-25.png', output=True)
# print(x)

