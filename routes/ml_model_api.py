from asyncio import sleep

from fastapi import APIRouter

router = APIRouter()


@router.get('/all')
async def send_get():
    await sleep(2)
    return "I was sleeping sorry"
