import joblib
import os
import numpy as np

# --- 1. Carregar os Artefatos (O "Cérebro" e o "Tradutor") ---

# Caminho para os modelos salvos na FASE 3
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MODEL_PATH = os.path.join(PROJECT_ROOT, 'modelos', 'health_score_classifier.joblib')
ENCODER_PATH = os.path.join(PROJECT_ROOT, 'modelos', 'label_encoder.joblib')

# Carrega os arquivos
try:
    model = joblib.load(MODEL_PATH)
    encoder = joblib.load(ENCODER_PATH)
    print("Modelo de Health Score e Encoder carregados com sucesso.")
except FileNotFoundError:
    print(f"Erro: Modelos não encontrados em {PROJECT_ROOT}/modelos/")
    print("Execute a FASE 3 (notebook 03) para treinar e salvar os modelos.")
    model = None
    encoder = None

# --- 2. A "Tabela de Regras" de Saída (Baseada na sua imagem) ---

REGRAS_SAIDA = {
    'Alta Performance': {
        "Atingimento de Meta (TPV)": ">= 100%",
        "Health Score": "90-100",
        "Ação Recomendada": "monitoria continua - oprotunidades de cross-sell"
    },
    'Boa Performance': {
        "Atingimento de Meta (TPV)": "80 a 99%",
        "Health Score": "75-89",
        "Ação Recomendada": "manter condições + avaliar upsell"
    },
    'Performance Regular': {
        "Atingimento de Meta (TPV)": "50 a 79%",
        "Health Score": "50-74",
        "Ação Recomendada": "revisão de condições + campanhas de engajamento"
    },
    'Baixa Performance': {
        "Atingimento de Meta (TPV)": "10 a 49%",
        "Health Score": "25-49",
        "Ação Recomendada": "ações corretivas (renegociação, ajuste de taxa)"
    },
    'Critico': {
        "Atingimento de Meta (TPV)": "< 10%",
        "Health Score": "0-24",
        "Ação Recomendada": "renegociação imediata ou decrescimento"
    }
}

# --- 3. A Função de Predição (O "Motor") ---

def predict_health_score(df_features_row):
    """
    Recebe UMA LINHA de features de um cliente e retorna a classificação completa.
    
    Args:
        df_features_row (pd.DataFrame): Um DataFrame de 1 linha com as
                                        features da FASE 2.
    
    Returns:
        dict: Um dicionário com a classificação e a ação recomendada.
    """
    
    if model is None or encoder is None:
        return {"erro": "Modelos não carregados."}
        
    # Garante que as colunas estejam na ordem correta que o modelo espera
    # (O 'model.feature_names_in_' foi salvo durante o treino na FASE 3)
    try:
        features_para_prever = df_features_row[model.feature_names_in_]
    except KeyError as e:
        return {"erro": f"Feature ausente nos dados de entrada: {e}"}

    # --- O CORAÇÃO DA IA ---
    
    # 1. Prever a CLASSE (formato numérico, ex: 2)
    predicao_numerica = model.predict(features_para_prever)
    
    # 2. Prever a PROBABILIDADE (o "Health Score" real)
    # Retorna um array, ex: [[0.05, 0.15, 0.7, 0.05, 0.05]]
    probabilidades = model.predict_proba(features_para_prever)
    
    # Pega a probabilidade máxima (o 0.7) e transforma em Score (70)
    score_real = np.max(probabilidades) * 100
    
    # 3. "Traduzir" a classe numérica para texto
    # ex: 2 -> 'Performance Regular'
    classe_texto = encoder.inverse_transform(predicao_numerica)[0]
    
    # 4. Buscar a linha de classificação na nossa tabela de regras
    linha_de_saida = REGRAS_SAIDA.get(classe_texto, {})
    
    # 5. Montar a resposta final
    resultado = {
        "Classificação": classe_texto,
        "Health Score (Calculado)": round(score_real, 2),
        "Range Score (Regra)": linha_de_saida.get("Health Score"),
        "Ação Recomendada": linha_de_saida.get("Ação Recomendada"),
        "Atingimento de Meta (Regra)": linha_de_saida.get("Atingimento de Meta (TPV)")
    }
    
    return resultado