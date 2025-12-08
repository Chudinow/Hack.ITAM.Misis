import React from "react";
import styles from "../hack-details-page.module.css";

interface Participant {
  id: number;
  name: string;
  role: string;
  skills: any[];
}

interface Props {
  loading: boolean;
  participants: Participant[];
  onInvite: (id: number) => void;
}

const ParticipantsList: React.FC<Props> = ({
  loading,
  participants,
  onInvite,
}) => {
  if (loading) {
    return <p className={styles.loading}>Загрузка участников...</p>;
  }

  if (participants.length === 0) {
    return <p className={styles.empty}>Нет результатов</p>;
  }

  return (
    <div className={styles.participantList}>
      {participants.map((p) => (
        <div key={p.id} className={styles.participantCard}>
          <h3 className={styles.participantName}>{p.name}</h3>
          <p className={styles.participantRole}>Роль: {p.role}</p>

          <button
            className={styles.inviteButton}
            onClick={() => onInvite(p.id)}
          >
            Пригласить в команду
          </button>
        </div>
      ))}
    </div>
  );
};

export default ParticipantsList;
