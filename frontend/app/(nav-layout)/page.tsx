import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="flex justify-center items-center h-full">
      <Button variant="outline">
        <Link href="/auth/register">Register</Link>
      </Button>
    </div>
  );
}
