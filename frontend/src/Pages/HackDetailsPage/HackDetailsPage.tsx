import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { Hack, HackAPI } from "../../Shared/api/HackApi";
import { TeamAPI } from "../../Shared/api/TeamApi";
import { UserAPI } from "../../Shared/api/UserApi";
import styles from "./hack-details-page.module.css";

const HackDetailsPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams();

  const [hack, setHack] = useState<Hack | null>(null);

  const [activeTab, setActiveTab] =
    useState<"participants" | "teams" | null>(null);

  const [participants, setParticipants] = useState<any[]>([]);
  const [loadingParticipants, setLoadingParticipants] = useState(false);

  const [teams, setTeams] = useState<any[]>([]);
  const [loadingTeams, setLoadingTeams] = useState(false);

  const [loadingHack, setLoadingHack] = useState(true);

  // ===== ЗАГРУЗКА ХАКАТОНА =====
  useEffect(() => {
    async function loadHack() {
      try {
        if (!id) return;
        const data = await HackAPI.getById(id);
        setHack(data);
      } catch (error) {
        console.error("Ошибка загрузки хакатона:", error);
      } finally {
        setLoadingHack(false);
      }
    }

    loadHack();
  }, [id]);

  if (loadingHack) {
    return <div className={styles.loading}>Загрузка...</div>;
  }

  if (!hack) {
    return <div className={styles.loading}>Хакатон не найден</div>;
  }

  // ===== НАВИГАЦИЯ =====
  const handleFindTeam = () =>
    navigate(`/hackdetails/${id}/participant-form`);

  const handleHaveTeam = () =>
    navigate(`/hackdetails/${id}/team-form`);

  // ===== ЗАГРУЗКА УЧАСТНИКОВ =====
  const loadParticipants = async () => {
    if (!id) return;
    setLoadingParticipants(true);

    try {
      const res = await TeamAPI.searchParticipants(Number(id));
      
      const normalized = (res.participants ?? []).map((p: any) => ({
        id: p.id,
        name: p.profile?.user_id ?? "",
        role: p.profile?.role ?? "",
        skills: p.profile?.skills ?? [],
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
      const res = await TeamAPI.searchEmpty(Number(id));

      const normalized = res.map((t: any) => ({
        id: t.id,
        name: t.name,
        about: t.about,
        roles: t.empty_roles?.map((r: any) => r.role) ?? [],
      }));

      setTeams(normalized);
      setActiveTab("teams");
    } catch (e) {
      console.error("Ошибка загрузки команд:", e);
    } finally {
      setLoadingTeams(false);
    }
  };

  // ===== ОТПРАВКА ЗАЯВКИ =====
  const applyToTeam = async (teamId: number) => {
    try {
      const me = await UserAPI.checkAuth();
      await TeamAPI.apply(Number(id), teamId, me.id);
      alert("Заявка отправлена!");
    } catch (e) {
      console.error("Ошибка отправки заявки:", e);
      alert("Не удалось отправить заявку");
    }
  };

  return (
    <div className={styles.page + " " + styles.fadePage}>
      <div className={styles.headerCard + " " + styles.fadeBlock}>
        <h1 className={styles.title}>{hack.name}</h1>

        <div className={styles.tagRow}>
          {(hack.tags ?? "")
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean)
            .map((tag) => (
              <span key={tag} className={styles.tag}>
                {tag}
              </span>
            ))}
        </div>
      </div>

      <div className={styles.content}>
        <p className={styles.description + " " + styles.fadeText}>
          {hack.description}
        </p>

        {/* КНОПКИ */}
        <button className={styles.mainButton} onClick={handleFindTeam}>
          Найти команду
        </button>

        <button className={styles.secondaryButton} onClick={handleHaveTeam}>
          У меня есть команда
        </button>

        {/* ТАБЫ */}
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
            {loadingParticipants && (
              <p className={styles.loading}>Загрузка участников...</p>
            )}

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
            {loadingTeams && (
              <p className={styles.loading}>Загрузка команд...</p>
            )}

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
