import streamlit as st
import google.generativeai as genai
import json
import os

# CONFIGURAÇÃO SEGURA DA API
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
else:
    st.error("⚠️ Chave 'GEMINI_API_KEY' não encontrada nos Secrets do Streamlit!")

SAVE_FILE = "rpg_engine_save.json"

# REGRAS PADRÃO AJUSTADAS PARA O NOVO ESTILO VISUAL E ESCOLHAS AMPLAS
REGRAS_PADRAO = """[DIRETRIZ DE INICIALIZAÇÃO OBRIGATÓRIA]
- Início do Jogo: O jogador SEMPRE começa estritamente como uma criança de 6 anos de idade.
- Localização Inicial: Um local totalmente diferente e gerado de forma 100% aleatória a cada Novo Jogo.
- Inventário Inicial: O jogador começa COMPLETAMENTE SEM NADA.
- Tabula Rasa Absoluta: O personagem não possui passado, memórias ou conhecimento sobre o mundo.

[DIRETRIZ DE ESTRUTURA DE ESCOLHAS DINÂMICAS E VARIÁVEIS]
- Padrão Estruturado: Termine os turnos com opções numéricas bem específicas de escolha.
- Quantidade Flutuante: O número de opções deve variar organicamente conforme a situação do cenário, podendo ir de 3 até 6 escolhas numéricas completas para dar mais profundidade estratégica quando necessário.
- Exceção Aberta: Perguntas totalmente em aberto ("O que você faz?") são raras e exclusivas de áreas seguras ou momentos de total calmaria.

[SISTEMA DE PROFICIÊNCIA E EVOLUÇÃO ORGÂNICA]
- Progresso por Uso (Prática): Toda ação repetida gera ganho direto e orgânico de proficiência percentual.
- Evolução de Nível e Fusão: Habilidades mudam de nome e sobem de nível conforme o uso (Ex: Caminhada -> Corrida -> Corrida Suprema com Poder). Habilidades compatíveis se fundem em técnicas superiores de Rank maior.

[UNIVERSOS CONVERGENTES (INTEGRAÇÃO TOTAL)]
- Dragon Ball, Bleach, Shangri-La Frontier, Solo Leveling, Tensei Slime: Inclusão absoluta de todos os conceitos, técnicas e sistemas."""

def carregar_jogo():
    if os.path.exists(SAVE_FILE):
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return resetar_jogo()

def resetar_jogo():
    return {
        "atributos": {"Poder de Luta": "0.5", "Estamina": "100%", "Sanidade": "100%", "Reputação": "Desconhecido", "Moedas": "0"},
        "inventario": "Completamente sem nada.",
        "habilidades": "Nenhuma. Estado de Tabula Rasa.",
        "regras_custom": REGRAS_PADRAO,
        "historico": []
    }

def salvar_jogo(state):
    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=4)

if "game_state" not in st.session_state:
    st.session_state.game_state = carregar_jogo()

state = st.session_state.game_state

# ----------------- INTERFACE GRÁFICA (UI) -----------------
st.set_page_config(page_title="AI RPG Engine Automation", layout="wide", initial_sidebar_state="expanded")

st.sidebar.title("🎮 Menu do Sistema")

if "confirmar_reset" not in st.session_state:
    st.session_state.confirmar_reset = False

col1, col2 = st.sidebar.columns(2)
if col2.button("💾 Salvar", use_container_width=True):
    salvar_jogo(state)
    st.sidebar.success("Progresso salvo!")

if not st.session_state.confirmar_reset:
    if col1.button("✨ Novo Jogo", use_container_width=True):
        st.session_state.confirmar_reset = True
        st.rerun()
else:
    st.sidebar.warning("⚠️ Deseja LIMPAR TUDO?")
    col_sim, col_nao = st.sidebar.columns(2)
    if col_sim.button("✅ Sim", use_container_width=True):
        st.session_state.game_state = resetar_jogo()
        salvar_jogo(st.session_state.game_state)
        st.session_state.confirmar_reset = False
        st.rerun()
    if col_nao.button("❌ Não", use_container_width=True):
        st.session_state.confirmar_reset = False
        st.rerun()

st.sidebar.markdown("---")
st.sidebar.subheader("📦 Backup (Nuvem / Celular)")

