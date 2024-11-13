import { ReactNode } from "react";
import { ToggleGroupItem } from "../../ui/toggle-group";
import { Tooltip, TooltipContent, TooltipTrigger } from "../../ui/tooltip";

interface ToolsToggleButtonProps {
  children: ReactNode;
  value: string;
  caption: string;
}

export const ToolsToggleButton = ({
  children,
  value,
  caption
}: ToolsToggleButtonProps) => {
  return (
    <Tooltip>
      <ToggleGroupItem value={value} asChild>
        <TooltipTrigger>{children}</TooltipTrigger>
      </ToggleGroupItem>
      <TooltipContent side="bottom">{caption}</TooltipContent>
    </Tooltip>
  );
};
