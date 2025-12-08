import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import { Hack, HackAPI } from "../../Shared/api/HackApi";
import { TeamAPI } from "../../Shared/api/TeamApi";
import { UserAPI } from "../../Shared/api/UserApi";

import ParticipantsList from "./components/ParticipantsList";
import TeamsList from "./components/TeamsList";

import styles from "./hack-details-page.module.css";

// ==== Фильтры ролей ====
const ROLE_FILTERS = [
  "all",
  "frontend",
  "backend",
  "mobile",
  "ml",
  "product",
  "designer",
] as const;

type FilterRole = (typeof ROLE_FILTERS)[number];

const HackDetailsPage: React.FC = () => {
  const navigate = useNavigate();
  const { id } = useParams();

  const [hack, setHack] = useState<Hack | null>(null);

  const [activeTab, setActiveTab] =
    useState<"participants" | "teams" | null>(null);

  const [loadingHack, setLoadingHack] = useState(true);

  // Участники
  const [participants, setParticipants] = useState<any[]>([]);
  const [loadingParticipants, setLoadingParticipants] = useState(false);

  // Команды
  const [teams, setTeams] = useState<any[]>([]);
  const [loadingTeams, setLoadingTeams] = useState(false);

  // Фильтр
  const [roleFilter, setRoleFilter] = useState<FilterRole>("all");

  // ==== Загрузка хакатона ====
  useEffect(() => {
    async function load() {
      try {
        if (!id) return;
        const data = await HackAPI.getById(id);
        setHack(data);
      } catch (e) {
        console.error("Ошибка загрузки хакатона:", e);
      } finally {
        setLoadingHack(false);
      }
    }

    load();
  }, [id]);

  if (loadingHack) return <div className={styles.loading}>Загрузка...</div>;
  if (!hack) return <div className={styles.loading}>Хакатон не найден</div>;

  // Навигация
  const handleFindTeam = () =>
    navigate(`/hackdetails/${id}/participant-form`);

  const handleHaveTeam = () =>
    navigate(`/hackdetails/${id}/team-form`);

  // ==== Участники ====
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

  const filteredParticipants =
    roleFilter === "all"
      ? participants
      : participants.filter((p) => p.role === roleFilter);

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

  // ==== Команды ====
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
      {/* HEADER */}
      <div className={styles.headerCard + " " + styles.fadeBlock}>
        <h1 className={styles.title}>{hack.name}</h1>

        <div className={styles.tagRow}>
          {(hack.tags ?? "")
            .split(",")
            .map((t) => t.trim())
            .filter(Boolean)
            .map((tag: string) => (
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

        {/* Основные кнопки */}
        <button className={styles.mainButton} onClick={handleFindTeam}>
          Найти команду
        </button>

        <button className={styles.secondaryButton} onClick={handleHaveTeam}>
          У меня есть команда
        </button>

        {/* Табы */}
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

        {/* Фильтр ролей (только для участников) */}
        {activeTab === "participants" && (
          <div className={styles.filterRow}>
            {ROLE_FILTERS.map((role) => (
              <div
                key={role}
                className={
                  roleFilter === role
                    ? styles.filterChipActive
                    : styles.filterChip
                }
                onClick={() => setRoleFilter(role)}
              >
                {role === "all" ? "Все" : role}
              </div>
            ))}
          </div>
        )}

        {/* Список участников */}
        {activeTab === "participants" && (
          <ParticipantsList
            loading={loadingParticipants}
            participants={filteredParticipants}
            onInvite={inviteParticipant}
          />
        )}

        {/* Список команд */}
        {activeTab === "teams" && (
          <TeamsList
            loading={loadingTeams}
            teams={teams}
            onApply={applyToTeam}
          />
        )}
      </div>
    </div>
  );
};

export default HackDetailsPage;
