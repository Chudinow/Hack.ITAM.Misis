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
    // коллбек, который дернёт Telegram-виджет
    window.onTelegramAuth = async (user: TelegramAuthPayload) => {
      try {
        // ⚙️ здесь бэкенд проверяет hash и СТАВИТ httpOnly cookie с токеном
        await UserAPI.authTelegram(user);

        // флаг для client-side guard (куку мы всё равно не видим из JS)
        localStorage.setItem("isAuth", "true");

        navigate("/main", { replace: true });
      } catch (e) {
        console.error("Ошибка авторизации через Telegram:", e);
      }
    };

    if (!widgetRef.current) return;

    const script = document.createElement("script");
    script.src = "https://telegram.org/js/telegram-widget.js?22";
    script.async = true;
    script.setAttribute("data-telegram-login", "AAAAAAAAAAAA"); // <-- имя твоего бота
    script.setAttribute("data-size", "large");
    script.setAttribute("data-radius", "16");
    script.setAttribute("data-userpic", "false");
    script.setAttribute("data-lang", "ru");
    script.setAttribute("data-request-access", "write");
    script.setAttribute("data-onauth", "onTelegramAuth(user)");

    widgetRef.current.innerHTML = "";
    widgetRef.current.appendChild(script);

    return () => {
      if (widgetRef.current) widgetRef.current.innerHTML = "";
      delete window.onTelegramAuth;
    };
  }, [navigate]);

  return (
    <div className={styles.wrapper}>
      <div className={styles.card}>
        <div ref={widgetRef} className={styles.tgWidgetContainer} />
        <p className={styles.note}>
          Не забудьте активировать бота — он присылает уведомления.
        </p>
      </div>
    </div>
  );
};

export default AuthPage;
