from fastapi import APIRouter, Depends

from dto.search_dto import SearchParam
from controller.places_controller import PlacesController

router = APIRouter()
places_controller = PlacesController()

@router.get("")
async def get_places(params: SearchParam = Depends()):
    return places_controller.get_places(params)