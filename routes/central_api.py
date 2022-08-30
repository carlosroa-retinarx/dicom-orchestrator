import json
from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request
import requests
from starlette.status import *

from lib_dev.scu_retina_get import search_dcm_image
from lib_dev.img_file_manager import dcm_format_to
from models.study_request_change_state import StudyChangeState

router = APIRouter()


@router.post('/mo01')
async def recieve_request_MO_01(uid: str):
    ml_url = ''
    api_url = ''
    # MO-02
    img = search_dcm_image(uid)  # MO-03
    if img:
        # MO-04
        png_img = dcm_format_to(img, output=True)
        data = dict(
            uid=uid,
        )
        study_to_change_state = StudyChangeState(**data)
        api_req = requests.post(api_url, data=json.dumps({study_to_change_state}))
        if api_req.status_code == 200:
            # MO-05
            ml_req = requests.post(ml_url, data=json.dumps({'img_info': png_img}))
            if ml_req.status_code == 200:
                return JSONResponse(content={"message": "image sended successfully to ml_model api"}, status_code=HTTP_200_OK)
            else:
                return JSONResponse(content={"message": "something happend with the ml_model api"}, status_code=HTTP_404_NOT_FOUND)
        else:
            return JSONResponse(content={"message": "something happend with the central api"}, status_code=HTTP_404_NOT_FOUND)
    else:
        return JSONResponse(content={"message": "image not found in retina´s pacs"}, status_code=HTTP_404_NOT_FOUND)


@router.post('/mo-06')
async def recieve_ml_model_results(request: Request):
    data = request.body()
