import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import styles from "./team-form-page.module.css";

import { HackAPI } from "../../Shared/api/HackApi";
import { TeamAPI } from "../../Shared/api/TeamApi";
import { UserAPI } from "../../Shared/api/UserApi";
import type { RoleType } from "../../Shared/api/TeamApi";

// Роли из твоего нового RoleType + "никого"
const ROLE_OPTIONS: RoleType[] = [
  "никого",
  "backend",
  "frontend",
  "mobile",
  "ml",
  "product",
  "designer",
];

const TeamFormPage: React.FC = () => {
  const { id: hackId } = useParams();
  const navigate = useNavigate();

  const [hack, setHack] = useState<any>(null);

  const [teamName, setTeamName] = useState("");
  const [aboutTeam, setAboutTeam] = useState("");
  const [findRoles, setFindRoles] = useState<RoleType[]>([]);

  const [userId, setUserId] = useState<number | null>(null);

  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    async function load() {
      try {
        const auth = await UserAPI.checkAuth();
        setUserId(auth.id);

        const hackData = await HackAPI.getById(Number(hackId));
        setHack(hackData);
      } catch (e) {
        console.error("Ошибка загрузки страницы:", e);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [hackId]);

  // Логика выбора ролей
  const toggleRole = (role: RoleType) => {
    // Если выбрали "никого"
    if (role === "никого") {
      // Если "никого" уже выбрана → снимаем выбор
      setFindRoles((prev) => (prev.includes("никого") ? [] : ["никого"]));
      return;
    }

    // Если выбрана другая роль → убираем "никого"
    setFindRoles((prev) => {
      const withoutNone = prev.filter((r) => r !== "никого");

      // Если уже выбрана → убираем
      if (withoutNone.includes(role)) {
        return withoutNone.filter((r) => r !== role);
      }

      // Добавляем новую роль
      return [...withoutNone, role];
    });
  };

  const handleSave = async () => {
    if (!userId) {
      alert("Ошибка: не удалось определить пользователя");
      return;
    }

    if (!teamName.trim()) {
      alert("Введите название команды");
      return;
    }

    if (findRoles.length === 0) {
      alert("Выберите хотя бы одну роль");
      return;
    }

    try {
      setSaving(true);

      // ВАЖНО:
      // Если выбрана "никого", то find_roles → []
      const finalRoles =
        findRoles.includes("никого") ? [] : (findRoles as RoleType[]);

      await TeamAPI.createTeam(Number(hackId), userId, {
        name: teamName,
        about: aboutTeam,
        find_roles: finalRoles,
      });

      navigate(`/hackdetails/${hackId}`);
    } catch (e) {
      console.error("Ошибка создания команды:", e);
      alert("Не удалось создать команду");
    } finally {
      setSaving(false);
    }
  };

  if (loading) return <div className={styles.loading}>Загрузка...</div>;

  return (
    <div className={styles.page}>
      {/* Хедер */}
      <div className={styles.headerCard}>
        <h1 className={styles.title}>{hack?.name}</h1>

        <div className={styles.tagRow}>
          {(hack?.tags?.split(",") ?? []).map((tag: string) => (
            <span key={tag} className={styles.tag}>
              {tag}
            </span>
          ))}
        </div>
      </div>

      {/* Форма */}
      <div className={styles.formWrapper}>
        <h2 className={styles.bigTitle}>Создание команды</h2>

        {/* Название */}
        <div className={styles.field}>
          <label className={styles.label}>Название команды:</label>
          <input
            className={styles.input}
            value={teamName}
            onChange={(e) => setTeamName(e.target.value)}
            placeholder="Введите название команды"
          />
        </div>

        {/* Роли */}
        <div className={styles.field}>
          <label className={styles.label}>Кого ищете:</label>

          <div className={styles.skillsGrid}>
            {ROLE_OPTIONS.map((role) => (
              <div
                key={role}
                className={
                  findRoles.includes(role)
                    ? styles.skillChipActive
                    : styles.skillChip
                }
                onClick={() => toggleRole(role)}
              >
                {role}
              </div>
            ))}
          </div>
        </div>

        {/* Описание */}
        <div className={styles.field}>
          <label className={styles.label}>О команде:</label>
          <textarea
            className={styles.textarea}
            rows={5}
            value={aboutTeam}
            onChange={(e) => setAboutTeam(e.target.value)}
            placeholder="Расскажите о вашей команде"
          />
        </div>

        {/* Кнопка */}
        <button
          className={styles.submitButton}
          onClick={handleSave}
          disabled={saving}
        >
          {saving ? "Создание..." : "Создать команду"}
        </button>
      </div>
    </div>
  );
};

export default TeamFormPage;
