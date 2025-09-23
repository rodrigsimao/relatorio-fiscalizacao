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
imagens = st.file_uploader(
    "Selecione imagens para inserir no relatório",
    type=["jpg", "jpeg", "png", "bmp", "gif"],
    accept_multiple_files=True
)

if st.button("Gerar Relatório"):
    if not (nome_projeto and nome_sindicato and cidade and data):
        st.error("⚠️ Por favor, preencha todos os campos obrigatórios!")
    else:
        try:
            # Carregar o modelo
            doc = Document("Modelo.docx")

            # Normalizar os textos
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

            # Substituir texto nos parágrafos e tabelas
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

            # Inserir imagens no marcador
            for i, paragraph in enumerate(doc.paragraphs):
                if "(FOTOS_ORGANIZADAS)" in paragraph.text:
                    p = paragraph._element
                    p.getparent().remove(p)

                    if imagens:
                        for idx, img in enumerate(imagens, 1):
                            # Compactar e salvar imagem temporária
                            with Image.open(img) as im:
                                im = im.convert("RGB")  # garantir compatibilidade
                                max_width = 1600
                                if im.width > max_width:
                                    ratio = max_width / im.width
                                    new_size = (max_width, int(im.height * ratio))
                                    im = im.resize(new_size, Image.LANCZOS)
                                temp_path = f"temp_{idx}.jpg"
                                im.save(temp_path, "JPEG", optimize=True, quality=70)

                            # Quebra de página antes da foto (menos a primeira)
                            if idx > 1:
                                doc.add_page_break()

                            # Foto alinhada à esquerda
                            p_img = doc.add_paragraph()
                            p_img.alignment = WD_ALIGN_PARAGRAPH.LEFT
                            run_img = p_img.add_run()
                            run_img.add_picture(temp_path, width=Inches(6))

                            # Legenda alinhada à esquerda
                            legenda = os.path.splitext(os.path.basename(img.name))[0]
                            p_legenda = doc.add_paragraph()
                            p_legenda.alignment = WD_ALIGN_PARAGRAPH.LEFT
                            run_legenda = p_legenda.add_run(f"Foto {idx}: {legenda}")
                            run_legenda.font.name = "Calibri"
                            run_legenda.font.size = Pt(10)
                            run_legenda.bold = True

                            # Apagar imagem temporária
                            os.remove(temp_path)
                    break

            # Salvar arquivo final
            output_path = "Relatorio_Gerado.docx"
            doc.save(output_path)

            with open(output_path, "rb") as f:
                st.success("✅ Relatório gerado com sucesso!")
                st.download_button(
                    "⬇️ Baixar Relatório",
                    f,
                    file_name="Relatorio_Gerado.docx",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )

        except Exception as e:
            st.error(f"❌ Erro ao gerar relatório: {e}")
