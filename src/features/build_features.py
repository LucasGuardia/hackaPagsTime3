import pandas as pd
import numpy as np
from scipy.stats import linregress

def calculate_trend(series):
    """
    Calcula a inclinação (tendência) de uma série temporal.
    Usa regressão linear sobre os valores ordenados pelo tempo.
    """
    # Garante que os dados estão ordenados (embora a query já deva fazer isso)
    y = series.values
    x = np.arange(len(y))
    
    # linregress retorna (slope, intercept, rvalue, pvalue, stderr)
    # Queremos apenas o 'slope' (inclinação)
    try:
        slope, _, _, _, _ = linregress(x, y)
    except ValueError:
        # Retorna 0 se não puder calcular (ex: dados insuficientes)
        return 0
    
    # Retorna 0 se a inclinação for NaN (acontece com dados constantes)
    return slope if not np.isnan(slope) else 0

def engineer_features(df_historico, df_metas=None):
    """
    Transforma o DataFrame histórico (várias linhas por cliente)
    em um DataFrame de features (uma linha por cliente).
    
    Args:
        df_historico (pd.DataFrame): O DataFrame da FASE 1 (make_dataset.py)
        df_metas (pd.DataFrame, opcional): Um DataFrame com 'id_cliente' como índice
                                           e uma coluna 'tpv_meta'.

    Returns:
        pd.DataFrame: A tabela de features (uma linha por cliente).
    """
    
    print(f"Iniciando engenharia de atributos para {df_historico['id_cliente'].nunique()} clientes...")
    
    # 0. Garante a ordem dos dados para o cálculo de tendência
    df_historico = df_historico.sort_values(by=['id_cliente', 'data'])

    # 1. Carregar DataFrame (cria a base de features)
    df_features = pd.DataFrame(index=df_historico['id_cliente'].unique())
    df_features.index.name = 'id_cliente'
    
    # 2. Atributo 1: TPV (Peso 70%)
    df_agregado = df_historico.groupby('id_cliente')['tpv_dia'].sum().to_frame('tpv_total')
    df_features = df_features.join(df_agregado)

    # --- PONTO CRÍTICO: Juntar com a Meta ---
    if df_metas is not None:
        # Garante que o índice de df_metas é 'id_cliente' se não for
        if 'id_cliente' in df_metas.columns:
            df_metas = df_metas.set_index('id_cliente')
            
        df_features = df_features.join(df_metas['tpv_meta'])
        
        # Evita divisão por zero se a meta for 0
        df_features['atingimento_meta_tpv'] = (
            df_features['tpv_total'] / df_features['tpv_meta'].replace(0, np.nan)
        )
    else:
        print("Aviso: 'df_metas' não fornecido. 'atingimento_meta_tpv' não será calculado.")
        df_features['atingimento_meta_tpv'] = np.nan
        df_features['tpv_meta'] = np.nan # Garante que a coluna exista

    # 3. Atributo 2: Margem (Peso 20%)
    df_features['margem_op_media'] = df_historico.groupby('id_cliente')['margem_op_dia'].mean()
    df_features['margem_op_total'] = df_historico.groupby('id_cliente')['margem_op_dia'].sum()

    # 4. Atributo 3: Comportamento Histórico (Peso 10%)
    print("Calculando atributos de comportamento (tendência, volatilidade)...")
    
    # Volatilidade (Desvio Padrão do TPV)
    df_features['volatilidade_tpv'] = df_historico.groupby('id_cliente')['tpv_dia'].std()
    
    # Tendência (Cliente Vagalume)
    # Aplicamos nossa função 'calculate_trend' a cada grupo de cliente
    tendencia_series = df_historico.groupby('id_cliente')['tpv_dia'].apply(calculate_trend)
    df_features['tendencia_tpv'] = tendencia_series

    # Mix de Pagamento (Feature Extra)
    print("Calculando mix de pagamento...")
    
    # Cria a pivot table (total de TPV por cliente e meio de pagamento)
    pivot_mix = df_historico.pivot_table(
        index='id_cliente',
        columns='meio_pagamento',
        values='tpv_dia',
        aggfunc='sum',
        fill_value=0
    )
    
    # Normaliza para percentual (divide o TPV de cada meio pelo TPV total)
    pivot_percent = pivot_mix.div(df_features['tpv_total'], axis=0)
    
    # Renomeia colunas para ex: 'mix_pct_CREDIT', 'mix_pct_DEBIT'
    pivot_percent.columns = [f'mix_pct_{col.replace(" ", "_").upper()}' for col in pivot_percent.columns]
    
    # Junta as features de mix ao DataFrame principal
    df_features = df_features.join(pivot_percent)

    # 5. Limpeza Final
    # Preenche NaNs (ex: volatilidade de cliente com 1 transação) com 0
    df_features = df_features.fillna(0)
    
    print("Engenharia de atributos concluída.")
    return df_features