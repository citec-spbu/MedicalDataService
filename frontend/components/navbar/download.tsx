import { DownloadIcon } from "@radix-ui/react-icons";
import { useEffect, useState } from "react";
import {
  Sheet,
  SheetClose,
  SheetContent,
  SheetDescription,
  SheetFooter,
  SheetHeader,
  SheetTitle,
  SheetTrigger
} from "../ui/sheet";
import { Button } from "../ui/button";
import { Label } from "../ui/label";
import { useCartSelector } from "@/stores";
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger
} from "../ui/accordion";

export const Download = () => {
  const [totalQuantity, setTotalQuantity] = useState(0);

  const store = useCartSelector((store) => store.cart.items);

  useEffect(() => {
    setTotalQuantity(store.reduce((acc, value) => value.data.length, 0));
  }, [store]);

  return (
    <Sheet>
      <SheetTrigger asChild>
        <Button variant="outline" size="icon" className="relative">
          <DownloadIcon />
          <span className="absolute top-3/4 right-2/3 bg-primary text-primary-foreground text-sm w-5 h-5 rounded-full flex justify-center items-center">
            {totalQuantity}
          </span>
        </Button>
      </SheetTrigger>
      <SheetContent>
        <SheetHeader>
          <SheetTitle>Выгрузка файлов</SheetTitle>
          <SheetDescription>
            Здесь будут отображаться выбранные для выгрузки файлы.
          </SheetDescription>
        </SheetHeader>
        {store.length ? (
          <Accordion type="single" collapsible className="w-full">
            {store.map((item) => (
              <AccordionItem
                value={item.patient_id.toString()}
                key={item.patient_id}
              >
                <AccordionTrigger>
                  Пациент {item.patient_id}. Серий: {item.data.length}
                </AccordionTrigger>

                <AccordionContent>
                  <div className="grid">
                    {item.data.map((data) => (
                      <span
                        key={data.uid}
                        className="text-ellipsis text-nowrap overflow-hidden"
                      >
                        {data.description}
                      </span>
                    ))}
                  </div>
                </AccordionContent>
              </AccordionItem>
            ))}
          </Accordion>
        ) : (
          <div className="flex justify-center ">
            <Label className="mt-4">Не выбрано файлов для выгрузки</Label>
          </div>
        )}
        <SheetFooter>
          <SheetClose asChild>
            <Button type="submit" disabled={store.length == 0} className="mt-4">
              Выгрузить
            </Button>
          </SheetClose>
        </SheetFooter>
      </SheetContent>
    </Sheet>
  );
};
