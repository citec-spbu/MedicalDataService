import { ColumnDef } from "@tanstack/react-table";
import { CaretSortIcon } from "@radix-ui/react-icons";
import { Button } from "@/components/ui/button";

export type Study = {
  date: string;
  time: string;
  modalities: string[];
  description: string;
  uid: string;
  seriesCount: number;
  instancesCount: number;
};

export const studyColumns: ColumnDef<Study>[] = [
  {
    accessorKey: "description",
    header: "Описание",
    cell: ({ row }) => row.getValue("description")
  },
  {
    accessorKey: "modalities",
    header: "Модальности",
    cell: ({ row }) =>
      (row.getValue("modalities") satisfies string[]).join(", ")
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
    accessorKey: "seriesCount",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="font-bold"
        >
          Количество серий
          <CaretSortIcon className="ml-2 h-6 w-6" />
        </Button>
      );
    },
    cell: ({ row }) => row.getValue("seriesCount")
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
