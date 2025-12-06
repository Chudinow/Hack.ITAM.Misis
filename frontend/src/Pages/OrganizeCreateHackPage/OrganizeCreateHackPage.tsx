import React, { useState, useEffect } from "react";
import styles from "./organize-create-hack-page.module.css";
import { useNavigate, useParams } from "react-router-dom";
import { OrganizerHackApi } from "../../Shared/api/OrganizerApi";

const OrganizeCreateHackPage: React.FC = () => {
  const { id } = useParams();
  const navigate = useNavigate();

  const [form, setForm] = useState({
    title: "",
    description: "",
    date_start: "",
    date_end: "",
  });

  const [photo, setPhoto] = useState<File | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function load() {
      if (!id) {
        setLoading(false);
        return;
      }

      try {
        const hack = await OrganizerHackApi.getHackathonById(id);

        setForm({
          title: hack.title,
          description: hack.description ?? "",
          date_start: hack.date_start,
          date_end: hack.date_end,
        });

      } catch (e) {
        console.error("Ошибка загрузки хакатона:", e);
      } finally {
        setLoading(false);
      }
    }

    load();
  }, [id]);

  const handleChange = (key: string, value: string) => {
    setForm({ ...form, [key]: value });
  };

  const save = async () => {
    try {
      let hackId = id;

      if (!id) {
        const created = await OrganizerHackApi.createHackathon({
          title: form.title,
          description: form.description,
          date_start: form.date_start,
          date_end: form.date_end,
        });
        hackId = created.id;
      } else {
        await OrganizerHackApi.updateHackathon(id, {
          title: form.title,
          description: form.description,
          date_start: form.date_start,
          date_end: form.date_end,
        });
      }

      if (photo && hackId) {
        await OrganizerHackApi.uploadPhoto(hackId, photo);
      }

      navigate("/organizer/hacks");
    } catch (e) {
      console.error("Ошибка сохранения:", e);
      alert("Ошибка сохранения");
    }
  };

  if (loading) return <div className={styles.loading}>Загрузка...</div>;

  return (
    <div className={styles.page}>
      <h1 className={styles.title}>
        {id ? "Редактирование хакатона" : "Создание хакатона"}
      </h1>

      <div className={styles.form}>
        <div className={styles.left}>
          <label>Название:</label>
          <input
            type="text"
            value={form.title}
            onChange={(e) => handleChange("title", e.target.value)}
          />

          <label>Описание:</label>
          <textarea
            value={form.description}
            onChange={(e) => handleChange("description", e.target.value)}
          />
        </div>

        <div className={styles.right}>
          <label>Фото:</label>
          <input type="file" onChange={(e) => setPhoto(e.target.files?.[0] ?? null)} />

          <label>Дата начала:</label>
          <input
            type="date"
            value={form.date_start}
            onChange={(e) => handleChange("date_start", e.target.value)}
          />

          <label>Дата конца:</label>
          <input
            type="date"
            value={form.date_end}
            onChange={(e) => handleChange("date_end", e.target.value)}
          />

          <button className={styles.save} onClick={save}>
            сохранить изменения
          </button>
        </div>
      </div>
    </div>
  );
};

export default OrganizeCreateHackPage;
