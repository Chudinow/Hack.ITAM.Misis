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
    const { data } = await apiInstance.get<HackListResponse>("/api/hack/all");
    return data;
  },

  getUpcoming: async (): Promise<HackListResponse> => {
    const { data } = await apiInstance.get<HackListResponse>("/api/hack/upcoming");
    return data;
  },

  getById: async (hackId: number | string): Promise<Hack> => {
    const { data } = await apiInstance.get<Hack>(`/api/hack/${hackId}`);
    return data;
  }
};
