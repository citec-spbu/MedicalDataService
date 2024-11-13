import { memo } from "react";
import { Card } from "../ui/card";
import { Series } from "./hooks/useViewportRef";
import { Tabs, TabsList, TabsTrigger } from "../ui/tabs";

interface SelectorProps {
  study: Series[];
  activeIdx: string;
  setActiveIdx: (value: string) => void;
}

const ViewerSelector = ({ study, activeIdx, setActiveIdx }: SelectorProps) => {
  return (
    <Card className="h-full w-[300px]">
      <Tabs
        orientation="vertical"
        value={activeIdx}
        onValueChange={(value) => {
          if (value) setActiveIdx(value);
        }}
        className="w-full h-full p-2"
      >
        <TabsList className="flex-col w-full h-full justify-start bg-card gap-2">
          {study.map((series, idx) => (
            <TabsTrigger
              key={series.SeriesInstanceUID}
              value={String(idx)}
              className="w-full data-[state=active]:bg-muted pt-4"
            >
              <div className="flex flex-col">
                <Card className="w-[240px] h-[135px]"></Card>
                qwe
              </div>
            </TabsTrigger>
          ))}
        </TabsList>
      </Tabs>
    </Card>
  );
};

export default memo(ViewerSelector);
