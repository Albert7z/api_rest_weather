API de Alerta de Risco Climático Pessoal
🚀 Sobre o Projeto
Esta API é uma solução de back-end desenvolvida em Python com Flask, projetada para ser uma ponte inteligente entre dados climáticos do mundo real e a segurança do usuário.

Em vez de apenas fornecer dados brutos, esta API consome informações em tempo real da OpenWeatherMap, analisa o Índice de Qualidade do Ar (AQI), persiste os dados para análise histórica e, de forma proativa, dispara alertas por e-mail para usuários inscritos caso o risco à saúde se torne elevado.

Este projeto foi construído para demonstrar habilidades em arquitetura de APIs REST, integração com serviços de terceiros, persistência de dados com SQLAlchemy e automação de tarefas.

✨ Funcionalidades
Consulta em Tempo Real: Obtém o Índice de Qualidade do Ar (AQI) para qualquer localidade via coordenadas.

Análise Inteligente: Traduz o índice numérico do AQI em um nível de risco (Bom, Moderado, Ruim, etc.) e fornece uma recomendação de saúde prática.

Persistência de Dados: Salva cada consulta em um banco de dados SQLite, criando um histórico valioso.

Análise de Tendência: Analisa os dados das últimas horas para determinar se a qualidade do ar está Melhorando, Piorando ou Estável.

Sistema de Alertas Proativo: Permite que usuários registrem seu e-mail para serem notificados automaticamente caso a qualidade do ar em sua região se deteriore.

🛠️ Tecnologias Utilizadas
Backend: Python

Framework: Flask

Banco de Dados: SQLite com Flask-SQLAlchemy

Comunicação com API Externa: Requests

Envio de E-mail: Flask-Mail

⚙️ Como Executar o Projeto Localmente
Clone o repositório:

git clone (https://github.com/Albert7z/api_rest_weather)
cd api_rest_weather

Crie e ative um ambiente virtual:

python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

Instale as dependências:

pip install Flask Flask-SQLAlchemy Flask-Mail requests

Configure suas credenciais:

Abra o arquivo app.py.

Insira sua chave da API da OpenWeatherMap.

Insira seu e-mail e sua "Senha de App" de 16 dígitos do Gmail.

Execute a API:

python app.py

O servidor estará rodando em http://127.0.0.1:5000.

🔌 Endpoints da API
GET /alerta-ar/<latitude>/<longitude>
Retorna o alerta de qualidade do ar em tempo real para as coordenadas fornecidas e salva o registro no histórico.

Exemplo: http://127.0.0.1:5000/alerta-ar/-27.5969/-48.5495

POST /registrar
Registra um novo usuário para receber alertas por e-mail.

Exemplo (usando cURL):

curl -X POST -H "Content-Type: application/json" -d "{\"email\":\"seuemail@exemplo.com\", \"latitude\":\"-27.5969\", \"longitude\":\"-48.5495\"}" [http://127.0.0.1:5000/registrar](http://127.0.0.1:5000/registrar)

GET /historico
Retorna todos os registros de qualidade do ar salvos no banco de dados, em ordem decrescente de data.

Exemplo: http://127.0.0.1:5000/historico

GET /tendencia/<latitude>/<longitude>
Analisa os registros das últimas 3 horas e retorna a tendência da qualidade do ar.

Exemplo: http://127.0.0.1:5000/tendencia/-27.5969/-48.5495


🔮 Próximos Passos e Melhorias Futuras
Desenvolvimento de um Frontend: Criar uma interface web (React, Vue, ou HTML/JS simples) para fornecer uma maneira visual e amigável para o usuário interagir com a API, ver dados em gráficos e se registrar para alertas através de um formulário.

Busca por Nome da Cidade: Integrar com a API de Geocoding da OpenWeatherMap para permitir que os usuários consultem a qualidade do ar pelo nome da cidade, em vez de coordenadas.

Tarefas Agendadas (Scheduler): Implementar um worker em segundo plano (com Celery ou APScheduler) que verifique periodicamente a qualidade do ar para todos os usuários inscritos, tornando o sistema de alertas 100% autônomo.

Cache de Dados: Adicionar um sistema de cache (como Redis) para reduzir chamadas repetidas à API externa e aumentar a velocidade de resposta para locais populares.
