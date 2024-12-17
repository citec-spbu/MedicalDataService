"use client";

import { ColumnFiltersState, SortingState } from "@tanstack/react-table";
import { cache, useEffect, useState } from "react";
import api from "@/lib/api";

interface TableData {
  data: any[];
  activeTab: "patient" | "study" | "series";
}

export default function useTableData(
  patient_id: string | null,
  study_uid: string | null
) {
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [rowSelection, setRowSelection] = useState({});

  const [tableData, setTableData] = useState<TableData>({
    data: [],
    activeTab: "patient"
  });

  useEffect(() => {
    const fetchData = cache(async () => {
      if (!patient_id) {
        const response = (await api.get(`/dicomweb/patients`)).data;

        setTableData({
          data: response.map((patient) => {
            return {
              name: patient["00100010"]?.["Value"]?.[0]?.["Alphabetic"],
              id: patient["00100020"]?.["Value"]?.[0],
              birthDate: patient["00100030"]?.["Value"]?.[0].replace(
                /(\d{4})(\d{2})(\d{2})/,
                "$1-$2-$3"
              ),
              sex: patient["00100040"]?.["Value"]?.[0]
            };
          }),
          activeTab: "patient"
        });
      } else if (!study_uid) {
        const response = (
          await api(`/dicomweb/studies?patient_id=${patient_id}`)
        ).data;

        setTableData({
          data: response.map((study) => {
            return {
              date: study["00080020"]?.["Value"]?.[0].replace(
                /(\d{4})(\d{2})(\d{2})/,
                "$1-$2-$3"
              ),
              time: study["00080030"]?.["Value"]?.[0]
                .slice(0, 6)
                .replace(/(\d{2})(\d{2})(\d{2})/, "$1:$2:$3"),
              modalities: study["00080061"]?.["Value"]?.[0],
              description: study["00081030"]?.["Value"]?.[0],
              uid: study["0020000D"]?.["Value"]?.[0],
              seriesCount: study["00201206"]?.["Value"]?.[0],
              instancesCount: study["00201208"]?.["Value"]?.[0]
            };
          }),
          activeTab: "study"
        });
      } else {
        const response = (await api(`/dicomweb/studies/${study_uid}/series`))
          .data;

        setTableData({
          data: response.map((series) => {
            return {
              date: series["00080021"]?.["Value"]?.[0].replace(
                /(\d{4})(\d{2})(\d{2})/,
                "$1-$2-$3"
              ),
              time: series["00080031"]?.["Value"]?.[0]
                .slice(0, 6)
                .replace(/(\d{2})(\d{2})(\d{2})/, "$1:$2:$3"),
              modality: series["00080060"]?.["Value"]?.[0],
              physicianName: series["00080090"]?.["Value"]?.[0]?.["Alphabetic"],
              description: series["0008103E"]?.["Value"]?.[0],
              uid: series["0020000E"]?.["Value"]?.[0],
              instancesCount: series["00201209"]?.["Value"]?.[0]
            };
          }),
          activeTab: "series"
        });
      }
    });
    fetchData();
    setSorting([]);
    setColumnFilters([]);
  }, [patient_id, study_uid]);

  return {
    tableData,
    sorting,
    setSorting,
    columnFilters,
    setColumnFilters,
    rowSelection,
    setRowSelection
  };
}
