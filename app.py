import sqlite3
import pandas as pd
import streamlit as st

from st_aggrid import AgGrid, GridOptionsBuilder

# Configuração do banco de dados
conn = sqlite3.connect('sample_management.db')
cursor = conn.cursor()

# Criação da tabela no banco de dados, caso ainda não exista
cursor.execute('''
    CREATE TABLE IF NOT EXISTS samples (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        categoria TEXT,
        fabricante TEXT,
        codigo TEXT,
        pn_fabricante TEXT,
        pn_intelbras TEXT,
        sn TEXT,
        tipo_amostra TEXT,
        status TEXT,
        localizacao TEXT,
        projeto_poc_evento TEXT,
        responsavel TEXT,
        data_saida DATE,
        data_retorno DATE,
        observacoes TEXT
    )
''')
conn.commit()


# Função para exibir a tabela com campo de pesquisa
from st_aggrid import AgGrid, GridOptionsBuilder

def exibir_tabela():
    st.header("Amostras em Estoque")

    # Campo de pesquisa
    pesquisa = st.text_input("Pesquisar amostras por código, fabricante ou categoria:")

    # Consulta ao banco de dados com base na pesquisa
    query = "SELECT * FROM samples WHERE codigo LIKE ? OR fabricante LIKE ? OR categoria LIKE ?"
    df = pd.read_sql_query(query, conn, params=(f'%{pesquisa}%', f'%{pesquisa}%', f'%{pesquisa}%'))

    if df.empty:
        st.warning("Nenhum registro encontrado.")
        return

    # Configuração da tabela com maior controle de largura
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column("codigo", width=600)  # Ajuste a largura da coluna conforme necessário
    gb.configure_column("fabricante", width=200)
    # Adicione mais configurações de largura para outras colunas conforme necessário
    grid_options = gb.build()

    st.write("**Tabela de Amostras**")
    AgGrid(df, gridOptions=grid_options, enable_enterprise_modules=True, theme='streamlit')





# Função para cadastrar nova amostra
def cadastrar_amostra():
    st.subheader("Cadastrar Nova Amostra")

    with st.form("form_cadastro"):
        categoria = st.text_input("Categoria")
        fabricante = st.text_input("Fabricante")
        codigo = st.text_input("Código")
        pn_fabricante = st.text_input("PN Fabricante")
        pn_intelbras = st.text_input("PN Intelbras")
        sn = st.text_input("SN")
        tipo_amostra = st.text_input("Tipo Amostra")
        status = st.selectbox("Status", ["Pending", "Processed", "Completed"])
        localizacao = st.text_input("Localização")
        projeto_poc_evento = st.text_input("Projeto/POC/Evento")
        responsavel = st.text_input("Responsável")
        data_saida = st.date_input("Data de Saída")
        data_retorno = st.date_input("Data de Retorno", None)
        observacoes = st.text_area("Observações")

        submit_button = st.form_submit_button("Cadastrar")

        if submit_button:
            if categoria and fabricante and codigo:
                cursor.execute('''
                    INSERT INTO samples 
                    (categoria, fabricante, codigo, pn_fabricante, pn_intelbras, sn, tipo_amostra, status, localizacao, projeto_poc_evento, responsavel, data_saida, data_retorno, observacoes) 
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (categoria, fabricante, codigo, pn_fabricante, pn_intelbras, sn, tipo_amostra, status, localizacao,
                      projeto_poc_evento, responsavel, data_saida, data_retorno, observacoes))
                conn.commit()
                st.success(f"Amostra '{codigo}' adicionada com sucesso!")
            else:
                st.error("Por favor, preencha os campos obrigatórios (Categoria, Fabricante, Código).")


# Função para editar uma amostra existente
def editar_amostra():
    st.subheader("Editar Amostra")

    # Selecione o registro a ser editado
    id_amostra = st.number_input("ID da Amostra", min_value=1, step=1)

    if id_amostra:
        # Consulta os dados existentes
        query = "SELECT * FROM samples WHERE id = ?"
        df = pd.read_sql_query(query, conn, params=(id_amostra,))

        if df.empty:
            st.error("Amostra não encontrada.")
            return

        # Preenche o formulário com os dados existentes
        amostra = df.iloc[0]
        with st.form("form_editar"):
            categoria = st.text_input("Categoria", amostra['categoria'])
            fabricante = st.text_input("Fabricante", amostra['fabricante'])
            codigo = st.text_input("Código", amostra['codigo'])
            pn_fabricante = st.text_input("PN Fabricante", amostra['pn_fabricante'])
            pn_intelbras = st.text_input("PN Intelbras", amostra['pn_intelbras'])
            sn = st.text_input("SN", amostra['sn'])
            tipo_amostra = st.text_input("Tipo Amostra", amostra['tipo_amostra'])
            status = st.selectbox("Status", ["Pending", "Processed", "Completed"],
                                  index=["Pending", "Processed", "Completed"].index(amostra['status']))
            localizacao = st.text_input("Localização", amostra['localizacao'])
            projeto_poc_evento = st.text_input("Projeto/POC/Evento", amostra['projeto_poc_evento'])
            responsavel = st.text_input("Responsável", amostra['responsavel'])
            data_saida = st.date_input("Data de Saída", pd.to_datetime(amostra['data_saida']))
            data_retorno = st.date_input("Data de Retorno", pd.to_datetime(amostra['data_retorno']))
            observacoes = st.text_area("Observações", amostra['observacoes'])

            submit_button = st.form_submit_button("Atualizar")

            if submit_button:
                # Atualiza os dados no banco de dados
                cursor.execute('''
                    UPDATE samples
                    SET categoria = ?, fabricante = ?, codigo = ?, pn_fabricante = ?, pn_intelbras = ?, sn = ?, tipo_amostra = ?, status = ?, localizacao = ?, projeto_poc_evento = ?, responsavel = ?, data_saida = ?, data_retorno = ?, observacoes = ?
                    WHERE id = ?
                ''', (categoria, fabricante, codigo, pn_fabricante, pn_intelbras, sn, tipo_amostra, status, localizacao,
                      projeto_poc_evento, responsavel, data_saida, data_retorno, observacoes, id_amostra))
                conn.commit()
                st.success(f"Amostra '{codigo}' atualizada com sucesso!")


# Função principal
def main():
    st.title("Controle de Amostras")

    # Exibir a tabela de amostras
    exibir_tabela()

    # Checkbox para cadastrar nova amostra
    if st.checkbox("Cadastrar Nova Amostra"):
        cadastrar_amostra()

    # Checkbox para editar amostra existente
    if st.checkbox("Editar Amostra Existente"):
        editar_amostra()


if __name__ == '__main__':
    main()
