import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import styles from "./team-form-page.module.css";

import { HackAPI } from "../../Shared/api/HackApi";
import { TeamAPI } from "../../Shared/api/TeamApi";
import { UserAPI } from "../../Shared/api/UserApi";

const roles = [
  "Никого не ищем",  
  "Frontend",
  "Backend",
  "Fullstack",
  "Designer",
  "Product",
  "Analyst",
];

const TeamFormPage: React.FC = () => {
  const { id: hackId } = useParams();
  const navigate = useNavigate();

  const [hack, setHack] = useState<any>(null);

  const [teamName, setTeamName] = useState("");
  const [lookingFor, setLookingFor] = useState("");
  const [aboutTeam, setAboutTeam] = useState("");

  const [userId, setUserId] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const user = await UserAPI.getUser("me");
        setUserId(user.id);

        const hackData = await HackAPI.getById(hackId!);
        setHack(hackData);
      } catch (e) {
        console.error(e);
        navigate("/auth");
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [hackId, navigate]);

  const handleSave = async () => {
    if (!userId) return;

    try {
      setSaving(true);

      await TeamAPI.createTeam(hackId!, {
        name: teamName,
        hackathon_id: Number(hackId),
        is_completed: false,
        member_ids: [
          {
            user_id: userId,
            role: lookingFor || "creator",
          },
        ],
      });

      navigate(`/hackdetails/${hackId}`);
    } catch (e) {
      console.error(e);
      alert("Ошибка сохранения");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className={styles.loading}>Загрузка...</div>;

  return (
    <div className={styles.page}>
      <div className={styles.headerCard}>
        <h1 className={styles.title}>{hack.name}</h1>
        <div className={styles.tagRow}>
          {hack.tags.split(",").map((t: string) => (
            <span key={t} className={styles.tag}>{t}</span>
          ))}
        </div>
      </div>

      <div className={styles.formWrapper}>
        <h2 className={styles.bigTitle}>Заполните анкету команды</h2>

        <div className={styles.field}>
          <label className={styles.label}>Название команды:</label>
          <input
            className={styles.input}
            value={teamName}
            onChange={(e) => setTeamName(e.target.value)}
          />
        </div>

        <div className={styles.field}>
          <label className={styles.label}>Кого ищете:</label>
          <select
            className={styles.select}
            value={lookingFor}
            onChange={(e) => setLookingFor(e.target.value)}
          >
            <option value="">Выберите роль</option>
            {roles.map((r) => (
              <option key={r}>{r}</option>
            ))}
          </select>
        </div>

        <div className={styles.field}>
          <label className={styles.label}>О команде:</label>
          <textarea
            className={styles.textarea}
            value={aboutTeam}
            onChange={(e) => setAboutTeam(e.target.value)}
            rows={5}
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

export default TeamFormPage;
