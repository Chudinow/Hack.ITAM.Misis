import { Navigate, Outlet } from "react-router-dom";
import { useEffect, useState } from "react";
import { UserAPI } from "../Shared/api/UserApi";

export default function RequireAuth() {
  const [authorized, setAuthorized] = useState<boolean | null>(null);

  useEffect(() => {
    let active = true;

    async function check() {
      try {
        await UserAPI.checkAuth(); // если 401 → catch
        if (active) setAuthorized(true);
      } catch {
        if (active) setAuthorized(false);
      }
    }

    check();

    return () => {
      active = false; // предотвращает утечки
    };
  }, []);

  // Пока проверяем → отображаем загрузку
  if (authorized === null) {
    return <div style={{ color: "#fff", padding: "2rem" }}>Загрузка...</div>;
  }

  // Если авторизация ОК → пропускаем
  if (authorized === true) {
    return <Outlet />;
  }

  // Если НЕ авторизован → отправляем на страницу логина
  return <Navigate to="/auth" replace />;
}
