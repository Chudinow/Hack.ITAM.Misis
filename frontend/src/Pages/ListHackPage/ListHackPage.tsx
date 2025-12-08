import React, { useEffect, useState } from "react";
import styles from "./list-hack-page.module.css";
import { Link } from "react-router-dom";
import { HackAPI, Hack } from "../../Shared/api/HackApi";

const ListHackPage: React.FC = () => {
  const [hacks, setHacks] = useState<Hack[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const res = await HackAPI.getAll();

        // Защита от undefined
        setHacks(res?.hacks ?? []);
      } catch (err) {
        console.error("Ошибка загрузки хакатонов:", err);
        setError(true);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  if (loading) {
    return (
      <div className={styles.wrapper}>
        <h1>Загрузка...</h1>
      </div>
    );
  }

  if (error) {
    return (
      <div className={styles.wrapper}>
        <h1>Не удалось загрузить хакатоны</h1>
        <p style={{ opacity: 0.7 }}>Попробуйте обновить страницу позже.</p>
      </div>
    );
  }

  return (
    <div className={styles.wrapper}>
      <h1 className={styles.title}>Хакатоны</h1>

      <div className={styles.cards}>
        {hacks.map((hack) => (
          <Link
            key={hack.id}
            to={`/hackdetails/${hack.id}`}
            className={styles.card}
          >
            <img
              src={hack.photo_url || "https://via.placeholder.com/600x300"}
              alt="hack-img"
              className={styles.image}
            />

            <div className={styles.cardContent}>
              <h2 className={styles.cardTitle}>{hack.name}</h2>

              <p className={styles.cardText}>
                {hack.description.length > 160
                  ? hack.description.slice(0, 160) + "..."
                  : hack.description}
              </p>
            </div>
          </Link>
        ))}
      </div>

      {hacks.length === 0 && (
        <p style={{ textAlign: "center", opacity: 0.7 }}>
          Пока нет доступных хакатонов.
        </p>
      )}
    </div>
  );
};

export default ListHackPage;
