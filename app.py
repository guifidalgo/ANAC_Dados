from shiny import App, render, ui, reactive
from shiny.types import ImgData
from shinywidgets import output_widget, render_widget
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import os


logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'vlls_logo.png')

file_path = os.path.join(os.path.dirname(__file__), 'notebooks', 'anac_dados_estatisticos.csv')

df = pd.read_csv(file_path)
df['dt_referencia'] = pd.to_datetime(df['dt_referencia'], format='%Y-%m-%d').dt.date
date_min = df['dt_referencia'].min()
date_max = df['dt_referencia'].max()

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
            choices=df['EMPRESA (NACIONALIDADE)'].sort_values().unique().tolist(),
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
            ui.card_body(output_widget("plot_rpk_ask_loadfactor"))
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
        # gap="md",
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
            "About",
            ),
        title=ui.output_image("logo", height="60px"),
    ),
    title="Dashboard ANAC - Dados Estatísticos",
)

def server(input, output, session):
    @reactive.effect
    def update_empresa_choices():
        nacionalidades = input.select_nacionalidade()
        empresas = df[df['EMPRESA (NACIONALIDADE)'].isin(nacionalidades)]['EMPRESA (SIGLA)'].sort_values().unique().tolist()
        empresas_default = ['AZU', 'GLO', 'TAM']
        return ui.update_selectize(
            "select_empresa",
            choices=empresas,
            selected=empresas_default if "BRASILEIRA" in nacionalidades else [],
            )
    
    @reactive.calc
    def filtered_data():
        date_range = input.select_date_kpis()
        empresas = input.select_empresa()
        # if not date_range or not empresas:
        #     return pd.DataFrame()  # Return empty DataFrame if no date range or companies selected
        start_date, end_date = date_range
        mask = (
            (df['dt_referencia'] >= start_date) &
            (df['dt_referencia'] <= end_date) &
            (df['EMPRESA (SIGLA)'].isin(empresas))
        )
        return df.loc[mask]


    @render.image
    def logo():
        img: ImgData = {"src": str(logo_path), "width": "200px"}
        return img

    @render.text
    def kpi_ask():
        df = filtered_data()
        return format_number(df['ASK'].sum())
    
    @render.text
    def kpi_rpk():
        df = filtered_data()
        return format_number(df['RPK'].sum())
    
    @render.text
    def kpi_load_factor():
        df = filtered_data()
        total_rpk = df['RPK'].sum()
        total_ask = df['ASK'].sum()
        if total_ask == 0:
            return "0%"
        load_factor = (total_rpk / total_ask) * 100
        return f"{load_factor:.2f}%"

    @render.text
    def kpi_passageiros():
        df = filtered_data()
        passageiros_pagos = df['PASSAGEIROS PAGOS'].sum()
        passageiros_gratuitos = df['PASSAGEIROS GRÁTIS'].sum()
        return format_number(passageiros_pagos + passageiros_gratuitos)

    @render.text
    def kpi_decolagens():
        df = filtered_data()
        return format_number(df['DECOLAGENS'].sum())
    
    @render.text
    def kpi_destinos():
        df = filtered_data()
        return format_number(df['AEROPORTO DE DESTINO (SIGLA)'].nunique())


    @render_widget
    def plot_rpk_ask_loadfactor():
        df = filtered_data()
        grouped = df.groupby('dt_referencia').agg({'RPK': 'sum', 'ASK': 'sum'}).reset_index()
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
        df = filtered_data()
        df['quarter'] = pd.to_datetime(df['dt_referencia']).dt.to_period('Q')
        grouped = df.groupby(['EMPRESA (SIGLA)','quarter']).agg({'PASSAGEIROS PAGOS': 'sum', 'PASSAGEIROS GRÁTIS': 'sum'}).reset_index()
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
        df = filtered_data()
        df['quarter'] = pd.to_datetime(df['dt_referencia']).dt.to_period('Q')
        grouped = df.groupby(['EMPRESA (SIGLA)','quarter']).agg({'DECOLAGENS': 'sum'}).reset_index()
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
        df = filtered_data()
        df['quarter'] = pd.to_datetime(df['dt_referencia']).dt.to_period('Q')
        grouped = df.groupby(['EMPRESA (SIGLA)','quarter']).agg({'AEROPORTO DE DESTINO (SIGLA)': 'nunique'}).reset_index()
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