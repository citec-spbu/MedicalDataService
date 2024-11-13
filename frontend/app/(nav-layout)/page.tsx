import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="flex justify-center items-center min-h-full">
      <Button variant="outline">
        <Link href="/auth/register">Register</Link>
      </Button>
    </div>
  );
}
