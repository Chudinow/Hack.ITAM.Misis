import { Navigate, Outlet, useLocation } from "react-router-dom";

const RequireAuth: React.FC = () => {
  const location = useLocation();
  const isAuth = localStorage.getItem("isAuth") === "true";

  if (!isAuth) {
    return <Navigate to="/auth" state={{ from: location }} replace />;
  }

  return <Outlet />;
};

export default RequireAuth;
