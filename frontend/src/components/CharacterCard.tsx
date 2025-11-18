import type { Character } from "../types/character";

type CharacterCardProps = {
    character: Character;
    onEdit: (character: Character) => void;
    onDelete: (character: Character) => void;
};

export function CharacterCard({ character, onEdit, onDelete }: CharacterCardProps) {
    return (
        <div className="character-card">
            <div className="character-card__header">
                <div>
                    <h3>{character.name}</h3>
                    {character.catchphrase && (
                        <p className="character-card__catchphrase">“{character.catchphrase}”</p>
                    )}
                </div>
                {character.image_url && (
                    <img
                        src={character.image_url}
                        alt={character.name}
                        className="character-card__avatar"
                    />
                )}
            </div>

            {character.description && (
                <p className="character-card__description">{character.description}</p>
            )}

            {character.personality_traits?.length ? (
                <div className="character-card__traits">
                    {character.personality_traits.map((trait) => (
                        <span key={trait} className="badge">
                            {trait}
                        </span>
                    ))}
                </div>
            ) : null}

            <div className="character-card__actions">
                <button className="btn btn-secondary" onClick={() => onEdit(character)}>
                    Editar
                </button>
                <button className="btn btn-danger" onClick={() => onDelete(character)}>
                    Excluir
                </button>
            </div>
        </div>
    );
}


