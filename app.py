# ========================
# CONTRAPARTIDAS NA TABELA (VERSÃO MAIS ROBUSTA)
# ========================
if st.session_state.contrapartidas:
    for table in doc.tables:
        for row_idx, row in enumerate(table.rows):
            row_text = ' '.join([cell.text for cell in row.cells])
            
            # Verificar se esta linha contém marcadores de contrapartida
            for idx, c in enumerate(st.session_state.contrapartidas, start=1):
                marcador = f"(contrapartida{idx:02d})"
                
                if marcador in row_text:
                    # Encontrar e substituir a descrição
                    for cell in row.cells:
                        for p in cell.paragraphs:
                            for run in p.runs:
                                if marcador in run.text:
                                    run.text = run.text.replace(marcador, c["descricao"])
                    
                    # Substituir checkboxes - abordagem mais específica
                    for cell_idx, cell in enumerate(row.cells):
                        cell_text = cell.text
                        
                        # Se for célula da coluna SIM (normalmente 3ª coluna)
                        if "(XSIM)" in cell_text:
                            for p in cell.paragraphs:
                                for run in p.runs:
                                    if c["status"] == "Sim":
                                        run.text = "SIM" if "(XSIM)" in run.text else run.text
                                    else:
                                        run.text = "" if "(XSIM)" in run.text else run.text
                        
                        # Se for célula da coluna NÃO (normalmente 4ª coluna)  
                        if "(XNAO)" in cell_text:
                            for p in cell.paragraphs:
                                for run in p.runs:
                                    if c["status"] == "Não":
                                        run.text = "NÃO" if "(XNAO)" in run.text else run.text
                                    else:
                                        run.text = "" if "(XNAO)" in run.text else run.text
