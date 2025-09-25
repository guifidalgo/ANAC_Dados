from shiny import App, render, ui, reactive
from shiny.types import ImgData
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import os


logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'vlls_logo.png')

file_operacional_path = os.path.join(os.path.dirname(__file__), 'data', 'anac_dados_estatisticos.csv')
file_financeiro_path = os.path.join(os.path.dirname(__file__), 'data', 'demonstrativos.csv')

df_operacional = pd.read_csv(file_operacional_path)
df_operacional['dt_referencia'] = pd.to_datetime(df_operacional['dt_referencia'], format='%Y-%m-%d').dt.date
date_min = df_operacional['dt_referencia'].min()
date_max = df_operacional['dt_referencia'].max()

df_financeiro = pd.read_csv(file_financeiro_path)
periodo_fin = df_financeiro['periodo'].sort_values(ascending=False).unique().tolist()
empresas_fin = df_financeiro['empresa'].sort_values().unique().tolist()

color_mapping = {
    'AZU': '#53B2E5',
    'GLO': '#EE793A',
    'TAM': '#D93555',
}

def format_number(value):
    """Formata números com abreviações K, M, B"""
    if pd.isna(value) or value == 0:
        return '0'
    
    abs_value = abs(value)
    sign = '-' if value < 0 else ''
    
    if abs_value >= 1e9:
        return f'{sign}{abs_value/1e9:.1f}B'
    elif abs_value >= 1e6:
        return f'{sign}{abs_value/1e6:.1f}M'
    elif abs_value >= 1e3:
        return f'{sign}{abs_value/1e3:.1f}K'
    else:
        return f'{sign}{abs_value:.0f}'
    

kpis_operacionais = ui.layout_sidebar(
    ui.sidebar(
        # ui.output_image("logo", height="50px"),
        ui.h2("Indicadores Operacionais"),
        ui.input_date_range(
            "select_date_kpis",
            "Período",
            start=date_min,
            end=date_max,
            min=date_min,
            max=date_max,
            format="mm/yyyy",
            startview="year",
            separator=" a "
        ),
        ui.input_selectize(
            "select_nacionalidade",
            "Nacionalidade Empresa",
            choices=df_operacional['EMPRESA (NACIONALIDADE)'].sort_values().unique().tolist(),
            selected="BRASILEIRA",
            multiple=True,
        ),
        ui.input_selectize(
            "select_empresa",
            "Empresa",
            choices=[],
            selected=['AZU', 'GLO', 'TAM'],
            multiple=True
        ),
        bg="#f8f8f8",
        open="always",
        fillable=True,
    ),
    ui.layout_columns(
        ui.value_box(
            "ASK",
            ui.output_text("kpi_ask"),
            fill=False
        ),
        ui.value_box(
            "RPK",
            ui.output_text("kpi_rpk"),
            fill=False
        ),
        ui.value_box(
            "Load Factor",
            ui.output_text("kpi_load_factor"),
            fill=False
        ),
        ui.value_box(
            "Passageiros",
            ui.output_text("kpi_passageiros"),
            fill=False
        ),
        ui.value_box(
            "Decolagens",
            ui.output_text("kpi_decolagens"),
            fill=False
        ),
        ui.value_box(
            "Destinos",
            ui.output_text("kpi_destinos"),
            fill=False
        ),
        ui.card(
            ui.card_header("RPK, ASK e Load Factor"),
            ui.card_body(output_widget("plot_rpk_ask_loadf_operacionalactor"))
        ),
        ui.card(
            ui.card_header("Passageiros"),
            ui.card_body(output_widget("plot_passageiros"))
        ),
        ui.card(
            ui.card_header("Decolagens"),
            ui.card_body(output_widget("plot_decolagens"))
        ),
        ui.card(
            ui.card_header("Destinos"),
            ui.card_body(output_widget("plot_destinos"))
        ),
        col_widths=[2, 2, 2, 2, 2, 2, 12, 4, 4, 4],
        align="center",

    )
)

