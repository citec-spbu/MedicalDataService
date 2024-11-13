import { DataTable } from "@/components/browser/table";
import { Card } from "@/components/ui/card";

const BrowserPage = () => {
  return (
    <div className="flex justify-center items-center w-full">
      <Card className="p-4 w-full xl:max-w-[1280px] text-xl mt-6">
        <DataTable />
      </Card>
    </div>
  );
};

export default BrowserPage;
