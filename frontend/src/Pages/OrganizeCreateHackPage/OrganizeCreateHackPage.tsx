import React, { useState, useEffect } from "react";
import styles from "./organize-create-hack-page.module.css";
import { useParams } from "react-router-dom";

const OrganizeCreateHackPage: React.FC = () => {
  const { id } = useParams();

  const [form, setForm] = useState({
    title: "",
    description: "",
    start:"",
    end:"",
  });

  useEffect(() => {
    if (id) {
      // TODO: fetch from API
      setForm({
        title: "ITAM HACK",
        description: "Описание хакатона…",
        start:"20-12-2025",
        end:"13-01-2026"
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
          <label>Название:</label>
          <input 
            type="text"
            value={form.title}
            onChange={(e) => handleChange("title", e.target.value)}
          />

          <label>Описание:</label>
          <textarea
            value={form.description}
            onChange={(e) => handleChange("description", e.target.value)}
          />
        </div>

        <div className={styles.right}>
          <label>Фото:</label>
          <input type="file" />

          <label>Дата начала:</label>
          <input
            type="date"
            value={form.start}
            onChange={(e) => handleChange("start", e.target.value)}
          />

          <label>Дата конца:</label>
          <input
            type="date"
            value={form.end}
            onChange={(e) => handleChange("end", e.target.value)}
          />

          <button className={styles.save} onClick={save}>
            сохранить изменения
          </button>
          </div>
        </div>
    </div>
  );
};

export default OrganizeCreateHackPage;
