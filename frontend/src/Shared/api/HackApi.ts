//крч это тестовые данные потом удалим
const MOCK = true; 

const mockHacks: Hack[] = [
  {
    id: 1,
    name: "ITAM.courses Hack",
    description: "Тестовый хакатон",
    photo_url: "https://picsum.photos/600/300?random=1",
    start_date: "2025-01-10",
    end_date: "2025-01-12",
    tags: "онлайн,активно,fullstack",
  },
  {
    id: 2,
    name: "Tula HackDays",
    description: "Пример хакатона",
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
      return mockHacks[0];
    }
    const { data } = await apiInstance.get<Hack>(`/api/hack/${hackId}`);
    return data;
  }
};
