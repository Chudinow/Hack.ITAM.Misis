import axios from "axios";

export const apiInstance = axios.create({
  baseURL: import.meta.env.VITE_API_URL, // обязательно читать из .env
  withCredentials: true,                 // обязательно для cookie JWT
  headers: {
    "Content-Type": "application/json",
  },
});

/**
 * Глобальный обработчик ошибок
 * Он не ломает THEN/CATCH и не поглощает ошибку
 */
apiInstance.interceptors.response.use(
  (response) => response,
  (error) => {
    // Простой вывод для отладки
    console.error("API error:", error);

    // Пробрасываем ошибку дальше → попадёт в catch()
    return Promise.reject(error);
  }
);

