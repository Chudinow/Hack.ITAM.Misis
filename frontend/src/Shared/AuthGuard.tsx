import { useEffect, useState } from "react";
import { Navigate, Outlet, useLocation } from "react-router-dom";
import { UserAPI } from "../Shared/api/UserApi";

const RequireAuth: React.FC = () => {
  const location = useLocation();

  // ВРЕМЕННО, пока backend недоступен:
  const isDevBypass = true;  // ← сейчас всё работает без авторизации (потом поменять на false)

  // НАСТОЯЩАЯ авторизация (будет работать когда backend отдаёт cookie-токен)
  const [isAuth, setIsAuth] = useState<boolean | null>(isDevBypass);

  useEffect(() => {
    if (isDevBypass) return; // пропускаем проверку пока ты в разработке

    async function checkAuth() {
      try {
        await UserAPI.getUser("me"); // backend проверяет токен в cookie
        setIsAuth(true);
      } catch {
        setIsAuth(false);
      }
    }

    checkAuth();
  }, []);

  // Пока проверка выполняется
  if (isAuth === null) return <div>Загрузка...</div>;

  if (!isAuth) {
    return <Navigate to="/auth" state={{ from: location }} replace />;
  }

  return <Outlet />;
};

export default RequireAuth;
