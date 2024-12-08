from pydicom import FileDataset
from app.slices.dao import SliceDAO


async def index_slice(ds: FileDataset, series_id: str, number_in_series: int):
    if "ImageType" in ds:
        slice_name: str = "DEFAULT SLICE NAME"
        query = {"series_id": series_id,
                 "number_in_series": number_in_series,
                 "slice_name": slice_name}
        return await SliceDAO.add(**query)
    return None
