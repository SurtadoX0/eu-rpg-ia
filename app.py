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

# REGRAS PADRÃO ATUALIZADAS (ESTILO BR / SEM FRESCURA)
REGRAS_PADRAO = """[DIRETRIZ DE INICIALIZAÇÃO OBRIGATÓRIA]
- Início do Jogo: O jogador SEMPRE começa estritamente como uma criança de 6 anos de idade.
- Localização Inicial: Um local totalmente diferente e gerado de forma 100% aleatória a cada Novo Jogo.
- Inventário Inicial: O jogador começa COMPLETAMENTE SEM NADA.
- Tabula Rasa Absoluta: O personagem não possui passado, memórias ou conhecimento sobre o mundo.

[ESTILO NARRATIVO: PAPO RETO / NOIS É BR]
- Linguagem Direta e Sem Frescura: O Mestre deve usar uma linguagem natural do Brasil, sem palavras difíceis, termos poéticos ou descrições muito requintadas/longas (nada de "paredes lapidadas", "dóceis aromas", etc). 
- Foco na Ação: Seja conciso, ágil e use termos simples e dinâmicos, mantendo uma vibe de webnovel/manhwa gamer nacional.

[DIRETRIZ DE ESTRUTURA DE ESCOLHAS DINÂMICAS]
- Padrão Estruturado: Termine os turnos com opções numéricas fechadas.
- Quebra de Linha Obrigatória: Cada opção DEVE ficar em sua própria linha isolada, uma embaixo da outra, usando quebra de linha dupla (\\n\\n).
- Quantidade Flutuante: O número de escolhas varia de acordo com a situação (de 3 até 6 opções completas).

[SISTEMA DE PROFICIÊNCIA E EVOLUÇÃO ORGÂNICA]
- Progresso por Uso (Prática): Toda ação repetida gera ganho direto e orgânico de proficiência percentual.
- Evolução de Nível e Fusão: Habilidades mudam de nome e sobem de nível conforme o uso. Habilidades compatíveis se fundem em técnicas superiores de Rank maior.

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
        Você é o Mestre do RPG. Responda APENAS em um JSON estruturado válido.
        Status Atual: {json.dumps(state['atributos'])}
        Inventário Atual: {state['inventario']}
        Habilidades Atuais: {state['habilidades']}
        Regras do Sistema: {state['regras_custom']}
        
        DIRETRIZ DE FILTRAGEM DE NARRATIVA:
        Monte o campo "narrativa" em Markdown respeitando a omissão de blocos vazios:
        - OMITA os blocos '🎁 Espólios', '📈 Atualização' e '🗺️ Cenário' se não houver mudanças reais neste turno.
        
        DIRETRIZ DE LINGUAGEM BR:
        Use tom direto, conciso, ágil e informal. Evite textos requintados, floreados ou palavras difíceis. Seja focado nos fatos e na ação.
        
        DIRETRIZ CRÍTICA DE QUEBRA DE LINHA NAS OPÇÕES:
        No final do campo "narrativa", as opções numéricas de escolha DEVEM ser separadas por duas quebras de linha de texto (\\n\\n). Elas precisam ficar estritamente uma embaixo da outra, sem exceção.
        
        Exemplo exato de como deve vir no texto do JSON:
        "\\n\\n[1] Primeira opção\\n\\n[2] Segunda opção"
        
        FORMATO JSON EXIGIDO:
        {{
          "narrativa": "Sua narração aqui...\\n\\n[1] Opção um\\n\\n[2] Opção dois",
          "atributos": {{
            "Poder de Luta": "Valor", "Estamina": "Valor", "Sanidade": "Valor", "Reputação": "Valor", "Moedas": "Valor"
          }},
          "inventario": "Lista de itens",
          "habilidades": "Lista de habilidades"
        }}
        """

        try:
            model = genai.GenerativeModel(model_name="gemini-2.5-pro", system_instruction=instrucao_sistema, ...
            response = model.generate_content([{"role": "user", "parts": [m["content"]]} for m in state["historico"]])
            dados = json.loads(response.text)
            
            state["atributos"] = dados.get("atributos", state["atributos"])
            state["inventario"] = dados.get("inventario", state["inventario"])
            state["habilidades"] = dados.get("habilidades", state["habilidades"])
            narrativa_final = dados.get("narrativa", "Erro no formato.")
            
            with container_chat:
                with st.chat_message("assistant"):
                    st.write(narrativa_final)
            state["historico"].append({"role": "assistant", "content": narrativa_final})
            salvar_jogo(state)
            st.rerun()
        except Exception as e:
            st.error(f"Erro no processamento da IA: {e}")

with aba_inv: state["inventario"] = st.text_area("Inventário", state["inventario"], height=300)
with aba_skills: state["habilidades"] = st.text_area("Habilidades", state["habilidades"], height=300)
with aba_regras: state["regras_custom"] = st.text_area("Regras", state["regras_custom"], height=300)
