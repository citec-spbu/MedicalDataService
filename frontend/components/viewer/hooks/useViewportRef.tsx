"use client";

import { MutableRefObject, useEffect, useRef, useState } from "react";

import {
  cornerstoneStreamingImageVolumeLoader,
  init as csInit,
  Enums,
  getRenderingEngine,
  RenderingEngine,
  Types,
  volumeLoader
} from "@cornerstonejs/core";
import { init as csToolsInit } from "@cornerstonejs/tools";
import { init as dicomImageLoaderInit } from "@cornerstonejs/dicom-image-loader";
import createImageIdsAndCacheMetaData from "@/lib/cornerstonejs/createImageIdsAndCacheMetaData";

const viewportId = "MAIN_VIEWPORT";

export interface Series {
  viewportID: string;
  StudyInstanceUID: string;
  SeriesInstanceUID: string;
  wadoRsRoot: string;
}

interface ViewportProps {
  series: Series;
  elementRef: MutableRefObject<HTMLDivElement | null>;
}

export default function useViewportRef({ series, elementRef }: ViewportProps): {
  viewport: Types.IVolumeViewport | null;
  isLoaded: boolean;
} {
  const renderingEngineRef = useRef<Types.IRenderingEngine | undefined>(
    undefined
  );
  const viewportRef = useRef<Types.IVolumeViewport | null>(null);
  const volumeRef = useRef<Types.IImageVolume | null>(null);
  const isRunning = useRef<boolean>(false);
  const [isLoaded, setIsLoaded] = useState<boolean>(false);

  //const viewportRef = useRef<Types.IVolumeViewport | null>(null);

  useEffect(() => {
    if (!isRunning.current) {
      csInit();
      csToolsInit();
      dicomImageLoaderInit({ maxWebWorkers: 3 });

      volumeLoader.registerUnknownVolumeLoader(
        // @ts-expect-error: According to official docs.
        cornerstoneStreamingImageVolumeLoader
      );
    }
    isRunning.current = true;

    const renderingEngineId = "myRenderingEngine";
    renderingEngineRef.current = getRenderingEngine(renderingEngineId);
    if (!renderingEngineRef.current)
      renderingEngineRef.current = new RenderingEngine(renderingEngineId);

    const viewportInput: Types.PublicViewportInput = {
      viewportId,
      type: Enums.ViewportType.ORTHOGRAPHIC,
      element: elementRef.current!,
      defaultOptions: {
        orientation: Enums.OrientationAxis.AXIAL
        //background: [0.2, 0, 0.2] as Types.Point3
      }
    };

    renderingEngineRef.current?.enableElement(viewportInput);
  }, [elementRef]);

  useEffect(() => {
    const handleResize = () => {
      renderingEngineRef.current?.resize();
    };

    window.addEventListener("resize", handleResize);
    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, []);

  useEffect(() => {
    (async () => {
      setIsLoaded(false);
      const volumeId = series.SeriesInstanceUID;

      const imageIds = await createImageIdsAndCacheMetaData({
        StudyInstanceUID: series.StudyInstanceUID,
        SeriesInstanceUID: series.SeriesInstanceUID,
        wadoRsRoot: series.wadoRsRoot
      });

      viewportRef.current = renderingEngineRef.current?.getViewport(
        viewportId
      ) as Types.IVolumeViewport;

      volumeRef.current = await volumeLoader.createAndCacheVolume(volumeId, {
        imageIds
      });

      (volumeRef.current as Types.IStreamingImageVolume).load();

      viewportRef.current.setVolumes([{ volumeId }]);

      viewportRef.current.render();
      setIsLoaded(true);
    })();
  }, [series]);

  return { viewport: viewportRef.current, isLoaded };
}
