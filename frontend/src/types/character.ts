export interface Phrase {
    id: number;
    character_id: number;
    phrase: string;
    purpose: string;
    created_at?: string | null;
    updated_at?: string | null;
}

export interface Character {
    id: number;
    name: string;
    description?: string | null;
    catchphrase?: string | null;
    personality_traits: string[];
    image_url?: string | null;
    who_is_character: string;
    phrases: Phrase[];
    created_at?: string | null;
    updated_at?: string | null;
}

export interface PhraseInput {
    phrase: string;
    purpose: string;
}

export type CharacterPayload = Omit<Character, "id" | "created_at" | "updated_at" | "phrases"> & {
    phrases: PhraseInput[];
};

export const AVAILABLE_PURPOSES = [
    "para se apresentar",
    "para surpresa",
    "para animar",
    "para comemorações",
    "para começar algo"
] as const;

export type Purpose = typeof AVAILABLE_PURPOSES[number];
