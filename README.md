# Dashboard ANAC - Dados Estatísticos ✈️

Um dashboard interativo desenvolvido com Python Shiny para análise dos dados estatísticos da Agência Nacional de Aviação Civil (ANAC). O projeto permite visualizar indicadores operacionais das principais companhias aéreas brasileiras.

![Python](https://img.shields.io/badge/python-v3.12+-blue.svg)
![Shiny](https://img.shields.io/badge/shiny-v0.7.0+-green.svg)
![Plotly](https://img.shields.io/badge/plotly-v5.17.0+-red.svg)

## 🚀 Demonstração

Acesse o dashboard online: [ANAC Dados Estatísticos](https://guilherme-fidalgo.shinyapps.io/ANAC-Dados-Estatisticos/)

## 📊 Funcionalidades

### Indicadores Operacionais

- **ASK** (Available Seat Kilometers) - Quilômetros de assentos disponíveis
- **RPK** (Revenue Passenger Kilometers) - Quilômetros de passageiros pagantes
- **Load Factor** - Taxa de ocupação das aeronaves
- **Passageiros** - Total de passageiros transportados
- **Decolagens** - Número total de decolagens
- **Destinos** - Quantidade de destinos únicos

### Visualizações Interativas

- Gráfico combinado de RPK, ASK e Load Factor com eixos duplos
- Gráficos de barras para passageiros, decolagens e destinos por empresa
- Filtros por período e nacionalidade das empresas
- Seleção múltipla de companhias aéreas

### Filtros Disponíveis

- **Período**: Seleção de intervalo de datas
- **Nacionalidade da Empresa**: Filtro por nacionalidade (Brasileira, Estrangeira, etc.)
- **Empresa**: Seleção múltipla das companhias aéreas (AZU, GOL, TAM, etc.)

## 🛠️ Tecnologias Utilizadas

- **[Python Shiny](https://shiny.posit.co/py/)**: Framework para criação de aplicações web interativas
- **[Plotly](https://plotly.com/python/)**: Biblioteca para visualizações interativas
- **[Pandas](https://pandas.pydata.org/)**: Manipulação e análise de dados
- **[ShinyWidgets](https://github.com/posit-dev/py-shinywidgets)**: Widgets interativos para Shiny

## 📁 Estrutura do Projeto

```
├── app.py                          # Aplicação principal
├── pyproject.toml                  # Configurações do projeto
├── requirements.txt                # Dependências Python
├── uv.lock                        # Lock file do UV
├── README.md                      # Documentação
├── assets/
│   └── vlls_logo.png              # Logo da aplicação
├── notebooks/
│   ├── anac_dados_estatisticos.csv # Dataset principal
│   └── dados_estatisticos.ipynb   # Análise exploratória
└── rsconnect-python/
    └── ANAC_Dados.json           # Configuração de deploy
```

## 🔧 Instalação e Execução

### Pré-requisitos

- Python 3.12+
- UV (recomendado) ou pip

### Instalação com UV (Recomendado)

```bash
# Clone o repositório
git clone https://github.com/guilhermefidalgo/ANAC_Dados.git
cd ANAC_Dados

# Instale as dependências
uv sync

# Execute a aplicação
uv run shiny run app.py
```

### Instalação com pip

```bash
# Clone o repositório
git clone https://github.com/guilhermefidalgo/ANAC_Dados.git
cd ANAC_Dados

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # No Windows: venv\Scripts\activate

# Instale as dependências
pip install -r requirements.txt

# Execute a aplicação
shiny run app.py
```

A aplicação estará disponível em `http://localhost:8000`

## 📊 Sobre os Dados

Os dados utilizados são provenientes da ANAC (Agência Nacional de Aviação Civil) e contêm informações estatísticas mensais das companhias aéreas brasileiras, incluindo:

- Dados de tráfego (passageiros, RPK, ASK)
- Informações operacionais (decolagens, destinos)
- Empresas por nacionalidade
- Período de referência dos dados

## 🎨 Características Visuais

- **Design Responsivo**: Interface adaptável a diferentes tamanhos de tela
- **Cores Personalizadas**: Esquema de cores específico para cada companhia aérea
- **Interatividade**: Gráficos com hover, zoom e filtros dinâmicos
- **Formatação Inteligente**: Números formatados com abreviações (K, M, B)

## 🚀 Deploy

O projeto está configurado para deploy no ShinyApps.io. Para fazer deploy:

```bash
# Instale o rsconnect-python
pip install rsconnect-python

# Faça o deploy (configure suas credenciais primeiro)
rsconnect deploy shiny . --name ANAC-Dados-Estatisticos
```

## 📈 Melhorias Futuras

- [ ] Adicionar mais visualizações (mapas, séries temporais)
- [ ] Implementar cache para melhor performance
- [ ] Adicionar exportação de dados
- [ ] Incluir análises estatísticas avançadas
- [ ] Adicionar comparações entre períodos
- [ ] Implementar alertas e notificações

## 🤝 Contribuição

Contribuições são bem-vindas! Por favor, siga estas etapas:

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## 👤 Autor

**Guilherme Fidalgo**

- GitHub: [@guifidalgo](https://github.com/guifidalgo)
- LinkedIn: [Guilherme Fidalgo](https://linkedin.com/in/guilherme-fidalgo)

## 🙏 Agradecimentos

- [ANAC](https://www.gov.br/anac/pt-br) pelos dados públicos disponibilizados
- [Posit](https://posit.co/) pelo framework Shiny
- Comunidade Python pela excelente documentação e suporte

---

⭐ Se este projeto foi útil para você, considere dar uma estrela no repositório!
