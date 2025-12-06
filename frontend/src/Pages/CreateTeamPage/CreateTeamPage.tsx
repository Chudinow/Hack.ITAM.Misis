import React, { useState } from "react";
import styles from "./create-team-page.module.css";
import { TeamAPI, TeamMemberCreate, TeamCreatePayload } from "../../Shared/api/TeamApi";
import { useNavigate, useSearchParams } from "react-router-dom";

const CreateTeamPage: React.FC = () => {
  const navigate = useNavigate();
  const [params] = useSearchParams();

  const initialHackId = Number(params.get("hackId")) || 0;

  const [teamName, setTeamName] = useState("");
  const [hackId, setHackId] = useState<number>(initialHackId);

  const [members, setMembers] = useState<TeamMemberCreate[]>([
    { user_id: 0, role: "" },
  ]);

  const [isCompleted, setIsCompleted] = useState(false);
  const [loading, setLoading] = useState(false);

  // ------------------------------
  // SAFE UPDATE MEMBER
  // ------------------------------

  const updateMember = <K extends keyof TeamMemberCreate>(
    index: number,
    key: K,
    value: TeamMemberCreate[K]
  ) => {
    setMembers((prev) =>
      prev.map((m, i) =>
        i === index ? { ...m, [key]: value } : m
      )
    );
  };

  const addMember = () => {
    setMembers((prev) => [...prev, { user_id: 0, role: "" }]);
  };

  const removeMember = (index: number) => {
    setMembers((prev) => prev.filter((_, i) => i !== index));
  };

  // ------------------------------
  // CREATE TEAM
  // ------------------------------

  const handleCreateTeam = async () => {
    if (!teamName || !hackId) {
      alert("Введите название команды и ID хакатона");
      return;
    }

    const payload: TeamCreatePayload = {
      name: teamName,
      hackathon_id: hackId,
      member_ids: members,
      is_completed: isCompleted,
    };

    try {
      setLoading(true);

      await TeamAPI.createTeam(hackId, payload);

      alert("Команда создана!");
      navigate(`/hackdetails?id=${hackId}`);
    } catch (err) {
      console.error(err);
      alert("Ошибка создания команды");
    } finally {
      setLoading(false);
    }
  };

  // ------------------------------
  // RENDER
  // ------------------------------

  return (
    <div className={styles.wrapper}>
      <h1 className={styles.title}>Создание команды</h1>

      <div className={styles.block}>
        <label>Название команды:</label>
        <input
          className={styles.input}
          value={teamName}
          onChange={(e) => setTeamName(e.target.value)}
        />
      </div>

      <div className={styles.block}>
        <label>ID хакатона:</label>
        <input
          className={styles.input}
          type="number"
          value={hackId}
          onChange={(e) => setHackId(Number(e.target.value))}
        />
      </div>

      <h2 className={styles.subtitle}>Участники</h2>

      {members.map((member, index) => (
        <div key={index} className={styles.memberRow}>
          <input
            className={styles.inputSmall}
            type="number"
            placeholder="user_id"
            value={member.user_id}
            onChange={(e) =>
              updateMember(index, "user_id", Number(e.target.value))
            }
          />

          <input
            className={styles.inputSmall}
            placeholder="роль (frontend / backend / design)"
            value={member.role}
            onChange={(e) =>
              updateMember(index, "role", e.target.value)
            }
          />

          {members.length > 1 && (
            <button
              className={styles.removeBtn}
              onClick={() => removeMember(index)}
            >
              ×
            </button>
          )}
        </div>
      ))}

      <button className={styles.addMemberBtn} onClick={addMember}>
        + добавить участника
      </button>

      <div className={styles.checkboxRow}>
        <input
          type="checkbox"
          checked={isCompleted}
          onChange={() => setIsCompleted((prev) => !prev)}
        />
        <span>команда завершена</span>
      </div>

      <button
        className={styles.createBtn}
        onClick={handleCreateTeam}
        disabled={loading}
      >
        {loading ? "Создание..." : "Создать команду"}
      </button>
    </div>
  );
};

export default CreateTeamPage;
