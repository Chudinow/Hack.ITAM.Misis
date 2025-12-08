import React, { useEffect, useState, useRef } from "react";
import styles from "./main-page.module.css";
import { Link } from "react-router-dom";
import { HackAPI, Hack } from "../../Shared/api/HackApi";

const MainPage: React.FC = () => {
  const [upcoming, setUpcoming] = useState<Hack[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(false);

  const hackSectionRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    async function load() {
      try {
        const res = await HackAPI.getUpcoming();
        setUpcoming(res.hacks ?? []);
      } catch (e) {
        console.error("Ошибка загрузки хакатонов:", e);
        setError(true);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, []);

  const scrollToHacks = () => {
    hackSectionRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  };

  return (
    <div className={styles.page}>
      {/* HERO */}
      <div className={styles.hero}>
        <h1 className={styles.title}>
          Выбери хакатон,<br />
          найди команду,<br />
          победи!
        </h1>

        <div className={styles.buttons}>
          <button onClick={scrollToHacks} className={styles.buttonPrimary}>
            Начать
          </button>

          <Link to="/organizer" className={styles.buttonOutline}>
            Я организатор
          </Link>
        </div>
      </div>

      {/* ХАКАТОНЫ */}
      <section ref={hackSectionRef} className={styles.hackSection}>
        <h2 className={styles.sectionTitle}>Ближайшие хакатоны</h2>

        {loading && <p className={styles.loading}>Загрузка...</p>}

        {error && (
          <p className={styles.loading}>Не удалось загрузить хакатоны</p>
        )}

        {!loading && !error && (
          <div className={styles.hackList}>
            {upcoming.map((hack) => (
              <Link
                key={hack.id}
                to={`/hackdetails/${hack.id}`}
                className={styles.hackCard}
              >
                <img src={hack.photo_url} className={styles.hackImage} />

                <div className={styles.hackInfo}>
                  <h3 className={styles.hackName}>{hack.name}</h3>

                  <div className={styles.tags}>
                    {(hack.tags ?? "")
                      .split(",")
                      .map((tag) => tag.trim())
                      .filter(Boolean)
                      .map((tag) => (
                        <span key={tag} className={styles.tag}>
                          {tag}
                        </span>
                      ))}
                  </div>
                </div>
              </Link>
            ))}
          </div>
        )}

        <Link to="/listhack" className={styles.viewAll}>
          Посмотреть все хакатоны
        </Link>
      </section>
    </div>
  );
};

export default MainPage;
