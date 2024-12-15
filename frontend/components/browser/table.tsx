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
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getSortedRowModel,
  useReactTable
} from "@tanstack/react-table";
import { Input } from "@/components/ui/input";

import { patientColumns } from "@/components/browser/patientTable";
import { studyColumns } from "@/components/browser/studyTable";
import { seriesColumns } from "@/components/browser/seriesTable";
import {
  Breadcrumb,
  BreadcrumbItem,
  BreadcrumbLink,
  BreadcrumbList,
  BreadcrumbSeparator
} from "../ui/breadcrumb";
import useTableData from "./hooks/useTableData";
import { useRouter, useSearchParams } from "next/navigation";
import Link from "next/link";
import { useCartDispatch } from "@/stores";
import { addToCart, removeFromCart } from "@/stores/cart";

export const DataTable = () => {
  const searchParams = useSearchParams();

  const router = useRouter();
  const dispatch = useCartDispatch();

  const patient_id = searchParams.get("PatientID");
  const study_uid = searchParams.get("StudyUID");

  const {
    tableData,
    sorting,
    setSorting,
    columnFilters,
    setColumnFilters,
    rowSelection,
    setRowSelection
  } = useTableData(patient_id, study_uid);

  const activeTabMapper = {
    patient: patientColumns,
    study: studyColumns,
    series: seriesColumns(
      (description, uid) =>
        dispatch(addToCart({ patient_id, description: description, uid: uid })),
      (uid) => dispatch(removeFromCart({ patient_id, uid: uid }))
    )
  } as const;

  const table = useReactTable({
    data: tableData?.data,
    columns: activeTabMapper[tableData?.activeTab],
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    getCoreRowModel: getCoreRowModel(),
    getSortedRowModel: getSortedRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    onRowSelectionChange: setRowSelection,
    state: {
      sorting,
      columnFilters,
      rowSelection
    }
  });

  return (
    <div className="w-full">
      <Breadcrumb>
        <BreadcrumbList>
          <BreadcrumbItem>
            <BreadcrumbLink asChild>
              <Link href="/browser">Главная</Link>
            </BreadcrumbLink>
          </BreadcrumbItem>
          <BreadcrumbSeparator />
          {tableData.activeTab != "patient" && (
            <>
              <BreadcrumbItem>
                <BreadcrumbLink asChild>
                  <Link href={`/browser?PatientID=${patient_id}`}>Пациент</Link>
                </BreadcrumbLink>
              </BreadcrumbItem>
              <BreadcrumbSeparator />
            </>
          )}
          {tableData.activeTab == "series" && (
            <BreadcrumbItem>
              <BreadcrumbLink asChild>
                <Link
                  href={`/browser?PatientID=${patient_id}&StudyUID=${study_uid}`}
                >
                  Исследование
                </Link>
              </BreadcrumbLink>
            </BreadcrumbItem>
          )}
        </BreadcrumbList>
      </Breadcrumb>
      <div className="flex items-center justify-start py-4">
        {tableData?.activeTab === "patient" && (
          <Input
            placeholder="Поиск по фамилии"
            value={(table.getColumn("name")?.getFilterValue() as string) ?? ""}
            onChange={(event) =>
              table.getColumn("name")?.setFilterValue(event.target.value)
            }
            className="max-w-sm"
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
                    <TableHead key={header.id} className="text-center">
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
                  onMouseDown={(e) => {
                    if (e.detail > 1) {
                      e.preventDefault();
                    }
                  }}
                  onDoubleClick={() => {
                    if (tableData.activeTab == "patient") {
                      router.push(`/browser?PatientID=${row.original["id"]}`);
                    }
                    if (tableData.activeTab == "study") {
                      router.push(
                        `/browser?PatientID=${patient_id}&StudyUID=${row.original["uid"]}`
                      );
                    }
                    if (tableData.activeTab == "series") {
                      router.push(
                        `/viewer?StudyUID=${study_uid}&SeriesUID=${row.original["uid"]}`
                      );
                    }
                  }}
                >
                  {row.getVisibleCells().map((cell) => (
                    <TableCell key={cell.id} className="text-center">
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
