import { memo, useEffect, useState } from "react";
import { Card } from "../ui/card";
import { Tabs, TabsList, TabsTrigger } from "../ui/tabs";
import { ScrollArea } from "../ui/scroll-area";
import { useSearchParams } from "next/navigation";
import { activeSeriesProps } from "./viewer";
import { CubeIcon } from "@radix-ui/react-icons";

const API = process.env.API;
interface SelectorProps {
  activeSeries: activeSeriesProps | null;
  setActiveSeries: (series: activeSeriesProps) => void;
}

interface seriesProps {
  StudyInstanceUID: string;
  SeriesInstanceUID: string;
  description: string;
  modality: string;
  instancesCount: number;
  firstInstanceUID?: string;
}

const ViewerSelector = ({ activeSeries, setActiveSeries }: SelectorProps) => {
  const searchParams = useSearchParams();

  const studyUID = searchParams.get("StudyUID");
  const seriesUID = searchParams.get("SeriesUID");

  const [series, setSeries] = useState<seriesProps[]>([]);

  useEffect(() => {
    const fetchData = async () => {
      const response = await fetch(`${API}/studies/${studyUID}/series`);
      if (response.ok) {
        const data = await response.json();
        const seriesWithInstances = await Promise.all(
          data.map(async (series) => {
            const instancesResponse = await fetch(
              `${API}/studies/${series["0020000D"]?.["Value"]?.[0]}/series/${
                series["0020000E"]?.["Value"]?.[0]
              }/instances`
            );
            const instances = await instancesResponse.json();
            const firstInstanceUID = instances[0]?.["00080018"]?.["Value"]?.[0];

            return {
              StudyInstanceUID: series["0020000D"]?.["Value"]?.[0],
              SeriesInstanceUID: series["0020000E"]?.["Value"]?.[0],
              description: series["0008103E"]?.["Value"]?.[0],
              modality: series["00080060"]?.["Value"]?.[0],
              instancesCount: series["00201209"]?.["Value"]?.[0],
              firstInstanceUID
            } as seriesProps;
          })
        );
        setSeries(seriesWithInstances);
        setActiveSeries({
          StudyInstanceUID: studyUID!,
          SeriesInstanceUID: seriesUID!
        });
      }
    };
    fetchData();
  }, [studyUID, seriesUID, setActiveSeries]);

  return (
    <Card className="h-full w-[300px]">
      <Tabs
        orientation="vertical"
        defaultValue={JSON.stringify(activeSeries)}
        value={JSON.stringify(activeSeries)}
        onValueChange={(value) => {
          if (value) setActiveSeries(JSON.parse(value));
        }}
        className="w-full h-full p-4"
      >
        <TabsList className="flex-col w-full h-full justify-start bg-card gap-2">
          <ScrollArea className="p-4" type="auto">
            {series.map((item) => (
              <TabsTrigger
                key={item.SeriesInstanceUID}
                value={JSON.stringify({
                  StudyInstanceUID: item.StudyInstanceUID,
                  SeriesInstanceUID: item.SeriesInstanceUID
                } as activeSeriesProps)}
                className="w-full data-[state=active]:bg-muted pt-4"
              >
                <div className="flex flex-col max-w-[224px]">
                  <Card className="w-[224px] h-[126px] relative">
                    {item.firstInstanceUID && (
                      <img
                        src={`${API}/studies/${item.StudyInstanceUID}/series/${item.SeriesInstanceUID}/instances/${item.firstInstanceUID}/preview`}
                        alt={item.description}
                        className="w-full h-full object-contain"
                        loading="lazy"
                        onError={(e) => {
                          e.currentTarget.style.display = 'none';
                        }}
                      />
                    )}
                    <div className="absolute top-2 left-2 bg-black/50 px-2 py-1 rounded text-white">
                      {item.modality}
                    </div>
                  </Card>
                  <div className="w-full grid grid-cols-[8fr_1fr_1fr]">
                    <div
                      className="text-nowrap text-ellipsis overflow-hidden text-start"
                      title={item.description}
                    >
                      {item.description}
                    </div>
                    <CubeIcon className="self-center justify-self-center" />
                    {item.instancesCount}
                  </div>
                </div>
              </TabsTrigger>
            ))}
          </ScrollArea>
        </TabsList>
      </Tabs>
    </Card>
  );
};

export default memo(ViewerSelector);
