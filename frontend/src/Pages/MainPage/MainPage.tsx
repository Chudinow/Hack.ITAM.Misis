import React, { useEffect, useState } from "react";
import styles from "./main-page.module.css";
import { Link } from "react-router-dom";
import { HackAPI, Hack } from "../../Shared/api/HackApi"

const MainPage: React.FC = () => {
  const [upcoming, setUpcoming] = useState<Hack[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    HackAPI.getUpcoming().then((res) => {
      setUpcoming(res.hacks);
      setLoading(false);
    });
  }, []);

  return (
    <div className={styles.wrapper}>
      
      <div className={styles.starsWrapper}>
        <div className={`${styles.star} ${styles.star1}`} />
        <div className={`${styles.star} ${styles.star2}`} />
        <div className={`${styles.star} ${styles.star3}`} />
      </div>

      <div className={styles.content}>
        <h1 className={styles.title}>
          Выбери хакатон,<br />
          найди команду,<br />
          победи!
        </h1>

        <div className={styles.buttons}>
          <Link to="/listhack" className={styles.buttonPrimary}>
            Начать
          </Link>

          <Link to="/organizer" className={styles.buttonOutline}>
            Я организатор
          </Link>
        </div>
      </div>

      <section className={styles.hackSection}>
        <h2 className={styles.sectionTitle}>Ближайшие хакатоны</h2>

        {loading ? (
          <p className={styles.loading}>Загрузка...</p>
        ) : (
          <div className={styles.hackList}>
            {upcoming.map((hack) => (
              <Link key={hack.id} to={`/hack/${hack.id}`} className={styles.hackCard}>
                
                <img src={hack.photo_url} className={styles.hackImage} />

                <div className={styles.hackInfo}>
                  <h3 className={styles.hackName}>{hack.name}</h3>
                  <div className={styles.tags}>
                    {hack.tags.split(",").map((tag) => (
                      <span key={tag} className={styles.tag}>
                        {tag.trim()}
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
