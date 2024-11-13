import { forwardRef, ReactNode, Ref } from "react";

const ViewerMain = (
  { children }: { children: ReactNode },
  ref: Ref<HTMLDivElement>
) => {
  return (
    <div
      ref={ref}
      className="w-full h-full bg-black border rounded"
      role="figure"
      onContextMenu={(e) => e.preventDefault()}
    >
      {children}
    </div>
  );
};

export default forwardRef(ViewerMain);
