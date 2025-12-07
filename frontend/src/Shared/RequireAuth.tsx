import { Navigate, Outlet } from "react-router-dom";
import { useEffect, useState } from "react";
import { UserAPI } from "./api/UserApi";

export default function RequireAuth() {
  const [loading, setLoading] = useState(true);
  const [authorized, setAuthorized] = useState(false);

  useEffect(() => {
    let isMounted = true;

    UserAPI.checkAuth()
      .then(() => {
        if (isMounted) {
          console.log("AUTH OK");
          setAuthorized(true);
        }
      })
      .catch(() => {
        if (isMounted) {
          console.log("AUTH FAIL");
          setAuthorized(false);
        }
      })
      .finally(() => {
        if (isMounted) {
          console.log("FINALLY");
          setLoading(false);
        }
      });

    return () => {
      isMounted = false;
    };
  }, []);

  if (loading) return <div>Loading...</div>;

  return authorized ? <Outlet /> : <Navigate to="/auth" replace />;
}
