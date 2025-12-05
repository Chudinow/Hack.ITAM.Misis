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
        
        <label className={styles.label}>login</label>
        <input
          type="text"
          value={login}
          placeholder=" "
          onChange={(e) => setLogin(e.target.value)}
          className={styles.input}
        />

        <label className={styles.label}>password</label>
        <input
          type="password"
          value={password}
          placeholder=" "
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
