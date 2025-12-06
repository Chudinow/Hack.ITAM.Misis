import React, { useEffect, useState } from "react";
import styles from "./list-hack-page.module.css";
import { Link } from "react-router-dom";
import { HackAPI, Hack } from "../../Shared/api/HackApi"

const ListHackPage: React.FC = () => {
  const [hacks, setHacks] = useState<Hack[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const res = await HackAPI.getAll();
        setHacks(res.hacks);
      } catch (err) {
        console.error("Ошибка загрузки хакатонов:", err);
      } finally {
        setLoading(false);
      }
    };

    load();
  }, []);

  if (loading) return <div className={styles.wrapper}><h1>Загрузка...</h1></div>;

  return (
    <div className={styles.wrapper}>
      <h1 className={styles.title}>Хакатоны</h1>

      <div className={styles.cards}>
        {hacks.map(hack => (
          <Link key={hack.id} to={`/hackdetails/${hack.id}`} className={styles.card}>
            <img src={hack.photo_url} alt="hack-img" className={styles.image} />

            <div className={styles.cardContent}>
              <h2 className={styles.cardTitle}>{hack.name}</h2>
              <p className={styles.cardText}>{hack.description}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
};

export default ListHackPage;