kpis_financeiros = ui.layout_sidebar(
    ui.sidebar(
        ui.h2("Indicadores Financeiros"),
        ui.input_selectize(
            "select_periodo_fin",
            "Período",
            choices=periodo_fin,
            selected=periodo_fin[0],
            multiple=False,
        ),
        ui.input_selectize(
            "select_empresa_fin",
            "Empresa",
            choices=empresas_fin,
            selected=empresas_fin,
            multiple=True,
        ),
        bg="#f8f8f8",
        open="always",
        fillable=True,
    ),
    ui.layout_columns(
        ui.value_box(
            "Receita Operacional Líquida",
            ui.output_text("kpi_receita_operacional"),
            fill=False
        ),
        ui.value_box(
            "Custo do Serviços Prestados",
            ui.output_text("kpi_custo_servicos"),
            fill=False
        ),
        ui.value_box(
            "Lucro Bruto",
            ui.output_text("kpi_lucro_bruto"),
            fill=False
        ),
        ui.value_box(
            "Resultado Líquido",
            ui.output_text("kpi_resultado_liquido"),
            fill=False
        ),
        ui.card(
            ui.card_header(
                ui.input_selectize(
                    "select_conta_fin",
                    "",
                    choices=[
                        '(=) Receita Operacional Líquida',
                        '(-) Custos dos Serviços Prestados',
                        '(=) Lucro Bruto',
                        '(=) Resultado Líquido do Período'
                    ],
                    selected='(=) Receita Operacional Líquida',
                    multiple=False,
                    width="100%"
                )
            ),
            ui.card_body(output_widget("plot_financeiro")),
        ),
        col_widths=[3, 3, 3, 3, 12],
        align="center",
    )

)

app_ui = ui.page_fluid(
    ui.page_navbar(
        ui.nav_panel(
            "Indicadores Operacionais",
            ui.card(
                kpis_operacionais
            ),
        ),
        ui.nav_panel(
            "Indicadores Financeiros",
            ui.card(
                kpis_financeiros
            ),
        ),
        title=ui.output_image("logo", height="60px"),
    ),
    title="Dashboard ANAC - Dados Estatísticos",
)

