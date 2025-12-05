import React from "react";
import styles from "./organize-hackathon-page.module.css";
import { useNavigate } from "react-router-dom";

const OrganizeHackathonPage: React.FC = () => {
  const navigate = useNavigate();

  const hacks = [
    { id: 1, title: "ITAM HACK" },
    { id: 2, title: "Cyber Challenge" }
  ];

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>Мои хакатоны</h1>

      <div className={styles.grid}>
        {/* create card */}
        <div className={styles.createCard} onClick={() => navigate("/organizer/hacks/create")}>
          <span className={styles.plus}>+</span>
        </div>

        {/* existing cards */}
        {hacks.map((h) => (
          <div
            key={h.id}
            className={styles.hackCard}
            onClick={() => navigate(`/organizer/hacks/${h.id}`)}
          >
            <h3>{h.title}</h3>
          </div>
        ))}
      </div>
    </div>
  );
};

export default OrganizeHackathonPage;
