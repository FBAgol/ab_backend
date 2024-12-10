from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def get_Projects():
    return {"message": "Hello World"}   
