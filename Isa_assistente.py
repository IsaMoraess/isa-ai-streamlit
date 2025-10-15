import os
import json 
import base64 
import streamlit as st
from groq import Groq

# Configuração da página
st.set_page_config(
    page_title="ISA AI", 
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Adiciona os estados necessários
if 'prompt_starter_value' not in st.session_state:
    st.session_state.prompt_starter_value = None
# NOVO: Estado para controlar o tema
if 'theme' not in st.session_state:
    st.session_state.theme = 'dark' # Tema padrão: escuro

# --- LÓGICA DE PERSISTÊNCIA ---

def load_history_from_url():
    """Carrega o histórico de mensagens da URL (parâmetro 'h') usando st.query_params."""
    query_params = st.query_params
    if 'h' in query_params:
        try:
            encoded_history = query_params['h']
            # Decodifica de base64 e depois de JSON
            json_string = base64.b64decode(encoded_history).decode('utf-8')
            return json.loads(json_string)
        except Exception:
            return []
    return []

def save_history_to_url():
    """Salva o histórico atual no parâmetro 'h' da URL usando st.query_params."""
    history_to_save = st.session_state.messages
    json_string = json.dumps(history_to_save)
    encoded_history = base64.b64encode(json_string.encode('utf-8')).decode('utf-8')
    st.query_params['h'] = encoded_history

# --- CONFIGURAÇÃO DE TEMA DINÂMICA (CORREÇÃO DE CORES INCLUÍDA) ---
# Lógica para alternar cores dependendo do estado do tema
is_dark = st.session_state.theme == 'dark'

# Cores base
# Fundo principal (Cor de Fundo Mais Escura)
BG_MAIN = '#0c121e' if is_dark else '#f1f5f9' 
# Fundo secundário/sidebar (Cor de Fundo da Sidebar, um pouco mais clara que o BG_MAIN)
BG_SECONDARY = '#111827' if is_dark else '#ffffff' 
# Cor do input e widget (Fundo da caixa de código, chat, input de texto)
BG_WIDGET_DARK = '#1e293b' 
BG_WIDGET_LIGHT = '#f8fafc' # Cor para widgets no tema claro
BG_WIDGET = BG_WIDGET_DARK if is_dark else BG_WIDGET_LIGHT 

# Cor do texto principal: BRANCO/NEON no escuro, PRETO/CINZA ESCURO no claro
COLOR_TEXT_DARK = '#e2e8f0' 
COLOR_TEXT_LIGHT = '#1e293b' # <-- ESTA É A COR PRETA/CINZA ESCURO
COLOR_TEXT = COLOR_TEXT_DARK if is_dark else COLOR_TEXT_LIGHT
# Cor Neon 
COLOR_ACCENT = '#00ffb3' 
# Sombra Neon
COLOR_SHADOW = 'rgba(0, 255, 179, 0.3)' 
# Cor das linhas separadoras (hr) e bordas
COLOR_HR_LIGHT = '#94a3b8' 
COLOR_BORDER_LIGHT = '#94a3b8' 

# Cor de Fundo do balão de CHAT e Fundo de Código
CHAT_BUBBLE_BG = BG_WIDGET

# CSS base para o tema
st.markdown(f"""
    <style>
    /* Estilo do corpo, Main, e App */
    body, .main, .stApp {{
        /* Fundo principal usa o BG_MAIN */
        background: linear-gradient(145deg, {BG_MAIN}, {'#1e293b' if is_dark else '#e2e8f0'}) !important;
        color: {COLOR_TEXT};
        font-family: 'Segoe UI', sans-serif;
    }}
    
    /* Títulos e Elementos Neon */
    h1, h2, h3, .stMarkdown h1, section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {{
        color: {COLOR_ACCENT if is_dark else COLOR_TEXT} !important;
        text-shadow: 0 0 15px {COLOR_ACCENT} {'!important' if is_dark else ''};
        font-weight: 700;
    }}
    
    /* Sidebar */
    section[data-testid="stSidebar"] {{
        background-color: {BG_SECONDARY};
        border-right: 2px solid {COLOR_ACCENT};
        box-shadow: 0 0 10px {COLOR_SHADOW};
    }}
    
    /* CORREÇÃO FINAL DE TEXTO: AGRESSIVIDADE MÁXIMA PARA A SIDEBAR */
    section[data-testid="stSidebar"] * {{
        color: {COLOR_TEXT} !important; 
    }}

    /* Seletor para o texto do Main (chat, markdown geral) */
    .stMarkdown, 
    .stMarkdown p, 
    .stMarkdown li {{
        color: {COLOR_TEXT} !important; 
    }}

    /* EXCEÇÃO: Mantém as cores do status da API (verde/vermelho) */
    p[style*='color: #00ffb3'] {{
        color: #00ffb3 !important;
    }}
    p[style*='color: #ff4b4b'] {{
        color: #ff4b4b !important;
    }}

    /* --- LINHAS SEPARADORAS (HR) --- */
    hr {{
        border-top: 1px solid {COLOR_ACCENT if is_dark else COLOR_HR_LIGHT} !important;
        margin: 1rem 0 !important;
    }}


    /* --- PADRONIZAÇÃO DE FUNDO DOS WIDGETS E CHAT/CÓDIGO --- */

    /* Fundo do Input do Chat */
    div[data-testid="stForm"] > div > div {{
        background-color: {BG_WIDGET} !important;
        border: 1px solid {COLOR_ACCENT if is_dark else COLOR_BORDER_LIGHT};
        border-radius: 10px;
    }}
    
    /* Fundo do ALERTA (st.info, st.warning etc.) */
    div[data-testid^="stAlert"] {{
        background-color: {BG_WIDGET} !important; 
        border: 1px solid {COLOR_ACCENT if is_dark else COLOR_BORDER_LIGHT};
        color: {COLOR_TEXT} !important; /* CORRIGINDO A COR DO TEXTO AQUI */
    }}
    /* Garante que o texto dentro do alerta também siga a cor */
    div[data-testid^="stAlert"] * {{
        color: {COLOR_TEXT} !important; 
    }}


    /* Fundo dos Balões de Chat (user e assistant) */
    div[data-testid="stChatMessage"] {{
        background-color: {CHAT_BUBBLE_BG} !important; 
    }}

    /* Balão de chat do usuário */
    div[data-testid="stChatMessage"]:nth-child(even) {{
        background-color: {CHAT_BUBBLE_BG} !important; 
    }}

    /* Balão de chat do assistente */
    div[data-testid="stChatMessage"]:nth-child(odd) {{
        background-color: {CHAT_BUBBLE_BG} !important; 
    }}
    
    /* Garante que o texto do balão também use a cor padrão */
    div[data-testid="stChatMessage"] div.stMarkdown, 
    div[data-testid="stChatMessage"] .stMarkdown p, 
    div[data-testid="stChatMessage"] .stMarkdown li {{
        color: {COLOR_TEXT} !important; 
    }}
    
    /* Fundo dos Widgets de Input na Sidebar (Slider, Selectbox, TextInput) */
    div[data-testid^="st"] > div > div > div[data-baseweb="input"],
    div[data-testid^="st"] > div > div > div[data-baseweb="select"],
    div[data-testid^="st"] > div > div > div[data-baseweb="slider"],
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] > div > div,
    section[data-testid="stSidebar"] div[data-testid="stSelectbox"] > div > div,
    section[data-testid="stSidebar"] div[data-testid="stSlider"] > div > div {{
        background-color: {BG_WIDGET} !important;
        color: {COLOR_TEXT} !important; 
    }}

    /* Fundo do código (bloco de código no markdown <pre>) */
    pre, div[data-testid="stCodeBlock"] {{
        background-color: {BG_WIDGET} !important;
        border: 1px solid {COLOR_ACCENT if is_dark else COLOR_BORDER_LIGHT};
        border-radius: 6px;
    }}

    /* Fundo do componente de UPLOAD de arquivo (Caixa de arquivo) */
    section[data-testid="stFileUploaderDropzone"] {{
        background-color: {BG_WIDGET} !important; 
        border: 2px dashed {COLOR_ACCENT if is_dark else COLOR_BORDER_LIGHT};
        border-radius: 6px;
    }}
    
    /* O botão 'Browse files' dentro do File Uploader */
    section[data-testid="stFileUploaderDropzone"] button {{
        background-color: {BG_WIDGET} !important; 
        color: {COLOR_TEXT} !important;
        border: 1px solid {COLOR_ACCENT if is_dark else COLOR_BORDER_LIGHT};
    }}
    section[data-testid="stFileUploaderDropzone"] button:hover {{
        background-color: {COLOR_ACCENT} !important;
        color: {BG_MAIN} !important;
    }}
    
    /* Cores do scrollbar */
    ::-webkit-scrollbar {{
        width: 8px;
    }}
    ::-webkit-scrollbar-thumb {{
        background: {COLOR_ACCENT};
        border-radius: 10px;
    }}
    
    /* Estilo dos botões de sugestão (Main) */
    .stButton>button {{
        color: {COLOR_ACCENT} !important;
        border-color: {COLOR_ACCENT} !important;
        background-color: {BG_MAIN} !important;
        border-radius: 20px;
        padding: 5px 15px;
        margin: 5px;
        transition: all 0.2s;
        white-space: normal; 
        line-height: 1.2;
        height: auto; 
    }}
    .stButton>button:hover {{
        background-color: {COLOR_ACCENT} !important;
        color: {BG_MAIN} !important;
        box-shadow: 0 0 10px {COLOR_ACCENT};
    }}

    /* CORREÇÃO DOS BOTÕES NA SIDEBAR (Tema, Limpar Histórico) */
    div[data-testid="stSidebar"] .stButton > button {{
        background-color: {BG_SECONDARY} !important;
        color: {COLOR_TEXT} !important; 
        border-color: {COLOR_ACCENT if is_dark else COLOR_BORDER_LIGHT} !important;
    }}
    div[data-testid="stSidebar"] .stButton > button:hover {{
        background-color: {COLOR_ACCENT} !important;
        color: {BG_MAIN} !important;
    }}
    
    /* CORREÇÃO VISUAL DO TRECHO "Modelo em Uso" E BOTÃO SUPORTE */
    /* Garante que todo texto da sidebar use COLOR_TEXT */
    section[data-testid="stSidebar"] p,
    section[data-testid="stSidebar"] span,
    section[data-testid="stSidebar"] div {{
        color: {COLOR_TEXT} !important;
    }}

    /* Corrigir o bloco de código inline (o nome do modelo) */
    section[data-testid="stSidebar"] code {{
        background-color: {BG_WIDGET} !important;
        color: {COLOR_TEXT} !important;
        border: 1px solid {COLOR_ACCENT if is_dark else COLOR_BORDER_LIGHT};
        border-radius: 4px;
        padding: 2px 4px;
        font-weight: bold;
    }}

    /* Botão "E-mail Para o Suporte" (Link Button) */
    section[data-testid="stSidebar"] a, 
    section[data-testid="stSidebar"] .st-link-button {{
        /* Cor do Texto do Link */
        color: {COLOR_TEXT} !important; 
        /* Cor de Fundo do Botão de Link */
        background-color: {BG_WIDGET} !important;
        /* Cor da Borda do Botão de Link */
        border: 1px solid {COLOR_ACCENT if is_dark else COLOR_BORDER_LIGHT} !important;
    }}

    /* Outras configurações (rodapé, etc.) */
    footer, div[role="contentinfo"] {{
        display: none;
    }}
    /* Otimização: remove a animação de digitação do H1 (causa problemas de layout) */
    .typing {{
        border-right: none;
        white-space: normal;
        overflow: visible;
        animation: none;
    }}
    </style>
""", unsafe_allow_html=True)

# Ícone animado da ISA (canto superior direito)
st.markdown("""
    <style>
    .isa-icon {
        position: fixed;
        top: 20px;
        right: 40px;
        font-size: 35px;
        color: #00ffb3;
        animation: pulse 2s infinite;
        z-index: 999;
    }
    @keyframes pulse {
        0% { text-shadow: 0 0 5px #00ffb3; }
        50% { text-shadow: 0 0 20px #00ffb3; transform: scale(1.1); }
        100% { text-shadow: 0 0 5px #00ffb3; transform: scale(1); }
    }
    </style>
    <div class="isa-icon">🤖</div>
""", unsafe_allow_html=True)

# --- PROMPT DO SISTEMA PADRÃO ---
BASE_PROMPT = """
Você é o "ISA AI", um assistente virtual amigável, inteligente e útil. 
Sua missão é responder perguntas sobre diversos tópicos, gerar códigos, dar explicações e fornecer resumos de forma clara, precisa e útil. Seu tom deve ser encorajador e profissional.
"""

# Modelo de IA fixo (o mais rápido e estável que funcionou)
MODELO_ESTAVEL = "llama-3.1-8b-instant" 

# --- SIDEBAR ---
with st.sidebar:
    st.title("🤖 ISA AI") 
    st.markdown("Seu assistente de IA para todas as dúvidas: informações, código, resumos e muito mais.") 

    # API Key Input e prioridade para variável de ambiente
    groq_api_key_input = st.text_input(
        "Insira sua API Key Groq", 
        type="password",
        help="Obtenha sua chave em https://console.groq.com/keys"
    )
    groq_api_key_final = groq_api_key_input or os.getenv("GROQ_API_KEY")
    
    # NOVO: Indicador Visual de API Key
    if groq_api_key_final:
        st.markdown("<p style='color: #00ffb3; font-weight: bold;'>🟢 API Key Detectada e Pronta</p>", unsafe_allow_html=True)
    else:
        st.markdown("<p style='color: #ff4b4b; font-weight: bold;'>🔴 API Key Faltando ou Inválida</p>", unsafe_allow_html=True)

    st.markdown("---")
    
    # Uploader de Arquivos para Análise
    st.subheader("📁 Análise de Arquivos")
    uploaded_file = st.file_uploader(
        "Carregue um arquivo de texto, código ou Markdown (.txt, .py, .md, .java, etc.)", 
        type=['txt', 'py', 'md', 'java', 'js', 'html', 'css'], 
        help="A ISA AI pode ler o conteúdo e responder perguntas sobre ele."
    )
    st.markdown("---") 
    
    # NOVAS CONFIGURAÇÕES AVANÇADAS
    with st.expander("⚙️ Configurações Avançadas"):
        
        # 1. Estilo da Resposta (Tone)
        estilo_resposta = st.selectbox(
            "Estilo da Resposta",
            options=["Profissional (Padrão)", "Casual e Amigável", "Formal e Detalhado", "Encorajador"],
            index=0,
            help="Define o tom da conversa da ISA AI."
        )

        # 2. Foco da Resposta (Focus)
        foco_resposta = st.selectbox(
            "Foco Principal",
            options=["Geral (Resumo e Explicação)", "Geração de Código", "Lista de Tópicos", "Respostas Curtas e Diretas"],
            index=0,
            help="Define o formato preferencial da resposta."
        )

        # 3. Max Tokens (Mantido por ser fundamental para controle de custo/tamanho)
        max_tokens = st.slider(
            'Max Tokens (Tamanho da Resposta)', 
            min_value=512, 
            max_value=4096, 
            value=2048, 
            step=512,
            help="O comprimento máximo da resposta da IA."
        )

    st.markdown("---")
    
    # --- Botão de Tema ---
    def toggle_theme():
        """Alterna entre os temas claro e escuro."""
        if st.session_state.theme == 'dark':
            st.session_state.theme = 'light'
        else:
            st.session_state.theme = 'dark'

    theme_label = "Tema Claro ☀️" if st.session_state.theme == 'dark' else "Tema Escuro 🌙"

    st.button(
        theme_label,
        on_click=toggle_theme,
        key="theme_toggle_button"
    )
    st.markdown("---") 

    # Botão para Limpar Histórico do Chat
    if st.button("Limpar Histórico do Chat 🧹"):
        st.session_state.messages = []
        st.session_state.prompt_starter_value = None 
        if 'h' in st.query_params:
            del st.query_params['h']
        st.rerun() 

    st.markdown("---")
    # O nome do modelo está entre crases (` `) para usar o novo estilo de bloco inline.
    st.markdown(f"**Modelo em Uso:** `{MODELO_ESTAVEL}` (Rápido e Estável)")
    st.markdown("Desenvolvido para auxiliar em suas dúvidas no geral. A IA pode cometer erros, sempre verifique as respostas.")
    st.link_button("✉️ E-mail Para o Suporte ISA", "mailto:isabellyidelfonso@gmail.com")

# --- CONTEÚDO PRINCIPAL ---
st.title("ISA AI") 

# Animação de digitação corrigida
st.markdown(f"""<h1>A sua IA para o próximo passo.</h1>""", unsafe_allow_html=True)
st.caption("Faça sua pergunta e obtenha código, resumo, explicações e referências.")

# --- Lógica do chat ---
# Inicialização das mensagens
if "messages" not in st.session_state:
    st.session_state.messages = load_history_from_url()
    if st.session_state.messages and 'h' in st.query_params:
        del st.query_params['h'] 

# Exibe o histórico de mensagens
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Inicialização do cliente Groq
client = None
if groq_api_key_final:
    try:
        client = Groq(api_key=groq_api_key_final)
    except Exception as e:
        # Se a chave for detectada, mas falhar na inicialização
        st.sidebar.error(f"Erro ao inicializar o cliente Groq. Tente novamente.")
        st.error(f"Detalhes do erro: {e}")
        groq_api_key_final = None # Marca como inválida para não prosseguir
else:
    if not st.session_state.messages:
        # Corrigido para st.info, que tem fundo claro, mas agora o texto será escuro
        st.info("🔑 Por favor, insira sua API Key da Groq na barra lateral para começar.")

# --- Montagem do PROMPT Personalizado ---
prompt_personalizado = f"""
{BASE_PROMPT}

Instruções Adicionais (Baseado nas Configurações Avançadas do Usuário):
1. ESTILO: Responda de forma {estilo_resposta.split('(')[0].strip()}.
2. FOCO: Sua resposta deve ter como foco principal {foco_resposta.lower()}. Se a resposta for um código, envolva-o em blocos de código Markdown com o idioma especificado (ex: ```python, ```javascript).
3. PRECISÃO: Mantenha a precisão e a utilidade acima de tudo.
"""
# --- Fim da montagem do PROMPT ---

# 4. Sugestões de Perguntas (Prompt Starters) - Lógica Mantida
SUGESTOES = [
    "Gere um código Python para uma calculadora.",
    "O que é Machine Learning em termos simples?",
    "Resuma a história da inteligência artificial.",
]

def set_prompt_starter(sugestao):
    st.session_state.prompt_starter_value = sugestao

# Cria um container temporário para os botões de sugestão
with st.container():
    cols = st.columns(len(SUGESTOES))
    
    for i, sugestao in enumerate(SUGESTOES):
        cols[i].button(
            sugestao, 
            key=f"starter_btn_{i}", 
            on_click=set_prompt_starter, 
            args=(sugestao,)
        )

# Define o prompt (priorizando o botão, depois o input do chat)
if st.session_state.prompt_starter_value:
    prompt = st.session_state.prompt_starter_value
    st.session_state.prompt_starter_value = None
elif st.session_state.prompt_starter_value is None:
    prompt = st.chat_input("Qual sua dúvida?")
else:
    prompt = None


if prompt:
    if not groq_api_key_final:
        st.warning("Por favor, insira sua API Key da Groq na barra lateral para começar.")
        st.stop() 

    # --- Lógica de Injeção de Arquivo ---
    full_user_prompt = prompt
    if uploaded_file is not None:
        try:
            file_content = uploaded_file.getvalue().decode("utf-8")
            file_injection = f"\n\n--- CONTEÚDO DO ARQUIVO: {uploaded_file.name} ---\n{file_content}\n--- FIM DO ARQUIVO ---\n\n"
            full_user_prompt = f"Com base no arquivo que forneci, responda o seguinte: {prompt}{file_injection}"
            
            # Adiciona a entrada do usuário ao histórico (com menção ao arquivo)
            st.session_state.messages.append({"role": "user", "content": f"Arquivo carregado: **{uploaded_file.name}**\n\nMinha pergunta: {prompt}"})
            with st.chat_message("user"):
                st.markdown(f"Arquivo carregado: **{uploaded_file.name}**\n\nMinha pergunta: {prompt}")

        except Exception as e:
            st.error(f"Não foi possível ler o arquivo. Certifique-se de que é um arquivo de texto válido. Erro: {e}")
            st.stop()
    else:
        # Se não há arquivo, apenas adiciona a pergunta normal
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

    # Prepara as mensagens para a API
    messages_for_api = [{"role": "system", "content": prompt_personalizado}]
    for msg in st.session_state.messages[:-1]:
        messages_for_api.append(msg)
    messages_for_api.append({"role": "user", "content": full_user_prompt})


    # Tenta obter o cliente Groq novamente (se a chave foi inserida agora)
    client = Groq(api_key=groq_api_key_final) 

    with st.chat_message("assistant"):
        with st.spinner(f"ISA AI analisando e pensando..."):
            try:
                chat_completion = client.chat.completions.create(
                    messages=messages_for_api,
                    model=MODELO_ESTAVEL, 
                    temperature=0.7, 
                    max_tokens=max_tokens,
                )
                dsa_ai_resposta = chat_completion.choices[0].message.content
                st.markdown(dsa_ai_resposta)
                
                # A resposta da IA é adicionada ao histórico
                st.session_state.messages.append({"role": "assistant", "content": dsa_ai_resposta})
            except Exception as e:
                # Exibe o erro no chat principal
                st.error(f"Erro da API: Não foi possível obter a resposta da ISA AI. Verifique se sua API Key está correta ou se o modelo está ativo.")
                st.info(f"Detalhes: {e}")
                # Remove a última mensagem do usuário do histórico para que não seja salva
                st.session_state.messages.pop() 

    # Salva o histórico na URL após cada interação (se não houve erro fatal)
    save_history_to_url()
    st.rerun() 

# --- Rodapé com brilho (Mantido) ---
st.markdown("""
    <div style="text-align: center; color: #94a3b8; margin-top: 50px;">
        <hr style="border: 1px solid rgba(0,255,179,0.3); width: 70%;">
        <p style="font-size: 14px;">Feito com ❤️ por <b style="color:#00ffb3;">Isabelly Moraes</b> | 
        <span style="color:#00ffb3;">ISA AI © 2025</span></p>
    </div>
""", unsafe_allow_html=True)