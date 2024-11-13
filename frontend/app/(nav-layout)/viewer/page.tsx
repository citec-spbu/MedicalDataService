import { Viewer } from "@/components/viewer/viewer";

const ViewerPage = () => {
  return (
    <div className="relative flex w-full flex-nowrap flex-row items-stretch h-[calc(100vh-5rem)] px-2 gap-2">
      <Viewer />
    </div>
  );
};

export default ViewerPage;
