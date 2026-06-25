# Postman-to-Robot

Gerador automatizado de testes **Robot Framework** a partir de **Postman Collections** (formato v2.1 JSON).

## Objetivo

Converter automaticamente collections do Postman em arquivos `.robot` executáveis, eliminando a necessidade de reescrever manualmente centenas de cenários de teste.

O gerador preserva a estrutura, variáveis, autenticação, assertions e documentação dos testes originais, produzindo arquivos compatíveis com o framework existente da Essilor.

## Estrutura do Projeto

```
postman-to-robot/
├── main.py                    # Entry point (CLI com click)
├── config.py                  # Configurações padrão
├── requirements.txt           # Dependências Python
├── .gitignore
│
├── input/                     # Collections Postman (entrada)
│   └── API Conecta Pedidos v1.postman_collection.json
│
├── output/                    # Arquivos .robot gerados (saída)
│   ├── f000_autenticacao.robot
│   ├── f001_get_pedidos.robot
│   ├── f002_get_pedidos_id.robot
│   ├── f003_post_integracao_laboratorio.robot
│   └── fluxo_integracao_laboratorio.robot
│
├── test-base/                 # Base de keywords reutilizáveis
│   └── base-api.robot
│
├── doc/                       # Documentação do projeto
│   ├── POC-GERADOR-TESTES-ROBOT.md
│   └── TEMPLATE-VALIDACAO.md
│
├── service/                   # Módulos do gerador
│   ├── parser.py              # Parse da collection Postman
│   ├── generator.py           # Geração dos arquivos .robot
│   ├── assertions.py          # Tradução de assertions Postman → Robot
│   ├── ai_helper.py           # Wrapper para IA (Fase 2)
│   └── config.py
│
├── tests/                     # Testes unitários (pytest)
│   ├── __init__.py
│   ├── test_parser.py         # 44 testes
│   ├── test_generator.py      # 65 testes
│   └── test_assertions.py     # 65 testes
│
└── templates/                 # Templates Jinja2 (próxima fase)
```

## Dependências

### Python (requirements.txt)

| Pacote | Versão | Uso |
|---|---|---|
| `click` | >=8.0 | Interface CLI |
| `jinja2` | >=3.1 | Templates (Fase 2) |
| `openai` | >=1.0 | IA (Fase 2) |
| `jsonschema` | >=4.0 | Validação de schemas |
| `pytest` | >=7.0 | Testes unitários |

### Robot Framework (para executar os testes gerados)

| Pacote | Versão | Uso |
|---|---|---|
| `robotframework` | >=6.0 | Framework de testes |
| `robotframework-requests` | >=0.9 | HTTP requests no Robot |
| `robotframework-collections` | >=2.0 | Manipulação de listas |
| `robotframework-stringlibrary` | >=4.0 | Strings no Robot |
| `robotframework-imaplibrary2` | >=2.0 | Email (MFA) |
| `robotframework-jsonlibrary` | >=1.0 | JSON no Robot |

## Instalação

### 1. Clonar o repositório

```powershell
git clone https://github.com/seu-usuario/postman-to-robot.git
cd postman-to-robot
```

### 2. Criar ambiente virtual (recomendado)

```powershell
python -m venv venv
venv\Scripts\Activate.ps1
```

### 3. Instalar dependências do gerador

```powershell
pip install -r requirements.txt
```

### 4. Instalar dependências do Robot Framework (para executar os testes)

```powershell
pip install robotframework-requests robotframework-jsonlibrary robotframework-imaplibrary2
```

## Como Usar

### Gerar testes a partir de uma collection Postman

```powershell
python main.py ^
    --input "input/API Conecta Pedidos v1.postman_collection.json" ^
    --output "output" ^
    --base-resource "test-base/base-api.robot" ^
    --env dev
```

### Parâmetros CLI

