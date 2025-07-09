import streamlit as st
import os
from agente_analizador import extraer_texto_de_pdf, generar_informe_completo

# Configuración de la página
st.set_page_config(
    page_title="Technology Transfer Analysis Assistant",
    page_icon="🔬",
    layout="wide"
)

# Logo centrado
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("assets/logo-openlab-verde.png", width=300)

st.markdown("---")

# Título principal
st.title("Technology Transfer Analysis Assistant")
st.markdown("---")

# Descripción de la aplicación
st.markdown("""
**Welcome to the AR+I Technology Transfer Analysis Assistant**

This tool will help you analyze the market potential of your research and identify the next steps 
to increase your project's TRL (Technology Readiness Level).

**How it works:**
1. Upload your scientific paper in PDF format
2. Click "Generate Report" 
3. Wait while we analyze your document and research market trends
4. Receive a comprehensive report with specific recommendations
""")

st.markdown("---")

# Componente de carga de archivos
uploaded_file = st.file_uploader(
    "📄 Drag and drop your scientific paper here (PDF format)",
    type=['pdf'],
    help="Upload a PDF file with your scientific paper or project summary"
)

# Mostrar información del archivo subido
if uploaded_file is not None:
    st.success(f"✅ File uploaded: {uploaded_file.name}")
    st.info(f"📊 Size: {uploaded_file.size / 1024:.1f} KB")

# Botón de acción - solo habilitado si hay archivo
generate_button = st.button(
    "🚀 Generate Report",
    disabled=uploaded_file is None,
    help="Generate a complete technology transfer analysis report" if uploaded_file is not None else "You must upload a PDF file first"
)

# Lógica de ejecución
if generate_button and uploaded_file is not None:
    try:
        # Spinner durante el procesamiento
        with st.spinner("🔍 Analyzing document and researching market trends... This process may take a few minutes."):
            # Extraer texto del PDF
            texto_paper = extraer_texto_de_pdf(uploaded_file)
            
            # Verificar que se extrajo texto
            if not texto_paper or len(texto_paper.strip()) < 100:
                st.error("❌ Error: Could not extract sufficient text from PDF. Please verify that the file contains readable text.")
                st.stop()
            
            # Generar informe completo
            informe = generar_informe_completo(texto_paper)
            
        # Mostrar el informe generado
        st.success("✅ Report generated successfully!")
        st.markdown("---")
        
        # Mostrar el informe con formato enriquecido
        st.markdown(informe)
        
        # Botón para descargar el informe
        st.download_button(
            label="📥 Download Report",
            data=informe,
            file_name=f"technology_transfer_report_{uploaded_file.name.replace('.pdf', '')}.md",
            mime="text/markdown"
        )
        
    except Exception as e:
        st.error(f"❌ Error during analysis: {str(e)}")
        st.error("Please verify that:")
        st.markdown("""
        - The PDF file contains readable text (not just images)
        - API keys are configured correctly
        - Your internet connection is stable
        """)
        
        # Información adicional para debugging
        if st.checkbox("Show technical error information"):
            st.code(str(e))

# Información adicional en la barra lateral
with st.sidebar:
    st.markdown("### ℹ️ Information")
    st.markdown("""
    **Developed for:** AR+I (Andorra Recerca + Innovació)
    
    **Features:**
    - Automatic scientific paper analysis
    - Market trend research
    - Competitive analysis
    - TRL recommendations
    
    **Technical Support:**
    If you experience issues, verify that the PDF contains readable text and that API keys are configured properly.
    """)
    
    st.markdown("---")
    st.markdown("### 📋 Report Structure")
    st.markdown("""
    1. **Project Analysis**
    2. **Market Context**
    3. **Competitive Landscape**
    4. **TRL Roadmap**
    5. **Sources & References**
    """)
