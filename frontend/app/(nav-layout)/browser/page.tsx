import { DataTable } from "@/components/browser/table";
import { Card } from "@/components/ui/card";

const BrowserPage = () => {
  return (
    <div className="flex justify-center">
      <Card className="p-4 w-[95%] text-xl mt-6">
        <DataTable />
      </Card>
    </div>
  );
};

export default BrowserPage;
