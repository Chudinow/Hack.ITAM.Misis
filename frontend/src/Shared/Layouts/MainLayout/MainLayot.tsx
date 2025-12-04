import { Outlet } from "react-router-dom";
import styles from "./main-layout.module.css";

const MainLayout = () => {
  return (
    <div className={styles.layout}>
      <div className={styles.dotsBackground} />
      <div className={styles.content}>
        <Outlet />
      </div>
    </div>
  );
};

export default MainLayout;
