import axios from "axios";

// Log da URL da API para debug (sempre, para ajudar no troubleshooting)
const apiUrl = import.meta.env.VITE_API_URL ?? "http://localhost:7000";
console.log("🔗 API URL configurada:", apiUrl);

const api = axios.create({
    baseURL: apiUrl,
    headers: {
        "Content-Type": "application/json",
    },
    timeout: 120000, // 120 segundos (2 minutos) - necessário para requisições da OpenAI que podem demorar
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
        
        // Diagnóstico de erros comuns
        if (error.code === "ECONNABORTED" || error.message.includes("timeout")) {
            console.error("🔴 Timeout - A requisição demorou muito para responder:");
            console.error("   Isso é normal para requisições da OpenAI que podem demorar até 2 minutos");
            console.error("   O timeout foi aumentado para 120 segundos");
            console.error("   Se o problema persistir, verifique os logs do backend");
        } else if (error.message === "Network Error" || !error.response) {
            console.error("🔴 Network Error - Possíveis causas:");
            console.error("   1. Backend não está acessível ou offline");
            console.error("   2. Problema de CORS (verifique ALLOWED_ORIGINS no backend)");
            console.error("   3. Timeout na requisição");
            console.error("   4. Problema de conectividade");
            console.error("   Teste a URL diretamente no navegador:", `${apiUrl}/health`);
            console.error("   Verifique se ALLOWED_ORIGINS inclui:", window.location.origin);
        } else if (error.response?.status === 502) {
            console.error("🔴 Erro 502 Bad Gateway - Possíveis causas:");
            console.error("   1. Backend não está acessível na URL:", apiUrl);
            console.error("   2. Problema de CORS (verifique ALLOWED_ORIGINS no backend)");
            console.error("   3. Backend está retornando erro 502");
            console.error("   Teste a URL diretamente:", `${apiUrl}/health`);
        } else if (error.response?.status === 0 || error.code === "ERR_NETWORK") {
            console.error("🔴 Erro de rede - Backend não está respondendo");
            console.error("   Verifique se o backend está rodando e acessível");
        }
        
        return Promise.reject(error);
    }
);

export default api;


