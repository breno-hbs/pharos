import { useLayoutEffect, useRef } from "react";

type Direction = "forward" | "back";

export function useViewMotion(query: string) {
  const current = useRef<{
    transition: ViewTransition;
    query: string;
    finishUpdate?: () => void;
  } | null>(null);

  useLayoutEffect(() => {
    if (current.current?.query === query) current.current.finishUpdate?.();
  }, [query]);

  return function move(nextQuery: string, update: () => void, direction?: Direction) {
    const previous = current.current;
    previous?.finishUpdate?.();
    previous?.transition.skipTransition();

    const root = document.documentElement;
    if (!direction || !document.startViewTransition || window.matchMedia("(prefers-reduced-motion: reduce)").matches) {
      current.current = null;
      delete root.dataset.pharosMotion;
      update();
      return;
    }

    root.dataset.pharosMotion = direction;
    const transition = document.startViewTransition(() => {
      // Next.js renders the URL change after this callback runs.
      const pending = current.current;
      if (pending?.transition !== transition) return;
      return new Promise<void>((resolve) => {
        const timeout = window.setTimeout(resolve, 180);
        pending.finishUpdate = () => {
          window.clearTimeout(timeout);
          resolve();
        };
        update();
      });
    });
    current.current = { transition, query: nextQuery };

    function cleanup() {
      if (current.current?.transition === transition) {
        current.current = null;
        delete root.dataset.pharosMotion;
      }
    }

    void transition.finished.then(cleanup, cleanup);
  };
}
