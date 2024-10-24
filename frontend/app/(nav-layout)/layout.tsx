import { Navbar } from "@/components/navbar";

const NavLayout = ({ children }: { children: React.ReactNode }) => {
  return (
    <>
      <Navbar />
      {children}
    </>
  );
};

export default NavLayout;
