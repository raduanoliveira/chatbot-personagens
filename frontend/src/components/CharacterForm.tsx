import { useEffect, useState, useRef, useCallback } from "react";
import { useForm, useFieldArray } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import type { Character, CharacterPayload } from "../types/character";
import { AVAILABLE_PURPOSES } from "../types/character";

const schema = z.object({
    name: z.string().min(2, "Informe pelo menos 2 caracteres"),
    description: z.string().optional(),
    catchphrase: z.string().optional(),
    personalityTraits: z.string().optional(),
    image_url: z
        .string()
        .url("Informe uma URL válida")
        .optional()
        .or(z.literal("")),
    who_is_character: z.string().min(1, "Este campo é obrigatório").max(255, "Máximo de 255 caracteres"),
    phrases: z.array(
        z.object({
            phrase: z.string().min(1, "A fala é obrigatória"),
            purpose: z.string().min(1, "A finalidade é obrigatória"),
        })
    ).length(5, "É necessário preencher todas as 5 finalidades"),
}).refine(
    (data) => {
        // Verifica se todas as finalidades estão presentes
        const purposes = data.phrases.map(p => p.purpose);
        const requiredPurposes = new Set(AVAILABLE_PURPOSES);
        const providedPurposes = new Set(purposes);
        return requiredPurposes.size === providedPurposes.size && 
               Array.from(requiredPurposes).every(p => providedPurposes.has(p));
    },
    {
        message: "Todas as finalidades devem ser preenchidas e não pode haver duplicatas",
        path: ["phrases"],
    }
).refine(
    (data) => {
        // Verifica se não há finalidades duplicadas
        const purposes = data.phrases.map(p => p.purpose);
        return purposes.length === new Set(purposes).size;
    },
    {
        message: "Não pode haver duas falas com a mesma finalidade",
        path: ["phrases"],
    }
);

type FormValues = z.infer<typeof schema>;

type CharacterFormProps = {
    selected?: Character | null;
    onSubmit: (payload: CharacterPayload, id?: number) => void;
    onCancelEdit: () => void;
    isSubmitting: boolean;
};

const defaultValues: FormValues = {
    name: "",
    description: "",
    catchphrase: "",
    personalityTraits: "",
    image_url: "",
    who_is_character: "",
    phrases: AVAILABLE_PURPOSES.map(purpose => ({ phrase: "", purpose })),
};

