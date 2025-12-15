import axios from "axios";

// Log da URL da API para debug (apenas em desenvolvimento)
if (import.meta.env.DEV) {
    console.log("🔗 API URL:", import.meta.env.VITE_API_URL ?? "http://localhost:7000");
}

const api = axios.create({
    baseURL: import.meta.env.VITE_API_URL ?? "http://localhost:7000",
    headers: {
        "Content-Type": "application/json",
    },
    timeout: 30000, // 30 segundos de timeout (aumentado para requisições mais lentas)
});

// Interceptor para log de erros
api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error("❌ Erro na API:", {
            message: error.message,
            status: error.response?.status,
            statusText: error.response?.statusText,
            url: error.config?.url,
            baseURL: error.config?.baseURL,
        });
        return Promise.reject(error);
    }
);

export default api;


