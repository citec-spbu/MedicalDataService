import { UploadIcon } from "@radix-ui/react-icons";
import { Button } from "../ui/button";
import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger
} from "../ui/sheet";
import { Input } from "../ui/input";
import { ChangeEvent, useState } from "react";
import api from "@/lib/api";
import { AxiosError } from "axios";
import { FormSuccess } from "../form-success";
import { FormError } from "../form-error";

type UploadStatus = {
  type: "idle" | "uploading" | "success" | "error";
  message?: string;
};

export const Upload = () => {
  const [file, setFile] = useState<File | null>(null);
  const [status, setStatus] = useState<UploadStatus>({
    type: "idle"
  });
  const [uploadProgress, setUploadProgress] = useState(0);

  function handleFileChange(e: ChangeEvent<HTMLInputElement>) {
    if (e.target.files) {
      setFile(e.target.files[0]);
    }
  }

  async function handleFileUpload() {
    if (!file) return;

    setStatus({ type: "uploading" });
    setUploadProgress(0);

    const formData = new FormData();
    formData.append("file", file);

    try {
      await api.post("/upload/", formData, {
        headers: {
          "Content-Type": "multipart/form-data"
        },
        onUploadProgress: (progressEvent) => {
          const progress = progressEvent.total
            ? Math.round((progressEvent.loaded * 100) / progressEvent.total)
            : 0;
          setUploadProgress(progress);
        }
      });

      setStatus({ type: "success" });
      setUploadProgress(100);
    } catch (error) {
      if (error instanceof AxiosError) {
        if (error.response) {
          setStatus({ type: "error", message: error.response.data.detail });
        } else if (error.request) {
          setStatus({
            type: "error",
            message: "Пожалуйста повторите попытку позже"
          });
        }
      } else {
        return setStatus({
          type: "error",
          message: "Неизвестная ошибка"
        });
      }
    }
  }

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline" size="icon">
          <UploadIcon />
        </Button>
      </SheetTrigger>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>Загрузка файлов</SheetTitle>
          <SheetDescription>
            Здесь можно загрузить архив с файлами (.zip)
          </SheetDescription>
        </SheetHeader>

        <div className="grid w-full max-w-sm items-center gap-4 py-4">
          <Input
            name="file"
            type="file"
            accept=".zip"
            onChange={handleFileChange}
          />

          {status.type === "uploading" && (
            <div className="space-y-2">
              <div className="h-2.5 w-full rounded-full bg-gray-200">
                <div
                  className="h-2.5 rounded-full bg-blue-600 transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                ></div>
              </div>
              <p className="text-sm text-gray-600">
                {uploadProgress}% uploaded
              </p>
            </div>
          )}

          {status.type === "success" && (
            <FormSuccess message="Файл успешно загружен" />
          )}

          {status.type === "error" && <FormError message={status.message} />}

          <SheetFooter>
            <Button
              type="submit"
              disabled={status.type === "uploading"}
              onClick={handleFileUpload}
            >
              Отправить
            </Button>
          </SheetFooter>
        </div>
      </SheetContent>
    </Sheet>
  );
};
