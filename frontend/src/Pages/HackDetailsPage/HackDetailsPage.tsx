import styles from "./hack-details-page.module.css";
import { useNavigate, useParams } from "react-router-dom";
import { HackAPI, Hack } from "../../Shared/api/HackApi";
import { TeamAPI } from "../../Shared/api/TeamApi";
import { UserAPI } from "../../Shared/api/UserApi";
import { useEffect, useState } from "react";

// ===== MOCK DATA =====
const MOCK = true;

const MOCK_PARTICIPANTS = [
  {
    participant_id: 101,
    name: "Максим Волков",
    role: "frontend",
    skills: [{ id: 1, name: "React" }],
  },
  {
    participant_id: 102,
    name: "София Лебедева",
    role: "ml",
    skills: [{ id: 2, name: "TensorFlow" }],
  },
  {
    participant_id: 103,
    name: "Илья Морозов",
    role: "backend",
    skills: [{ id: 3, name: "FastAPI" }],
  },
];

const MOCK_TEAMS = [
  {
    id: 501,
    name: "CyberFox",
    about: "Frontend + Mobile",
    empty_roles: [{ role: "backend" }, { role: "ml" }],
  },
  {
    id: 502,
    name: "DeepVision",
    about: "ML команда для CV",
    empty_roles: [{ role: "frontend" }],
  },
  {
    id: 503,
    name: "Rocket Labs",
    about: "Fullstack + Product",
    empty_roles: [{ role: "designer" }, { role: "mobile" }],
  },
];

// =====================

const HackDetailsPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams();

  const [hack, setHack] = useState<Hack | null>(null);

  const [activeTab, setActiveTab] = useState<"participants" | "teams" | null>(null);

  const [participants, setParticipants] = useState<any[]>([]);
  const [loadingParticipants, setLoadingParticipants] = useState(false);

  const [teams, setTeams] = useState<any[]>([]);
  const [loadingTeams, setLoadingTeams] = useState(false);

  // ===== ЗАГРУЗКА ХАКАТОНА =====
  useEffect(() => {
    if (!id) return;

    async function loadHack() {
      try {
        const data = await HackAPI.getById(id!);
        setHack(data);
      } catch (error) {
        console.error("Ошибка загрузки хакатона:", error);
      }
    }

    loadHack();
  }, [id]);

  if (!hack) {
    return <div className={styles.loading}>Загрузка...</div>;
  }

  // ===== НАВИГАЦИЯ =====
  const handleFindTeam = () => navigate(`/hackdetails/${id}/participant-form`);
  const handleHaveTeam = () => navigate(`/hackdetails/${id}/team-form`);

  // ===== ЗАГРУЗКА УЧАСТНИКОВ =====
  const loadParticipants = async () => {
    if (!id) return;
    setLoadingParticipants(true);

    try {
      let res;

      if (MOCK) {
        res = MOCK_PARTICIPANTS;
      } else {
        res = await TeamAPI.searchParticipants(Number(id));
      }

      const normalized = res.map((p: any) => ({
        id: p.participant_id,
        name: p.name,
        role: p.role,
        skills: p.skills,
      }));

      setParticipants(normalized);
      setActiveTab("participants");
    } catch (e) {
      console.error("Ошибка загрузки участников:", e);
    } finally {
      setLoadingParticipants(false);
    }
  };

  // ===== ПРИГЛАШЕНИЕ УЧАСТНИКА =====
  const inviteParticipant = async (participantId: number) => {
    try {
      const me = await UserAPI.checkAuth();
      const myTeam = await TeamAPI.getUserTeam(Number(id), me.id);

      await TeamAPI.invite(Number(id), myTeam.id, participantId);
      alert("Приглашение отправлено!");
    } catch (e) {
      console.error("Ошибка приглашения:", e);
      alert("Не удалось отправить приглашение");
    }
  };

  // ===== ЗАГРУЗКА КОМАНД =====
  const loadTeams = async () => {
    if (!id) return;
    setLoadingTeams(true);

    try {
      let res;

      if (MOCK) {
        res = MOCK_TEAMS;
      } else {
        res = await TeamAPI.searchEmpty(Number(id));
      }

      const normalized = res.map((t: any) => ({
        id: t.id,
        name: t.name,
        about: t.about,
        roles: t.empty_roles.map((r: any) => r.role),
      }));

      setTeams(normalized);
      setActiveTab("teams");
    } catch (e) {
      console.error("Ошибка загрузки команд:", e);
    } finally {
      setLoadingTeams(false);
    }
  };

  // ===== ОТПРАВКА ЗАЯВКИ В КОМАНДУ =====
  const applyToTeam = async (teamId: number) => {
    try {
      const me = await UserAPI.checkAuth();
      await TeamAPI.apply(Number(id), teamId, me.id);
      alert("Заявка отправлена!");
    } catch (e) {
      console.error("Ошибка заявки:", e);
      alert("Не удалось отправить заявку");
    }
  };

  return (
    <div className={styles.page + " " + styles.fadePage}>

      <div className={styles.headerCard + " " + styles.fadeBlock}>
        <h1 className={styles.title}>{hack.name}</h1>

        <div className={styles.tagRow}>
          {hack.tags?.split(",").map((t) => (
            <span key={t.trim()} className={styles.tag}>
              {t.trim()}
            </span>
          ))}
        </div>
      </div>

      <div className={styles.content}>
        <p className={styles.description + " " + styles.fadeText}>
          {hack.description}
        </p>

        {/* ОСНОВНЫЕ КНОПКИ */}
        <button className={styles.mainButton} onClick={handleFindTeam}>
          Найти команду
        </button>

        <button className={styles.secondaryButton} onClick={handleHaveTeam}>
          У меня есть команда
        </button>

        {/* ПЕРЕКЛЮЧАТЕЛИ */}
        <div className={styles.selectorRow}>
          <button
            className={
              activeTab === "participants"
                ? styles.selectorButtonActive
                : styles.selectorButton
            }
            onClick={loadParticipants}
          >
            Участники
          </button>

          <button
            className={
              activeTab === "teams"
                ? styles.selectorButtonActive
                : styles.selectorButton
            }
            onClick={loadTeams}
          >
            Команды
          </button>
        </div>

        {/* СПИСОК УЧАСТНИКОВ */}
        {activeTab === "participants" && (
          <div className={styles.participantList}>
            {loadingParticipants && <p className={styles.loading}>Загрузка участников...</p>}

            {!loadingParticipants && participants.length === 0 && (
              <p className={styles.empty}>Пока нет участников</p>
            )}

            {participants.map((p) => (
              <div key={p.id} className={styles.participantCard}>
                <h3 className={styles.participantName}>{p.name}</h3>
                <p className={styles.participantRole}>Роль: {p.role}</p>

                <button
                  className={styles.inviteButton}
                  onClick={() => inviteParticipant(p.id)}
                >
                  Пригласить в команду
                </button>
              </div>
            ))}
          </div>
        )}

        {/* СПИСОК КОМАНД */}
        {activeTab === "teams" && (
          <div className={styles.participantList}>
            {loadingTeams && <p className={styles.loading}>Загрузка команд...</p>}

            {!loadingTeams && teams.length === 0 && (
              <p className={styles.empty}>Пока нет команд</p>
            )}

            {teams.map((team) => (
              <div key={team.id} className={styles.participantCard}>
                <h3 className={styles.participantName}>{team.name}</h3>

                <p className={styles.participantRole}>
                  Ищут: {team.roles.join(", ")}
                </p>

                <button
                  className={styles.inviteButton}
                  onClick={() => applyToTeam(team.id)}
                >
                  Подать заявку
                </button>
              </div>
            ))}
          </div>
        )}

      </div>
    </div>
  );
};

export default HackDetailsPage;
