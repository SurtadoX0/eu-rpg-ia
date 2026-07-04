import streamlit as st
import google.generativeai as genai
import json
import os

# CONFIGURAÇÃO DA API 
API_KEY = "AQ.Ab8RN6KmmYLr2ccKqnG6wc2pRTrVAVNZEAp8buG3Jdc1VFHJhw"
genai.configure(api_key=API_KEY)

SAVE_FILE = "rpg_engine_save.json"

# REGRAS PADRÃO COMPLETAS
REGRAS_PADRAO = """[DIRETRIZ DE INICIALIZAÇÃO OBRIGATÓRIA]
- Início do Jogo: O jogador SEMPRE começa estritamente como uma criança de 6 anos de idade.
- Localização Inicial: Um local totalmente diferente e gerado de forma 100% aleatória a cada Novo Jogo.
- Inventário Inicial: O jogador começa COMPLETAMENTE SEM NADA (absolutamente nenhum item, arma, ferramenta ou recurso).
- Tabula Rasa Absoluta: O personagem não possui passado, memórias, fardos ou qualquer conhecimento sobre o mundo.
- Limitação de Aprendizado: É mandatório que o personagem falhe ou seja incapaz de realizar ações complexas no início.

[SISTEMA DE RAÇAS E DESCOBERTA OCULTA]
- Linhagem Imprevisível: O jogador pode nascer pertencendo a qualquer raça, mutação ou hibridismo dos 5 universos convergentes.
- Despertar Tardio: A verdadeira natureza pode ser mantida em segredo absoluto, manifestando-se apenas sob gatilhos lógicos.
- Pistas Orgânicas: O Mestre deve injetar pistas sutis em vez de exposições baratas.

[SISTEMA DE PSICOLOGIA E SOBREVIVÊNCIA]
- Sanidade e Trauma: A mente de uma criança é frágil. Presenciar horrores drena a Sanidade. Sanidade baixa resulta em tremores, pesadelos ou paralisia.
- Percepção Mundial: O mundo reage à sua presença. NPCs e monstros podem vê-lo como presa fácil, aberração ou alguém digno de proteção.

[UNIVERSOS CONVERGENTES (INTEGRAÇÃO TOTAL)]
- Dragon Ball, Bleach, Shangri-La Frontier, Solo Leveling, Tensei Slime: Inclusão absoluta de todos os conceitos, técnicas e sistemas.

[SISTEMA DE TEMPO E TURNOS]
- Ciclo Diário: Dividido estritamente em Manhã, Tarde e Noite. 
- Cada ação complexa, expedição ou treino pesado consome exatamente 1 Turno.

[ATRIBUTOS VITAIS E PROGRESSÃO]
- Estamina: Consumida por ações físicas e habilidades.
- Poder de Luta (PL): Valor absoluto de força, recalculado após feitos ou evoluções.
- Estado Corporal: Condição física real (Fadiga do SNC, lesões). Treinos até a falha amplificam PL.

[MECÂNICAS DE JOGO]
- Ações com Dado d20: Rolagens realistas e punitivas.
- A Morte Não é o Fim: Gatilho para recomeço imprevisível, reencarnação ou transição caótica.
- Alertas de Sistema: "[ALERTA DE SISTEMA: NOVA HABILIDADE ADQUIRIDA]".
- Fusão de Habilidades: Habilidades compatíveis se fundem."""

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

# --- NOVO SISTEMA DE BACKUP INFALÍVEL PARA NUVEM ---
st.sidebar.markdown("---")
st.sidebar.subheader("📦 Backup (Nuvem / Celular)")

# Botão de Exportar Save
json_save_string = json.dumps(state, ensure_ascii=False, indent=4)
st.sidebar.download_button(
    label="📥 Baixar Arquivo de Save",
    data=json_save_string,
    file_name="rpg_engine_save.json",
    mime="application/json",
    use_container_width=True
)

# Campo de Importar Save
arquivo_enviado = st.sidebar.file_uploader("📤 Carregar Arquivo de Save", type=["json"])
if arquivo_enviado is not None:
    try:
        dados_carregados = json.load(arquivo_enviado)
        st.session_state.game_state = dados_carregados
        salvar_jogo(dados_carregados)
        st.sidebar.success("Progresso restaurado com sucesso!")
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
    container_chat = st.container(height=500)
    with container_chat:
        for msg in state["historico"]:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

    if prompt := st.chat_input("Digite ação..."):
        with container_chat:
            with st.chat_message("user"):
                st.write(prompt)
        
        state["historico"].append({"role": "user", "content": prompt})

        instrucao_sistema = f"""
        Você é o Mestre do RPG. Responda APENAS em JSON.
        Status: {json.dumps(state['atributos'])}
        Regras: {state['regras_custom']}
        
        FORMATO JSON:
        {{
          "narrativa": "Narração com opções 1, 2, 3 numeradas ao final.",
          "atributos": {{
            "Poder de Luta": "Valor", "Estamina": "Valor", "Sanidade": "Valor", "Reputação": "Valor", "Moedas": "Valor"
          }},
          "inventario": "...",
          "habilidades": "..."
        }}
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
            st.error(f"Erro: {e}")

with aba_inv: state["inventario"] = st.text_area("Inventário", state["inventario"], height=300)
with aba_skills: state["habilidades"] = st.text_area("Habilidades", state["habilidades"], height=300)
with aba_regras: state["regras_custom"] = st.text_area("Regras", state["regras_custom"], height=300)
