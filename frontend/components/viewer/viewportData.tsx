import { Enums, Types } from "@cornerstonejs/core";
import { useEffect, useState } from "react";

interface ViewportDataProps {
  viewport: Types.IVolumeViewport | Types.IStackViewport | null;
  element: HTMLDivElement | null;
}

const ViewportData = ({ viewport, element }: ViewportDataProps) => {
  const [imageIndex, setImageIndex] = useState<number | undefined>(
    viewport!.getCurrentImageIdIndex() + 1
  );
  const [imageCount, setImageCount] = useState<number | undefined>(
    viewport?.getNumberOfSlices()
  );
  const [voi, setVoi] = useState<Types.VOIRange | undefined>(
    viewport?.getProperties().voiRange
  );

  useEffect(() => {
    const handleScrolling = () => {
      if (viewport) {
        setImageIndex(viewport.getCurrentImageIdIndex() + 1);
        setImageCount(viewport.getNumberOfSlices);
      }
    };

    const handleVoi = () => {
      const voiProperties = viewport?.getProperties()?.voiRange;
      if (voiProperties)
        setVoi({ upper: voiProperties.upper, lower: voiProperties.lower });
    };

    const { VOLUME_NEW_IMAGE, STACK_NEW_IMAGE, VOI_MODIFIED } = Enums.Events;

    element?.addEventListener(VOLUME_NEW_IMAGE, handleScrolling);
    element?.addEventListener(STACK_NEW_IMAGE, handleScrolling);
    element?.addEventListener(VOI_MODIFIED, handleVoi);
    return () => {
      element?.removeEventListener(VOLUME_NEW_IMAGE, handleScrolling);
      element?.removeEventListener(STACK_NEW_IMAGE, handleScrolling);
      element?.removeEventListener(VOI_MODIFIED, handleVoi);
    };
  });

  return (
    <>
      <p>
        {imageIndex} / {imageCount}
      </p>
      <p>WW : {voi?.upper}</p>
      <p>WC : {voi?.lower}</p>
    </>
  );
};

export default ViewportData;
