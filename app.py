# app.py (corrigido: compatibilidade session_state + gestão completa das contrapartidas)
import streamlit as st
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image
import os
import datetime
import copy

# ---------------------------
# Compatibilidade session_state
# ---------------------------
# Em versões muito antigas do Streamlit 'session_state' pode não existir.
# Fazemos um fallback seguro para evitar o erro que você mostrou.
if not hasattr(st, "session_state") or st.session_state is None:
    class _SimpleSession(dict):
        def __getattr__(self, name):
            return self.get(name)
        def __setattr__(self, name, value):
            self[name] = value
    st.session_state = _SimpleSession()

# Inicializações seguras das chaves usadas
if "contrapartidas" not in st.session_state:
    st.session_state["contrapartidas"] = []
if "edit_index" not in st.session_state:
    st.session_state["edit_index"] = None

# ---------------------------
# Config
# ---------------------------
st.set_page_config(page_title="Gerador de Relatórios", layout="centered")
st.title("📑 Gerador de Relatórios Automático")

# ========================
# FORMULÁRIO PRINCIPAL
# ========================
nome_projeto = st.text_input("Nome do Projeto")
nome_sindicato = st.text_input("Nome do Sindicato")
cidade = st.text_input("Cidade")
data = st.date_input("Data", datetime.date.today())

# ========================
# CONTRAPARTIDAS (adicionar / listar / editar / remover)
# ========================
st.subheader("➕ Adicionar Contrapartida")

col1, col2 = st.columns([3, 1])
with col1:
    nova_desc = st.text_input("Descrição da Contrapartida", key="desc_contrapartida")
with col2:
    nova_status = st.selectbox("Comprovada?", ["Sim", "Não"], key="status_contrapartida")

if st.button("Adicionar Contrapartida"):
    if nova_desc:
        st.session_state.contrapartidas.append({
            "descricao": nova_desc,
            "status": nova_status
        })
        st.success(f"Contrapartida adicionada: {nova_desc} ({nova_status})")
        # limpar campo de input
        st.session_state["desc_contrapartida"] = ""

# Mostrar contrapartidas já adicionadas com botões Editar / Remover
if st.session_state.contrapartidas:
    st.write("📋 Contrapartidas adicionadas:")
    for i, c in enumerate(st.session_state.contrapartidas):
        colA, colB, colC = st.columns([4, 1, 1])
        with colA:
            st.write(f"**{i+1}.** {c['descricao']} — *{c['status']}*")
        with colB:
            if st.button("✏️ Editar", key=f"edit_{i}"):
                st.session_state.edit_index = i
        with colC:
            if st.button("🗑 Remover", key=f"del_{i}"):
                st.session_state.contrapartidas.pop(i)
                st.experimental_rerun()

    # Modo edição (aparece somente quando se clica em editar)
    if st.session_state.edit_index is not None:
        idx = st.session_state.edit_index
        if 0 <= idx < len(st.session_state.contrapartidas):
            st.info(f"✏️ Editando contrapartida {idx+1}")
            edit_desc = st.text_input("Nova descrição", value=st.session_state.contrapartidas[idx]["descricao"], key="edit_desc")
            edit_status = st.selectbox("Comprovada?", ["Sim", "Não"], index=0 if st.session_state.contrapartidas[idx]["status"] == "Sim" else 1, key="edit_status")
            colSave, colCancel = st.columns([1,1])
            with colSave:
                if st.button("💾 Salvar Alterações"):
                    st.session_state.contrapartidas[idx] = {"descricao": edit_desc, "status": edit_status}
                    st.session_state.edit_index = None
                    st.experimental_rerun()
            with colCancel:
                if st.button("❌ Cancelar Edição"):
                    st.session_state.edit_index = None
                    st.experimental_rerun()
        else:
            st.session_state.edit_index = None

# ========================
# UPLOAD DE IMAGENS
# ========================
st.subheader("📷 Upload de Fotos")
imagens = st.file_uploader(
    "Selecione imagens para inserir no relatório",
    type=["jpg", "jpeg", "png", "bmp", "gif"],
    accept_multiple_files=True
)

# Checkbox para compactar imagens (opcional)
compact_option = st.checkbox("Compactar imagens antes de inserir (reduz tamanho do arquivo)", value=True)

# ========================
# GERAR RELATÓRIO
# ========================
if st.button("Gerar Relatório"):
    if not (nome_projeto and nome_sindicato and cidade and data):
        st.error("⚠️ Por favor, preencha todos os campos obrigatórios!")
    else:
        try:
            doc = Document("Modelo.docx")

            # Normalizar textos
            nome_projeto_fmt = nome_projeto.upper()
            nome_sindicato_fmt = nome_sindicato.upper()
            cidade_fmt = cidade.capitalize()
            data_fmt = data.strftime("%d/%m/%Y")

            substituicoes = {
                "(TEXTO_NOMEPROJETO)": nome_projeto_fmt,
                "(TEXTO_NOMESINDICATO)": nome_sindicato_fmt,
                "(CIDADE)": cidade_fmt,
                "(DATA)": data_fmt
            }

            # Substituir texto em parágrafos e tabelas
            def substituir(doc, antigo, novo):
                for p in doc.paragraphs:
                    if antigo in p.text:
                        for run in p.runs:
                            run.text = run.text.replace(antigo, novo)
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for p in cell.paragraphs:
                                if antigo in p.text:
                                    for run in p.runs:
                                        run.text = run.text.replace(antigo, novo)

            for k, v in substituicoes.items():
                substituir(doc, k, v)

            # ========================
            # CONTRAPARTIDAS NA TABELA
            # ========================
            # Preenche marcadores existentes (contrapartida01, 02, 03 ...)
            if st.session_state.contrapartidas:
                # Primeiro preenche os marcadores que já existem nas células
                for table in doc.tables:
                    for row in table.rows:
                        for cell in row.cells:
                            for p in cell.paragraphs:
                                for idx, c in enumerate(st.session_state.contrapartidas, start=1):
                                    marcador = f"(contrapartida{idx:02d})"
                                    if marcador in p.text:
                                        for run in p.runs:
                                            run.text = run.text.replace(marcador, c["descricao"])
                                        # Preencher SIM / NÃO na mesma linha: substitui (XSIM)/(XNAO) nas runs dessa linha
                                        for rcell in row.cells:
                                            for rp in rcell.paragraphs:
                                                for run in rp.runs:
                                                    if c["status"] == "Sim":
