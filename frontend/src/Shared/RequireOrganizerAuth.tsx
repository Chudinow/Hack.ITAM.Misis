// src/RequireOrganizerAuth.tsx
import { Navigate, Outlet } from "react-router-dom";
import { useEffect, useState } from "react";
import { OrganizerApi } from "../Shared/api/OrganizerApi";

export default function RequireOrganizerAuth() {
  const [loading, setLoading] = useState(true);
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    let isMounted = true;

    OrganizerApi.me()
      .then(() => {
        if (isMounted) {
          setAuthorized(true);
        }
      })
      .catch((err) => {
        console.error("Organizer auth failed:", err);
        if (isMounted) {
          setAuthorized(false);
        }
      })
      .finally(() => {
        if (isMounted) {
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) return <div>Загрузка...</div>;

  return authorized ? <Outlet /> : <Navigate to="/organizer/login" replace />;
}
