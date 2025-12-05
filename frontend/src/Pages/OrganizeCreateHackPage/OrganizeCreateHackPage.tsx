import React, { useState, useEffect } from "react";
import styles from "./organize-create-hack-page.module.css";
import { useParams } from "react-router-dom";

const OrganizeCreateHackPage: React.FC = () => {
  const { id } = useParams();

  const [form, setForm] = useState({
    title: "",
    regEnd: "",
    startTasks: "",
    sessions: "",
    commission: "",
    final: "",
    winners: "",
    description: "",
  });

  useEffect(() => {
    if (id) {
      // TODO: fetch from API
      setForm({
        title: "ITAM HACK",
        regEnd: "2025-02-10",
        startTasks: "2025-02-11",
        sessions: "2025-02-12",
        commission: "2025-02-15",
        final: "2025-02-20",
        winners: "2025-02-21",
        description: "Описание хакатона…",
      });
    }
  }, [id]);

  const handleChange = (key: string, value: string) => {
    setForm({ ...form, [key]: value });
  };

  const save = () => {
    console.log("DATA SAVED:", form);
    // TODO: POST or PUT request
  };

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Создание хакатона:</h1>

      <div className={styles.form}>
        <div className={styles.left}>

          <label>название:</label>
          <input value={form.title} onChange={(e) => handleChange("title", e.target.value)} />

          <label>регистрация до:</label>
          <input type="date" value={form.regEnd} onChange={(e) => handleChange("regEnd", e.target.value)} />

          <label>старт задач:</label>
          <input type="date" value={form.startTasks} onChange={(e) => handleChange("startTasks", e.target.value)} />

          <label>экспертные сессии:</label>
          <input type="date" value={form.sessions} onChange={(e) => handleChange("sessions", e.target.value)} />

          <label>работа комиссии:</label>
          <input type="date" value={form.commission} onChange={(e) => handleChange("commission", e.target.value)} />

          <label>Финал / объявление победителей:</label>
          <input type="date" value={form.winners} onChange={(e) => handleChange("winners", e.target.value)} />
        </div>

        <div className={styles.right}>
          <label>Фото:</label>
          <input type="file" />

          <label>Описание:</label>
          <textarea
            value={form.description}
            onChange={(e) => handleChange("description", e.target.value)}
          />
        </div>
      </div>

      <button className={styles.save} onClick={save}>
        сохранить изменения
      </button>
    </div>
  );
};

export default OrganizeCreateHackPage;