| Parâmetro | Obrigatório | Padrão | Descrição |
|---|---|---|---|
| `--input` | Sim | — | Caminho para o arquivo da collection Postman (JSON) |
| `--output` | Sim | — | Diretório de saída para os arquivos `.robot` |
| `--base-resource` | Não | `test-base/base-api.robot` | Caminho para o `base-api.robot` |
| `--env` | Não | `dev` | Ambiente (`dev` ou `hml`) |
| `--ai-api` | Não | `opencode` | Provedor de IA (`opencode`, `openai`) |
| `--ai-model` | Não | `opencode/oci` | Modelo de IA |

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
┌─────────────────────────────────┐
│ FASE 1: 100% COMPUTACIONAL      │
│ (Script Python)                 │
│                                 │
│ • Parsear JSON                  │
│ • Navegar estrutura aninhada    │
│ • Extrair method, URL, headers  │
│ • Resolver {{variaveis}}        │
│ • Gerar Settings, Variables     │
│ • Gerar chamadas HTTP           │
│ • Gerar assertions básicas      │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ FASE 2: IA NECESSÁRIA           │
│ (API call - OpenAI)             │
│                                 │
│ • Extrair schemas JSON inline   │
│   do JavaScript                 │
│ • Traduzir lógica complexa      │
│   (if/else, loops, Math.)       │
│ • Decidir keyword Robot         │
│   mais adequada                 │
│ • Gerar documentação legível    │
│ • Decidir quando Skip           │
└────────────────┬────────────────┘
                 │
                 ▼
┌─────────────────────────────────┐
│ FASE 3: 100% COMPUTACIONAL      │
│ (Script Python)                 │
│                                 │
│ • Montar arquivo .robot final   │
│ • Salvar schemas JSON           │
│ • Escrever no filesystem        │
└────────────────┬────────────────┘
                 │
                 ▼
        .robot files gerados
        + schemas JSON (opcional)
```

### Mapeamento Postman → Robot Framework

| Postman Field | Robot Equivalent | Tratamento |
|---|---|---|
| `request.method` | Keyword HTTP (`GET On Session`, `POST On Session`) | Direto |
| `request.url.raw` | URL da session | Resolve variáveis, extrai path + query |
| `request.header[]` | Headers da request | Array → dicionário |
| `request.body.raw` | `json=` param | Parse JSON → dict |
| `request.auth.type` | Keyword de auth (OAuth, JWT) | Condicional |
| `event[].script.exec` | Assertions em Robot | JS → keywords Robot |
| `variable[]` | `${var}` no Robot | Resolve e injeta |

### Assertions traduzidas

| Postman JS | Robot Framework |
|---|---|
| `pm.response.to.have.status(200)` | `Status Should Be    200    ${api_response}` |
| `pm.expect(x).to.not.be.empty` | `Should Not Be Empty    ${x}` |
| `pm.expect(x).to.be.null` | `Should Be Empty    ${x}` |
| `pm.expect(x).to.eql(y)` | `Should Be Equal As Strings    ${x}    ${y}` |
| `pm.expect(x).to.be.a('string')` | `Should Not Be Empty    ${x}` |
| `pm.expect(x).to.be.a('number')` | `Should Be Equal As Numbers    ${x}` |
| `pm.expect(x).to.contain(y)` | `Should Contain    ${x}    ${y}` |
| `pm.expect(pm.response.text()).to.be.empty` | `Should Be Empty    ${api_response.content}` |
| `pm.expect(x).to.be.above(0)` | `Should Be True    ${x} > 0` |
| `pm.collectionVariables.set(k, v)` | `Set Test Variable    ${k}    ${v}` |
| `pm.environment.set(k, v)` | `Set Test Variable    ${k}    ${v}` |

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

### Resumo dos testes

| Módulo | Arquivo | Quantidade |
|---|---|---|
| Parser | `test_parser.py` | 44 testes |
| Generator | `test_generator.py` | 65 testes |
| Assertions | `test_assertions.py` | 65 testes |
| **Total** | | **174 testes** |

## Status da POC

| Fase | Status | Descrição |
|---|---|---|
| Fase 1: Gerador Básico | ✅ Concluída | Parser, generator e assertions básicas |
| Fase 2: IA Integration | 🔄 Pendente | Extração de schemas, assertions complexas |
| Fase 3: Validação | 🔄 Pendente | Comparação com testes existentes |

## Limitações Atuais

- Requests com query parameters `disabled: true` são gerados com `Skip`
- Assertions complexas (jsonSchema, if/else, Math.random) requerem IA (Fase 2)
- Variáveis encadeadas (`{{random_id_pedido}}`) são resolvidas com valores estáticos
- Schemas JSON inline são marcados como `TODO` (Fase 2)

## Contribuição

1. Faça um fork do projeto
2. Crie uma branch (`git checkout -b feature/nova-feature`)
3. Commit suas mudanças (`git commit -m 'feat: nova feature'`)
4. Push para a branch (`git push origin feature/nova-feature`)
5. Abra um Pull Request

## Licença

Este projeto é parte de uma POC interna da Essilor para automação de testes de API.
