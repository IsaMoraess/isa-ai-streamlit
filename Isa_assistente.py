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

# CSS base para o tema Dark e Neon (Mantido)
st.markdown("""
    <style>
    body, .main, .stApp {
        background: linear-gradient(145deg, #0f172a, #1e293b);
        color: #e2e8f0;
        font-family: 'Segoe UI', sans-serif;
    }
    h1, h2, h3, .stMarkdown h1 {
        color: #00ffb3;
        text-shadow: 0 0 15px #00ffb3;
        font-weight: 700;
    }
    section[data-testid="stSidebar"] {
        background-color: #111827;
        border-right: 2px solid #00ffb3;
        box-shadow: 0 0 10px rgba(0, 255, 179, 0.3);
    }
    ::-webkit-scrollbar {
        width: 8px;
    }
    ::-webkit-scrollbar-thumb {
        background: #00ffb3;
        border-radius: 10px;
    }
    footer, div[role="contentinfo"] {
        display: none;
    }
    /* Estilo para a animação de digitação */
    .typing {
        border-right: 3px solid #00ffb3;
        white-space: nowrap;
        overflow: hidden;
        animation: typing 3.5s steps(30, end), blink-caret .7s step-end infinite;
    }
    @keyframes typing {
        from { width: 0 }
        to { width: 100% }
    }
    @keyframes blink-caret {
        from, to { border-color: transparent }
        50% { border-color: #00ffb3 }
    }
    /* Estilo para os botões de sugestão */
    .stButton>button {
        color: #00ffb3 !important;
        border-color: #00ffb3 !important;
        background-color: #1e293b !important;
        border-radius: 20px;
        padding: 5px 15px;
        margin: 5px;
        transition: all 0.2s;
        white-space: normal; 
        line-height: 1.2;
        height: auto; 
    }
    .stButton>button:hover {
        background-color: #00ffb3 !important;
        color: #0f172a !important;
        box-shadow: 0 0 10px #00ffb3;
    }
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

    # Botão para Limpar Histórico do Chat
    if st.button("Limpar Histórico do Chat 🧹"):
        st.session_state.messages = []
        st.session_state.prompt_starter_value = None 
        if 'h' in st.query_params:
            del st.query_params['h']
        st.rerun() 

    st.markdown("---")
    st.markdown(f"**Modelo em Uso:** `{MODELO_ESTAVEL}` (Rápido e Estável)")
    st.markdown("Desenvolvido para auxiliar em suas dúvidas no geral. A IA pode cometer erros, sempre verifique as respostas.")
    st.link_button("✉️ E-mail Para o Suporte ISA", "mailto:isabellyidelfonso@gmail.com")

# --- CONTEÚDO PRINCIPAL ---
st.title("ISA AI") 

# Animação de digitação
st.markdown(f"""<h1 class="typing">A sua IA para o próximo passo.</h1>""", unsafe_allow_html=True)
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
