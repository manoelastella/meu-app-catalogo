import streamlit as st
import pandas as pd
import os
from PIL import Image
import base64
from io import BytesIO

# Configuração da página
st.set_page_config(
    page_title="Catálogo de Louças",
    page_icon="🍽️",
    layout="wide"
)

# Título do app
st.title("🍽️ Catálogo de Louças - Encontre seus Itens")
st.markdown("---")

# Função para carregar os dados do Excel
@st.cache_data
def carregar_catalogo():
    try:
        # Tenta carregar do Excel
        df = pd.read_excel('catalogo_loucas.xlsx')
        return df
    except FileNotFoundError:
        # Se não existir, cria um DataFrame exemplo
        st.warning("Arquivo 'catalogo_loucas.xlsx' não encontrado. Usando dados de exemplo.")
        dados_exemplo = {
            'ID': [1, 2, 3, 4, 5, 6],
            'Nome': ['Prato Branco', 'Copo Americano', 'Taça de Vinho', 'Xícara Café', 'Prato Sobremesa', 'Copo Long Drink'],
            'Categoria': ['Louça', 'Copos', 'Taças', 'Xícaras', 'Louça', 'Copos'],
            'Armario': ['Armário 1', 'Armário 2', 'Armário 3', 'Armário 4', 'Armário 1', 'Armário 2'],
            'Prateleira': ['2', '1', '3', '2', '1', '4'],
            'Descricao': ['Prato fundo branco 25cm', 'Copo americano 300ml', 'Taça para vinho tinto', 'Xícara para café 150ml', 'Prato raso 20cm', 'Copo longo drink 400ml'],
            'Nome_Arquivo': ['prato_branco.jpg', 'copo_americano.jpg', 'taca_vinho.jpg', 'xicara_cafe.jpg', 'prato_sobremesa.jpg', 'copo_long_drink.jpg']
        }
        df = pd.DataFrame(dados_exemplo)
        return df

# Função para carregar imagem
def carregar_imagem(nome_arquivo):
    caminho_imagem = os.path.join('fotos_pecas', nome_arquivo)
    try:
        if os.path.exists(caminho_imagem):
            imagem = Image.open(caminho_imagem)
            return imagem
        else:
            # Imagem placeholder se não encontrar
            return None
    except Exception as e:
        st.error(f"Erro ao carregar imagem: {e}")
        return None

# Função para buscar item
def buscar_item(df, termo_busca):
    # Busca por nome ou ID
    if termo_busca.isdigit():
        resultado = df[df['ID'] == int(termo_busca)]
    else:
        resultado = df[df['Nome'].str.contains(termo_busca, case=False, na=False)]
    return resultado

# Carregar dados
df = carregar_catalogo()

# Sidebar - Filtros e informações
with st.sidebar:
    st.header("🔍 Buscar Item")
    
    # Campo de busca
    termo_busca = st.text_input("Digite o nome ou ID do item:", placeholder="Ex: Prato Branco ou 1")
    
    # Botão de pesquisa
    if st.button("🔍 Pesquisar", use_container_width=True):
        if termo_busca:
            resultados = buscar_item(df, termo_busca)
            if not resultados.empty:
                st.session_state['resultado_busca'] = resultados
                st.session_state['busca_realizada'] = True
                st.success(f"Encontrado(s) {len(resultados)} item(ns)!")
            else:
                st.warning("Nenhum item encontrado. Tente outro termo.")
                st.session_state['busca_realizada'] = False
        else:
            st.warning("Digite um termo para pesquisar.")
    
    # Filtros adicionais
    st.markdown("---")
    st.header("📂 Filtros")
    
    categoria = st.selectbox(
        "Filtrar por categoria:",
        ["Todas"] + sorted(df['Categoria'].unique().tolist())
    )
    
    armario = st.selectbox(
        "Filtrar por armário:",
        ["Todos"] + sorted(df['Armario'].unique().tolist())
    )

# Aplicar filtros
df_filtrado = df.copy()
if categoria != "Todas":
    df_filtrado = df_filtrado[df_filtrado['Categoria'] == categoria]
if armario != "Todos":
    df_filtrado = df_filtrado[df_filtrado['Armario'] == armario]

# Área principal
col1, col2 = st.columns([1, 2])

with col1:
    st.subheader("📋 Lista de Itens")
    st.caption(f"Total: {len(df_filtrado)} itens")
    
    # Mostrar lista de itens
    for idx, row in df_filtrado.iterrows():
        with st.container():
            st.markdown(f"**{row['Nome']}**")
            st.caption(f"📍 {row['Armario']} - Prateleira {row['Prateleira']}")
            st.caption(f"🏷️ {row['Categoria']}")
            if st.button(f"Ver detalhes #{row['ID']}", key=f"btn_{row['ID']}"):
                st.session_state['resultado_busca'] = pd.DataFrame([row])
                st.session_state['busca_realizada'] = True
            st.divider()

with col2:
    st.subheader("🔍 Resultado da Busca")
    
    # Verificar se há resultado de busca
    if 'resultado_busca' in st.session_state and st.session_state['busca_realizada']:
        resultado = st.session_state['resultado_busca']
        
        for idx, row in resultado.iterrows():
            # Criar card para o item
            with st.container():
                st.markdown(f"### {row['Nome']}")
                
                # Mostrar imagem
                imagem = carregar_imagem(row['Nome_Arquivo'])
                if imagem:
                    # Redimensionar imagem para manter proporção
                    st.image(imagem, caption=row['Nome'], use_container_width=True)
                else:
                    st.info("📷 Imagem não disponível")
                
                # Informações do item
                st.markdown("---")
                col_info1, col_info2 = st.columns(2)
                with col_info1:
                    st.markdown("**📍 Localização:**")
                    st.write(f"Armário: {row['Armario']}")
                    st.write(f"Prateleira: {row['Prateleira']}")
                
                with col_info2:
                    st.markdown("**🏷️ Categoria:**")
                    st.write(f"{row['Categoria']}")
                    st.write(f"ID: #{row['ID']}")
                
                st.markdown("**📝 Descrição:**")
                st.write(row['Descricao'])
                
                # Botão para limpar busca
                if st.button("Limpar busca", key="clear_search"):
                    st.session_state['busca_realizada'] = False
                    st.rerun()
                
                st.divider()
    else:
        # Mostrar mensagem padrão
        st.info("👆 Digite o nome ou ID no menu lateral e clique em Pesquisar")
        
        # Mostrar alguns itens em destaque
        st.subheader("📌 Itens em destaque")
        destaque = df_filtrado.head(3)
        for idx, row in destaque.iterrows():
            with st.container():
                col_img, col_info = st.columns([1, 2])
                with col_img:
                    imagem = carregar_imagem(row['Nome_Arquivo'])
                    if imagem:
                        st.image(imagem, caption=row['Nome'], use_container_width=True)
                    else:
                        st.info("📷")
                with col_info:
                    st.markdown(f"**{row['Nome']}**")
                    st.write(f"📍 {row['Armario']} - Prateleira {row['Prateleira']}")
                    st.write(f"🏷️ {row['Categoria']}")
                st.divider()

# Rodapé
st.markdown("---")
st.caption("📦 Catálogo de Louças v1.0 | Dados atualizados em: 13/07/2026")
