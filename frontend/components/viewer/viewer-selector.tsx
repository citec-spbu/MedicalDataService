import { memo, useEffect, useState } from "react";
import { Card } from "../ui/card";
import { Tabs, TabsList, TabsTrigger } from "../ui/tabs";
import { ScrollArea } from "../ui/scroll-area";
import { useRouter, useSearchParams } from "next/navigation";
import { activeSeriesProps } from "./viewer";
import { CubeIcon } from "@radix-ui/react-icons";
import Image from "next/image";
import api from "@/lib/api";
import useApiCall from "@/lib/hooks/useApiCall";

const API = process.env.API;
interface SelectorProps {
  activeSeries: activeSeriesProps | null;
  setActiveSeries: (series: activeSeriesProps) => void;
}

interface SeriesProps {
  StudyInstanceUID: string;
  SeriesInstanceUID: string;
  description: string;
  modality: string;
  instancesCount: number;
}

const ViewerSelector = ({ activeSeries, setActiveSeries }: SelectorProps) => {
  const searchParams = useSearchParams();
  const router = useRouter();

  const studyUID = searchParams.get("StudyUID");
  const seriesUID = searchParams.get("SeriesUID");

  const [series, setSeries] = useState<SeriesProps[]>([]);

  const getData = useApiCall<any[]>(api.get);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const response = (await getData(`/dicomweb/studies/${studyUID}/series`))
          .data;

        const seriesData = response.map((series) => ({
          StudyInstanceUID: series["0020000D"]?.["Value"]?.[0],
          SeriesInstanceUID: series["0020000E"]?.["Value"]?.[0],
          description: series["0008103E"]?.["Value"]?.[0],
          modality: series["00080060"]?.["Value"]?.[0],
          instancesCount: series["00201209"]?.["Value"]?.[0]
        }));
        setSeries(seriesData);
        setActiveSeries({
          StudyInstanceUID: studyUID!,
          SeriesInstanceUID: seriesUID!
        });
      } catch {
        router.push("/studynotfound");
      }
    };
    fetchData();
  }, [studyUID, seriesUID, setActiveSeries, router, getData]);

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
                    <Image
                      src={`${API}/dicomweb/studies/${item.StudyInstanceUID}/series/${item.SeriesInstanceUID}/preview`}
                      alt={item.description}
                      width={300}
                      height={168}
                      className="w-full h-full object-contain"
                      loading="eager"
                      onError={(e) => {
                        e.currentTarget.style.display = "none";
                      }}
                    />
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
