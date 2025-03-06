import transformar

"""###########################################################################################
                                    Carregar
##########################################################################################"""

df_dividendos = (transformar.df_dividendos)

df_dividendos.to_csv('df_dividendos.csv', index=False, encoding='utf-8-sig', sep=';', decimal=',')

print("3. Exportação de planilha realizada!")

print(df_dividendos)