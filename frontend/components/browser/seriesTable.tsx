import { ColumnDef } from "@tanstack/react-table";

export type Series = {
  bodyPart: string;
  modality: string;
};

export const seriesColumns: ColumnDef<Series>[] = [
  {
    accessorKey: "bodyPart",
    header: "Часть тела",
    cell: ({ row }) => <div>{row.getValue("bodyPart")}</div>
  },
  {
    accessorKey: "modality",
    header: "Модальность",
    cell: ({ row }) => (
      <div className="uppercase">{row.getValue("modality")}</div>
    )
  }
];

export const seriesData: Series[] = [
  {
    bodyPart: "Finger",
    modality: "CT"
  },
  {
    bodyPart: "Leg",
    modality: "WC"
  },
  {
    bodyPart: "Abdomen",
    modality: "KW"
  }
];
