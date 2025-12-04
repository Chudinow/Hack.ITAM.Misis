import React from "react";
import styles from "./list-hack-page.module.css";
import { Link } from "react-router-dom";
import exampleImg from "../../Photos/1.png";

const ListHackPage: React.FC = () => {
  return (
    <div className={styles.wrapper}>
      <h1 className={styles.title}>Ближайшие Хакатоны</h1>
      
      <div className={styles.cards}>
        
        <Link to="../hackdetails" className={styles.card}>
          <img src={exampleImg} alt="hack-img" className={styles.image} />

          <div className={styles.cardContent}>
            <h2 className={styles.cardTitle}>Название</h2>
            <p className={styles.cardText}>
              описание крч оч интересное все такое классное реально респект
              всем всех люблю уважаю поддерживаю ну или что-то другое
            </p>
          </div>
        </Link>

        <Link to="../hackdetails" className={styles.card}>
          <img src={exampleImg} alt="hack-img" className={styles.image} />

          <div className={styles.cardContent}>
            <h2 className={styles.cardTitle}>Название</h2>
            <p className={styles.cardText}>
              описание крч оч интересное все такое классное реально респект
              всем всех люблю уважаю поддерживаю ну или что-то другое
            </p>
          </div>
        </Link>

        <Link to="../hackdetails" className={styles.card}>
          <img src={exampleImg} alt="hack-img" className={styles.image} />

          <div className={styles.cardContent}>
            <h2 className={styles.cardTitle}>Название</h2>
            <p className={styles.cardText}>
              описание крч оч интересное все такое классное реально респект
              всем всех люблю уважаю поддерживаю ну или что-то другое
            </p>
          </div>
        </Link>
      </div>
    </div>
  );
};

export default ListHackPage;
