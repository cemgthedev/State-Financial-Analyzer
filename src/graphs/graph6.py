import pandas as pd
import matplotlib.pyplot as plt

# Carregar os dados do Excel
convenios_2007_df = pd.read_excel('../data/Convênios 2007 - Setembro 2023.xlsx')
df = convenios_2007_df

# Extrair o ano da data de assinatura
df['Ano de Assinatura'] = pd.to_datetime(df['Data de assinatura']).dt.year

# Agrupar os dados por ano e somar os valores
df_agrupado = df.groupby('Ano de Assinatura')[['Valor pago']].sum()


df_agrupado.plot(kind='line', figsize=(12, 6), marker='o') # Adicionado marker='o' para marcar os pontos
plt.title('Evolução dos Valores Totais Pagos de Convênios por Ano')
plt.xlabel('Ano de Assinatura')
plt.ylabel('Valor (bilhões)')

# Adicionar grade para melhor visualização
plt.grid(True)

# Exibir o gráfico
plt.show()
