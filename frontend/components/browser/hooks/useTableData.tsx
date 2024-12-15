"use client";

import { ColumnFiltersState, SortingState } from "@tanstack/react-table";
import { useEffect, useState } from "react";

interface TableData {
  data: any[];
  activeTab: "patient" | "study" | "series";
}

export default function useTableData(
  patient_id: string | null,
  study_uid: string | null
) {
  const API = process.env.API;
  const [sorting, setSorting] = useState<SortingState>([]);
  const [columnFilters, setColumnFilters] = useState<ColumnFiltersState>([]);
  const [rowSelection, setRowSelection] = useState({});

  const [tableData, setTableData] = useState<TableData>({
    data: [],
    activeTab: "patient"
  });

  useEffect(() => {
    const fetchData = async () => {
      if (!patient_id) {
        const response = await fetch(`${API}/patients`).then((data) =>
          data.json()
        );

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
        const response = await fetch(
          `${API}/studies?patient_id=${patient_id}`
        ).then((data) => data.json());

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
        const response = await fetch(`${API}/studies/${study_uid}/series`).then(
          (data) => data.json()
        );

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
    };
    fetchData();
    setSorting([]);
    setColumnFilters([]);
  }, [patient_id, study_uid, API]);

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
