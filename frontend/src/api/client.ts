import axios from "axios";

// Log da URL da API para debug (sempre, para ajudar no troubleshooting)
const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:7000";
console.log("🔗 API URL configurada:", apiUrl);

const api = axios.create({
    baseURL: apiUrl,
    headers: {
        "Content-Type": "application/json",
    },
    timeout: 30000, // 30 segundos de timeout (aumentado para requisições mais lentas)
});

// Interceptor para log de requisições e erros
api.interceptors.request.use(
    (config) => {
        console.log("📤 Requisição:", {
            method: config.method?.toUpperCase(),
            url: config.url,
            fullURL: `${config.baseURL}${config.url}`,
        });
        return config;
    },
    (error) => {
        console.error("❌ Erro na requisição:", error);
        return Promise.reject(error);
    }
);

api.interceptors.response.use(
    (response) => {
        console.log("✅ Resposta:", {
            status: response.status,
            url: response.config.url,
        });
        return response;
    },
    (error) => {
        const errorInfo = {
            message: error.message,
            status: error.response?.status,
            statusText: error.response?.statusText,
            url: error.config?.url,
            baseURL: error.config?.baseURL,
            fullURL: error.config ? `${error.config.baseURL}${error.config.url}` : "N/A",
            responseData: error.response?.data,
        };
        console.error("❌ Erro na API:", errorInfo);
        
        // Se for 502, adiciona informação extra
        if (error.response?.status === 502) {
            console.error("🔴 Erro 502 Bad Gateway - Possíveis causas:");
            console.error("   1. Backend não está acessível na URL:", apiUrl);
            console.error("   2. Problema de CORS (verifique ALLOWED_ORIGINS no backend)");
            console.error("   3. Backend está retornando erro 502");
            console.error("   Teste a URL diretamente:", `${apiUrl}/health`);
        }
        
        return Promise.reject(error);
    }
);

export default api;


