import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className=" flex flex-col justify-center items-center space-y-4 h-full">
      <Button variant="outline" size = "lg">
        <Link href="/auth/register">Register</Link>
      </Button>
      <Button variant="outline" size = "lg">
        <Link href="/auth/login">Login</Link>
      </Button>
    </div>
  );
}
