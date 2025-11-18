export interface Character {
    id: number;
    name: string;
    description?: string | null;
    catchphrase?: string | null;
    personality_traits: string[];
    image_url?: string | null;
    system_prompt?: string | null;
    created_at?: string | null;
    updated_at?: string | null;
}

export type CharacterPayload = Omit<Character, "id" | "created_at" | "updated_at">;


