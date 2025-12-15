import { useState, useEffect, useRef } from "react";
import { useQuery } from "@tanstack/react-query";
import { fetchCharacters, fetchCharacter } from "../api/characters";
import { sendChatMessage } from "../api/chat";
import { MessageContent } from "../components/MessageContent";
import "./ChatPage.css";

const LAST_CHARACTER_KEY = "last_character_id";

interface ChatPageProps {
    onNavigateToCharacters: () => void;
}

export function ChatPage({ onNavigateToCharacters }: ChatPageProps) {
    const [selectedCharacterId, setSelectedCharacterId] = useState<number | null>(null);
    const [message, setMessage] = useState("");
    const [conversation, setConversation] = useState<Array<{ role: "user" | "assistant"; content: string }>>([]);
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef<HTMLDivElement>(null);
    const [showCharacterSelect, setShowCharacterSelect] = useState(false);

    const charactersQuery = useQuery({
        queryKey: ["characters"],
        queryFn: fetchCharacters,
    });

    const selectedCharacterQuery = useQuery({
        queryKey: ["character", selectedCharacterId],
        queryFn: () => fetchCharacter(selectedCharacterId!),
        enabled: !!selectedCharacterId,
    });

    // Carrega o último personagem usado ou o primeiro disponível
    useEffect(() => {
        if (charactersQuery.data && charactersQuery.data.length > 0) {
            const lastId = localStorage.getItem(LAST_CHARACTER_KEY);
            const lastIdNum = lastId ? parseInt(lastId, 10) : null;
            
            // Verifica se o último personagem ainda existe
            const lastCharacter = lastIdNum 
                ? charactersQuery.data.find(c => c.id === lastIdNum)
                : null;
            
            const characterToUse = lastCharacter || charactersQuery.data[0];
            setSelectedCharacterId(characterToUse.id);
        }
    }, [charactersQuery.data]);

    // Scroll automático para a última mensagem
    useEffect(() => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [conversation]);

    const handleSendMessage = async () => {
        if (!message.trim() || !selectedCharacterId || isLoading) return;

        const userMessage = message.trim();
        setMessage("");
        setIsLoading(true);

        // Adiciona mensagem do usuário
        const newConversation = [...conversation, { role: "user" as const, content: userMessage }];
        setConversation(newConversation);

        try {
            const response = await sendChatMessage({
                message: userMessage,
                character_id: selectedCharacterId,
                conversation_history: conversation,
            });

            // Adiciona resposta do assistente
            setConversation([
                ...newConversation,
                { role: "assistant" as const, content: response.response },
            ]);
        } catch (error: any) {
            console.error("Erro ao enviar mensagem:", error);
            
            // Extrai mensagem de erro mais detalhada
            let errorMessage = "❌ Erro ao processar sua mensagem. Tente novamente.";
            
            if (error?.response?.data?.detail) {
                // Erro do backend com detalhes
                errorMessage = `❌ Erro: ${error.response.data.detail}`;
            } else if (error?.response?.status === 500) {
                errorMessage = "❌ Erro interno do servidor. Verifique os logs do backend.";
            } else if (error?.response?.status === 404) {
                errorMessage = "❌ Personagem não encontrado.";
            } else if (error?.message) {
                errorMessage = `❌ Erro: ${error.message}`;
            }
            
            setConversation([
                ...newConversation,
                {
                    role: "assistant" as const,
                    content: errorMessage,
                },
            ]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleCharacterChange = (characterId: number) => {
        setSelectedCharacterId(characterId);
        localStorage.setItem(LAST_CHARACTER_KEY, characterId.toString());
        setConversation([]); // Limpa a conversa ao trocar de personagem
        setShowCharacterSelect(false);
    };

    const character = selectedCharacterQuery.data;

    if (charactersQuery.isPending) {
        return (
            <div className="chat-page">
                <div className="chat-loading">Carregando personagens...</div>
            </div>
        );
    }

    if (charactersQuery.isError) {
        console.error("Erro ao carregar personagens:", charactersQuery.error);
        return (
            <div className="chat-page">
                <div className="chat-error">
                    <p>Erro ao carregar personagens.</p>
                    <p style={{ fontSize: "0.9rem", marginTop: "0.5rem" }}>
                        {charactersQuery.error instanceof Error 
                            ? charactersQuery.error.message 
                            : "Verifique se o backend está rodando em http://localhost:7000"}
                    </p>
                    <button
                        onClick={onNavigateToCharacters}
                        className="btn btn--primary"
                        style={{ marginTop: "1rem" }}
                    >
                        Gerenciar Personagens
                    </button>
                </div>
            </div>
        );
    }

    if (!charactersQuery.data || charactersQuery.data.length === 0) {
        return (
            <div className="chat-page">
                <div className="chat-error">
                    <p>Nenhum personagem disponível.</p>
                    <button
                        onClick={onNavigateToCharacters}
                        className="btn btn--primary"
                        style={{ marginTop: "1rem" }}
                    >
                        Criar Primeiro Personagem
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="chat-page">
            <header className="chat-header">
                <div className="chat-header__content">
                    <h1>💬 Chat dos Personagens</h1>
                    <div className="chat-header__actions">
                        {character && (
                            <div className="character-selector">
                                <button
                                    className="btn btn--secondary"
                                    onClick={() => setShowCharacterSelect(!showCharacterSelect)}
                                >
                                    {character.name} {showCharacterSelect ? "▲" : "▼"}
                                </button>
                                {showCharacterSelect && (
                                    <div className="character-dropdown">
                                        {charactersQuery.data.map((char) => (
                                            <button
                                                key={char.id}
                                                className={`character-option ${
                                                    char.id === selectedCharacterId ? "active" : ""
                                                }`}
                                                onClick={() => handleCharacterChange(char.id)}
                                            >
                                                {char.name}
                                            </button>
                                        ))}
                                    </div>
                                )}
                            </div>
                        )}
                        <button
                            onClick={onNavigateToCharacters}
                            className="btn btn--primary"
                        >
                            ⚙️ Gerenciar Personagens
                        </button>
                    </div>
                </div>
            </header>

            <div className="chat-container">
                <div className="chat-messages">
                    {conversation.length === 0 && character && (
                        <div className="chat-welcome">
                            <div className="chat-welcome__character">
                                {character.image_url && (
                                    <img
                                        src={character.image_url}
                                        alt={character.name}
                                        className="chat-welcome__image"
                                    />
                                )}
                                <h2>{character.name}</h2>
                                <p>{character.description}</p>
                            </div>
                            <p className="chat-welcome__hint">
                                Comece a conversar digitando uma mensagem abaixo!
                            </p>
                        </div>
                    )}

                    {conversation.map((msg, idx) => (
                        <div
                            key={idx}
                            className={`chat-message chat-message--${msg.role}`}
                        >
                            <div className="chat-message__content">
                                <MessageContent content={msg.content} role={msg.role} />
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="chat-message chat-message--assistant">
                            <div className="chat-message__content">
                                <span className="typing-indicator">●</span>
                                <span className="typing-indicator">●</span>
                                <span className="typing-indicator">●</span>
                            </div>
                        </div>
                    )}

                    <div ref={messagesEndRef} />
                </div>

                <form 
                    className="chat-input-container"
                    onSubmit={(e) => {
                        e.preventDefault();
                        handleSendMessage();
                    }}
                >
                    <input
                        type="text"
                        className="chat-input"
                        placeholder="Digite sua mensagem..."
                        value={message}
                        onChange={(e) => setMessage(e.target.value)}
                        onKeyDown={(e) => {
                            if (e.key === "Enter" && !e.shiftKey) {
                                e.preventDefault();
                                handleSendMessage();
                            }
                        }}
                        disabled={isLoading || !selectedCharacterId}
                    />
                    <button
                        type="submit"
                        className="btn btn--send"
                        disabled={isLoading || !message.trim() || !selectedCharacterId}
                    >
                        Enviar
                    </button>
                </form>
            </div>
        </div>
    );
}

