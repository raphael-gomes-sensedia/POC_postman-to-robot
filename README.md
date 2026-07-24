# Postman-to-Robot

Gerador automatizado de testes **Robot Framework** a partir de **Postman Collections** (formato v2.1 JSON).

## Objetivo

Converter automaticamente collections do Postman em arquivos `.robot` executáveis, eliminando a necessidade de reescrever manualmente centenas de cenários de teste.

O gerador preserva a estrutura, variáveis, autenticação, assertions e documentação dos testes originais, produzindo arquivos compatíveis com o framework existente da Essilor.

## Estrutura do Projeto

```
postman-to-robot/
├── main.py                    # Entry point (CLI com click)
├── requirements.txt           # Dependências Python
├── .gitignore
│
├── input/                     # Collections Postman (entrada)
│   └── API Conecta Pedidos v1.postman_collection.json
│
├── output/                    # Arquivos .robot gerados (saída)
│
├── .opencode/                 # Configuração opencode
│   ├── agents/                # Agentes opencode
│   │   ├── postman-to-robot-orchestrator.md
│   │   ├── robot-test-writer.md
│   ├── skills/                # Skills
│   │   └── robot-test-pattern/
│   └── context/               # Contexto do base-api.robot
        ├── exemple/
        │   ├──ESSL-4360-conecta-pedidos.robot
        │   ├──neg-ESSL-4360-conecta-pedidos.robot
        └── resource/               
│           └── base-api.robot
│
├── service/                   # Módulos do gerador (parte determinística)
│   ├── parser.py              # Parse da collection Postman
│   ├── generator.py           # Geração do esqueleto .robot
│   └── assertions.py          # Tradução de assertions Postman → Robot
│
├── tests/                     # Testes unitários (pytest)
│   ├── __init__.py
│   ├── test_parser.py
│   ├── test_generator.py
│   └── test_assertions.py
```

## Dependências

### Python (requirements.txt)

| Pacote | Versão | Uso |
|---|---|---|
| `click` | >=8.0 | Interface CLI |
| `pytest` | >=7.0 | Testes unitários |

## Instalação

### 1. Clonar o repositório

```powershell
git clone https://github.com/seu-usuario/postman-to-robot.git
cd postman-to-robot
```

### 2. Instalar dependências do gerador

```powershell
pip install -r requirements.txt
```

### 3. Instalar dependências do Robot Framework (para executar os testes)

```powershell
pip install robotframework-requests robotframework-jsonlibrary robotframework-imaplibrary2
```

## Como Usar

### Gerar esqueleto .robot (parte determinística)

```powershell
python main.py ^
    --input "input/API Conecta Pedidos v1.postman_collection.json" ^
    --output "output" ^
    --base-resource "../api-tests/base-api.robot"
```

### Preencher keywords via agente opencode (parte não-determinística)

Após gerar os esqueletos, o orquestrador opencode preenche keywords, validações e schemas:

1. Inicie o orquestrador: `opencode` no diretório do projeto
2. O orquestrador perguntará qual Collection converter
3. Execute os passos guiados pelo orquestrador

### Parâmetros CLI

| Parâmetro | Obrigatório | Padrão | Descrição |
|---|---|---|---|
| `--input` | Sim | — | Caminho para o arquivo da collection Postman (JSON) |
| `--output` | Sim | — | Diretório de saída para os arquivos `.robot` |
| `--base-resource` | Não | `../api-tests/base-api.robot` | Caminho relativo para o `base-api.robot` |

### Executar os testes gerados

```powershell
# Executar um arquivo específico
robot output\f000_autenticacao.robot

# Executar todos os testes de uma pasta
robot output\

# Especificar diretório de resultados
robot -d results output\f000_autenticacao.robot
```

## Como Funciona

### Fluxo de geração

```
Postman Collection JSON
         │
         ▼
┌───────────────────────────────────────────────┐
│ 1. SCRIPTS PYTHON (parte determinística)      │
│                                                │
│ • Parsear JSON (parser.py)                    │
│ • Navegar estrutura aninhada                  │
│ • Extrair method, URL, headers, body, auth    │
│ • Resolver {{variaveis}} com valores reais    │
│ • Separar requests por grupo (F001, F002...)  │
│ • Separar sucesso/erro por status code        │
│ • Gerar esqueleto .robot:                     │
│   - *** Settings *** (Resource, Documentation)│
│   - *** Variables *** (collection vars)        │
│   - *** Test Cases *** (apenas nomes)         │
│   - *** Keywords *** (vazio para LLM)         │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
┌───────────────────────────────────────────────┐
│ 2. AGENTES OPENCODE (parte não-determinística)│
│                                                │
│ • Carregar skills e contexto base-api.robot   │
│ • Identificar tipo de autenticação            │
│ • Mapear API para @{api_*} do base-api        │
│ • Mapear path para ${oper_*} do base-api      │
│ • Criar keywords de ação (POST/GET Sucesso)   │
│ • Criar keywords de validação (Response 200)  │
│ • Montar headers (JWT, client_id, lab)        │
│ • Adicionar validações (schema, campos)       │
│ • Extrair schemas JSON dos test scripts       │
│ • Extrair payloads para resources/            │
│ • Traduzir assertions Postman → Robot         │
└──────────────────────┬────────────────────────┘
                       │
                       ▼
              .robot files completos
              + schemas/*.json
              + resources/*.json
```

## Testes Unitários

O projeto utiliza **pytest** para testes unitários com abordagem TDD (Test-Driven Development).

### Executar todos os testes

```powershell
python -m pytest tests/ -v
```

### Executar testes de um módulo específico

```powershell
python -m pytest tests/test_parser.py -v
python -m pytest tests/test_generator.py -v
python -m pytest tests/test_assertions.py -v
```

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'feat: nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto é parte de uma POC interna da Essilor para automação de testes de API.
