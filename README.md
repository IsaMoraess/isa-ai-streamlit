# 🤖 ISA AI – Assistente Inteligente com Streamlit e Groq

ISA AI é uma aplicação interativa construída com **Streamlit**, que simula um assistente de inteligência artificial integrado à API da **Groq**. O projeto oferece uma interface moderna, personalização visual e funcionalidades avançadas para resposta, análise de arquivos e persistência de histórico.

---

## 🚀 Funcionalidades Principais

- ✅ Interface com tema escuro e estilo neon personalizado  
- ✅ Integração com o modelo `llama-3.1-8b-instant` via Groq  
- ✅ Histórico de chat salvo na URL (compartilhável)  
- ✅ Upload de arquivos (.txt, .py, .md, .java etc.) para análise  
- ✅ Sugestões rápidas de prompts iniciais  
- ✅ Configurações avançadas:
  - Estilo da resposta
  - Foco da resposta
  - Tamanho máximo (tokens)  
- ✅ Indicador visual de chave da API  
- ✅ Limpeza de histórico com um clique

---

## 📁 Estrutura do Projeto

isa-ai-streamlit/
│
├── Isa_assistente.py # Código principal da aplicação
├── requer.txt # Dependências do projeto
├── LEIAME.txt # Instruções de execução (ambiente)
└── README.md # (Você irá adicionar este arquivo)

---

## 🛠 Tecnologias Utilizadas

- Python 3.10+  
- Streamlit  
- Groq API  
- JSON / Base64  
- CSS customizado para tema e animações

---

## 📦 Instalação

### 1️⃣ Clone o repositório:
```bash
git clone https://github.com/IsaMoraess/isa-ai-streamlit.git
cd isa-ai-streamlit

2️⃣ Crie e ative um ambiente virtual (opcional):
conda create --name isaai python=3.13
conda activate isaai

3️⃣ Instale as dependências:
pip install -r requer.txt

▶️ Como Executar
streamlit run Isa_assistente.py
Acesse no navegador o endereço gerado (ex: http://localhost:8501).

🔑 Uso da Groq API
Para utilizar a IA, insira sua chave no campo lateral:
Obtenha a chave em: https://console.groq.com/keys
Cole na barra lateral da aplicação

👩‍💻 Autoria
Projeto desenvolvido por Isabelly Moraes
📧 Contato: isabellyidelfonso@gmail.com
