import { ReactNode } from "react";
import { Tooltip, TooltipContent, TooltipTrigger } from "../../ui/tooltip";
import { Button } from "@/components/ui/button";

interface ToolsToggleButtonProps {
  children: ReactNode;
  caption: string;
  onClick: () => void;
}

export const ToolsButton = ({
  children,
  caption,
  onClick
}: ToolsToggleButtonProps) => {
  return (
    <Tooltip>
      <Button
        variant="outline"
        className="border-none h-full"
        onClick={onClick}
        asChild
      >
        <TooltipTrigger>{children}</TooltipTrigger>
      </Button>
      <TooltipContent side="bottom">{caption}</TooltipContent>
    </Tooltip>
  );
};
