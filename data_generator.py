from faker import Faker
import random
import json
from datetime import datetime, timedelta

fake = Faker('pt_BR')  # Para nomes e datas no padrão brasileiro

# Quantidade de clientes
num_clientes = 10

# Função para gerar histórico dos últimos 10 dias
def gerar_historico():
    historico = []
    for i in range(1, 11):
        data = (datetime.now() - timedelta(days=i)).strftime("%d/%m/%Y")
        valor_transacao_dia = round(random.uniform(50_000, 900_000), 2)
        qtd_transacoes = random.randint(5_000, 10_000)
        historico.append({
            "data": data,
            "valor_transacao_dia": valor_transacao_dia,
            "qtd_transacoes_diarias": qtd_transacoes
        })
    return historico

# Gerar dados dos clientes
clientes = []
for _ in range(num_clientes):
    tpv_meta = round(random.uniform(100_000, 900_000), 2)
    margem_percentual = round(random.uniform(0.5, 5.0), 2)
    margem_valor = round(tpv_meta * (margem_percentual / 100), 2)

    cliente = {
        "nome_cliente": fake.company(),
        "tpv_meta": tpv_meta,
        "margem_percentual": margem_percentual,
        "margem_valor": margem_valor,
        "historico": gerar_historico()
    }
    clientes.append(cliente)
