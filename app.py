import streamlit as st
import io
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm

st.title("📋 Teste - Preencher PDF Modelo")

# --- Campos de teste ---
patrocinado = st.text_input("Patrocinado")
numero_contrato = st.text_input("Nº do Contrato")
nome_evento = st.text_input("Nome do Evento")
municipio = st.text_input("Município de Realização")

# --- Upload do PDF modelo ---
modelo_pdf = st.file_uploader("Carregue o PDF modelo", type=["pdf"])

if st.button("Gerar Relatório") and modelo_pdf:
    # Criar overlay (camada transparente com textos)
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=A4)
    can.setFont("Helvetica", 11)

    # ⚠️ OBS: essas coordenadas são apenas exemplo!
    # Precisamos ajustar testando até os textos ficarem nas posições certas
    can.drawString(30*mm, 250*mm, f"Patrocinado: {patrocinado}")
    can.drawString(30*mm, 240*mm, f"Nº do Contrato: {numero_contrato}")
    can.drawString(30*mm, 230*mm, f"Nome do Evento: {nome_evento}")
    can.drawString(30*mm, 220*mm, f"Município: {municipio}")

    can.save()
    packet.seek(0)

    # Juntar overlay com o PDF original
    overlay_pdf = PdfReader(packet)
    original_pdf = PdfReader(modelo_pdf)
    writer = PdfWriter()

    for i, page in enumerate(original_pdf.pages):
        if i == 0:  # só aplicar overlay na primeira página
            page.merge_page(overlay_pdf.pages[0])
        writer.add_page(page)

    # Exportar resultado
    output = io.BytesIO()
    writer.write(output)

    st.success("✅ PDF gerado com sucesso!")
    st.download_button("⬇️ Baixar PDF", output.getvalue(), "relatorio_teste.pdf", "application/pdf")
