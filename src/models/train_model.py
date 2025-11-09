import pandas as pd
import joblib
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import classification_report

# Caminho raiz do projeto (sobe 2 níveis: src/models -> projeto_raiz)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, 'dados', 'processed', 'features_clientes.csv')
MODEL_OUTPUT_PATH = os.path.join(PROJECT_ROOT, 'modelos')

def apply_classification_rules(df):
    """
    Aplica as regras de negócio (do saida.xlsx) para criar o "label" (alvo).
    Usa a coluna 'atingimento_meta_tpv' como base.
    """
    # atingimento_meta_tpv já é um percentual (ex: 1.12, 0.75)
    
    def get_class(atingimento):
        if atingimento >= 1.0:
            return 'Alta Performance'
        if atingimento >= 0.8:
            return 'Boa Performance'
        if atingimento >= 0.5:
            return 'Performance Regular'
        if atingimento >= 0.1:
            return 'Baixa Performance'
        return 'Critico' # Menor que 0.1 (10%)

    df['Classificacao'] = df['atingimento_meta_tpv'].apply(get_class)
    return df

def train_and_save_model():
    """
    Função principal da FASE 3.
    Carrega features, aplica regras, treina o modelo e salva os artefatos.
    """
    
    print("--- Iniciando FASE 3: Treinamento do Modelo ---")
    
    # 1. Carregar DataFrame de Features (da FASE 2)
    try:
        df_features = pd.read_csv(PROCESSED_DATA_PATH, index_col='id_cliente')
        print(f"DataFrame de features carregado: {df_features.shape}")
    except FileNotFoundError:
        print(f"Erro: Arquivo de features não encontrado em {PROCESSED_DATA_PATH}")
        print("Certifique-se que a FASE 2 (notebook 02) foi executada com sucesso.")
        return

    # 2. Definição do Alvo (Label 'y')
    # Aplicamos as regras do 'saida.xlsx' para criar nossa coluna alvo
    df_features = apply_classification_rules(df_features)
    
    # 3. Preparação para Treino
    
    # X = São todas as 'features' (atributos) que calculamos
    # (Removendo colunas que não são features, como o TPV total ou a própria meta)
    features_list = [
        'atingimento_meta_tpv', 
        'margem_op_media', 
        'tendencia_tpv', 
        'volatilidade_tpv',
        # Adiciona todas as colunas de 'mix_pct_' que criamos
    ] + [col for col in df_features.columns if 'mix_pct_' in col]
    
    X = df_features[features_list]
    
    # y = É o 'alvo' que queremos prever (a Classificação)
    y = df_features['Classificacao']
    
    # Limpa possíveis NaNs (ex: se um cliente teve 0 transações)
    X = X.fillna(0)

    # 4. Codificar 'y' (Transformar 'Alta Performance' em 0, 'Boa' em 1, etc)
    encoder = LabelEncoder()
    y_encoded = encoder.fit_transform(y)
    
    print(f"Classes encontradas e codificadas: {encoder.classes_}")

    # 5. Split (Dividir em dados de Treino e Teste)
    # Usamos 80% para treinar, 20% para testar se o modelo acertou
    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, 
        test_size=0.2, 
        random_state=42, # Garante reprodutibilidade
        stratify=y_encoded # Garante que a proporção de classes seja igual no treino/teste
    )

    print(f"Dados divididos: {len(X_train)} para treino, {len(X_test)} para teste.")

    # 6. Treinamento do Modelo (Random Forest)
    print("Treinando o modelo RandomForestClassifier...")
    model = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=10)
    model.fit(X_train, y_train)
    print("Treinamento concluído.")

    # 7. Avaliação (Ver se o modelo é bom)
    y_pred = model.predict(X_test)
    print("\n--- Relatório de Classificação (Performance do Modelo) ---")
    # Imprime o relatório com as classes reais (decodificadas)
    print(classification_report(y_test, y_pred, target_names=encoder.classes_))
    
    # 8. Salvar Modelo e Encoder
    # Criamos a pasta /modelos/ se ela não existir
    os.makedirs(MODEL_OUTPUT_PATH, exist_ok=True)
    
    model_path = os.path.join(MODEL_OUTPUT_PATH, 'health_score_classifier.joblib')
    encoder_path = os.path.join(MODEL_OUTPUT_PATH, 'label_encoder.joblib')
    
    joblib.dump(model, model_path)
    joblib.dump(encoder, encoder_path)
    
    print(f"\nModelo salvo em: {model_path}")
    print(f"Encoder salvo em: {encoder_path}")
    print("--- FASE 3 Concluída ---")

if __name__ == '__main__':
    # Permite rodar este script diretamente do terminal
    # (com o venv ativado): python src/models/train_model.py
    train_and_save_model()