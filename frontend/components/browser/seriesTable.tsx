import { CaretSortIcon } from "@radix-ui/react-icons";
import { ColumnDef } from "@tanstack/react-table";
import { Button } from "../ui/button";
import { Checkbox } from "../ui/checkbox";

export type Series = {
  date: string;
  time: string;
  modality: string;
  physicianName: string;
  description: string;
  uid: string;
  instancesCount: number;
};

export const seriesColumns = (
  onChecked: (description: string, uid: string) => void,
  onUnchecked: (uid: string) => void
): ColumnDef<Series>[] => [
  {
    id: "select",
    header: ({ table }) => (
      <Checkbox
        checked={
          table.getIsAllPageRowsSelected() ||
          (table.getIsSomePageRowsSelected() && "indeterminate")
        }
        onCheckedChange={(value) => {
          table.toggleAllRowsSelected(!!value);
          table.getRowModel().rows.forEach((row) => {
            if (!!value) {
              onChecked(row.original.description, row.original.uid);
            } else {
              onUnchecked(row.original.uid);
            }
          });
        }}
        aria-label="Добавить все"
      />
    ),
    cell: ({ row }) => (
      <Checkbox
        onDoubleClick={(e) => e.stopPropagation()}
        checked={row.getIsSelected()}
        onCheckedChange={(value) => {
          row.toggleSelected(!!value);
          if (!row.getIsSelected()) {
            onChecked(row.original.description, row.original.uid);
          } else {
            onUnchecked(row.original.uid);
          }
        }}
        aria-label="Добавить для выгрузки"
      />
    ),
    enableSorting: false
  },
  {
    accessorKey: "description",
    header: "Описание",
    cell: ({ row }) => row.getValue("description")
  },
  {
    accessorKey: "modality",
    header: "Модальность",
    cell: ({ row }) => row.getValue("modality")
  },
  {
    accessorKey: "physicianName",
    header: "Имя врача",
    cell: ({ row }) => row.getValue("physicianName")
  },
  {
    accessorKey: "date",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="font-bold"
        >
          Дата съемки
          <CaretSortIcon className="ml-2 h-6 w-6" />
        </Button>
      );
    },
    cell: ({ row }) => row.getValue("date")
  },
  {
    accessorKey: "time",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="font-bold"
        >
          Время съемки
          <CaretSortIcon className="ml-2 h-6 w-6" />
        </Button>
      );
    },
    cell: ({ row }) => row.getValue("time")
  },
  {
    accessorKey: "instancesCount",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="font-bold"
        >
          Количество изображений
          <CaretSortIcon className="ml-2 h-6 w-6" />
        </Button>
      );
    },
    cell: ({ row }) => row.getValue("instancesCount")
  }
];