export function CharacterForm({ selected, onSubmit, onCancelEdit, isSubmitting }: CharacterFormProps) {
    const {
        register,
        handleSubmit,
        reset,
        setValue,
        control,
        formState: { errors },
    } = useForm<FormValues>({
        resolver: zodResolver(schema),
        defaultValues,
    });

    const { fields } = useFieldArray({
        control,
        name: "phrases",
    });

    // Usa estado local em vez de watch para ter controle total
    const [imageUrl, setImageUrl] = useState<string>("");
    const [imagePreview, setImagePreview] = useState<string | null>(null);
    const [imageError, setImageError] = useState(false);
    const [imageLoading, setImageLoading] = useState(false);
    const imageInputRef = useRef<HTMLInputElement | null>(null);

    useEffect(() => {
        if (selected) {
            const imageUrlValue = selected.image_url ?? "";
            
            // Mapeia as phrases do personagem para o formato do formulário
            const phrasesMap = new Map(selected.phrases.map(p => [p.purpose, p.phrase]));
            const phrases = AVAILABLE_PURPOSES.map(purpose => ({
                phrase: phrasesMap.get(purpose) || "",
                purpose,
            }));
            
            reset({
                name: selected.name,
                description: selected.description ?? "",
                catchphrase: selected.catchphrase ?? "",
                personalityTraits: selected.personality_traits?.join(", ") ?? "",
                image_url: imageUrlValue,
                who_is_character: selected.who_is_character ?? "",
                phrases,
            });
            // Necessário sincronizar estado local com o formulário
            setImageUrl(imageUrlValue);
        } else {
            reset(defaultValues);
            // Necessário limpar estado local ao resetar formulário
            setImageUrl("");
        }
    }, [selected, reset]);

    // Função para configurar listeners nativos no input
    const setupListeners = useCallback((input: HTMLInputElement) => {
        const updateState = () => {
            const value = input.value;
            setImageUrl(value);
            setValue("image_url", value, { shouldValidate: true });
        };

        input.addEventListener('input', updateState);
        input.addEventListener('paste', () => {
            setTimeout(updateState, 10);
        });

        return () => {
            input.removeEventListener('input', updateState);
        };
    }, [setValue]);

    // Adiciona listeners nativos ao input quando o ref estiver disponível
    useEffect(() => {
        const input = imageInputRef.current;
        if (!input) {
            // Tenta novamente após um pequeno delay
            const timer = setTimeout(() => {
                const inputRetry = imageInputRef.current;
                if (inputRetry) {
                    setupListeners(inputRetry);
                }
            }, 100);
            return () => clearTimeout(timer);
        }
        
        return setupListeners(input);
    }, [setupListeners]);

    // Pré-carrega a imagem quando a URL é alterada (com debounce)
    useEffect(() => {
        const url = imageUrl?.trim();
        
        // Se não há URL, limpa tudo
        if (!url) {
            // Necessário limpar estados de preview quando URL é removida
            setImagePreview(null);
            setImageError(false);
            setImageLoading(false);
            return;
        }

        // Valida se é uma URL válida
        try {
            new URL(url);
        } catch {
            // URL inválida - não faz nada, apenas limpa estados
            setImagePreview(null);
            setImageError(false);
            setImageLoading(false);
            return;
        }

        // Se chegou aqui, a URL é válida - inicia o carregamento após debounce
        setImageError(false);
        setImagePreview(null);
        
        // Debounce: aguarda 300ms após o usuário parar de digitar
        const timeoutId = setTimeout(() => {
            // Agora sim inicia o loading
            setImageLoading(true);
            
            const img = new Image();
            
            // Timeout de segurança (10 segundos)
            const errorTimeout = setTimeout(() => {
                setImagePreview(null);
                setImageError(true);
                setImageLoading(false);
            }, 10000);
            
            img.onload = () => {
                clearTimeout(errorTimeout);
                setImagePreview(url);
                setImageError(false);
                setImageLoading(false);
            };
            
            img.onerror = () => {
                clearTimeout(errorTimeout);
                setImagePreview(null);
                setImageError(true);
                setImageLoading(false);
            };
            
            img.src = url;
        }, 300);

        return () => {
            clearTimeout(timeoutId);
        };
    }, [imageUrl]);

    const submitHandler = (values: FormValues) => {
        // Processa image_url: se vazio ou inválido, envia undefined
        let imageUrlValue: string | undefined = undefined;
        if (imageUrl && imageUrl.trim()) {
            try {
                // Valida se é uma URL válida ou data URI
                if (imageUrl.startsWith('data:')) {
                    imageUrlValue = imageUrl;
                } else {
                    new URL(imageUrl);
                    imageUrlValue = imageUrl;
                }
            } catch {
                // URL inválida, envia undefined
                imageUrlValue = undefined;
            }
        }
        
        const payload: CharacterPayload = {
            name: values.name,
            description: values.description || undefined,
            catchphrase: values.catchphrase || undefined,
            personality_traits: values.personalityTraits
                ? values.personalityTraits
                      .split(",")
                      .map((trait) => trait.trim())
                      .filter(Boolean)
                : [],
            image_url: imageUrlValue,
            who_is_character: values.who_is_character,
            phrases: values.phrases.map(p => ({
                phrase: p.phrase.trim(),
                purpose: p.purpose,
            })),
        };

        console.log("📤 Payload sendo enviado:", JSON.stringify(payload, null, 2));
        onSubmit(payload, selected?.id);
    };

    // Limpa campos quando não há personagem selecionado (após criação bem-sucedida)
    useEffect(() => {
        if (!selected) {
            reset(defaultValues);
            setImageUrl("");
            setImagePreview(null);
            setImageError(false);
            setImageLoading(false);
        }
    }, [selected, reset]);

    return (
        <form className="character-form" onSubmit={handleSubmit(submitHandler)}>
            <div className="character-form__header">
                <h2>{selected ? "Editar personagem" : "Novo personagem"}</h2>
                <button
                    type="button"
                    className="btn-close"
                    onClick={onCancelEdit}
                    aria-label="Fechar formulário"
                >
                    ✕
                </button>
            </div>

            <label>
                Nome *
                <input type="text" {...register("name")} placeholder="Mario Bros" />
                {errors.name && <span className="error">{errors.name.message}</span>}
            </label>

            <label>
                Quem é o personagem? *
                <input 
                    type="text" 
                    {...register("who_is_character")} 
                    placeholder="o famoso encanador italiano do Reino dos Cogumelos"
                    maxLength={255}
                />
                {errors.who_is_character && <span className="error">{errors.who_is_character.message}</span>}
            </label>

            <label>
                Descrição
                <textarea {...register("description")} placeholder="Breve resumo do personagem" rows={3} />
            </label>

            <label>
                Bordão
                <input type="text" {...register("catchphrase")} placeholder="It's-a me, Mario!" />
            </label>

            <label>
                Traços de personalidade (separe por vírgula)
                <input
                    type="text"
                    {...register("personalityTraits")}
                    placeholder="Corajoso, Engraçado, Otimista"
                />
            </label>

            <label>
                URL da imagem
                <input 
                    type="url" 
                    {...register("image_url")}
                    ref={(e) => {
                        const { ref } = register("image_url");
                        if (typeof ref === 'function') {
                            ref(e);
                        }
                        imageInputRef.current = e;
                    }}
                    placeholder="https://..."
                />
                {errors.image_url && <span className="error">{errors.image_url.message}</span>}
                
                {/* Preview da imagem */}
                {imageUrl && (
                    <div style={{ marginTop: "0.5rem" }}>
                        {imageLoading && (
                            <div style={{ 
                                padding: "1rem", 
                                textAlign: "center", 
                                background: "#f5f5f5", 
                                borderRadius: "4px",
                                color: "#666"
                            }}>
                                🔄 Carregando imagem...
                            </div>
                        )}
                        {imagePreview && !imageLoading && (
                            <div style={{ 
                                marginTop: "0.5rem",
                                display: "flex",
                                justifyContent: "center"
                            }}>
                                <img
                                    src={imagePreview}
                                    alt="Preview"
                                    style={{
                                        width: "100%",
                                        maxWidth: "300px",
                                        maxHeight: "300px",
                                        height: "auto",
                                        objectFit: "contain",
                                        borderRadius: "8px",
                                        border: "2px solid #e0e0e0",
                                        display: "block",
                                    }}
                                    onError={() => {
                                        setImageError(true);
                                        setImagePreview(null);
                                    }}
                                />
                            </div>
                        )}
                        {imageError && !imageLoading && (
                            <div style={{ 
                                padding: "0.5rem", 
                                background: "#fee", 
                                color: "#c33",
                                borderRadius: "4px",
                                fontSize: "0.9rem",
                                marginTop: "0.5rem"
                            }}>
                                ⚠️ Não foi possível carregar a imagem. Verifique se a URL está correta.
                            </div>
                        )}
                    </div>
                )}
            </label>

            <div style={{ marginTop: "1.5rem" }}>
                <h3 style={{ marginBottom: "1rem" }}>Falas do personagem *</h3>
                <p style={{ fontSize: "0.9rem", color: "#666", marginBottom: "1rem" }}>
                    Preencha uma fala para cada finalidade. Todas são obrigatórias.
                </p>
                
                {fields.map((field, index) => {
                    // Placeholders baseados nas falas do seed do Mario
                    const placeholders: Record<string, string> = {
                        "para se apresentar": "It's-a me, Mario!",
                        "para surpresa": "Mamma mia!",
                        "para animar": "Let's-a go!",
                        "para comemorações": "Wahoo!",
                        "para começar algo": "Here we go!",
                    };
                    
                    const placeholder = placeholders[field.purpose] || "Digite a fala...";
                    
                    return (
                        <div key={field.id} style={{ marginBottom: "1rem" }}>
                            <label>
                                Fala: {field.purpose} *
                                <input
                                    type="text"
                                    {...register(`phrases.${index}.phrase`)}
                                    placeholder={placeholder}
                                    maxLength={255}
                                />
                                <input
                                    type="hidden"
                                    {...register(`phrases.${index}.purpose`)}
                                    value={field.purpose}
                                />
                                {errors.phrases?.[index]?.phrase && (
                                    <span className="error">{errors.phrases[index]?.phrase?.message}</span>
                                )}
                            </label>
                        </div>
                    );
                })}
                
                {errors.phrases && typeof errors.phrases.message === 'string' && (
                    <span className="error" style={{ display: "block", marginTop: "0.5rem" }}>
                        {errors.phrases.message}
                    </span>
                )}
            </div>

            <div className="character-form__actions">
                {selected ? (
                    <button type="button" className="btn btn-secondary" onClick={onCancelEdit}>
                        Cancelar
                    </button>
                ) : (
                    <button 
                        type="button" 
                        className="btn btn-secondary" 
                        onClick={() => {
                            reset(defaultValues);
                            setImageUrl("");
                            setImagePreview(null);
                            setImageError(false);
                            setImageLoading(false);
                        }}
                    >
                        Limpar
                    </button>
                )}
                <button type="submit" className="btn btn-primary" disabled={isSubmitting}>
                    {isSubmitting ? "Salvando..." : selected ? "Atualizar" : "Cadastrar"}
                </button>
            </div>
        </form>
    );
}
