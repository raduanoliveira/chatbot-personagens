import { useEffect, useState, useRef, useCallback } from "react";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";

import type { Character, CharacterPayload } from "../types/character";

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
    system_prompt: z.string().min(1, "O contexto do prompt é obrigatório"),
});

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
    system_prompt: "",
};

export function CharacterForm({ selected, onSubmit, onCancelEdit, isSubmitting }: CharacterFormProps) {
    const {
        register,
        handleSubmit,
        reset,
        setValue,
        formState: { errors },
    } = useForm<FormValues>({
        resolver: zodResolver(schema),
        defaultValues,
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
            reset({
                name: selected.name,
                description: selected.description ?? "",
                catchphrase: selected.catchphrase ?? "",
                personalityTraits: selected.personality_traits?.join(", ") ?? "",
                image_url: imageUrlValue,
                system_prompt: selected.system_prompt ?? "",
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
            // Usa o estado local imageUrl em vez do values.image_url
            image_url: imageUrl || undefined,
            system_prompt: values.system_prompt || undefined,
        };

        onSubmit(payload, selected?.id);
    };

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

            <label>
                Contexto do prompt *
                <textarea
                    {...register("system_prompt")}
                    rows={5}
                    placeholder="Instruções específicas usadas pelo modelo"
                    required
                />
                {errors.system_prompt && <span className="error">{errors.system_prompt.message}</span>}
            </label>

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


