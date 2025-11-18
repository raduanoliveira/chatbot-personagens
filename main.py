import os
from openai import OpenAI
from dotenv import load_dotenv

# Tenta carregar do arquivo .env primeiro
load_dotenv()

# Tenta obter a chave do .env, se não encontrar, tenta do config.py
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    try:
        from config import OPENAI_API_KEY as config_key
        api_key = config_key
    except ImportError:
        api_key = None
    except Exception:
        api_key = None

# Configuração da API da OpenAI
client = OpenAI(api_key=api_key) if api_key else None

# Prompt do sistema para fazer o chatbot se comportar como Mario
MARIO_SYSTEM_PROMPT = """Você é Mario, o famoso encanador italiano do Reino dos Cogumelos! 
Você fala com entusiasmo e energia, sempre usando expressões características como:
- "Mamma mia!" para surpresa
- "It's-a me, Mario!" para se apresentar
- "Let's-a go!" para animar
- "Wahoo!" para comemorações
- "Here we go!" para começar algo

Você é otimista, corajoso e sempre pronto para ajudar. Fale em português brasileiro, mas mantenha 
algumas expressões italianas características. Seja amigável, divertido e mantenha o espírito 
aventureiro do personagem. Use emojis ocasionalmente para dar mais vida à conversa! 🍄⭐"""

def chat_with_mario():
    """
    Função principal que gerencia a conversa com o Mario
    """
    print("=" * 60)
    print("🍄 Bem-vindo ao Chat do Mario Bros! 🍄")
    print("=" * 60)
    print("Mario: It's-a me, Mario! Pronto para uma aventura?")
    print("Digite 'sair' para encerrar a conversa.\n")
    
    # Lista para armazenar o histórico da conversa
    messages = [
        {"role": "system", "content": MARIO_SYSTEM_PROMPT}
    ]
    
    while True:
        # Recebe a mensagem do usuário
        user_input = input("Você: ").strip()
        
        # Verifica se o usuário quer sair
        if user_input.lower() in ['sair', 'exit', 'quit', 'tchau']:
            print("\nMario: Até logo! It's-a me, Mario! Volte sempre para mais aventuras! 🍄")
            break
        
        # Ignora mensagens vazias
        if not user_input:
            continue
        
        # Adiciona a mensagem do usuário ao histórico
        messages.append({"role": "user", "content": user_input})
        
        try:
            # Chama a API da OpenAI
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.8,  # Um pouco de criatividade para manter o personagem divertido
                max_tokens=300
            )
            
            # Extrai a resposta do Mario
            mario_response = response.choices[0].message.content
            
            # Adiciona a resposta do Mario ao histórico
            messages.append({"role": "assistant", "content": mario_response})
            
            # Exibe a resposta
            print(f"\nMario: {mario_response}\n")
            
        except Exception as e:
            print(f"\n❌ Erro ao comunicar com a API: {e}")
            print("Verifique se sua OPENAI_API_KEY está configurada corretamente.\n")

if __name__ == "__main__":
    # Verifica se a API key está configurada
    if not api_key or api_key == "sua-chave-aqui" or not client:
        print("⚠️  AVISO: A chave da API não está configurada!")
        print("\nConfigure sua chave de uma das seguintes formas:")
        print("\n1. No arquivo config.py:")
        print("   - Abra o arquivo config.py")
        print("   - Substitua 'sua-chave-aqui' pela sua chave real")
        print("\n2. No arquivo .env (opcional):")
        print("   - Crie um arquivo .env na raiz do projeto")
        print("   - Adicione: OPENAI_API_KEY=sua-chave-aqui")
        print("\n3. Variável de ambiente:")
        print("   - export OPENAI_API_KEY='sua-chave-aqui'")
        exit(1)
    
    chat_with_mario()

