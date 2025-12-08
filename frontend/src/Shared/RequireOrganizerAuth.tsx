import { Navigate, Outlet, useLocation } from "react-router-dom";

export default function RequireOrganizerAuth() {
  const location = useLocation();

  // const hasToken = document.cookie.includes("organizer_token=");
  const hasToken = true;

  if (!hasToken) {
    return <Navigate to="/organizer/login" state={{ from: location }} replace />;
  }

  return <Outlet />;
}
