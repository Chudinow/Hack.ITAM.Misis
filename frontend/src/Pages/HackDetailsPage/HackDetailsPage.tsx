import React from "react";
import styles from "./hack-details-page.module.css";
import exampleImg from "../../Photos/1.png"; 
import { useNavigate } from "react-router-dom";

const HackDetailsPage: React.FC = () => {

  const navigate = useNavigate();

  const handleParticipate = () => {
    window.open("https://t.me/YOUR_BOT_NAME?start=register", "_blank");
    navigate("/profile");
  };

  return (
    <div className={styles.wrapper}>
      <div className={styles.container}>

        <img src={exampleImg} alt="hack" className={styles.image} />

        <div className={styles.info}>
          <h1 className={styles.title}>Название хакатона</h1>

          <p className={styles.label}>
            <span>дата проведения:</span>10.08.2023–32.12.2302
          </p>

          <p className={styles.description}>
            <span>Описание:</span> тут очень крутое описание тут очень крутое описание
            тут очень крутое описание тут очень крутое описание тут очень крутое
            описание тут очень крутое описание тут очень крутое описание тут очень
            крутое описание тут очень крутое описание
          </p>

          <button className={styles.button} onClick={handleParticipate}>участвовать</button>
        </div>

      </div>
    </div>
  );
};

export default HackDetailsPage;
