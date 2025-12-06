import styles from "./hack-details-page.module.css";
import { useNavigate, useSearchParams } from "react-router-dom";
import { HackAPI, Hack } from "../../Shared/api/HackApi";
import { useEffect, useState } from "react";

const HackDetailsPage: React.FC = () => {
  const navigate = useNavigate();
  const [params] = useSearchParams();
  const hackId = params.get("id");

  const [hack, setHack] = useState<Hack | null>(null);

  useEffect(() => {
    if (!hackId) return;

    const load = async () => {
      try {
        const data = await HackAPI.getById(hackId);
        setHack(data);
      } catch (e) {
        console.error("Ошибка загрузки:", e);
      }
    };

    load();
  }, [hackId]);

  const handleParticipate = () => {
    navigate(`/team/create?hackId=${hackId}`);
  };

  if (!hack) return <div className={styles.wrapper}><h1>Загрузка...</h1></div>;

  return (
    <div className={styles.wrapper}>
      <div className={styles.container}>

        <img src={hack.photo_url} alt="hack" className={styles.image} />

        <div className={styles.info}>
          <h1 className={styles.title}>{hack.name}</h1>

          <p className={styles.label}>
            <span>дата проведения:</span> {hack.start_date} — {hack.end_date}
          </p>

          <p className={styles.description}>
            <span>Описание:</span> {hack.description}
          </p>

          <button className={styles.button} onClick={handleParticipate}>
            участвовать
          </button>
        </div>

      </div>
    </div>
  );
};

export default HackDetailsPage;
