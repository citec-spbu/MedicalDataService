import { memo, useEffect, useState } from "react";

import { ToggleGroup } from "../ui/toggle-group";
import { Card } from "../ui/card";
import {
  HeightIcon,
  MoveIcon,
  RulerHorizontalIcon,
  MagnifyingGlassIcon,
  ReloadIcon,
  Half2Icon,
  EraserIcon
} from "@radix-ui/react-icons";
import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuRadioGroup,
  DropdownMenuRadioItem
} from "../ui/dropdown-menu";
import { Button } from "../ui/button";
import { ToolsToggleButton } from "./ui/tools-toggle";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger
} from "../ui/tooltip";

import { IStackViewport, IVolumeViewport } from "@cornerstonejs/core/types";
import {
  PanTool,
  WindowLevelTool,
  ZoomTool,
  LengthTool,
  StackScrollTool,
  EraserTool,
  ToolGroupManager,
  BaseTool
} from "@cornerstonejs/tools";

import * as cornerstoneTools from "@cornerstonejs/tools";
import { MouseBindings } from "@cornerstonejs/tools/enums";
import { OrientationAxis } from "@cornerstonejs/core/enums";
import { ToolsButton } from "./ui/tools-button";
import { Enums } from "@cornerstonejs/core";

const toolGroupId = "TOOL_GROUP_ID";
const toolGroup = ToolGroupManager.createToolGroup(toolGroupId);

const ToggleButtons: {
  value: typeof BaseTool | typeof WindowLevelTool;
  caption: string;
  icon: typeof Half2Icon;
}[] = [
  {
    value: WindowLevelTool,
    caption: "Яркость / Контрастность",
    icon: Half2Icon
  },
  { value: PanTool, caption: "Перемещение", icon: MoveIcon },
  { value: StackScrollTool, caption: "Пролистывание", icon: HeightIcon },
  { value: ZoomTool, caption: "Приближение", icon: MagnifyingGlassIcon },
  {
    value: LengthTool,
    caption: "Измерение расстояния",
    icon: RulerHorizontalIcon
  },
  { value: EraserTool, caption: "Удаление аннотаций", icon: EraserIcon }
];

ToggleButtons.forEach((button) => {
  cornerstoneTools.addTool(button.value);
  toolGroup?.addTool(button.value.toolName);
});

interface ToolsProps {
  viewport: IVolumeViewport | IStackViewport | null;
  isLoaded: boolean;
}

const ViewerTools = ({ viewport, isLoaded }: ToolsProps) => {
  const [selectedTool, setSelectedTool] = useState(WindowLevelTool.toolName);
  const [axisType, setAxisType] = useState<OrientationAxis>(
    OrientationAxis.AXIAL
  );
  useEffect(() => {
    if (isLoaded) {
      toolGroup?.addViewport(viewport!.id);
    }
  }, [isLoaded, viewport]);

  useEffect(() => {
    if (viewport?.type == Enums.ViewportType.ORTHOGRAPHIC) {
      (viewport as IVolumeViewport)?.setOrientation(axisType);
    }
  }, [axisType, viewport]);

  useEffect(() => {
    toolGroup?.setActivePrimaryTool(selectedTool); // Left Button

    toolGroup?.setToolActive(PanTool.toolName, {
      bindings: [{ mouseButton: MouseBindings.Auxiliary }] // Wheel Button
    });

    toolGroup?.setToolActive(StackScrollTool.toolName, {
      bindings: [{ mouseButton: MouseBindings.Wheel }] // Wheel Mouse
    });

    toolGroup?.setToolActive(ZoomTool.toolName, {
      bindings: [{ mouseButton: MouseBindings.Secondary }] // Right Button
    });

    if (toolGroup?.prevActivePrimaryToolName === LengthTool.toolName) {
      toolGroup?.setToolPassive(LengthTool.toolName);
    }
  }, [selectedTool]);

  return (
    <Card className="flex justify-center">
      <TooltipProvider>
        <ToggleGroup
          type="single"
          size="lg"
          value={selectedTool}
          onValueChange={(value) => {
            if (value) setSelectedTool(value);
          }}
        >
          {ToggleButtons.map((button) => (
            <ToolsToggleButton
              value={button.value.toolName}
              caption={button.caption}
              key={button.value.toolName}
            >
              <button.icon className="h-4 w-4" />
            </ToolsToggleButton>
          ))}

          <ToolsButton
            caption="Сброс"
            onClick={() => {
              viewport?.resetCamera();
              viewport?.resetProperties();
              viewport?.render();
            }}
          >
            <ReloadIcon className="h-4 w-4" />
          </ToolsButton>

          <DropdownMenu>
            <Tooltip>
              <DropdownMenuTrigger asChild>
                <TooltipTrigger className="capitalize" asChild>
                  <Button
                    variant="outline"
                    className="border-none h-full"
                    disabled={viewport?.type == Enums.ViewportType.STACK}
                  >
                    {axisType}
                  </Button>
                </TooltipTrigger>
              </DropdownMenuTrigger>
              <TooltipContent side="bottom">Плоскости</TooltipContent>
            </Tooltip>
            <DropdownMenuContent onCloseAutoFocus={(e) => e.preventDefault()}>
              <DropdownMenuRadioGroup
                value={axisType}
                onValueChange={(value) => {
                  setAxisType(value as OrientationAxis);
                }}
              >
                <DropdownMenuRadioItem value={OrientationAxis.AXIAL}>
                  Axial
                </DropdownMenuRadioItem>
                <DropdownMenuRadioItem value={OrientationAxis.SAGITTAL}>
                  Sagittal
                </DropdownMenuRadioItem>
                <DropdownMenuRadioItem value={OrientationAxis.CORONAL}>
                  Coronal
                </DropdownMenuRadioItem>
              </DropdownMenuRadioGroup>
            </DropdownMenuContent>
          </DropdownMenu>
        </ToggleGroup>
      </TooltipProvider>
    </Card>
  );
};

export default memo(ViewerTools);
