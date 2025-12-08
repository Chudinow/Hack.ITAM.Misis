import React, { useEffect, useState } from "react";
import styles from "./organize-hackathon-page.module.css";
import { useNavigate } from "react-router-dom";
import { OrganizerHackApi, HackathonResponse } from "../../Shared/api/OrganizerApi";

const OrganizeHackathonPage: React.FC = () => {
  const navigate = useNavigate();
  const [hacks, setHacks] = useState<HackathonResponse[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      try {
        const res = await OrganizerHackApi.getMyHackathons();
        setHacks(res);
      } catch (e) {
        console.error("Ошибка загрузки хакатонов:", e);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  if (loading) return <div className={styles.loading}>Загрузка...</div>;

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Мои хакатоны</h1>

      <div className={styles.grid}>

        {/* Создать */}
        <div
          className={styles.createCard}
          onClick={() => navigate("/organizer/hacks/create")}
        >
          <span className={styles.plus}>+</span>
        </div>

        {/* Существующие */}
        {hacks.map((h) => (
          <div
            key={h.id}
            className={styles.hackCard}
            onClick={() => navigate(`/organizer/hacks/${h.id}`)}
          >
            <h3>{h.title}</h3>
            <p>{h.date_start} — {h.date_end}</p>
          </div>
        ))}

      </div>
    </div>
  );
};

export default OrganizeHackathonPage;
