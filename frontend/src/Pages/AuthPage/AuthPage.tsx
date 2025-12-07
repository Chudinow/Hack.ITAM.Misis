import { useEffect, useRef } from "react";
import { useNavigate } from "react-router-dom";
import styles from "./auth-page.module.css";
import { UserAPI, TelegramAuthPayload } from "../../Shared/api/UserApi";

declare global {
  interface Window {
    onTelegramAuth?: (user: TelegramAuthPayload) => void;
  }
}

const AuthPage: React.FC = () => {
  const navigate = useNavigate();
  const widgetRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    window.onTelegramAuth = async (user: TelegramAuthPayload) => {
      try {
        // Авторизация и установка HttpOnly cookie на сервере
        await UserAPI.authTelegram(user);

        // Проверяем валидность токена
        await UserAPI.checkAuth();

        // Авторизован — ведём на главную
        navigate("/main", { replace: true });
      } catch (error) {
        console.error("Ошибка Telegram авторизации:", error);
      }
    };

    if (!widgetRef.current) return;

    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.async = true;

    script.setAttribute("data-telegram-login", "AAAAAAAAAAAA"); // Укажи имя бота
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
