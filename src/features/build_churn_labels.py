import pandas as pd
import os
import sys

# Adiciona a raiz do projeto ao path para podermos importar 'make_dataset'
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
SRC_PATH = os.path.join(PROJECT_ROOT, 'src')
if SRC_PATH not in sys.path:
    sys.path.append(SRC_PATH)

from data.make_dataset import get_historical_data

def create_churn_labels(df_historico, days_for_churn=45):
    """
    Define o "label" de churn (1 ou 0) para cada cliente.
    
    Regra: Se a última transação do cliente ocorreu há mais de 
    'days_for_churn' dias (default=45) da data mais recente no dataset,
    ele é marcado como churn (1).

    Args:
        df_historico (pd.DataFrame): O DataFrame bruto da FASE 1.
        days_for_churn (int): Janela em dias para considerar churn.

    Returns:
        pd.DataFrame: Um DataFrame com [id_cliente (índice), is_churn (0 ou 1)]
    """
    
    print(f"Iniciando definição de labels de churn (Janela: {days_for_churn} dias)")
    
    if 'data' not in df_historico.columns or 'id_cliente' not in df_historico.columns:
        print("Erro: df_historico deve conter 'data' e 'id_cliente'.")
        return None
        
    # 1. Converter 'data' para datetime (crucial)
    df_historico['data'] = pd.to_datetime(df_historico['data'])

    # 2. Encontrar a data mais recente EM TODO o dataset
    data_mais_recente_global = df_historico['data'].max()
    print(f"Data mais recente no dataset: {data_mais_recente_global.date()}")

    # 3. Encontrar a última data de transação PARA CADA cliente
    df_ultima_transacao = df_historico.groupby('id_cliente')['data'].max().to_frame('ultima_transacao')

    # 4. Calcular há quantos dias foi a última transação
    df_ultima_transacao['dias_desde_ultima_transacao'] = (
        data_mais_recente_global - df_ultima_transacao['ultima_transacao']
    ).dt.days

    # 5. Aplicar a Regra de Churn
    # Se 'dias_desde_ultima_transacao' > 45, então 'is_churn' = 1
    df_ultima_transacao['is_churn'] = (
        df_ultima_transacao['dias_desde_ultima_transacao'] > days_for_churn
    ).astype(int)
    
    print("Labels de churn definidos.")
    
    # Retorna apenas o índice (id_cliente) e o label (is_churn)
    return df_ultima_transacao[['is_churn']]

if __name__ == '__main__':
    # Teste rápido do módulo (rode com: python src/features/build_churn_labels.py)
    
    print("--- Testando módulo build_churn_labels ---")
    
    # 1. Busca os dados brutos
    df_raw = get_historical_data(dat_start_filter='2024-01-01') # Use um período longo
    
    if df_raw is not None and not df_raw.empty:
        # 2. Gera os labels
        df_labels = create_churn_labels(df_raw, days_for_churn=45)
        
        if df_labels is not None:
            print("\n--- Resultado do Teste ---")
            print(df_labels.head())
            print("\nDistribuição de Churn:")
            print(df_labels['is_churn'].value_counts(normalize=True))
    else:
        print("Falha ao carregar dados históricos para o teste.")