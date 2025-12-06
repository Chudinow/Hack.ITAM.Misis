import styles from "./hack-details-page.module.css";
import { useNavigate, useParams } from "react-router-dom";
import { HackAPI, Hack } from "../../Shared/api/HackApi";
import { useEffect, useState } from "react";

const HackDetailsPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams();

  const [hack, setHack] = useState<Hack | null>(null);

  useEffect(() => {
    if (!id) return;

    async function loadHack() {
      try {
        const data = await HackAPI.getById(id!);
        setHack(data);
      } catch (error) {
        console.error("Ошибка загрузки хакатона:", error);
      }
    }

    loadHack();
  }, [id]);

  if (!hack) {
    return <div className={styles.loading}>Загрузка...</div>;
  }

  return (
    <div className={styles.page}>

      {/* КАРТИНКА-СЕКЦИЯ С ГРАДИЕНТОМ */}
      <div className={styles.headerCard}>
        <h1 className={styles.title}>{hack.name}</h1>

        <div className={styles.tagRow}>
          {hack.tags
            ?.split(",")
            .map(t => (
              <span key={t.trim()} className={styles.tag}>
                {t.trim()}
              </span>
            ))}
        </div>
      </div>

      {/* ОСНОВНОЙ КОНТЕНТ */}
      <div className={styles.content}>
        <p className={styles.description}>{hack.description}</p>

        {/* КНОПКИ */}
        <button className={styles.mainButton}>
          Найти команду
        </button>

        <button className={styles.secondaryButton}>
          У меня есть команда
        </button>
      </div>
    </div>
  );
};

export default HackDetailsPage;
