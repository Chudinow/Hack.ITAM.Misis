import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./auth-page.module.css";
import { UserAPI } from "../../Shared/api/UserApi";
import type { TelegramAuthPayload } from "../../Shared/api/UserApi";

declare global {
  interface Window {
    onTelegramAuth?: (user: unknown) => void;
  }
}

const AuthPage: React.FC = () => {
  const navigate = useNavigate();
  const widgetRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    window.onTelegramAuth = async (rawUser: unknown) => {
      try {
        // Приведение типов — Telegram SDK не типизирован
        const user = rawUser as TelegramAuthPayload;

        // 1) Авторизация. Бэкенд ставит HttpOnly cookie.
        await UserAPI.authTelegram(user);

        // 2) Проверка того, что cookie корректно установлена.
        await UserAPI.checkAuth();

        // 3) Успешная авторизация -> редирект.
        navigate("/main", { replace: true });
      } catch (error) {
        console.error("Ошибка Telegram авторизации:", error);
      }
    };

    if (!widgetRef.current) return;

    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.async = true;

    script.setAttribute("data-telegram-login", "itamhackpay2win_bot");
    script.setAttribute("data-size", "large");
    script.setAttribute("data-radius", "16");
    script.setAttribute("data-userpic", "false");
    script.setAttribute("data-lang", "ru");
    script.setAttribute("data-request-access", "write");
    script.setAttribute("data-onauth", "onTelegramAuth(user)");

    widgetRef.current.innerHTML = "";
    widgetRef.current.appendChild(script);

    return () => {
      delete window.onTelegramAuth;
      if (widgetRef.current) widgetRef.current.innerHTML = "";
    };
  }, [navigate]);

  return (
    <div className={styles.wrapper}>
      <div className={styles.card}>
        <div ref={widgetRef} className={styles.tgWidgetContainer} />
      </div>
    </div>
  );
};

export default AuthPage;
