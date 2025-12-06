import React, { useEffect, useState, useRef } from "react";
import styles from "./main-page.module.css";
import { Link } from "react-router-dom";
import { HackAPI, Hack } from "../../Shared/api/HackApi"

const MainPage: React.FC = () => {
  const [upcoming, setUpcoming] = useState<Hack[]>([]);
  const [loading, setLoading] = useState(true);

  const hackSectionRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    HackAPI.getUpcoming().then((res) => {
      setUpcoming(res.hacks);
      setLoading(false);
    });
  }, []);

  const scrollToHacks = () => {
    hackSectionRef.current?.scrollIntoView({
      behavior: "smooth",
      block: "start",
    });
  };

  return (
    <div className={styles.page}>
      
      <div className={styles.hero}>
        <h1 className={styles.title}>
          Выбери хакатон,<br />
          найди команду,<br />
          победи!
        </h1>

        <div className={styles.buttons}>

          {/* КНОПКА, КОТОРАЯ ПРОКРУЧИВАЕТ ВНИЗ */}
          <button onClick={scrollToHacks} className={styles.buttonPrimary}>
            Начать
          </button>

          <Link to="/organizer" className={styles.buttonOutline}>
            Я организатор
          </Link>
          
        </div>
      </div>

      {/* СЕКЦИЯ ДЛЯ СКРОЛЛА */}
      <section ref={hackSectionRef} className={styles.hackSection}>
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
