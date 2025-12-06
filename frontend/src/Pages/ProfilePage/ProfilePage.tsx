import React, { useEffect, useState } from "react";
import styles from "./profile-page.module.css";
import RoleSelector from "./components/roleSelector";
import LanguageSelector from "./components/languageSelector";
import { ProfileAPI, UserProfile, Skill } from "../../Shared/api/ProfileApi";

const ProfilePage: React.FC = () => {
  const userId = 1; // TEMP — обычно берётся из auth context

  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [selectedSkills, setSelectedSkills] = useState<number[]>([]);
  const [about, setAbout] = useState("");

  useEffect(() => {
    const load = async () => {
      try {
        const prof = await ProfileAPI.getProfile(userId);
        setProfile(prof);
        setSelectedSkills(prof.skills.map(s => s.id));
        setAbout(prof.about);

        const skillList = await ProfileAPI.getSkills();
        setSkills(skillList.skills);
      } catch (err) {
        console.error("Ошибка загрузки профиля:", err);
      }
    };

    load();
  }, []);

  const toggleSkill = (id: number) => {
    if (selectedSkills.includes(id)) {
      setSelectedSkills(prev => prev.filter(s => s !== id));
    } else {
      setSelectedSkills(prev => [...prev, id]);
    }
  };

  const saveProfile = async () => {
    try {
      await ProfileAPI.updateProfile(userId, {
        user_id: userId,
        about,
        skills_id: selectedSkills
      });

      alert("Профиль обновлён!");
    } catch (err) {
      console.error(err);
      alert("Ошибка сохранения");
    }
  };

  if (!profile) return <div className={styles.wrapper}><h1>Загрузка...</h1></div>;

  return (
    <div className={styles.wrapper}>
      <h1 className={styles.title}>Мой профиль</h1>

      <div className={styles.container}>

        <div className={styles.info}>
          <p className={styles.field}><span>Имя:</span> {profile.user_id}</p>

          <p className={styles.fieldTitle}>О себе:</p>
          <textarea
            className={styles.textarea}
            value={about}
            onChange={(e) => setAbout(e.target.value)}
          />

          <p className={styles.fieldTitle}>Навыки:</p>

          <div className={styles.skills}>
            {skills.map(skill => (
              <button
                key={skill.id}
                className={`${styles.tag} ${selectedSkills.includes(skill.id) ? styles.active : ""}`}
                onClick={() => toggleSkill(skill.id)}
              >
                {skill.name}
              </button>
            ))}
          </div>

          <button className={styles.saveBtn} onClick={saveProfile}>
            Сохранить изменения
          </button>
        </div>
      </div>
    </div>
  );
};

export default ProfilePage;
