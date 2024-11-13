import { ColumnDef } from "@tanstack/react-table";
import { CaretSortIcon } from "@radix-ui/react-icons";
import { Button } from "@/components/ui/button";

export type Image = {
  number: number;
};

export const imageColumns: ColumnDef<Image>[] = [
  {
    accessorKey: "number",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="font-bold"
        >
          Номер снимка
          <CaretSortIcon className="ml-2 h-6 w-6" />
        </Button>
      );
    },
    cell: ({ row }) => <div>{row.getValue("number")}</div>
  }
];

export const imageData: Image[] = [
  { number: 23 },
  { number: 12 },
  { number: 1 },
  { number: 2 }
];
