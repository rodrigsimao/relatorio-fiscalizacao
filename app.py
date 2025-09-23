import streamlit as st
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from PIL import Image
import os
import datetime

st.set_page_config(page_title="Gerador de Relatórios", layout="centered")

st.title("📑 Gerador de Relatórios Automático")

# Formulário de entrada
nome_projeto = st.text_input("Nome do Projeto")
nome_sindicato = st.text_input("Nome do Sindicato")
cidade = st.text_input("Cidade")
data = st.date_input("Data", datetime.date.today())

# Upload de múltiplas imagens
imagens = st.file
