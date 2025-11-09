import pandas as pd
import sqlalchemy
import os
from dotenv import load_dotenv

# codigo de exemplo para realizar a conexão com o redshift, porém durante o hacka não foi possível realizar essa conexão
# possivelmente por alguma restrição de acesso ao banco, que gerou uma "busca eterna"

def get_historical_data(dat_start_filter='2024-01-01'):
    """
    Conecta ao Redshift e busca os dados históricos da ent_margin_summary.
    
    Esta função lê as credenciais do arquivo .env na raiz do projeto.
    
    Args:
        dat_start_filter (str): Data de início para o filtro (formato YYYY-MM-DD).

    Returns:
        pd.DataFrame: Um DataFrame com os dados históricos, ou None se falhar.
    """
    
    load_dotenv()

    try:
        user = os.environ['RS_USER']
        password = os.environ['RS_PASS']
        host = os.environ['RS_HOST']
        port = os.environ['RS_PORT']
        database = os.environ['RS_DB']
    except KeyError as e:
        print(f"Erro: Variável de ambiente {e} não encontrada.")
        print("Certifique-se que seu arquivo .env está preenchido na raiz do projeto.")
        return None

    connection_string = (
        f"postgresql+psycopg2://{user}:{password}@"
        f"{host}:{port}/{database}"
    )

    try:
        engine = sqlalchemy.create_engine(connection_string)
        print("Engine do SQLAlchemy criado com sucesso.")
    except Exception as e:
        print(f"Erro ao criar o engine do SQLAlchemy: {e}")
        return None

    query_base = f"""
    SELECT
        dat_reference AS data,
        idt_safepay_creditor AS id_cliente,
        num_tpv_value AS tpv_dia,
        num_contribution_margin AS margem_op_dia, -- OK, usei sua coluna

        -- COLUNAS CORRIGIDAS (essenciais para FASE 2)
        idt_main_payment_method AS meio_pagamento,
        num_installment_qty AS parcelas
        
    FROM
        hackathon_dax.dax_ent_margin_summary -- OK, usei sua tabela
        
    WHERE
        dat_reference >= '{dat_start_filter}'
    ORDER BY
        id_cliente, data;
    """

    print("Buscando dados históricos no Redshift...")
    
    try:
        with engine.connect() as connection:
            df_historico = pd.read_sql_query(query_base, connection)
        
        if df_historico.empty:
            print("Aviso: A query de dados históricos foi executada, mas não retornou dados.")
        else:
            print(f"Sucesso! {len(df_historico)} registros históricos carregados.")
        
        return df_historico

    except Exception as e:
        print(f"Erro ao executar a query de DADOS HISTÓRICOS: {e}")
        return None

def get_metas_from_redshift():
    """
    Busca a 'tpv_meta' de outra tabela no Redshift.
    
    Returns:
        pd.DataFrame: DataFrame de metas com 'id_cliente' como índice.
    """
    print("\nBuscando metas (tpv_meta) do Redshift...")

    project_root = os.path.join(os.path.dirname(__file__), '..', '..')
    load_dotenv(os.path.join(project_root, '.env'))

    try:
        user = os.environ['RS_USER']
        password = os.environ['RS_PASS']
        host = os.environ['RS_HOST']
        port = os.environ['RS_PORT']
        database = os.environ['RS_DB']
        
        connection_string = (
            f"postgresql+psycopg2://{user}:{password}@"
            f"{host}:{port}/{database}"
        )
        engine = sqlalchemy.create_engine(connection_string)
    except Exception as e:
        print(f"Erro ao conectar no Redshift (função de metas): {e}")
        return None

    query_metas = """
    SELECT
        num_total_contract_tpv AS tpv_meta,
        idt_safepay_creditor AS id_cliente
    FROM
        hacka03.tpv_target_client;           
    """
    
    try:
        with engine.connect() as connection:
            df_metas = pd.read_sql_query(query_metas, connection)
            
        if df_metas.empty:
            print("Aviso: A query de metas foi executada, mas não retornou dados.")
            return None

        df_metas = df_metas.set_index('id_cliente')
        
        print("Metas do Redshift carregadas com sucesso.")
        return df_metas[['tpv_meta']]

    except Exception as e:
        print(f"Erro ao executar a query de METAS: {e}")
        return None

if __name__ == '__main__':    
    print("--- Testando o módulo make_dataset ---")
    
    df_hist = get_historical_data()
    
    if df_hist is not None:
        print("\n--- Amostra dos Dados Históricos ---")
        print(df_hist.head())
        print("\n--- Info dos Dados Históricos ---")
        df_hist.info()
    else:
        print("\n--- Teste de Dados Históricos FALHOU ---")

    df_metas_teste = get_metas_from_redshift()
    
    if df_metas_teste is not None:
        print("\n--- Amostra dos Dados de Metas ---")
        print(df_metas_teste.head())
        print("\n--- Info dos Dados de Metas ---")
        df_metas_teste.info()
    else:
        print("\n--- Teste de Dados de Metas FALHOU ---")