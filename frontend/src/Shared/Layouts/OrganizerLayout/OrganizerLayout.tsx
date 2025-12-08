import React from "react";
import { Outlet } from "react-router-dom";
import styles from "./organizer-layout.module.css";

const OrganizerLayout: React.FC = () => {
  return (
    <div className={styles.wrapper}>
      <div className={styles.dotsBackground} />
        <Outlet />
    </div>
  );
};

export default OrganizerLayout;
