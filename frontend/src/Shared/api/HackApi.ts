//крч это тестовые данные потом удалим
const MOCK = true; 

const mockHacks: Hack[] = [
  {
    id: 1,
    name: "ITAM.courses Hack",
    description: "Это не просто соревнование — это 48 часов чистого креатива, кофеина и коллаборации. Мы стираем границы между битами и реальностью. Собери свою команду мечты или найди ее здесь, чтобы создать прототип, который перевернет представление о цифровом взаимодействии.",
    photo_url: "https://picsum.photos/600/300?random=1",
    start_date: "2025-01-10",
    end_date: "2025-01-12",
    tags: "онлайн,активно,fullstack",
  },
  {
    id: 2,
    name: "Tula HackDays",
    description: "DataHack 2024 — это 36-часовое соревнование, направленное на решение практических задач в области анализа больших данных и машинного обучения. Участникам предстоит работать с реальными датасетами, предоставленными компаниями-партнерами из финтех-сектора.",
    photo_url: "https://picsum.photos/600/300?random=2",
    start_date: "2025-02-05",
    end_date: "2025-02-06",
    tags: "офлайн,закрыто,frontend",
  }
];

import { apiInstance } from "./apiInstance";

export interface Hack {
  id: number;
  name: string;
  description: string;
  photo_url: string;
  start_date: string; 
  end_date: string;  
  tags: string;
}

export interface HackListResponse {
  hacks: Hack[];
  meta: {
    total: number;
    page: number;
    per_page: number;
    total_pages: number;
  };
}

export const HackAPI = {

  getAll: async (): Promise<HackListResponse> => {
    if (MOCK) {
    return {
        hacks: mockHacks,
        meta: { total: 2, page: 1, per_page: 10, total_pages: 1 }
      };
    }
    const { data } = await apiInstance.get<HackListResponse>("/api/hack/all");
    return data;
  },

  getUpcoming: async (): Promise<HackListResponse> => {
    if (MOCK) {
    return {
        hacks: mockHacks,
        meta: { total: 2, page: 1, per_page: 10, total_pages: 1 }
      };
    }
    const { data } = await apiInstance.get<HackListResponse>("/api/hack/upcoming");
    return data;
  },

  getById: async (hackId: number | string): Promise<Hack> => {
    if (MOCK) {
      return mockHacks.find(h => h.id === Number(hackId))!;
    }
    const { data } = await apiInstance.get<Hack>(`/api/hack/${hackId}`);
    return data;
  }
};
