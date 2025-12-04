import React, { useState } from "react";
import styles from "./profile-page.module.css";
import RoleSelector from "./components/roleSelector";
import LanguageSelector from "./components/languageSelector";
import exampleImg from "../../Photos/myphoto.jpg"; 

const ProfilePage: React.FC = () => {
  const [name, _] = useState("Максим");

  const [roles, setRoles] = useState<string[]>([]);
  const [languages, setLanguages] = useState<string[]>([]);

  const handleSave = () => {
    const payload = { name, roles, languages };
    console.log("Отправляем на сервер:", payload);
  };

  return (
    <div className={styles.wrapper}>
      <h1 className={styles.title}>Мой профиль</h1>

      <div className={styles.container}>
        <img src={exampleImg} alt="avatar" className={styles.avatar} />

        <div className={styles.info}>
          <p className={styles.field}>
            <span>Имя:</span> {name}
          </p>

          <p className={styles.fieldTitle}>Кто я?</p>
          <RoleSelector selected={roles} setSelected={setRoles} />

          <p className={styles.fieldTitle}>Языки программирования:</p>
          <LanguageSelector selected={languages} setSelected={setLanguages} />

          <button className={styles.saveBtn} onClick={handleSave}>
            Сохранить изменения
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
