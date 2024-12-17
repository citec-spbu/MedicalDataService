import { Provider } from "react-redux";
import { store } from "@/stores/index";

export default function ReduxProvider({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return <Provider store={store}>{children}</Provider>;
}
