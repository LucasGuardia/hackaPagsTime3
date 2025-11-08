📊 Projeto Adquirência: Previsão de Indicadores Chave para Price Health Scoring

💡 Motivação

No setor de Adquirência (Meios de Pagamento), a capacidade de prever a saúde do pricing e a sustentabilidade das taxas é fundamental. Este projeto estabelece um serviço robusto de previsão de Indicadores Pais (como volume de transações, take rates ou taxas de churn), que servirão como input primário para o cálculo de um Price Health Scoring centralizado.

O foco inicial é utilizar o modelo SARIMAX para modelar e prever a série temporal de um desses Indicadores Pais (por exemplo, o volume transacionado em um canal específico).

A motivação é fornecer insumos preditivos e acionáveis para que um serviço de score dedicado (externo a esta API) possa avaliar e alertar sobre a sustentabilidade e competitividade da política de preços da empresa.

🏛️ Arquitetura do Projeto

O projeto utiliza uma arquitetura Machine Learning as a Service (MLaaS) focada em modularidade e escalabilidade:

Componente

Tecnologia

Função

Modelagem

SARIMAX (Statsmodels)

Modelo estatístico para prever um Indicador Pai, servindo como input para o Price Health Scoring.

API de Inferência

Flask

Cria uma rota leve e rápida (/predict) para executar as previsões do modelo SARIMAX.

Containerização

Docker

Empacota a API Flask e todas as suas dependências, garantindo reprodutibilidade e consistência em qualquer ambiente.

📦 Estrutura de Arquivos

/projeto_sarimax_adquirencia
├── app.py                      # Serviço principal da API Flask
├── Dockerfile                  # Define o ambiente do container Docker
├── requirements.txt            # Dependências do Python (Flask, statsmodels, pandas)
└── modelos/
    └── modelo_sarimax.pkl      # Modelo SARIMAX treinado e serializado


⚙️ Configuração e Instalação

Pré-requisitos

Python 3.8+

Docker (Recomendado para deploy)

1. Preparação do Ambiente Local

Crie um ambiente virtual e instale as dependências:

python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install -r requirements.txt


Conteúdo de requirements.txt:

Flask
pandas
numpy
statsmodels
gunicorn


2. Treinamento e Salvamento do Modelo

Certifique-se de que seu modelo SARIMAX treinado (para o Indicador Pai escolhido) esteja salvo no caminho /modelos/modelo_sarimax.pkl antes de executar a API.

3. Execução da API (Modo Desenvolvimento)

python app.py
# A API estará acessível em [http://127.0.0.1:5000/](http://127.0.0.1:5000/)


🐳 Execução via Docker (Recomendado)

O Docker garante que o ambiente de execução da API seja isolado e consistente:

1. Construir a Imagem

docker build -t sarimax-api-adquirencia .


2. Rodar o Container

Mapeie a porta 5000:

docker run -d -p 5000:5000 --name sarimax-service sarimax-api-adquirencia
# A API estará acessível em http://localhost:5000/


🎯 Endpoint de Inferência

O serviço expõe um único endpoint de previsão, retornando o valor futuro de um Indicador Pai.

POST /predict

Descrição: Retorna a previsão do Indicador Pai para $N$ passos (períodos), que será usado no cálculo do Score.

URL: http://localhost:5000/predict

Corpo da Requisição (JSON):

Campo

Tipo

Obrigatório?

Descrição

steps

Inteiro

Sim

O número de períodos futuros para previsão (ex: 7 dias).

exog

Lista de Listas

Não*

Matriz com os valores exógenos futuros, se o modelo for SARIMAX. Deve ter steps linhas.

Exemplo (com exógenas):

{
    "steps": 3,
    "exog": [
        [0.5],
        [1.2],
        [0.8]
    ]
}


Corpo da Resposta (JSON - Sucesso):

{
    "status": "sucesso",
    "steps": 3,
    "datas_previsao": ["2025-11-09", "2025-11-10", "2025-11-11"],
    "previsoes_indicador": [12345.67, 15000.00, 14500.25]
}


🔮 Próximos Passos

Cálculo do Score: Desenvolver o serviço que consumirá as previsões desta API (e, futuramente, de outras APIs de Indicadores Pais) para calcular o Price Health Scoring final.

Expansão: Adaptar o código e a arquitetura para suportar a previsão dos 4 Indicadores Pais (inputs necessários para o Score).

Segurança: Implementar autenticação na API (ex: API Key) para ambientes de produção.
