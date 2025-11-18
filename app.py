import os
import streamlit as st
from openai import OpenAI
from dotenv import load_dotenv

# Configuração da página
st.set_page_config(
    page_title="Chatbot Mario Bros 🍄",
    page_icon="🍄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

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

# Inicializa o cliente OpenAI
@st.cache_resource
def get_openai_client():
    if api_key and api_key != "sua-chave-aqui":
        return OpenAI(api_key=api_key)
    return None

client = get_openai_client()

# Inicializa o histórico de mensagens na sessão
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": MARIO_SYSTEM_PROMPT},
        {"role": "assistant", "content": "It's-a me, Mario! 🍄 Bem-vindo ao Reino dos Cogumelos! Pronto para uma aventura? Let's-a go! ⭐"}
    ]

def get_mario_response(user_message):
    """
    Obtém a resposta do Mario usando a API da OpenAI
    """
    if not client:
        return "❌ Erro: Cliente OpenAI não configurado. Verifique sua chave de API."
    
    try:
        # Adiciona a mensagem do usuário ao histórico
        st.session_state.messages.append({"role": "user", "content": user_message})
        
        # Chama a API da OpenAI
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=st.session_state.messages,
            temperature=0.8,
            max_tokens=300
        )
        
        # Extrai a resposta do Mario
        mario_response = response.choices[0].message.content
        
        # Adiciona a resposta do Mario ao histórico
        st.session_state.messages.append({"role": "assistant", "content": mario_response})
        
        return mario_response
    
    except Exception as e:
        return f"❌ Erro ao comunicar com a API: {str(e)}"

# CSS personalizado para melhorar a aparência
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        padding: 1rem 0;
        background: linear-gradient(90deg, #FF6B6B 0%, #FFD93D 50%, #6BCF7F 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 3rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .stChatMessage {
        padding: 1rem;
    }
    .user-message {
        background-color: #E3F2FD;
        padding: 0.5rem;
        border-radius: 10px;
    }
    .mario-message {
        background-color: #FFF3E0;
        padding: 0.5rem;
        border-radius: 10px;
    }
    .mario-image-container {
        text-align: center;
        padding: 1rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🍄 Chatbot Mario Bros 🍄</h1>', unsafe_allow_html=True)

# Imagem do Mario Bros centralizada abaixo do título
mario_image_urls = [
    "https://www.nintendo.com/eu/media/images/08_content_images/others_2/characterhubs/supermariohub/MarioHub_Overview_Mario_sideimg_mario.png",
    "https://www.pngmart.com/files/2/Mario-PNG-Transparent-Image.png",
]

image_loaded = False
for url in mario_image_urls:
    try:
        # Usa markdown com CSS para centralizar perfeitamente
        st.markdown(f"""
        <div style='display: flex; justify-content: center; align-items: center; padding: 10px 0;'>
            <img src='{url}' style='width: 160px; height: auto; display: block; margin: 0 auto;' />
        </div>
        <div style='text-align: center; padding-bottom: 10px; color: #666; font-style: italic;'>
            It's-a me, Mario! 🍄
        </div>
        """, unsafe_allow_html=True)
        image_loaded = True
        break
    except Exception as e:
        # Se falhar, tenta a próxima URL
        continue

# Se nenhuma imagem carregou, mostra um emoji grande estilizado
if not image_loaded:
    st.markdown("""
    <div style='text-align: center; padding: 20px;'>
        <div style='font-size: 120px; margin-bottom: 10px;'>🍄</div>
        <div style='font-size: 24px; color: #FF6B6B; font-weight: bold;'>It's-a me, Mario!</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# Verifica se a API key está configurada
if not api_key or api_key == "sua-chave-aqui" or not client:
    st.error("⚠️ **AVISO: A chave da API não está configurada!**")
    st.info("""
    Configure sua chave de uma das seguintes formas:
    
    1. **No arquivo config.py:**
       - Abra o arquivo `config.py`
       - Substitua `"sua-chave-aqui"` pela sua chave real
    
    2. **No arquivo .env (opcional):**
       - Crie um arquivo `.env` na raiz do projeto
       - Adicione: `OPENAI_API_KEY=sua-chave-aqui`
    
    3. **Variável de ambiente:**
       - `export OPENAI_API_KEY='sua-chave-aqui'`
    """)
    st.stop()

# Container principal do chat
chat_container = st.container()

# Exibe o histórico de mensagens (exceto a mensagem do sistema)
with chat_container:
    for message in st.session_state.messages[1:]:  # Pula a mensagem do sistema
        if message["role"] == "user":
            with st.chat_message("user"):
                st.write(message["content"])
        else:
            with st.chat_message("assistant", avatar="🍄"):
                st.write(message["content"])

# Input do usuário
user_input = st.chat_input("Digite sua mensagem aqui...")

if user_input:
    # Exibe a mensagem do usuário
    with st.chat_message("user"):
        st.write(user_input)
    
    # Obtém e exibe a resposta do Mario
    with st.chat_message("assistant", avatar="🍄"):
        with st.spinner("Mario está pensando..."):
            response = get_mario_response(user_input)
            st.write(response)
    
    # Rerun para atualizar a interface
    st.rerun()

# Sidebar com informações
with st.sidebar:
    st.header("ℹ️ Sobre")
    st.markdown("""
    **Chatbot Mario Bros** 🍄
    
    Um chatbot interativo que imita o personagem 
    Mario Bros usando a API da OpenAI com o 
    modelo GPT-4o-mini.
    
    ---
    
    **Como usar:**
    - Digite sua mensagem no campo abaixo
    - O Mario responderá com seu estilo característico
    - Use o botão "Clear chat" para limpar a conversa
    """)
    
    if st.button("🗑️ Limpar Conversa", width='stretch'):
        st.session_state.messages = [
            {"role": "system", "content": MARIO_SYSTEM_PROMPT},
            {"role": "assistant", "content": "It's-a me, Mario! 🍄 Bem-vindo ao Reino dos Cogumelos! Pronto para uma aventura? Let's-a go! ⭐"}
        ]
        st.rerun()
    
    st.markdown("---")
    st.markdown("**Feito com ❤️ usando Streamlit**")

