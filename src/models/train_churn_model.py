import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix
import warnings

# Ignorar avisos futuros do scikit-learn
warnings.filterwarnings('ignore', category=FutureWarning)

# Caminhos
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, 'dados', 'processed', 'features_churn_clientes.csv')
MODEL_OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'modelos')

def train_and_save_churn_model():
    """
    Função principal da FASE 5 (Modelagem).
    Carrega features+labels de churn, treina o modelo e salva o artefacto.
    """
    
    print("--- Iniciando FASE 5: Treinamento do Modelo de Churn ---")
    
    # 1. Carregar DataFrame (da FASE 5 - Preparação)
    try:
        df_churn_treino = pd.read_csv(PROCESSED_DATA_PATH, index_col='id_cliente')
        print(f"DataFrame de treino de churn carregado: {df_churn_treino.shape}")
    except FileNotFoundError:
        print(f"Erro: Arquivo 'features_churn_clientes.csv' não encontrado em {PROCESSED_DATA_PATH}")
        print("Certifique-se que a FASE 5 (notebook 04) foi executada com sucesso.")
        return

    # 2. Preparação para Treino
    
    # y = É o 'alvo' que queremos prever (o rótulo 0 ou 1)
    y = df_churn_treino['is_churn']
    
    # X = São todas as 'features' (atributos)
    # IMPORTANTE: Excluímos 'atingimento_meta_tpv', 'tpv_meta', 'tpv_total'
    # e 'Classificacao' (se existir), pois são do Modelo 1 (Score).
    # Também excluímos o próprio 'is_churn' da lista de features.
    
    features_para_excluir = [
        'atingimento_meta_tpv', 'tpv_meta', 'tpv_total', 
        'Classificacao', 'is_churn'
    ]
    
    features_list = [col for col in df_churn_treino.columns if col not in features_para_excluir]
    
    X = df_churn_treino[features_list]
    
    # Limpa possíveis NaNs (ex: se um cliente teve 0 transações)
    X = X.fillna(0)
    
    print(f"Features selecionadas para o modelo de churn: {features_list}")
    
    # 3. Split (Dividir em dados de Treino e Teste)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, 
        test_size=0.25, # Usar 25% para teste
        random_state=42,
        stratify=y # CRUCIAL para churn: garante que a proporção de 0s e 1s
                   # seja a mesma no treino e no teste.
    )

    print(f"Dados divididos: {len(X_train)} para treino, {len(X_test)} para teste.")
    print(f"Distribuição de Churn no Treino:\n{y_train.value_counts(normalize=True)}")

    # 4. Treinamento do Modelo (Random Forest com ajuste para desequilíbrio)
    print("Treinando o modelo RandomForestClassifier para Churn...")
    
    # class_weight='balanced' é fundamental.
    # Diz ao modelo: "Dê mais importância (peso) aos erros na classe '1' (churn),
    # porque ela é mais rara e mais importante de acertar."
    model_churn = RandomForestClassifier(
        n_estimators=100, 
        random_state=42, 
        max_depth=8,
        class_weight='balanced' 
    )
    
    model_churn.fit(X_train, y_train)
    print("Treinamento concluído.")

    # 5. Avaliação (Ver se o modelo é bom)
    y_pred = model_churn.predict(X_test)
    
    print("\n--- Relatório de Classificação (Churn) ---")
    # Foco no 'recall' da classe '1':
    # De todos os clientes que REALMENTE deram churn, quantos o modelo acertou?
    print(classification_report(y_test, y_pred, target_names=['Classe 0 (Ativo)', 'Classe 1 (Churn)']))
    
    print("\n--- Matriz de Confusão ---")
    # [Verdadeiro Negativo, Falso Positivo]
    # [Falso Negativo    , Verdadeiro Positivo]
    print(confusion_matrix(y_test, y_pred))
    
    # 6. Salvar Modelo
    os.makedirs(MODEL_OUTPUT_PATH, exist_ok=True)
    model_path = os.path.join(MODEL_OUTPUT_PATH, 'churn_predictor.joblib')
    
    joblib.dump(model_churn, model_path)
    
    print(f"\nModelo de CHURN salvo em: {model_path}")
    print("--- FASE 5 (Modelagem) Concluída ---")

if __name__ == '__main__':
    # Permite rodar este script diretamente do terminal
    # (com o venv ativado): python src/models/train_churn_model.py
    train_and_save_churn_model()