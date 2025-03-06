import matplotlib.pyplot as plt
import pandas as pd

# Caminho para o seu arquivo Excel
caminho_arquivo = '/src/data/Convênios 2007 - Setembro 2023.xlsx'

# Carrega o arquivo Excel em um DataFrame
df = pd.read_excel(caminho_arquivo)
df['Ano_assinatura'] = pd.to_datetime(df['Data de assinatura']).dt.year

# Agrupar por ano e calcular as somas dos valores
comparacao_valores = df.groupby('Ano_assinatura').agg(
    Valor_original=('Valor inicial total', 'sum'),
    Valor_atualizado=('Valor atualizado total', 'sum')
).reset_index()

# Ordenar por ano
comparacao_valores = comparacao_valores.sort_values(by='Ano_assinatura')

# Converter para dicionário para facilitar a visualização e uso em gráficos
resultado = comparacao_valores.to_dict(orient='records')

# Cria o gráfico
anos = [item['Ano_assinatura'] for item in resultado]
valores_originais = [item['Valor_original'] for item in resultado]
valores_atualizados = [item['Valor_atualizado'] for item in resultado]

plt.figure(figsize=(12, 6))
plt.bar(anos, valores_originais, label='Valores Originais', alpha=0.7)
plt.bar(anos, valores_atualizados, label='Valores Atualizados', alpha=0.7)
plt.xlabel('Ano de Assinatura')
plt.ylabel('Valor')
plt.title('Comparação de Valores de Convênios por Ano')
plt.legend()
plt.xticks(anos)
plt.tight_layout()
plt.show()
