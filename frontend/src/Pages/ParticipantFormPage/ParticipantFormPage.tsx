import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import styles from "./participant-form-page.module.css";

import { HackAPI } from "../../Shared/api/HackApi";
import { UserAPI } from "../../Shared/api/UserApi";
import { ProfileAPI } from "../../Shared/api/ProfileApi";
import type { Skill } from "../../Shared/api/UserApi";
import type { RoleType } from "../../Shared/api/ProfileApi";

const ROLE_OPTIONS: RoleType[] = [
  "backend",
  "frontend",
  "mobile",
  "ml",
  "product",
  "designer",
];

// ВСЕГДА показываем эти навыки
const FALLBACK_SKILLS: Skill[] = [
  { id: 1, name: "JS", type: "hard" },
  { id: 2, name: "TS", type: "hard" },
  { id: 3, name: "React", type: "hard" },
  { id: 4, name: "Vite", type: "hard" },
  { id: 5, name: "Python", type: "hard" },
  { id: 6, name: "C#", type: "hard" },
  { id: 7, name: "C++", type: "hard" },
  { id: 8, name: "GO", type: "hard" },
  { id: 9, name: "Docker", type: "hard" },
  { id: 10, name: "AI", type: "soft" },
];

const ParticipantFormPage: React.FC = () => {
  const navigate = useNavigate();
  const { id: hackId } = useParams();

  const [hack, setHack] = useState<any>(null);

  // ВСЕГДА показываем fallback-список навыков!
  const [skillsList] = useState<Skill[]>(FALLBACK_SKILLS);

  const [skills, setSkills] = useState<number[]>([]);
  const [about, setAbout] = useState("");
  const [role, setRole] = useState<RoleType | null>(null);

  const [profileId, setProfileId] = useState<number | null>(null);
  const [userId, setUserId] = useState<number | null>(null);
  const [userName, setUserName] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const auth = await UserAPI.checkAuth();
        setUserId(auth.id);
        setUserName(auth.name);

        // Загружаем профиль
        let profile;
        try {
          profile = await ProfileAPI.getProfile(auth.id);
        } catch {
          profile = {
            id: auth.id,
            user_id: auth.id,
            about: "",
            role: null,
            skills: [],
          };
        }

        setProfileId(profile.id);
        setAbout(profile.about ?? "");
        setRole(profile.role ?? null);

        // Из профиля нам нужны только IDs навыков
        const extractedSkillIds =
          Array.isArray(profile.skills)
            ? profile.skills
                .map((s: any) => Number(s.id))
                .filter((x) => !isNaN(x))
            : [];

        setSkills(extractedSkillIds);

        // Загружаем хакатон
        const hackData = await HackAPI.getById(Number(hackId));
        setHack(hackData);

      } catch (e) {
        console.error("Ошибка загрузки:", e);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [hackId]);

  const toggleSkill = (id: number) => {
    setSkills((prev) =>
      prev.includes(id)
        ? prev.filter((s) => s !== id)
        : [...prev, id]
    );
  };

  const handleSave = async () => {
    if (!userId || !profileId) return;
    if (!role) {
      alert("Выберите вашу основную роль");
      return;
    }

    try {
      setSaving(true);

      await ProfileAPI.updateProfile(profileId, userId, {
        user_id: userId,
        about,
        role,
        skills_id: skills,
      });

      navigate(`/hackdetails/${hackId}`);
    } catch (e) {
      console.error("Ошибка сохранения профиля:", e);
      alert("Ошибка сохранения");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className={styles.loading}>Загрузка...</div>;

  return (
    <div className={styles.page}>
      <div className={styles.headerCard}>
        <h1 className={styles.title}>{hack?.name ?? ""}</h1>

        <div className={styles.tagRow}>
          {(hack?.tags?.split(",") ?? []).map((tag: string) => (
            <span key={tag} className={styles.tag}>
              {tag}
            </span>
          ))}
        </div>
      </div>

      <div className={styles.formWrapper}>
        <h2 className={styles.bigTitle}>Анкета участника</h2>

        <div className={styles.field}>
          <label className={styles.label}>Имя:</label>
          <input className={styles.input} value={userName} readOnly />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Основная роль:</label>
          <select
            className={styles.select}
            value={role ?? ""}
            onChange={(e) => setRole(e.target.value as RoleType)}
          >
            <option value="">Выберите роль</option>
            {ROLE_OPTIONS.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Навыки:</label>

          <div className={styles.skillsGrid}>
            {skillsList.map((s) => (
              <div
                key={s.id}
                className={
                  skills.includes(s.id)
                    ? styles.skillChipActive
                    : styles.skillChip
                }
                onClick={() => toggleSkill(s.id)}
              >
                {s.name}
              </div>
            ))}
          </div>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>О себе:</label>
          <textarea
            className={styles.textarea}
            rows={5}
            value={about}
            onChange={(e) => setAbout(e.target.value)}
          />
        </div>

        <button
          className={styles.submitButton}
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? "Сохранение..." : "Сохранить"}
        </button>
      </div>
    </div>
  );
};

export default ParticipantFormPage;
