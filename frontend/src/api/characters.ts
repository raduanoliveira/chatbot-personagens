import api from "./client";
import type { Character, CharacterPayload } from "../types/character";

export const fetchCharacters = async (): Promise<Character[]> => {
    const { data } = await api.get<Character[]>("/api/characters/");
    return data;
};

export const fetchCharacter = async (id: number): Promise<Character> => {
    const { data } = await api.get<Character>(`/api/characters/${id}`);
    return data;
};

export const createCharacter = async (payload: CharacterPayload): Promise<Character> => {
    const { data } = await api.post<Character>("/api/characters/", payload);
    return data;
};

export const updateCharacter = async (
    id: number,
    payload: Partial<CharacterPayload>,
): Promise<Character> => {
    const { data } = await api.put<Character>(`/api/characters/${id}`, payload);
    return data;
};

export const deleteCharacter = async (id: number): Promise<void> => {
    await api.delete(`/api/characters/${id}`);
};


