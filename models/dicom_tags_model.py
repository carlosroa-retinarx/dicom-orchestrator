from typing import Optional

from pydantic import BaseModel


class DicomTags(BaseModel):
    SpecificCharacterSet: str
    StudyDate: str
    QueryRetrieveLevel: str
    RetrieveAETitle: str
    InstanceAvailability: str
    ModalitiesInStudy: str
    StudyDescription: str
    PatientName: str
    PatientID: str
    StudyInstanceUID: str
    SeriesInstanceUID: str
    SeriesNumber: str
    PerformedProcedureStepStartDate: Optional[str]
    PerformedProcedureStepStartTime: Optional[str]
    # study_instance_uid: str
    # transfer_syntax_uid: str
    # study_date: str
    # series_date: str
    # sop_class_uid: str
    # study_time: str
    # series_time: str
    # accession_number: str
    # modality: str
    # manufacturer: str
    # series_description: str
    # patient_name: str
    # patient_id: str
    # patient_birth_date: str
    # patient_sex: str
    # serie_instance_uid: str
    # samples_per_pixel: str
    # photometric_interpretation: str
    # number_of_frames: str
    # rows: int
    # columns: int
    # bits_allocated: str
    # bits_stored: str
    # high_bit: str
    # lossy_image_compress: str
