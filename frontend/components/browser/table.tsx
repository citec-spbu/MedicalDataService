"use client";

import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow
} from "@/components/ui/table";
import {
  ColumnFiltersState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  SortingState,
  useReactTable
} from "@tanstack/react-table";
import { useState } from "react";
import { Input } from "@/components/ui/input";

const mapper = {
  0: [patientData, patientColumns],
  1: [studyData, studyColumns],
  2: [seriesData, seriesColumns],
  3: [imageData, imageColumns]
};

import { patientData, patientColumns } from "@/components/browser/patientTable";
import { studyData, studyColumns } from "@/components/browser/studyTable";
import { seriesData, seriesColumns } from "@/components/browser/seriesTable";
import { imageData, imageColumns } from "@/components/browser/imageTable";

export const DataTable = () => {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);

  const [tableState, setTableState] = useState(0);
  const [data, setData] = useState(patientData);
  const [columns, setColumns] = useState(patientColumns);

  const table = useReactTable({
    data: data,
    columns: columns,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    state: {
      sorting,
      columnFilters
    }
  });

  return (
    <div className="w-full">
      <div className="flex items-center justify-center py-4">
        {data === patientData && (
          <Input
            placeholder="Поиск по фамилии"
            value={(table.getColumn("name")?.getFilterValue() as string) ?? ""}
            onChange={(event) =>
              table.getColumn("name")?.setFilterValue(event.target.value)
            }
            className="max-w-sm text-lg"
          />
        )}
      </div>
      <div className="rounded-md border">
        <Table>
          <TableHeader>
            {table.getHeaderGroups().map((headerGroup) => (
              <TableRow key={headerGroup.id}>
                {headerGroup.headers.map((header) => {
                  return (
                    <TableHead key={header.id}>
                      {header.isPlaceholder
                        ? null
                        : flexRender(
                            header.column.columnDef.header,
                            header.getContext()
                          )}
                    </TableHead>
                  );
                })}
              </TableRow>
            ))}
          </TableHeader>
          <TableBody>
            {table.getRowModel().rows?.length ? (
              table.getRowModel().rows.map((row) => (
                <TableRow
                  key={row.id}
                  onClick={(e) => {
                    if (e.detail === 2) {
                      const nextTableState = (tableState + 1) % 4;

                      table.resetSorting();
                      setData(mapper[nextTableState][0]);
                      setColumns(mapper[nextTableState][1]);
                      setTableState(nextTableState);
                    }
                  }}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id}>
                      {flexRender(
                        cell.column.columnDef.cell,
                        cell.getContext()
                      )}
                    </TableCell>
                  ))}
                </TableRow>
              ))
            ) : (
              <TableRow>
                <TableCell
                  colSpan={patientColumns.length}
                  className="h-24 text-center"
                >
                  No results.
                </TableCell>
              </TableRow>
            )}
          </TableBody>
        </Table>
      </div>
    </div>
  );
};
