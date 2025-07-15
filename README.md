# Projeto de Pipeline de Dados Pokémon na GCP

Este projeto implementa um pipeline de dados serverless na Google Cloud Platform (GCP) para processar uma lista de URLs da PokéAPI. O processo extrai informações específicas de cada Pokémon e as armazena em um banco de dados NoSQL para consulta.

O pipeline é projetado para ser automatizado, escalável e com custo otimizado, executando diariamente de forma autônoma.

## Arquitetura da Solução

A solução utiliza uma arquitetura 100% serverless, o que significa que não há servidores para gerenciar, e o custo é estritamente baseado no uso.

Os componentes principais são:

- **Cloud Scheduler**: Atua como um serviço de cron (agendador) que dispara o pipeline uma vez por dia.
- **Cloud Functions**: O coração do projeto. Uma função em Python que é acionada pelo Scheduler, responsável por ler as URLs, chamar a API, extrair os dados e salvá-los.
- **Firestore**: Um banco de dados NoSQL, escalável e serverless, usado para armazenar os dados estruturados de cada Pokémon.

O fluxo de dados segue a seguinte ordem:

```
+------------------+        (1) Dispara 1x/dia       +-----------------+
|                  | ------------------------------> |                 |
|  Cloud Scheduler |                                 |  Cloud Function |
|                  |        (2) Processa os dados    |   (Python)      |
|                  |                                 |                 |
+------------------+        (3) Salva no Firestore   +-------+---------+
                                                              |
                                                             _V_
                                         +------------------------------------+
                                         |             Firestore              |
                                         |      (Banco de Dados NoSQL)        |
                                         +------------------------------------+
```

## Passo a Passo para Implantação

Siga os passos abaixo para configurar e implantar a solução no seu próprio ambiente GCP.

### Pré-requisitos

- Uma conta na Google Cloud Platform com um projeto criado.
- A ferramenta de linha de comando `gcloud` instalada e configurada.
- `Git` instalado na sua máquina local.

### Estrutura do Projeto

```
.
├── .gitignore
├── README.md
├── main.py
├── requirements.txt
└── urls.txt
```

### 1. Preparação do Ambiente

Primeiro, clone o repositório e configure a autenticação da gcloud.

```bash
# Clone o repositório para sua máquina local
git clone <URL_DO_SEU_REPOSITORIO_GIT>
cd <NOME_DA_PASTA_DO_PROJETO>

# Inicialize a gcloud e configure seu projeto
gcloud init

# Configure a autenticação padrão para aplicações
gcloud auth application-default login

# Habilite as APIs necessárias para o projeto
gcloud services enable cloudfunctions.googleapis.com
gcloud services enable cloudscheduler.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable run.googleapis.com
gcloud services enable cloudbuild.googleapis.com
```

### 2. Configuração dos Serviços na GCP

Crie a instância do Firestore que armazenará os dados.

- No Console da GCP, navegue até Firestore.
- Clique em "Criar banco de dados".
- Escolha o modo Nativo e uma localização (ex: `southamerica-east1`).
- Clique em "Criar".

### 3. Deploy da Cloud Function

Execute o comando abaixo no seu terminal, dentro da pasta do projeto, para implantar a função. Este comando já inclui o tempo limite de 9 minutos (540s).

Substitua `[PROJECT_ID]` pelo ID do seu projeto.

```bash
gcloud functions deploy pokemon-processor --project=[PROJECT_ID] --runtime=python311 --region=southamerica-east1 --source=. --entry-point=process_pokemon_urls --trigger-http --allow-unauthenticated --timeout=540s
```

### 4. Agendamento com o Cloud Scheduler

Finalmente, crie o agendamento para executar a função diariamente.

- Acesse a página do Cloud Scheduler no Console da GCP.
- Clique em "Criar job".
- Preencha os seguintes campos:
  - **Nome**: `daily-pokemon-fetch`
  - **Frequência**: `0 2 * * *` (Executa todo dia às 2h da manhã).
  - **Fuso horário**: Selecione seu fuso (ex: (GMT-03:00) São Paulo).
  - **Destino**: HTTP.
  - **URL**: Cole a URL de gatilho da sua Cloud Function (obtida no passo anterior).
  - **Método HTTP**: GET.
- Expanda as "Configurações de repetição".
  - No campo "Prazo final da tentativa", insira `540s` para alinhar com o timeout da função.
- Clique em "Criar".

## Estimativa de Custo Anual

A seguir, a estimativa de custo anual com base nos requisitos da atividade.

### Premissas de Cálculo

- **Volumetria**: 1.150 URLs iniciais, aumentada em 100x = 115.000 Pokémons.
- **Execução**: 1 vez por dia.
- **Ciclo de Vida**: Dados acessados por 6 meses e armazenados por 1 ano.

### Detalhamento

- **Cloud Functions**: As 180 execuções anuais e o tempo de computação correspondente se enquadram confortavelmente na camada gratuita da GCP (2 milhões de invocações/mês).  
  **Custo Estimado**: $0

- **Cloud Scheduler**: A camada gratuita inclui 3 jobs por conta.  
  **Custo Estimado**: $0

- **Firestore**: Este é o principal custo, impulsionado pelas operações de escrita.
  - Operações de Escrita: 115.000 escritas/dia * 180 dias = ~207 milhões de escritas.
  - Armazenamento: O volume de dados (~175 MB) tem custo negligenciável.  
  **Custo Estimado**: ~ $373

**Custo Total Anual Estimado**: ≈ $373
