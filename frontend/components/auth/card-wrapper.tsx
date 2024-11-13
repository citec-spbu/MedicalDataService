import {
  Card,
  CardContent,
  CardFooter,
  CardHeader
} from "@/components/ui/card";
import { Header } from "@/components/auth/header";
import { Footer } from "@/components/auth/footer";

interface CardWrapperProps {
  children: React.ReactNode;
  headerLabel: string;
  showFooter?: boolean;
  footerLabels?: string[];
  footerHrefs?: string[];
}

export const CardWrapper = ({
  children,
  headerLabel,
  showFooter,
  footerLabels,
  footerHrefs
}: CardWrapperProps) => {
  return (
    <Card className="w-[400px] flex flex-col items-center justify-center">
      <CardHeader className="mt-8 mb-3">
        <Header label={headerLabel} />
      </CardHeader>
      <CardContent>{children}</CardContent>
      {showFooter && (
        <CardFooter>
          <Footer labels={footerLabels} hrefs={footerHrefs} />
        </CardFooter>
      )}
    </Card>
  );
};
