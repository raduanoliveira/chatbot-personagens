import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import {
    createCharacter,
    deleteCharacter,
    fetchCharacters,
    updateCharacter,
} from "../api/characters";
import { CharacterForm } from "../components/CharacterForm";
import { CharacterCard } from "../components/CharacterCard";
import { ConfirmDialog } from "../components/ConfirmDialog";
import type { Character, CharacterPayload } from "../types/character";

type ToastState = { type: "success" | "error"; message: string } | null;

interface CharactersPageProps {
    onNavigateToChat: () => void;
}

export function CharactersPage({ onNavigateToChat }: CharactersPageProps) {
    const queryClient = useQueryClient();
    const [selected, setSelected] = useState<Character | null>(null);
    const [toast, setToast] = useState<ToastState>(null);
    const [deleteConfirm, setDeleteConfirm] = useState<Character | null>(null);
    const [showForm, setShowForm] = useState(false);

    const charactersQuery = useQuery({
        queryKey: ["characters"],
        queryFn: fetchCharacters,
    });

    const createMutation = useMutation({
        mutationFn: (payload: CharacterPayload) => createCharacter(payload),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["characters"] });
            setToast({ type: "success", message: "Personagem criado com sucesso!" });
            // Limpa campos e fecha formulário
            setSelected(null);
            setShowForm(false);
            // Scroll para o topo
            window.scrollTo({ top: 0, behavior: "smooth" });
        },
        onError: () => {
            setToast({ type: "error", message: "Erro ao criar personagem." });
        },
    });

    const updateMutation = useMutation({
        mutationFn: ({ id, payload }: { id: number; payload: CharacterPayload }) =>
            updateCharacter(id, payload),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["characters"] });
            setToast({ type: "success", message: "Personagem atualizado!" });
        },
        onError: () => {
            setToast({ type: "error", message: "Erro ao atualizar personagem." });
        },
    });

    const deleteMutation = useMutation({
        mutationFn: (id: number) => deleteCharacter(id),
        onSuccess: () => {
            queryClient.invalidateQueries({ queryKey: ["characters"] });
            setToast({ type: "success", message: "Personagem removido." });
        },
        onError: () => {
            setToast({ type: "error", message: "Erro ao remover personagem." });
        },
    });

    const handleSubmit = (payload: CharacterPayload, id?: number) => {
        if (id) {
            updateMutation.mutate({ id, payload });
            // Para edição, também fecha o formulário e faz scroll
            setSelected(null);
            setShowForm(false);
            window.scrollTo({ top: 0, behavior: "smooth" });
        } else {
            createMutation.mutate(payload);
            // Para criação, o onSuccess já faz tudo
        }
    };

    const handleDelete = (character: Character) => {
        setDeleteConfirm(character);
    };

    const confirmDelete = () => {
        if (deleteConfirm) {
            deleteMutation.mutate(deleteConfirm.id);
            if (selected?.id === deleteConfirm.id) {
                setSelected(null);
            }
            setDeleteConfirm(null);
        }
    };

    const cancelDelete = () => {
        setDeleteConfirm(null);
    };

    const isMutating = createMutation.isPending || updateMutation.isPending;

    // Auto-dismiss toast após 3 segundos
    useEffect(() => {
        if (toast) {
            const timer = setTimeout(() => {
                setToast(null);
            }, 3000);
            return () => clearTimeout(timer);
        }
    }, [toast]);

    return (
        <>
            {toast && createPortal(
                <div 
                    className={`toast toast--${toast.type}`} 
                    onClick={() => setToast(null)}
                    style={{
                        position: "fixed",
                        top: "1rem",
                        right: "1rem",
                        zIndex: 9999,
                        cursor: "pointer",
                        boxShadow: "0 4px 12px rgba(0, 0, 0, 0.15)",
                        animation: "slideIn 0.3s ease-out",
                        maxWidth: "400px",
                    }}
                >
                    {toast.message}
                </div>,
                document.body
            )}
        <main className="page">
            <header className="page__header">
                <div>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1rem" }}>
                        <div>
                            <p className="eyebrow">👾 Personagens</p>
                            <h1>Biblioteca de Chatbots</h1>
                            <p>
                                Cadastre e gerencie personas que poderão ser usadas pelo seu chatbot.
                                Defina prompts, traços de personalidade e imagens para deixá-los únicos.
                            </p>
                        </div>
                        <button
                            onClick={onNavigateToChat}
                            className="btn btn--primary"
                            style={{ marginTop: "1rem" }}
                        >
                            💬 Voltar ao Chat
                        </button>
                    </div>
                </div>
            </header>

            <ConfirmDialog
                isOpen={!!deleteConfirm}
                title="Excluir Personagem"
                message={`Tem certeza que deseja excluir "${deleteConfirm?.name}"? Esta ação não pode ser desfeita.`}
                confirmText="Excluir"
                cancelText="Cancelar"
                onConfirm={confirmDelete}
                onCancel={cancelDelete}
                variant="danger"
            />

            <section className="layout">
                <div className={`column column--form ${showForm || selected ? 'column--form--visible' : ''}`}>
                    <CharacterForm
                        selected={selected}
                        onSubmit={handleSubmit}
                        onCancelEdit={() => {
                            setSelected(null);
                            setShowForm(false);
                        }}
                        isSubmitting={isMutating}
                    />
                </div>

                <div className={`column column--list ${showForm || selected ? 'column--list--hidden' : ''}`}>
                    {!showForm && !selected && (
                        <div className="characters-list-header">
                            <button
                                onClick={() => setShowForm(true)}
                                className="btn btn--primary btn-add-character"
                                style={{ width: '100%', marginBottom: '1.5rem' }}
                            >
                                ➕ Adicionar Novo Personagem
                            </button>
                        </div>
                    )}
                    
                    {charactersQuery.isPending && <p>Carregando personagens...</p>}
                    {charactersQuery.isError && (
                        <p className="error">Erro ao carregar personagens. Tente novamente.</p>
                    )}

                    {charactersQuery.data && charactersQuery.data.length === 0 && (
                        <div className="empty-state">
                            <p>Nenhum personagem cadastrado ainda.</p>
                            <p>Clique no botão acima para criar o primeiro!</p>
                        </div>
                    )}

                    <div className="characters-grid">
                        {charactersQuery.data?.map((character) => (
                            <CharacterCard
                                key={character.id}
                                character={character}
                                onEdit={(char) => {
                                    setSelected(char);
                                    setShowForm(true);
                                }}
                                onDelete={handleDelete}
                            />
                        ))}
                    </div>
                </div>
            </section>
        </main>
        </>
    );
}


