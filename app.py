# ========================
# CONTRAPARTIDAS
# ========================
if "contrapartidas" not in st.session_state:
    st.session_state.contrapartidas = []
if "edit_index" not in st.session_state:
    st.session_state.edit_index = None

st.subheader("➕ Adicionar Contrapartida")

# Campos para adicionar nova contrapartida
col1, col2 = st.columns([2, 1])
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
        st.session_state.desc_contrapartida = ""  # limpar campo

# Mostrar contrapartidas já adicionadas
if st.session_state.contrapartidas:
    st.write("📋 Contrapartidas adicionadas:")

    for i, c in enumerate(st.session_state.contrapartidas):
        col1, col2, col3 = st.columns([3, 1, 1])
        with col1:
            st.write(f"{i+1}. {c['descricao']} - {c['status']}")

        with col2:
            if st.button(f"✏️ Editar {i}", key=f"edit_{i}"):
                st.session_state.edit_index = i

        with col3:
            if st.button(f"🗑 Remover {i}", key=f"del_{i}"):
                st.session_state.contrapartidas.pop(i)
                st.experimental_rerun()

    # Se estiver em modo de edição
    if st.session_state.edit_index is not None:
        idx = st.session_state.edit_index
        st.info(f"✏️ Editando contrapartida {idx+1}")
        edit_desc = st.text_input("Nova descrição", value=st.session_state.contrapartidas[idx]["descricao"], key="edit_desc")
        edit_status = st.selectbox("Comprovada?", ["Sim", "Não"], index=0 if st.session_state.contrapartidas[idx]["status"]=="Sim" else 1, key="edit_status")
        
        colA, colB = st.columns(2)
        with colA:
            if st.button("💾 Salvar Alterações"):
                st.session_state.contrapartidas[idx] = {"descricao": edit_desc, "status": edit_status}
                st.session_state.edit_index = None
                st.experimental_rerun()
        with colB:
            if st.button("❌ Cancelar Edição"):
                st.session_state.edit_index = None
                st.experimental_rerun()
