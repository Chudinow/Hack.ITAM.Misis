import React from "react";
import styles from "./main-page.module.css";
import { Link } from "react-router-dom";

const MainPage: React.FC = () => {
  return (
    <div className={styles.wrapper}>
      <div className={styles.backgroundText}>
        <span className={`${styles.letter} ${styles.animateLetter}`}>I</span>
        <span className={`${styles.letter} ${styles.animateLetter}`}>T</span>
        <span className={`${styles.letter} ${styles.animateLetter}`}>A</span>
        <span className={`${styles.letter} ${styles.animateLetter}`}>M</span>
      </div>

      <div className={`${styles.content} ${styles.fadeUp}`}>

        <h1 className={styles.title}>
          Выбери хакатон,<br />
          найди команду,<br />
          победи!
        </h1>

        <div className={styles.buttons}>
          <Link to="../listhack" className={styles.buttonPrimary}>
            начать
          </Link>

          <Link to="../listhack" className={styles.buttonOutline}>
            для организаторов
          </Link>
        </div>

      </div>
    </div>


  );
};

export default MainPage;