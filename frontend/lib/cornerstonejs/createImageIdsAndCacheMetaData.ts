import { api } from "dicomweb-client";
import cornerstoneDICOMImageLoader from "@cornerstonejs/dicom-image-loader";
import { refreshAccessToken } from "../api";
import { redirect } from "next/navigation";

/**
/**
 * Uses dicomweb-client to fetch metadata of a study, cache it in cornerstone,
 * and return a list of imageIds for the frames.
 *
 * Uses the app config to choose which study to fetch, and which
 * dicom-web server to fetch it from.
 *
 * @returns {string[]} An array of imageIds for instances in the study.
 */

interface SearchParams {
  StudyInstanceUID: string;
  SeriesInstanceUID: string;
  wadoRsRoot: string;
}

interface ReturnParams {
  imageIds: string[];
  viewportType: "volume" | "stack";
}

export default async function createImageIdsAndCacheMetaData({
  StudyInstanceUID,
  SeriesInstanceUID,
  wadoRsRoot
}: SearchParams): Promise<ReturnParams> {
  const SOP_INSTANCE_UID = "00080018";
  const SERIES_INSTANCE_UID = "0020000E";
  const PIXEL_SPACING = "00280030";

  const studySearchOptions = {
    studyInstanceUID: StudyInstanceUID,
    seriesInstanceUID: SeriesInstanceUID
  };

  try {
    await refreshAccessToken();
  } catch {
    localStorage.removeItem("accessToken");
    redirect("/auth/login");
  }

  const client = new api.DICOMwebClient({
    url: wadoRsRoot,
    singlepart: false,
    headers: { Authorization: `Bearer ${localStorage.getItem("accessToken")}` }
  });

  const instances = await client.retrieveSeriesMetadata(studySearchOptions);
  let viewportType: "volume" | "stack" = "volume";
  const imageIds = instances.map((instanceMetaData) => {
    const SeriesInstanceUID = instanceMetaData[SERIES_INSTANCE_UID]?.Value![0];
    const SOPInstanceUIDToUse = instanceMetaData[SOP_INSTANCE_UID]?.Value![0];
    if (instanceMetaData[PIXEL_SPACING] === undefined) {
      viewportType = "stack";
    }
    const prefix = "wadors:";

    const imageId =
      prefix +
      wadoRsRoot +
      "/studies/" +
      StudyInstanceUID +
      "/series/" +
      SeriesInstanceUID +
      "/instances/" +
      SOPInstanceUIDToUse +
      "/frames/1";

    cornerstoneDICOMImageLoader.wadors.metaDataManager.add(
      imageId,
      instanceMetaData
    );
    return imageId;
  });

  // we don't want to add non-pet
  // Note: for 99% of scanners SUV calculation is consistent bw slices

  return { imageIds: imageIds, viewportType: viewportType };
}
