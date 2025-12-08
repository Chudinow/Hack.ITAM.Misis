// src/pages/organizer/OrganizeCreateHackPage.tsx
import React, { useState, useEffect } from "react";
import styles from "./organize-create-hack-page.module.css";
import { useNavigate, useParams } from "react-router-dom";
import {
  OrganizerApi,
  HackathonResponse,
  ParticipantResponse,
  TeamOrgResponse,
  AnalyticsResponse,
} from "../../Shared/api/OrganizerApi";

const OrganizeCreateHackPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [_, setHack] = useState<HackathonResponse | null>(null);

  const [form, setForm] = useState({
    name: "",
    description: "",
    start_date: "",
    end_date: "",
    tags: "",
    max_teams: 20,
    min_team_size: 2,
    max_team_size: 5,
  });

  const [photo, setPhoto] = useState<File | null>(null);
  const [loading, setLoading] = useState(true);

  const [teams, setTeams] = useState<TeamOrgResponse[]>([]);
  const [participants, setParticipants] = useState<ParticipantResponse[]>([]);
  const [analytics, setAnalytics] = useState<AnalyticsResponse | null>(null);

  const [loadingTeams, setLoadingTeams] = useState(false);
  const [loadingParticipants, setLoadingParticipants] = useState(false);
  const [loadingAnalytics, setLoadingAnalytics] = useState(false);
  const [exporting, setExporting] = useState(false);

  useEffect(() => {
    async function load() {
      if (!id) {
        setLoading(false);
        return;
      }

      try {
        const hackData = await OrganizerApi.getHackathonById(id);
        setHack(hackData);

        setForm({
          name: hackData.name,
          description: hackData.description ?? "",
          start_date: hackData.start_date,
          end_date: hackData.end_date,
          tags: hackData.tags ?? "",
          max_teams: hackData.max_teams ?? 20,
          min_team_size: hackData.min_team_size ?? 2,
          max_team_size: hackData.max_team_size ?? 5,
        });

        // параллельно можно подтянуть команды / участников
        loadTeams(hackData.id);
        loadParticipants(hackData.id);
      } catch (e) {
        console.error("Ошибка загрузки хакатона:", e);
      } finally {
        setLoading(false);
      }
    }

    load();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [id]);

  const handleChange = (key: string, value: string | number) => {
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const saveHackathon = async () => {
    try {
      let hackId = id;

      if (!id) {
        // создаём
        const created = await OrganizerApi.createHackathon({
          name: form.name,
          description: form.description,
          start_date: form.start_date,
          end_date: form.end_date,
          tags: form.tags,
          max_teams: form.max_teams,
          min_team_size: form.min_team_size,
          max_team_size: form.max_team_size,
        });
        hackId = String(created.id);
      } else {
        // обновляем
        await OrganizerApi.updateHackathon(id, {
          name: form.name,
          description: form.description,
          start_date: form.start_date,
          end_date: form.end_date,
          tags: form.tags,
          max_teams: form.max_teams,
          min_team_size: form.min_team_size,
          max_team_size: form.max_team_size,
        });
      }

      if (photo && hackId) {
        await OrganizerApi.uploadPhoto(hackId, photo);
      }

      navigate("/organizer/hacks");
    } catch (e) {
      console.error("Ошибка сохранения:", e);
      alert("Ошибка сохранения");
    }
  };

  const loadTeams = async (hackathonId: number | string) => {
    setLoadingTeams(true);
    try {
      const res = await OrganizerApi.getHackathonTeams(hackathonId);
      setTeams(res);
    } catch (e) {
      console.error("Ошибка загрузки команд:", e);
    } finally {
      setLoadingTeams(false);
    }
  };

  const loadParticipants = async (hackathonId: number | string) => {
    setLoadingParticipants(true);
    try {
      const res = await OrganizerApi.getHackathonParticipants(hackathonId);
      setParticipants(res);
    } catch (e) {
      console.error("Ошибка загрузки участников:", e);
    } finally {
      setLoadingParticipants(false);
    }
  };

  const loadAnalytics = async () => {
    if (!id) return;
    setLoadingAnalytics(true);
    try {
      const data = await OrganizerApi.getAnalytics(id);
      setAnalytics(data);
    } catch (e) {
      console.error("Ошибка загрузки аналитики:", e);
    } finally {
      setLoadingAnalytics(false);
    }
  };

  const exportCsv = async () => {
    if (!id) return;
    setExporting(true);
    try {
      const blob = await OrganizerApi.exportTeamsCsv(id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `hackathon_${id}_teams.csv`;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (e) {
      console.error("Ошибка экспорта CSV:", e);
      alert("Не удалось экспортировать CSV");
    } finally {
      setExporting(false);
    }
  };

  const approveTeam = async (teamId: number, approve: boolean) => {
    if (!id) return;
    try {
      await OrganizerApi.approveTeam(id, teamId, approve);
      await loadTeams(id);
    } catch (e) {
      console.error("Ошибка смены статуса команды:", e);
      alert("Не удалось изменить статус команды");
    }
  };

  const assignParticipant = async (userId: number) => {
    if (!id) return;

    const teamIdStr = window.prompt("ID команды, в которую добавить участника:");
    if (!teamIdStr) return;

    const teamId = Number(teamIdStr);
    if (Number.isNaN(teamId)) {
      alert("Некорректный ID команды");
      return;
    }

    const role = window.prompt("Роль участника в команде:") || "";
    if (!role.trim()) {
      alert("Роль не может быть пустой");
      return;
    }

    try {
      await OrganizerApi.assignParticipant(id, userId, teamId, role.trim());
      await loadParticipants(id);
      await loadTeams(id);
    } catch (e) {
      console.error("Ошибка назначения участника:", e);
      alert("Не удалось назначить участника");
    }
  };

  if (loading) return <div className={styles.loading}>Загрузка...</div>;

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>
        {id ? "Редактирование хакатона" : "Создание хакатона"}
      </h1>

      {/* Форма хакатона */}
      <div className={styles.form}>
        <div className={styles.left}>
          <label>Название:</label>
          <input
            type="text"
            value={form.name}
            onChange={(e) => handleChange("name", e.target.value)}
          />

          <label>Описание:</label>
          <textarea
            value={form.description}
            onChange={(e) => handleChange("description", e.target.value)}
          />

          <label>Теги (через запятую):</label>
          <input
            type="text"
            value={form.tags}
            onChange={(e) => handleChange("tags", e.target.value)}
          />
        </div>

        <div className={styles.right}>
          <label>Фото:</label>
          <input
            type="file"
            onChange={(e) =>
              setPhoto(e.target.files && e.target.files[0]
                ? e.target.files[0]
                : null)
            }
          />

          <label>Дата начала:</label>
          <input
            type="date"
            value={form.start_date}
            onChange={(e) => handleChange("start_date", e.target.value)}
          />

          <label>Дата конца:</label>
          <input
            type="date"
            value={form.end_date}
            onChange={(e) => handleChange("end_date", e.target.value)}
          />

          <label>Макс. команд:</label>
          <input
            type="number"
            value={form.max_teams}
            onChange={(e) =>
              handleChange("max_teams", Number(e.target.value) || 0)
            }
          />

          <label>Мин. размер команды:</label>
          <input
            type="number"
            value={form.min_team_size}
            onChange={(e) =>
              handleChange("min_team_size", Number(e.target.value) || 0)
            }
          />

          <label>Макс. размер команды:</label>
          <input
            type="number"
            value={form.max_team_size}
            onChange={(e) =>
              handleChange("max_team_size", Number(e.target.value) || 0)
            }
          />

          <button className={styles.save} onClick={saveHackathon}>
            Сохранить изменения
          </button>
        </div>
      </div>

      {/* Блок управления / аналитики */}
      {id && (
        <div className={styles.toolbar}>
          <button onClick={() => loadTeams(id!)} disabled={loadingTeams}>
            Обновить команды
          </button>
          <button
            onClick={() => loadParticipants(id!)}
            disabled={loadingParticipants}
          >
            Обновить участников
          </button>
          <button onClick={loadAnalytics} disabled={loadingAnalytics}>
            Аналитика
          </button>
          <button onClick={exportCsv} disabled={exporting}>
            Экспорт CSV
          </button>
        </div>
      )}

      {/* Аналитика */}
      {analytics && (
        <div className={styles.analyticsBlock}>
          <h2>Аналитика</h2>
          <p>Команд: {analytics.total_teams}</p>
          <p>Одобренных команд: {analytics.approved_teams}</p>
          <p>Участников: {analytics.total_participants}</p>
          <p>С командами: {analytics.participants_with_team}</p>
          <p>Без команды: {analytics.participants_without_team}</p>
        </div>
      )}

      {/* Список команд */}
      {id && (
        <div className={styles.teamsSection}>
          <h2>Команды</h2>

          {loadingTeams && <div>Загрузка команд...</div>}

          {!loadingTeams && teams.length === 0 && (
            <div>Пока нет команд</div>
          )}

          <div className={styles.teamGrid}>
            {teams.map((team) => (
              <div key={team.id} className={styles.teamCard}>
                <div className={styles.teamHeader}>
                  <h3>{team.name}</h3>
                  <span>
                    {team.approved ? "Одобрена" : "Ожидает одобрения"}
                  </span>
                </div>

                <div className={styles.teamMembers}>
                  {team.members.map((m) => (
                    <div key={m.user_id} className={styles.memberRow}>
                      <span>{m.name}</span>
                      <span>{m.role ?? "без роли"}</span>
                      <span>{m.approved ? "✓" : "✗"}</span>
                    </div>
                  ))}
                </div>

                <div className={styles.teamActions}>
                  <button onClick={() => approveTeam(team.id, true)}>
                    Одобрить
                  </button>
                  <button onClick={() => approveTeam(team.id, false)}>
                    Отклонить
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Список участников */}
      {id && (
        <div className={styles.participantsSection}>
          <h2>Участники</h2>

          {loadingParticipants && <div>Загрузка участников...</div>}

          {!loadingParticipants && participants.length === 0 && (
            <div>Пока нет участников</div>
          )}

          <div className={styles.participantGrid}>
            {participants.map((p) => (
              <div key={p.user_id} className={styles.participantCard}>
                <div className={styles.participantHeader}>
                  <span className={styles.participantName}>{p.name}</span>
                  {p.has_team && (
                    <span className={styles.participantTeam}>
                      В команде: {p.team_name}
                    </span>
                  )}
                </div>
                <div className={styles.participantRole}>
                  Роль: {p.role ?? "не указана"}
                </div>
                <div className={styles.participantSkills}>
                  {p.skills && p.skills.length > 0
                    ? p.skills.join(", ")
                    : "Навыки не указаны"}
                </div>
                <button
                  className={styles.assignButton}
                  onClick={() => assignParticipant(p.user_id)}
                >
                  Assign в команду
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default OrganizeCreateHackPage;
