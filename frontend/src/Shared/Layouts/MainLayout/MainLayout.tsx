import React from "react";
import { Outlet } from "react-router-dom";
import styles from "./main-layout.module.css";

const MainLayout: React.FC = () => {
  return (
    <div className={styles.wrapper}>
      
      {/* ОБЩИЙ ФОН И ЗВЁЗДЫ */}
      <div className={styles.starsWrapper}>

        <div className={`${styles.star} ${styles.star1}`} />
        <div className={`${styles.star} ${styles.star2}`} />
        <div className={`${styles.star} ${styles.star3}`} />

        <div className={`${styles.secondStar} ${styles.secondStar1}`} />
        <div className={`${styles.secondStar} ${styles.secondStar2}`} />
        <div className={`${styles.secondStar} ${styles.secondStar3}`} />
      </div>

      {/* КОНТЕНТ СТРАНИЦЫ */}
      <div className={styles.contentWrapper}>
        <Outlet />
      </div>

    </div>
  );
};

export default MainLayout;
