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
import { activeSeriesProps } from "../viewer";
import { IVolumeViewport } from "@cornerstonejs/core/types";

const volumeViewportId = "VOLUME_VIEWPORT";
const stackViewportId = "STACK_VIEWPORT";

const API = process.env.API;

const volumeViewportInput = (
  element: HTMLDivElement,
  axisType: Enums.OrientationAxis
): Types.PublicViewportInput => {
  return {
    viewportId: volumeViewportId,
    type: Enums.ViewportType.ORTHOGRAPHIC,
    element: element,
    defaultOptions: {
      orientation: axisType
      //background: [0.2, 0, 0.2] as Types.Point3
    }
  };
};

const stackViewportInput = (
  element: HTMLDivElement
): Types.PublicViewportInput => {
  return {
    viewportId: stackViewportId,
    type: Enums.ViewportType.STACK,
    element: element
  };
};

interface ViewportProps {
  activeSeries: activeSeriesProps | null;
  elementRef: MutableRefObject<HTMLDivElement | null>;
}

export default function useViewport({
  activeSeries,
  elementRef
}: ViewportProps): {
  viewport: Types.IVolumeViewport | Types.IStackViewport | null;
  isLoaded: boolean;
} {
  const renderingEngineRef = useRef<Types.IRenderingEngine | undefined>(
    undefined
  );
  const viewportRef = useRef<
    Types.IVolumeViewport | Types.IStackViewport | null
  >(null);
  const volumeRef = useRef<Types.IImageVolume | Types.IImage | null>(null);
  const isRunning = useRef<boolean>(false);
  const axisType = useRef<Enums.OrientationAxis>(Enums.OrientationAxis.AXIAL);
  const [isLoaded, setIsLoaded] = useState<boolean>(false);

  useEffect(() => {
    if (!isRunning.current) {
      csInit();
      csToolsInit();
      dicomImageLoaderInit({
        maxWebWorkers: 3,
        beforeSend(xhr) {
          xhr.setRequestHeader(
            "Authorization",
            `Bearer ${localStorage.getItem("accessToken")}`
          );
        }
      });

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

    renderingEngineRef.current.enableElement(
      volumeViewportInput(elementRef.current!, axisType.current)
    );
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
    if (activeSeries) {
      (async () => {
        setIsLoaded(false);

        const { imageIds, viewportType } = await createImageIdsAndCacheMetaData(
          {
            StudyInstanceUID: activeSeries.StudyInstanceUID,
            SeriesInstanceUID: activeSeries.SeriesInstanceUID,
            wadoRsRoot: `${API}/dicomweb`
          }
        );

        const volumeId = activeSeries.SeriesInstanceUID;
        if (viewportType == "volume") {
          if (renderingEngineRef.current?.getStackViewports().length) {
            renderingEngineRef.current?.disableElement(stackViewportId);
            renderingEngineRef.current?.enableElement(
              volumeViewportInput(elementRef.current!, axisType.current)
            );
          }

          viewportRef.current = renderingEngineRef.current?.getViewport(
            volumeViewportId
          ) as Types.IVolumeViewport;

          volumeRef.current = await volumeLoader.createAndCacheVolume(
            volumeId,
            {
              imageIds
            }
          );

          (volumeRef.current as Types.IStreamingImageVolume).load();

          viewportRef.current.setVolumes([{ volumeId }]);
        } else if (viewportType == "stack") {
          if (renderingEngineRef.current?.getVolumeViewports().length) {
            axisType.current = (
              renderingEngineRef.current.getViewport(
                volumeViewportId
              ) as IVolumeViewport
            ).viewportProperties.orientation!;
            renderingEngineRef.current?.disableElement(volumeViewportId);
            renderingEngineRef.current?.enableElement(
              stackViewportInput(elementRef.current!)
            );
          }

          viewportRef.current = renderingEngineRef.current?.getViewport(
            stackViewportId
          ) as Types.IStackViewport;

          viewportRef.current.setStack(imageIds);
        }
        viewportRef.current?.render();
        setIsLoaded(true);
      })();
    }
  }, [activeSeries, elementRef]);

  return { viewport: viewportRef.current, isLoaded };
}
