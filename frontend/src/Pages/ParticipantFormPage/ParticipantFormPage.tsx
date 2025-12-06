import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import styles from "./participant-form-page.module.css";

import { HackAPI } from "../../Shared/api/HackApi";
import { UserAPI, Skill } from "../../Shared/api/UserApi";

// 🔥 Fallback навыки — используются, если backend ничего не отдаёт
const FALLBACK_SKILLS: Skill[] = [
  { id: 1, name: "JavaScript", type: "hard" },
  { id: 2, name: "TypeScript", type: "hard" },
  { id: 3, name: "React", type: "hard" },
  { id: 4, name: "Figma", type: "hard" },
  { id: 5, name: "Teamwork", type: "soft" },
];

const roles = ["Frontend", "Backend", "Fullstack", "Designer", "Product", "Analyst"];

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
        // Загружаем пользователя
        const user = await UserAPI.getUser("me");
        setUserId(user.id ?? null);
        setUserName(user.name ?? "");

        // Загружаем профиль
        const profile = await UserAPI.getProfile("me");
        setAbout(profile?.about ?? "");
        setRole(profile?.role ?? "");
        setSkills(profile?.skills?.map((s) => s.id) ?? []);

        // Загружаем хакатон
        const hackData = await HackAPI.getById(hackId!);
        setHack(hackData ?? {});

        // Загружаем навыки
        let skillsFromApi: Skill[] = [];

        try {
          const skillsData = await UserAPI.getSkills();
          skillsFromApi = skillsData?.skills ?? [];
        } catch {
          console.warn("Backend skills not available — using fallback list");
        }

        // Если API отдал ничего → fallback
        if (!skillsFromApi.length) {
          setSkillsList(FALLBACK_SKILLS);
        } else {
          setSkillsList(skillsFromApi);
        }

      } catch (e) {
        console.error("Ошибка загрузки:", e);
        navigate("/auth");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [hackId]);

  const handleSkillChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const selected = Array.from(e.target.selectedOptions).map((o) =>
      Number(o.value)
    );
    setSkills(selected);
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

        <div className={styles.field}>
          <label className={styles.label}>Навыки:</label>

          <select
            multiple
            className={styles.selectMultiple}
            value={skills.map(String)}
            onChange={handleSkillChange}
          >
            {skillsList.map((s) => (
              <option key={s.id} value={s.id}>
                {s.name}
              </option>
            ))}
          </select>
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
