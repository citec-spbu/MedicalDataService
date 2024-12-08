from pydicom import FileDataset
from app.series.dao import SeriesDAO


async def index_series(ds: FileDataset, study_id: str, dicom_file_id: int):
    if "ImageType" in ds:
        series_id: str = ds.SeriesInstanceUID
        series_name: str = "DEFAULT SERIES NAME"
        if "SeriesDescription" in ds:
            series_name = str(ds.SeriesDescription)
        series = await SeriesDAO.find_one_or_none(
            id=series_id
        )
        if series is None:
            query = {"id": series_id,
                     "study_id": study_id,
                     "dicom_file_id": dicom_file_id,
                     "scale": [1, 1, 1],
                     "series_name": series_name}
            return await SeriesDAO.add(**query)
        return series
