import api from "./client";

export interface ChatRequest {
    message: string;
    character_id: number;
    conversation_history: Array<{ role: "user" | "assistant"; content: string }>;
}

export interface ChatResponse {
    response: string;
}

export const sendChatMessage = async (payload: ChatRequest): Promise<ChatResponse> => {
    const { data } = await api.post<ChatResponse>("/api/chat", payload);
    return data;
};