json_save_string = json.dumps(state, ensure_ascii=False, indent=4)
st.sidebar.download_button(
    label="📥 Baixar Arquivo de Save",
    data=json_save_string,
    file_name="rpg_engine_save.json",
    mime="application/json",
    use_container_width=True
)

arquivo_enviado = st.sidebar.file_uploader("📤 Carregar Arquivo de Save", type=["json"])
if arquivo_enviado is not None:
    try:
        dados_carregados = json.load(arquivo_enviado)
        st.session_state.game_state = dados_carregados
        salvar_jogo(dados_carregados)
        st.sidebar.success("Progresso restaurado!")
        st.rerun()
    except Exception:
        st.sidebar.error("Arquivo de save inválido.")

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Atributos Vitais")
for attr in state["atributos"]:
    state["atributos"][attr] = st.sidebar.text_input(attr, state["atributos"][attr])

st.title("🧙‍♂️ Mestre Automatizado")

aba_chat, aba_inv, aba_skills, aba_regras = st.tabs(["💬 Jogo & Narrativa", "🎒 Inventário", "🥋 Habilidades", "⚙️ Regras"])

with aba_chat:
    container_chat = st.container(height=600)
    with container_chat:
        for msg in state["historico"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    if prompt := st.chat_input("Digite sua escolha ou ação..."):
        with container_chat:
            with st.chat_message("user"):
                st.write(prompt)
        
        state["historico"].append({"role": "user", "content": prompt})

        instrucao_sistema = f"""
        Você é o Mestre do RPG. Responda APENAS em um JSON estruturado.
        Status Atual: {json.dumps(state['atributos'])}
        Inventário Atual: {state['inventario']}
        Habilidades Atuais: {state['habilidades']}
        Regras do Sistema: {state['regras_custom']}
        
        DIRETRIZ DE FORMATAÇÃO DO CAMPO 'NARRATIVA':
        Monte o campo "narrativa" obrigatoriamente usando Markdown estruturado em blocos exatamente como o exemplo a seguir:
        
        ### [Título do Evento ou Local]
        **Resultado do Dado (Se aplicável):** X (Descrição do sucesso/falha)
        
        O Confronto / Ação:
        (Texto narrativo descrevendo os acontecimentos)
        
        🎮 ALERTA DE SISTEMA: EVOLUÇÃO DE HABILIDADE (Mecânica Shangri-La / Solo Leveling)
        [Condição Atendida]: (Se houver ganho de proficiência ou evolução/fusão de skill, coloque aqui com bônus e ranks)
        
        🎁 Espólios de Guerra & Consequências (Se houver loot, moedas ou benefícios territoriais/alianças)
        
        📈 Atualização do Sistema Inconsciente
        Estamina: X% ➔ Y%
        Poder de Luta Individual: X ➔ Y
        Poder de Luta Combinado/Mascote: (Se houver)
        
        📊 Painel do Jogador (Mostre os dados em uma tabela Markdown limpa contendo Poder de Luta, Estamina, Moedas, Territórios, Equipamentos e Resumo do Inventário)
        
        🗺️ Cenário: (Contexto atual do mapa, nós, clima e dia/tempo do jogo)
        
        (Pergunta final de ação do Mestre)
        [1] Opção Dinâmica 1
        [2] Opção Dinâmica 2
        ...
        [6] Opção Dinâmica 6 (Apresente de 3 a 6 opções numeradas dependendo da complexidade imediata do cenário)
        """

        try:
            model = genai.GenerativeModel(model_name="gemini-2.5-flash", system_instruction=instrucao_sistema, generation_config={"response_mime_type": "application/json"})
            response = model.generate_content([{"role": "user", "parts": [m["content"]]} for m in state["historico"]])
            dados = json.loads(response.text)
            state["atributos"], state["inventario"], state["habilidades"] = dados["atributos"], dados["inventario"], dados["habilidades"]
            
            with container_chat:
                with st.chat_message("assistant"):
                    st.write(dados["narrativa"])
            state["historico"].append({"role": "assistant", "content": dados["narrativa"]})
            salvar_jogo(state)
            st.rerun()
        except Exception as e:
            st.error(f"Erro no processamento da IA: {e}")

with aba_inv: state["inventario"] = st.text_area("Inventário", state["inventario"], height=300)
with aba_skills: state["habilidades"] = st.text_area("Habilidades", state["habilidades"], height=300)
with aba_regras: state["regras_custom"] = st.text_area("Regras", state["regras_custom"], height=300)
