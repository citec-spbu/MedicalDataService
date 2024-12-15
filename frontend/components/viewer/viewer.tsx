"use client";

import { useRef, useState } from "react";

import Tools from "./viewer-tools";

import useViewport from "./hooks/useViewport";
import ViewportData from "./viewportData";
import ViewerField from "./viewer-main";
import ViewerSelector from "./viewer-selector";

export interface activeSeriesProps {
  StudyInstanceUID: string;
  SeriesInstanceUID: string;
}

export const Viewer = () => {
  const elementRef = useRef<HTMLDivElement>(null);
  const [activeSeries, setActiveSeries] = useState<activeSeriesProps | null>(
    null
  );
  const { viewport, isLoaded } = useViewport({
    activeSeries,
    elementRef
  });

  return (
    <>
      <ViewerSelector
        activeSeries={activeSeries}
        setActiveSeries={setActiveSeries}
      />

      <div className="grow flex flex-col h-full gap-2">
        <Tools viewport={viewport} isLoaded={isLoaded} />

        <ViewerField ref={elementRef}>
          <div className="absolute text-white z-10 p-4">
            {isLoaded && (
              <ViewportData viewport={viewport} element={elementRef.current} />
            )}
          </div>
        </ViewerField>
      </div>
    </>
  );
};