def server(input, output, session):
    @reactive.effect
    def update_empresa_choices():
        nacionalidades = input.select_nacionalidade()
        empresas = df_operacional[df_operacional['EMPRESA (NACIONALIDADE)'].isin(nacionalidades)]['EMPRESA (SIGLA)'].sort_values().unique().tolist()
        empresas_default = ['AZU', 'GLO', 'TAM']
        return ui.update_selectize(
            "select_empresa",
            choices=empresas,
            selected=empresas_default if "BRASILEIRA" in nacionalidades else [],
            )
    
    @reactive.calc
    def filtered_data_operacional():
        date_range = input.select_date_kpis()
        empresas = input.select_empresa()
        # if not date_range or not empresas:
        #     return pd.DataFrame()  # Return empty DataFrame if no date range or companies selected
        start_date, end_date = date_range
        mask = (
            (df_operacional['dt_referencia'] >= start_date) &
            (df_operacional['dt_referencia'] <= end_date) &
            (df_operacional['EMPRESA (SIGLA)'].isin(empresas))
        )
        return df_operacional.loc[mask]
    
    @reactive.calc
    def filtered_data_financeiro():
        empresas = input.select_empresa_fin()
        mask = (
            (df_financeiro['empresa'].isin(empresas))
        )
        return df_financeiro.loc[mask]


    @render.image
    def logo():
        img: ImgData = {"src": str(logo_path), "width": "200px"}
        return img

    @render.text
    def kpi_ask():
        df_operacional = filtered_data_operacional()
        return format_number(df_operacional['ASK'].sum())
    
    @render.text
    def kpi_rpk():
        df_operacional = filtered_data_operacional()
        return format_number(df_operacional['RPK'].sum())
    
    @render.text
    def kpi_load_factor():
        df_operacional = filtered_data_operacional()
        total_rpk = df_operacional['RPK'].sum()
        total_ask = df_operacional['ASK'].sum()
        if total_ask == 0:
            return "0%"
        load_factor = (total_rpk / total_ask) * 100
        return f"{load_factor:.2f}%"

    @render.text
    def kpi_passageiros():
        df_operacional = filtered_data_operacional()
        passageiros_pagos = df_operacional['PASSAGEIROS PAGOS'].sum()
        passageiros_gratuitos = df_operacional['PASSAGEIROS GRÁTIS'].sum()
        return format_number(passageiros_pagos + passageiros_gratuitos)

    @render.text
    def kpi_decolagens():
        df_operacional = filtered_data_operacional()
        return format_number(df_operacional['DECOLAGENS'].sum())
    
    @render.text
    def kpi_destinos():
        df_operacional = filtered_data_operacional()
        return format_number(df_operacional['AEROPORTO DE DESTINO (SIGLA)'].nunique())

    @render_widget
    def plot_rpk_ask_loadf_operacionalactor():
        df_operacional = filtered_data_operacional()
        grouped = df_operacional.groupby('dt_referencia').agg({'RPK': 'sum', 'ASK': 'sum'}).reset_index()
        grouped['Load Factor'] = (grouped['RPK'] / grouped['ASK']) * 100
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(
            x=grouped['dt_referencia'],
            y=grouped['RPK'],
            name='RPK',
            marker_color='#B3B3B3',
            yaxis='y1',
            text=grouped['RPK'].apply(lambda x: format_number(x)),
            textangle=-90,
            textposition='inside',
            textfont=dict(color='white', size=12),
            hovertext=[f"{format_number(val)}" for val in grouped['RPK']],
            hoverinfo='text+name',
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Bar(
                x=grouped['dt_referencia'],
                y=grouped['ASK'],
                name='ASK',
                marker_color='#666666',
                yaxis='y1',
                text=grouped['ASK'].apply(lambda x: format_number(x)),
                textangle=-90,
                textposition='inside',
                textfont=dict(color='white', size=12),
                hovertext=[f"{format_number(val)}" for val in grouped['ASK']],
                hoverinfo='text+name',
            ),
            secondary_y=False,
        )

        fig.add_trace(
            go.Scatter(
                x=grouped['dt_referencia'],
                y=grouped['Load Factor'],
                name='Load Factor',
                mode='lines+markers',
                line=dict(color='black', width=2),
                text=grouped['Load Factor'].apply(lambda x: f'{x:.2f}%'),
                textposition='top center',
                textfont=dict(color='black', size=12),
                yaxis='y2',
                hovertext=[f"{lf:.2f}%" for lf in grouped['Load Factor']],
                hoverinfo='text+name',
            ),
            secondary_y=True,
        )

        # Configurar layout para melhor visualização dos rótulos
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode='x unified',
            margin=dict(t=50, b=50, l=50, r=50),
            plot_bgcolor='rgba(0,0,0,0)',  # Remove cor de fundo do gráfico
            paper_bgcolor='rgba(0,0,0,0)',  # Remove cor de fundo do papel
        )
        
        # Remover completamente o menu de opções do Plotly
        fig.update_layout(
            modebar={'remove': ['pan2d', 'select2d', 'lasso2d', 'resetScale2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'zoom2d', 'toImage', 'downloadPlot']}
        )
        
        # Configurar eixos
        fig.update_xaxes(
            dtick="M1",
            tickformat="%b\n%Y",
        )

        fig.update_yaxes(
            title_text="RPK / ASK",
            secondary_y=False,
            showgrid=True,  # Adiciona linhas de grade ao eixo y primário
            gridcolor='LightGray',
        )
        fig.update_yaxes(
            title_text="Load Factor (%)", 
            secondary_y=True,
            showgrid=False,  # Remove linhas de grade do eixo y secundário
            # range=[50, 100],  # Define range de 50% a 100%
            ticksuffix="%",  # Adiciona símbolo % aos números do eixo
        )

        return fig
    
    @render_widget
    def plot_passageiros():
        df_operacional = filtered_data_operacional()
        df_operacional['quarter'] = pd.to_datetime(df_operacional['dt_referencia']).dt.to_period('Q')
        grouped = df_operacional.groupby(['EMPRESA (SIGLA)','quarter']).agg({'PASSAGEIROS PAGOS': 'sum', 'PASSAGEIROS GRÁTIS': 'sum'}).reset_index()
        grouped['Total Passageiros'] = grouped['PASSAGEIROS PAGOS'] + grouped['PASSAGEIROS GRÁTIS']
        fig = go.Figure()
        for empresa in grouped['EMPRESA (SIGLA)'].unique():
            empresa_data = grouped[grouped['EMPRESA (SIGLA)'] == empresa]
            fig.add_trace(
                go.Bar(
                    x=empresa_data['quarter'].astype(str),
                    y=empresa_data['PASSAGEIROS PAGOS'],
                    name=f'{empresa}',
                    marker_color=color_mapping.get(empresa, '#f8f8f8'),
                    text=empresa_data['PASSAGEIROS PAGOS'].apply(lambda x: format_number(x)),
                    textangle=-90,
                    textposition='inside',
                    textfont=dict(color='white', size=12),
                    hovertext=[f"{format_number(val)}" for val in empresa_data['PASSAGEIROS PAGOS']],
                    hoverinfo='text+name',
                )
            )

        fig.update_xaxes(
            tickangle=-45,
        )

        # Configurar layout para melhor visualização dos rótulos
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode='x unified',
            margin=dict(t=50, b=50, l=50, r=50),
            plot_bgcolor='rgba(0,0,0,0)',  # Remove cor de fundo do gráfico
            paper_bgcolor='rgba(0,0,0,0)',  # Remove cor de fundo do papel
        )
        
        # Remover completamente o menu de opções do Plotly
        fig.update_layout(
            modebar={'remove': ['pan2d', 'select2d', 'lasso2d', 'resetScale2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'zoom2d', 'toImage', 'downloadPlot']}
        )
        return fig
    
    @render_widget
    def plot_decolagens():
        df_operacional = filtered_data_operacional()
        df_operacional['quarter'] = pd.to_datetime(df_operacional['dt_referencia']).dt.to_period('Q')
        grouped = df_operacional.groupby(['EMPRESA (SIGLA)','quarter']).agg({'DECOLAGENS': 'sum'}).reset_index()
        fig = go.Figure()
        for empresa in grouped['EMPRESA (SIGLA)'].unique():
            empresa_data = grouped[grouped['EMPRESA (SIGLA)'] == empresa]
            fig.add_trace(
                go.Bar(
                    x=empresa_data['quarter'].astype(str),
                    y=empresa_data['DECOLAGENS'],
                    name=f'{empresa}',
                    marker_color=color_mapping.get(empresa, '#f8f8f8'),
                    text=empresa_data['DECOLAGENS'].apply(lambda x: format_number(x)),
                    textangle=-90,
                    textposition='inside',
                    textfont=dict(color='white', size=12),
                    hovertext=[f"{format_number(val)}" for val in empresa_data['DECOLAGENS']],
                    hoverinfo='text+name',
                )
            )
        fig.update_xaxes(
            tickangle=-45,
        )
        # Configurar layout para melhor visualização dos rótulos
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode='x unified',
            margin=dict(t=50, b=50, l=50, r=50),
            plot_bgcolor='rgba(0,0,0,0)',  # Remove cor de fundo do gráfico
            paper_bgcolor='rgba(0,0,0,0)',  # Remove cor de fundo do papel
        )
        
        # Remover completamente o menu de opções do Plotly
        fig.update_layout(
            modebar={'remove': ['pan2d', 'select2d', 'lasso2d', 'resetScale2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'zoom2d', 'toImage', 'downloadPlot']}
        )
        return fig
    
    @render_widget
    def plot_destinos():
        df_operacional = filtered_data_operacional()
        df_operacional['quarter'] = pd.to_datetime(df_operacional['dt_referencia']).dt.to_period('Q')
        grouped = df_operacional.groupby(['EMPRESA (SIGLA)','quarter']).agg({'AEROPORTO DE DESTINO (SIGLA)': 'nunique'}).reset_index()
        fig = go.Figure()
        for empresa in grouped['EMPRESA (SIGLA)'].unique():
            empresa_data = grouped[grouped['EMPRESA (SIGLA)'] == empresa]
            fig.add_trace(
                go.Bar(
                    x=empresa_data['quarter'].astype(str),
                    y=empresa_data['AEROPORTO DE DESTINO (SIGLA)'],
                    name=f'{empresa}',
                    marker_color=color_mapping.get(empresa, '#f8f8f8'),
                    text=empresa_data['AEROPORTO DE DESTINO (SIGLA)'].apply(lambda x: format_number(x)),
                    textangle=-90,
                    textposition='inside',
                    textfont=dict(color='white', size=12),
                    hovertext=[f"{format_number(val)}" for val in empresa_data['AEROPORTO DE DESTINO (SIGLA)']],
                    hoverinfo='text+name',
                )
            )
        fig.update_xaxes(
            tickangle=-45,
        )
        # Configurar layout para melhor visualização dos rótulos
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode='x unified',
            margin=dict(t=50, b=50, l=50, r=50),
            plot_bgcolor='rgba(0,0,0,0)',  # Remove cor de fundo do gráfico
            paper_bgcolor='rgba(0,0,0,0)',  # Remove cor de fundo do papel
        )
        
        # Remover completamente o menu de opções do Plotly
        fig.update_layout(
            modebar={'remove': ['pan2d', 'select2d', 'lasso2d', 'resetScale2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'zoom2d', 'toImage', 'downloadPlot']}
        )
        return fig

    @render.text
    def kpi_receita_operacional():
        df_financeiro = filtered_data_financeiro()
        periodo = input.select_periodo_fin()
        df_financeiro = df_financeiro[
            (df_financeiro['periodo'] == periodo) &
            (df_financeiro['tipo_saldo'] == 'saldo_inicio_periodo') &
            (df_financeiro['descricao_conta'] == '(=) Receita Operacional Líquida')
            ]
        valor = df_financeiro['valor_saldo'].sum()
        return format_number(valor)
    
    @render.text
    def kpi_custo_servicos():
        df_financeiro = filtered_data_financeiro()
        periodo = input.select_periodo_fin()
        df_financeiro = df_financeiro[
            (df_financeiro['periodo'] == periodo) &
            (df_financeiro['tipo_saldo'] == 'saldo_inicio_periodo') &
            (df_financeiro['descricao_conta'] == '(-) Custos dos Serviços Prestados')
            ]
        valor = -df_financeiro['valor_saldo'].sum()
        return format_number(valor)
    
    @render.text
    def kpi_lucro_bruto():
        df_financeiro = filtered_data_financeiro()
        periodo = input.select_periodo_fin()
        df_financeiro = df_financeiro[
            (df_financeiro['periodo'] == periodo) &
            (df_financeiro['tipo_saldo'] == 'saldo_inicio_periodo') &
            (df_financeiro['descricao_conta'] == '(=) Lucro Bruto')
            ]
        valor = df_financeiro['valor_saldo'].sum()
        return format_number(valor)
    
    @render.text
    def kpi_resultado_liquido():
        df_financeiro = filtered_data_financeiro()
        periodo = input.select_periodo_fin()
        df_financeiro = df_financeiro[
            (df_financeiro['periodo'] == periodo) &
            (df_financeiro['tipo_saldo'] == 'saldo_inicio_periodo') &
            (df_financeiro['descricao_conta'] == '(=) Resultado Líquido do Período')
            ]
        valor = df_financeiro['valor_saldo'].sum()
        return format_number(valor)
    
    @render_widget
    def plot_financeiro():
        df_financeiro = filtered_data_financeiro()
        conta = input.select_conta_fin()
        df_financeiro = df_financeiro[
            (df_financeiro['tipo_saldo'] == 'saldo_inicio_periodo') &
            (df_financeiro['descricao_conta'] == conta)
            ]
        if conta == "(-) Custos dos Serviços Prestados":
            df_financeiro['valor_saldo'] = -df_financeiro['valor_saldo']
        
        df_financeiro = df_financeiro.sort_values(by=['periodo'])
        fig = go.Figure()
        for empresa in df_financeiro['empresa'].sort_values().unique():
            empresa_data = df_financeiro[df_financeiro['empresa'] == empresa]
            fig.add_trace(
                go.Bar(
                    x=empresa_data['periodo'],
                    y=empresa_data['valor_saldo'],
                    name=f'{empresa}',
                    marker_color=color_mapping.get(empresa, '#f8f8f8'),
                    text=empresa_data['valor_saldo'].apply(lambda x: format_number(x)),
                    textangle=-90,
                    textposition='inside',
                    textfont=dict(color='white', size=12),
                    hovertext=[f"{format_number(val)}" for val in empresa_data['valor_saldo']],
                    hoverinfo='text+name',
                )
            )
        # Configurar layout para melhor visualização dos rótulos
        fig.update_layout(
            showlegend=True,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            hovermode='x unified',
            margin=dict(t=50, b=50, l=50, r=50),
            plot_bgcolor='rgba(0,0,0,0)',  # Remove cor de fundo do gráfico
            paper_bgcolor='rgba(0,0,0,0)',  # Remove cor de fundo do papel
        )
        
        # Remover completamente o menu de opções do Plotly
        fig.update_layout(
            modebar={'remove': ['pan2d', 'select2d', 'lasso2d', 'resetScale2d', 'zoomIn2d', 'zoomOut2d', 'autoScale2d', 'zoom2d', 'toImage', 'downloadPlot']}
        )
        return fig

app = App(app_ui, server)