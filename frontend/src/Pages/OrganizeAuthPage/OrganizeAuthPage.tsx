import React, { useState } from "react";
import styles from "./organize-auth-page.module.css";
import { useNavigate } from "react-router-dom";
import { OrganizerApi } from "../../Shared/api/OrganizerApi";

const OrganizeAuthPage: React.FC = () => {
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  // --- Функция безопасного сохранения токена в cookie ---
  const setAuthCookie = (token: string) => {
    document.cookie = `organizer_token=${token}; path=/; max-age=604800; secure; samesite=strict`;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    setError("");

    try {
      const response = await OrganizerApi.login({
        email: login,
        password: password,
      });

      if (response?.access_token) {
        setAuthCookie(response.access_token);
        navigate("/organizer/hacks");
      }
    } catch (err: any) {
      console.error("Login error:", err);
      setError("Неверный логин или пароль");
    }
  };

  return (
    <div className={styles.container}>
      <form className={styles.form} onSubmit={handleSubmit}>

        <h1 className={styles.title}>Авторизация организатора</h1>

        <label className={styles.label}>Email</label>
        <input
          type="text"
          value={login}
          onChange={(e) => setLogin(e.target.value)}
          className={styles.input}
        />

        <label className={styles.label}>Пароль</label>
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className={styles.input}
        />

        {error && <div className={styles.error}>{error}</div>}

        <button className={styles.button} type="submit">
          ВОЙТИ
        </button>
      </form>
    </div>
  );
};

export default OrganizeAuthPage;
