import React from "react";
import styles from "./role-selector.module.css";

const roles = ["Frontend", "BackEnd", "Designer", "ML", "GameDev", "Mobile"];

interface Props {
  selected: string[];
  setSelected: (v: string[]) => void;
}

const RoleSelector: React.FC<Props> = ({ selected, setSelected }) => {
  const toggleRole = (role: string) => {
    if (selected.includes(role)) {
      setSelected(selected.filter((r) => r !== role));
    } else {
      setSelected([...selected, role]);
    }
  };

  return (
    <div className={styles.container}>
      {roles.map((role) => (
        <button
          key={role}
          className={`${styles.button} ${
            selected.includes(role) ? styles.active : ""
          }`}
          onClick={() => toggleRole(role)}
        >
          {role}
        </button>
      ))}
    </div>
  );
};

export default RoleSelector;
