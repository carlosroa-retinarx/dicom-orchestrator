import os
from dotenv import load_dotenv
from pydantic import ValidationError
from pydicom import Dataset
from pydicom.uid import JPEGLSLossless
from pynetdicom import AE, debug_logger, build_role, evt, build_context
from models.dicom_tags_model import DicomTags
from pynetdicom.sop_class import (PatientRootQueryRetrieveInformationModelGet,
                                  ComputedRadiographyImageStorage,
                                  StudyRootQueryRetrieveInformationModelGet)


debug_logger()


def search_dcm_image(uid: str):

    load_dotenv()

    # Implement the handler for evt.EVT_C_STORE
    def handle_store(event):
        """Handle a C-STORE request event."""
        ds = event.dataset
        ds.file_meta = event.file_meta

        # Save the dataset using the SOP Instance UID as the filename
        ds.save_as(ds.SOPInstanceUID, write_like_original=False)

        # Return a 'Success' status
        return 0x0000

    handlers = [(evt.EVT_C_GET, handle_store)]

    ae = AE(ae_title=os.environ.get('MY_AETITLE'))
    # ae.add_requested_context(Verification)
    # ae.add_requested_context(StudyRootQueryRetrieveInformationModelGet)
    req_contexts = [build_context(StudyRootQueryRetrieveInformationModelGet), build_context("1.2.840.10008.1.2.4.80")]
    # ae.add_requested_context(StudyRootQueryRetrieveInformationModelGet)
    # ae.add_requested_context(JPEGLSLossless)
    # ae.add_requested_context(UID("1.2.840.10008.1.2.4.80"))
    # ae.add_requested_context("1.2.840.10008.1.2.4.80")
    # Add the requested presentation context (Storage SCP)
    # ae.add_requested_context(ComputedRadiographyImageStorage)

    # Create an SCP/SCU Role Selection Negotiation item for CT Image Storage
    role = build_role(JPEGLSLossless, scp_role=True)

    # Creating an Application Entity (AE) object.
    # Create our Identifier (query) dataset
    ds = Dataset()

    ds.StudyInstanceUID = uid
    ds.QueryRetrieveLevel = 'STUDY'
    ds.PatientID = '10569431-8'
    # ds.SeriesInstanceUID = '1.3.51.0.7.12398455002.49502.20811.41540.47660.2090.21658'

    PEER_PORT = int(os.environ.get('PEER_PACS_PORT'))
    PEER_PACS_ADDRESS = os.environ.get('PEER_PACS_ADDRESS')
    PEER_PACS_AETITLE = os.environ.get('PEER_PACS_AETITLE')
    # Associate with the peer AE at IP 127.0.0.1 and port 11112
    assoc = ae.associate(PEER_PACS_ADDRESS, PEER_PORT, ae_title=PEER_PACS_AETITLE, ext_neg=[role], evt_handlers=handlers, contexts=req_contexts)

    if assoc.is_established:
        # Send the C-FIND request
        responses = assoc.send_n_get(ds, StudyRootQueryRetrieveInformationModelGet, instance_uid=uid)

        # --> Group uids and studies elements
        for (status, identifier) in responses:
            if status:
                print('C-GET query status: 0x{0:04x}'.format(status.Status))
                if identifier is not None:
                    # print(identifier.FailedSOPInstanceUIDList)
                    for elem in identifier:
                        print(elem)

            else:
                print('Connection timed out, was aborted or received invalid response')

        # Release the association
        assoc.release()

    else:
        print('Association rejected, aborted or never connected')


ARCHIVO_EJEMPLO = {"StudyInstanceUID": "1.3.51.0.7.11889403511.11057.11336.32858.32735.7961.22171"}
search_dcm_image(ARCHIVO_EJEMPLO.get("StudyInstanceUID"))
