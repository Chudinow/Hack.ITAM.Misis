import React from "react";
import styles from "./language-selector.module.css";

const langs = [
  "TS",
  "JS",
  "Python",
  "Go",
  "Rust",
  "C++",
  "Java",
  "Kotlin",
  "Swift",
  "PHP"
];

interface Props {
  selected: string[];
  setSelected: (v: string[]) => void;
}

const LanguageSelector: React.FC<Props> = ({ selected, setSelected }) => {
  const toggleLang = (lang: string) => {
    if (selected.includes(lang)) {
      setSelected(selected.filter((l) => l !== lang));
    } else {
      setSelected([...selected, lang]);
    }
  };

  return (
    <div className={styles.container}>
      {langs.map((lang) => (
        <button
          key={lang}
          className={`${styles.tag} ${
            selected.includes(lang) ? styles.active : ""
          }`}
          onClick={() => toggleLang(lang)}
        >
          {lang}
        </button>
      ))}
    </div>
  );
};

export default LanguageSelector;
