import React from "react";
import styles from "./hack-details-page.module.css";
import exampleImg from "../../Photos/1.png"; 

const HackDetailsPage: React.FC = () => {
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

          <button className={styles.button}>участвовать</button>
        </div>

      </div>
    </div>
  );
};

export default HackDetailsPage;
