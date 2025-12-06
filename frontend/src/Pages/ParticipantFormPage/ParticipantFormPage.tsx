import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import styles from "./participant-form-page.module.css";

import { HackAPI } from "../../Shared/api/HackApi";
import { UserAPI, Skill } from "../../Shared/api/UserApi";

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

const roles = ["Frontend", "Backend", "Fullstack", "Designer", "Product", "Analyst", "просто забавный чел"];

const ParticipantFormPage: React.FC = () => {
  const navigate = useNavigate();
  const { id: hackId } = useParams();

  const [hack, setHack] = useState<any>(null);
  const [skillsList, setSkillsList] = useState<Skill[]>([]);
  const [userId, setUserId] = useState<number | null>(null);

  const [userName, setUserName] = useState("");
  const [role, setRole] = useState("");
  const [skills, setSkills] = useState<number[]>([]);
  const [about, setAbout] = useState("");

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const user = await UserAPI.getUser("me");
        setUserId(user.id ?? null);
        setUserName(user.name ?? "");

        const profile = await UserAPI.getProfile("me");
        setAbout(profile?.about ?? "");
        setRole(profile?.role ?? "");
        setSkills(profile?.skills?.map((s) => s.id) ?? []);

        const hackData = await HackAPI.getById(hackId!);
        setHack(hackData ?? {});

        let apiSkills: Skill[] = [];
        try {
          const skillResp = await UserAPI.getSkills();
          apiSkills = skillResp.skills ?? [];
        } catch {
          console.warn("Skills API unavailable — using fallback");
        }

        setSkillsList(apiSkills.length ? apiSkills : FALLBACK_SKILLS);
      } catch (e) {
        console.error("Ошибка загрузки:", e);
        navigate("/auth");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [hackId]);

  const toggleSkill = (id: number) => {
    setSkills((prev) =>
      prev.includes(id)
        ? prev.filter((s) => s !== id) // убрать
        : [...prev, id] // добавить
    );
  };

  const handleSave = async () => {
    if (!userId) return;

    try {
      setSaving(true);

      await UserAPI.updateProfile(userId, {
        user_id: userId,
        about,
        skills_id: skills,
        role,
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
          {(hack?.tags?.split(",") ?? []).map((t: string) => (
            <span key={t} className={styles.tag}>
              {t}
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
            value={role}
            onChange={(e) => setRole(e.target.value)}
          >
            <option value="">Выберите роль</option>
            {roles.map((r) => (
              <option key={r} value={r}>
                {r}
              </option>
            ))}
          </select>
        </div>

        {/* ⭐ КАСТОМНЫЙ ВЫБОР НАВЫКОВ (ЧИПЫ) ⭐ */}
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
