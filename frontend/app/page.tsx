import { Suspense } from "react";
import Prototype from "./prototype";

export default function Page() {
  return <Suspense fallback={null}><Prototype /></Suspense>;
}
