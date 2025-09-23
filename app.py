# ========================
# CONTRAPARTIDAS NA TABELA
# ========================
if st.session_state.contrapartidas:
    # Preencher marcadores existentes
    for table in doc.tables:
        for row_idx, row in enumerate(table.rows):
            for cell in row.cells:
                for p in cell.paragraphs:
                    for idx, c in enumerate(st.session_state.contrapartidas, start=1):
                        marcador = f"(contrapartida{idx:02d})"
                        if marcador in p.text:
                            for run in p.runs:
                                run.text = run.text.replace(marcador, c["descricao"])
                            
                            # SIM / NÃO - CORREÇÃO: Processar toda a linha
                            for cell_idx, rcell in enumerate(row.cells):
                                for rp in rcell.paragraphs:
                                    if "(XSIM)" in rp.text or "(XNAO)" in rp.text:
                                        for run in rp.runs:
                                            if c["status"] == "Sim":
                                                run.text = run.text.replace("(XSIM)", "SIM").replace("(XNAO)", "")
                                            else:
                                                run.text = run.text.replace("(XNAO)", "NÃO").replace("(XSIM)", "")

    # Se houver extras, duplicar última linha
    max_default = 3
    if len(st.session_state.contrapartidas) > max_default:
        for table in doc.tables:
            if any("(contrapartida01)" in c.text for r in table.rows for c in r.cells):
                template_row = table.rows[max_default]._tr
                for extra_idx, c in enumerate(st.session_state.contrapartidas[max_default:], start=max_default+1):
                    new_tr = copy.deepcopy(template_row)
                    table._tbl.append(new_tr)
                    new_row = table.rows[-1]
                    for cell in new_row.cells:
                        for p in cell.paragraphs:
                            if "(contrapartida03)" in p.text:
                                p.text = p.text.replace("(contrapartida03)", c["descricao"])
                            if "(XSIM)" in p.text or "(XNAO)" in p.text:
                                for run in p.runs:
                                    if c["status"] == "Sim":
                                        run.text = run.text.replace("(XSIM)", "SIM").replace("(XNAO)", "")
                                    else:
                                        run.text = run.text.replace("(XNAO)", "NÃO").replace("(XSIM)", "")
                break
