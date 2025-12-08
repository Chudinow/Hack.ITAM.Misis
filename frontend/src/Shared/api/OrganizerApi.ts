import { apiInstance } from "./apiInstance";

/* ===============================
      MOCK MODE
================================= */

const MOCK = true;

// Мок-данные
const MOCK_HACKS = [
  {
    id: "1",
    title: "ITAM HACK 2025",
    description: "Лучший хакатон по разработке EdTech",
    date_start: "2025-01-10",
    date_end: "2025-01-12",
    photo_url: "",
  },
  {
    id: "2",
    title: "Cyber Challenge",
    description: "Хакатон по кибербезопасности",
    date_start: "2025-02-05",
    date_end: "2025-02-06",
    photo_url: "",
  },
];

/* ===============================
      TYPES
================================= */

export interface OrganizerLoginRequest {
  email: string;
  password: string;
}

export interface OrganizerLoginResponse {
  access_token: string;
  organizer: { id: string; name: string };
}

export interface HackathonCreate {
  title: string;
  description?: string;
  date_start: string;
  date_end: string;
}

export interface HackathonUpdate {
  title?: string;
  description?: string;
  date_start?: string;
  date_end?: string;
}

export interface HackathonResponse {
  id: string;
  title: string;
  description?: string;
  date_start: string;
  date_end: string;
  photo_url?: string;
}

/* ===============================
      ORGANIZER API
================================= */

export const OrganizerApi = {
  login: async (data: OrganizerLoginRequest): Promise<OrganizerLoginResponse> => {
    if (MOCK) {
      // мок авторизации
      return {
        access_token: "MOCK_TOKEN",
        organizer: { id: "0", name: "Mock Admin" },
      };
    }

    const res = await apiInstance.post("/organizers/login", data);
    return res.data;
  },
};

/* ===============================
      HACKATHON API
================================= */

export const OrganizerHackApi = {
  getMyHackathons: async (): Promise<HackathonResponse[]> => {
    if (MOCK) return MOCK_HACKS;

    const res = await apiInstance.get("/organizer/hackathons");
    return res.data;
  },

  createHackathon: async (data: HackathonCreate): Promise<HackathonResponse> => {
    if (MOCK) {
      return {
        id: Date.now().toString(),
        photo_url: "",
        ...data,
      };
    }

    const res = await apiInstance.post("/organizer/hackathons", data);
    return res.data;
  },

  getHackathonById: async (id: string): Promise<HackathonResponse> => {
    if (MOCK) {
      return MOCK_HACKS.find((h) => h.id === id)!;
    }

    const res = await apiInstance.get(`/organizer/hackathons/${id}`);
    return res.data;
  },

  updateHackathon: async (id: string, data: HackathonUpdate) => {
  if (MOCK) {
    const original = MOCK_HACKS.find(h => h.id === id)!;

    return {
      ...original,
      ...data,       // обновляем только изменённые поля
      id,            // и явно указываем id только ОДИН раз
    };
  }

  const res = await apiInstance.patch(`/organizer/hackathons/${id}`, data);
  return res.data;
},

  uploadPhoto: async (id: string, file: File) => {
    if (MOCK) {
      const url = URL.createObjectURL(file);
      return { success: true, photo_url: url };
    }

    const form = new FormData();
    form.append("photo", file);

    const res = await apiInstance.post(
      `/organizer/hackathons/${id}/photo`,
      form,
      { headers: { "Content-Type": "multipart/form-data" } }
    );
    return res.data;
  },
};
