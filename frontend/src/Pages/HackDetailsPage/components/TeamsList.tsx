import React from "react";
import styles from "./hack-details-page.module.css";

interface Team {
  id: number;
  name: string;
  about: string;
  roles: string[];
}

interface Props {
  loading: boolean;
  teams: Team[];
  onApply: (teamId: number) => void;
}

const TeamsList: React.FC<Props> = ({ loading, teams, onApply }) => {
  if (loading) {
    return <p className={styles.loading}>Загрузка команд...</p>;
  }

  if (teams.length === 0) {
    return <p className={styles.empty}>Пока нет команд</p>;
  }

  return (
    <div className={styles.participantList}>
      {teams.map((team) => (
        <div key={team.id} className={styles.participantCard}>
          <h3 className={styles.participantName}>{team.name}</h3>

          <p className={styles.participantRole}>
            Ищут: {team.roles.join(", ")}
          </p>

          <button
            className={styles.inviteButton}
            onClick={() => onApply(team.id)}
          >
            Подать заявку
          </button>
        </div>
      ))}
    </div>
  );
};

export default TeamsList;
