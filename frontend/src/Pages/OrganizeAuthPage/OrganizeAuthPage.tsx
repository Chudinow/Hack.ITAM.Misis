import React, { useState } from "react";
import styles from "./organize-auth-page.module.css";
import { useNavigate } from "react-router-dom";

const OrganizeAuthPage: React.FC = () => {
  const [login, setLogin] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();

    if (login && password) {
      navigate("/organizer/hacks");
    }
  };

  return (
    <div className={styles.container}>

      <form className={styles.form} onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="login"
          value={login}
          onChange={(e) => setLogin(e.target.value)}
          className={styles.input}
        />

        <input
          type="password"
          placeholder="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className={styles.input}
        />

        <button className={styles.button} type="submit">
          ВОЙТИ
        </button>
      </form>
    </div>
  );
};

export default OrganizeAuthPage;
