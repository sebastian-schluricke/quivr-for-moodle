"use client";

import {
  createBrowserSupabaseClient,
  Session,
} from "@supabase/auth-helpers-nextjs";
import { useRouter } from "next/navigation";
import { createContext, useEffect, useState } from "react";

import { SupabaseContextType } from "./types";

export const SupabaseContext = createContext<SupabaseContextType | undefined>(
  undefined
);

/**
 * After a Supabase verify (invite/recovery), the redirect URL contains
 * tokens and `type=invite|recovery` in its hash fragment. Detect that
 * and route the user to /user?setpw=1 so they can set a password.
 */
const checkAndRedirectAfterInvite = (router: ReturnType<typeof useRouter>): void => {
  if (typeof window === "undefined") {
    return;
  }
  const hash = window.location.hash;
  if (!hash) {
    return;
  }
  const params = new URLSearchParams(hash.replace(/^#/, ""));
  const type = params.get("type");
  if (type === "invite" || type === "recovery") {
    // Clear hash so this doesn't loop.
    window.history.replaceState(
      null,
      "",
      window.location.pathname + window.location.search
    );
    router.push("/user?setpw=1");
  }
};

export const SupabaseProvider = ({
  children,
  session,
}: {
  children: React.ReactNode;
  session: Session | null;
}): JSX.Element => {
  const [supabase] = useState(() => createBrowserSupabaseClient());
  const router = useRouter();

  useEffect(() => {
    // On mount, handle the case where we just landed from an invite link
    // (Supabase has already created the session via URL fragment).
    checkAndRedirectAfterInvite(router);

    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange((event) => {
      if (event === "SIGNED_IN") {
        checkAndRedirectAfterInvite(router);
      }
      router.refresh();
    });

    return () => {
      subscription.unsubscribe();
    };
  }, [router, supabase]);

  return (
    <SupabaseContext.Provider value={{ supabase, session }}>
      <>{children}</>
    </SupabaseContext.Provider>
  );
};
