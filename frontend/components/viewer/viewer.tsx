"use client";

import { useCallback, useRef, useState } from "react";

import Tools from "./viewer-tools";

import useViewportRef, { Series } from "./hooks/useViewportRef";
import ViewportData from "./viewportData";
import ViewerField from "./viewer-main";
import ViewerSelector from "./viewer-selector";

const study: Series[] = [
  {
    viewportID: "CT",
    StudyInstanceUID:
      "1.3.6.1.4.1.14519.5.2.1.7009.2403.334240657131972136850343327463",
    SeriesInstanceUID:
      "1.3.6.1.4.1.14519.5.2.1.7009.2403.226151125820845824875394858561",
    wadoRsRoot: "https://d14fa38qiwhyfd.cloudfront.net/dicomweb"
  },

  {
    viewportID: "PT",
    StudyInstanceUID:
      "2.16.840.1.114362.1.11972228.22789312658.616067305.306.2",
    SeriesInstanceUID:
      "2.16.840.1.114362.1.11972228.22789312658.616067305.306.3",
    wadoRsRoot: "https://d14fa38qiwhyfd.cloudfront.net/dicomweb"
  }
];

export const Viewer = () => {
  const elementRef = useRef<HTMLDivElement>(null);
  const [activeSeriesIdx, setActiveSeriesIdx] = useState<string>("0");
  const { viewport, isLoaded } = useViewportRef({
    series: study[Number(activeSeriesIdx)],
    elementRef
  });

  const setActiveSeriesIdxCallback = useCallback((value: string) => {
    setActiveSeriesIdx(value);
  }, []);

  return (
    <>
      <ViewerSelector
        study={study}
        activeIdx={activeSeriesIdx}
        setActiveIdx={setActiveSeriesIdxCallback}
      />

      <div className="grow flex flex-col h-full gap-2">
        <Tools viewport={viewport} isLoaded={isLoaded} />

        <ViewerField ref={elementRef}>
          <div className="absolute text-white z-10 p-4">
            <button onClick={() => console.log(viewport)}>click</button>
            {isLoaded && (
              <ViewportData viewport={viewport} element={elementRef.current} />
            )}
          </div>
        </ViewerField>
      </div>
    </>
  );
};
