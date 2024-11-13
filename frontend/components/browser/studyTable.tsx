import { ColumnDef } from "@tanstack/react-table";
import { CaretSortIcon } from "@radix-ui/react-icons";
import { Button } from "@/components/ui/button";

export type Study = {
  protocolName: string;
  studyDate: string;
};

export const studyColumns: ColumnDef<Study>[] = [
  {
    accessorKey: "protocolName",
    header: "Название протокола",
    cell: ({ row }) => <div>{row.getValue("protocolName")}</div>
  },
  {
    accessorKey: "studyDate",
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
    cell: ({ row }) => <div>{row.getValue("studyDate")}</div>
  }
];

export const studyData: Study[] = [
  {
    protocolName: "Hand / Finger ABC DE",
    studyDate: new Date("1998-10-10").toISOString().slice(0, 10)
  },
  {
    protocolName: "Leg / Ankle QWE GG",
    studyDate: new Date("2004-12-31").toISOString().slice(0, 10)
  },
  {
    protocolName: "Chest / Abdomen HCT GG",
    studyDate: new Date("2012-09-11").toISOString().slice(0, 10)
  }
];
