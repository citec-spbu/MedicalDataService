import { ColumnDef } from "@tanstack/react-table";
import { CaretSortIcon } from "@radix-ui/react-icons";
import { Button } from "@/components/ui/button";

export type Patient = {
  name: string;
  sex: string;
  birthDate: string;
};

export const patientColumns: ColumnDef<Patient>[] = [
  {
    accessorKey: "name",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="text-lg hover:text-alternative hover:bg-alternative/15 font-bold"
        >
          Имя пациента
          <CaretSortIcon className="ml-2 h-6 w-6" />
        </Button>
      );
    },
    cell: ({ row }) => <div className="capitalize">{row.getValue("name")}</div>
  },
  {
    accessorKey: "sex",
    header: "Пол",
    cell: ({ row }) => <div className="capitalize">{row.getValue("sex")}</div>
  },
  {
    accessorKey: "birthDate",
    header: ({ column }) => {
      return (
        <Button
          variant="ghost"
          onClick={() => column.toggleSorting(column.getIsSorted() === "asc")}
          className="text-lg hover:text-alternative hover:bg-alternative/15 font-bold"
        >
          Дата рождения
          <CaretSortIcon className="ml-2 h-6 w-6" />
        </Button>
      );
    },
    cell: ({ row }) => <div>{row.getValue("birthDate")}</div>
  }
];

export const patientData: Patient[] = [
  {
    name: "Vasiliy A.O.",
    sex: "M",
    birthDate: new Date("1998-10-10").toISOString().slice(0, 10)
  },
  {
    name: "Anatoliy B.F.",
    sex: "M",
    birthDate: new Date("2004-12-31").toISOString().slice(0, 10)
  },
  {
    name: "Jabova A.N.",
    sex: "F",
    birthDate: new Date("2012-09-11").toISOString().slice(0, 10)
  }
];
