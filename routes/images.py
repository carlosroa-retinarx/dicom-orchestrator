from fastapi import APIRouter, Request
from dev_utils.img_file_manager import base64_encode, base64_decode
from db_conn.psql_connector import Cursor


router = APIRouter()


@router.get('/get_image')
async def get_images(cod: int = 0):
    cursor = Cursor()
    query = """SELECT * from dcm_study"""
    data = cursor.dictfetchall(query)
    return data


@router.post('/save_image')
async def save_image():
    con = Cursor().con
    con.autocommit = True
    cursor = Cursor().cursor()
    query = """INSERT INTO dcm_study (desc_dcm_study, study_instance_uid, image_file, procesable) VALUES (%s, %s, %s, %s) returning cod_dcm_study"""
    # query = """SELECT * FROM dcm_study"""
    cursor.execute(
        query,
        ('TEST1', 'bbbbb', base64_encode('./dev_utils/RG1_JLSN.dcm'), 1)
    )
    data = cursor.fetchone()[0]
    return data