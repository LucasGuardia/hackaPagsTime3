import pandas as pd
import sqlalchemy
import os
from dotenv import load_dotenv

def get_historical_data(dat_start_filter='2024-01-01'):
    """
    Conecta ao Redshift e busca os dados históricos da ent_margin_summary.
    
    Esta função lê as credenciais do arquivo .env na raiz do projeto.
    
    Args:
        dat_start_filter (str): Data de início para o filtro (formato YYYY-MM-DD).

    Returns:
        pd.DataFrame: Um DataFrame com os dados históricos, ou None se falhar.
    """
    
    project_root = os.path.join(os.path.dirname(__file__), '..', '..')
    load_dotenv(os.path.join(project_root, '.env'))

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
        num_operational_margin AS margem_op_dia,
        idt_main_payment_method AS meio_pagamento,
        num_installment_qty AS parcelas
    FROM
        dax.ent_margin_summary
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
            print("Aviso: A query foi executada, mas não retornou dados.")
        else:
            print(f"Sucesso! {len(df_historico)} registros carregados.")
        
        return df_historico

    except Exception as e:
        print(f"Erro ao executar a query no Redshift: {e}")
        return None

def get_metas_from_redshift():
    """
    Busca a 'tpv_meta' de outra tabela no Redshift.
    
    !! ESTA FUNÇÃO É UM EXEMPLO E PRECISA SER AJUSTADA !!
    
    Returns:
        pd.DataFrame: DataFrame de metas com 'id_cliente' como índice.
    """
    print("Buscando metas (tpv_meta) do Redshift...")

    # Carrega as variáveis de ambiente (caminho relativo)
    project_root = os.path.join(os.path.dirname(__file__), '..', '..')
    load_dotenv(os.path.join(project_root, '.env'))

    # 1. Conexão (repetido da função get_historical_data)
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

    # 2. Query de Metas (!! AJUSTE AQUI !!)
    # Você precisa descobrir qual tabela e colunas contêm a meta.
    # O 'idt_safepay_creditor' (ou 'idt_safepay_user') deve ser o ID.
    
    query_metas = """
    SELECT
        -- !! AJUSTE AQUI !! (ex: idt_safepay_user ou idt_safepay_creditor)
        idt_safepay_creditor AS id_cliente, 
        
        -- !! AJUSTE AQUI !! (qual coluna é a meta?)
        num_meta_tpv_objetivo AS tpv_meta 
        
    FROM
        -- !! AJUSTE AQUI !! (qual tabela tem as metas?)
        dax.NOME_DA_SUA_TABELA_DE_METAS 
        
    WHERE
        -- (Talvez você precise filtrar pelo período de meta mais recente)
        -- dat_referencia_meta = '2024-10-01'
        flg_meta_ativa = 1
    ;
    """
    
    try:
        with engine.connect() as connection:
            df_metas = pd.read_sql_query(query_metas, connection)
            
        if df_metas.empty:
            print("Aviso: A query de metas não retornou dados.")
            return None

        # Define o id_cliente como índice (necessário para a FASE 2)
        df_metas = df_metas.set_index('id_cliente')
        
        print("Metas do Redshift carregadas com sucesso.")
        return df_metas[['tpv_meta']] # Retorna só a coluna necessária

    except Exception as e:
        print(f"Erro ao executar a query de METAS: {e}")
        print("Verifique sua query_metas e os nomes de tabelas/colunas.")
        return None

if __name__ == '__main__':    
    print("--- Testando o módulo make_dataset ---")
    df = get_historical_data()
    
    if df is not None:
        print("\n--- Amostra dos Dados ---")
        print(df.head())
        print("\n--- Info dos Dados ---")
        df.info()