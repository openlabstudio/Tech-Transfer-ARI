import streamlit as st
import os
from agente_analizador import extraer_texto_de_pdf, generar_informe_completo

# Configuración de la página
st.set_page_config(
    page_title="Asistente de Análisis para Transferencia Tecnológica",
    page_icon="🔬",
    layout="wide"
)

# Título principal
st.title("🔬 Asistente de Análisis para Transferencia Tecnológica")
st.markdown("---")

# Descripción de la aplicación
st.markdown("""
**Bienvenido al Asistente de Análisis para Transferencia Tecnológica de AR+I**

Esta herramienta te ayudará a analizar el potencial de mercado de tu investigación y los siguientes pasos 
para aumentar el TRL (Technology Readiness Level) de tu proyecto.

**¿Cómo funciona?**
1. Sube tu paper científico en formato PDF
2. Haz clic en "Generar Informe" 
3. Espera mientras analizamos tu documento y consultamos tendencias de mercado
4. Recibe un informe completo con recomendaciones específicas
""")

st.markdown("---")

# Componente de carga de archivos
uploaded_file = st.file_uploader(
    "📄 Arrastra y suelta tu paper científico aquí (formato PDF)",
    type=['pdf'],
    help="Sube un archivo PDF con tu paper científico o resumen de proyecto"
)

# Mostrar información del archivo subido
if uploaded_file is not None:
    st.success(f"✅ Archivo cargado: {uploaded_file.name}")
    st.info(f"📊 Tamaño: {uploaded_file.size / 1024:.1f} KB")

# Botón de acción - solo habilitado si hay archivo
generate_button = st.button(
    "🚀 Generar Informe",
    disabled=uploaded_file is None,
    help="Genera un informe completo de análisis de transferencia tecnológica" if uploaded_file is not None else "Primero debes subir un archivo PDF"
)

# Lógica de ejecución
if generate_button and uploaded_file is not None:
    try:
        # Spinner durante el procesamiento
        with st.spinner("🔍 Analizando documento y consultando el mercado... Este proceso puede tardar unos minutos."):
            # Extraer texto del PDF
            texto_paper = extraer_texto_de_pdf(uploaded_file)
            
            # Verificar que se extrajo texto
            if not texto_paper or len(texto_paper.strip()) < 100:
                st.error("❌ Error: No se pudo extraer suficiente texto del PDF. Por favor, verifica que el archivo contiene texto legible.")
                st.stop()
            
            # Generar informe completo
            informe = generar_informe_completo(texto_paper)
            
        # Mostrar el informe generado
        st.success("✅ ¡Informe generado exitosamente!")
        st.markdown("---")
        
        # Mostrar el informe con formato enriquecido
        st.markdown(informe)
        
        # Botón para descargar el informe
        st.download_button(
            label="📥 Descargar Informe",
            data=informe,
            file_name=f"informe_transferencia_{uploaded_file.name.replace('.pdf', '')}.md",
            mime="text/markdown"
        )
        
    except Exception as e:
        st.error(f"❌ Error durante el análisis: {str(e)}")
        st.error("Por favor, verifica que:")
        st.markdown("""
        - El archivo PDF contiene texto legible (no solo imágenes)
        - Las claves de API están configuradas correctamente
        - Tu conexión a internet es estable
        """)
        
        # Información adicional para debugging
        if st.checkbox("Mostrar información técnica del error"):
            st.code(str(e))

# Información adicional en la barra lateral
with st.sidebar:
    st.markdown("### ℹ️ Información")
    st.markdown("""
    **Desarrollado para:** AR+I (Andorra Recerca + Innovació)
    
    **Funcionalidades:**
    - Análisis automático de papers científicos
    - Búsqueda de tendencias de mercado
    - Análisis competitivo
    - Recomendaciones de TRL
    
    **Soporte técnico:**
    Si experimentas problemas, verifica que el PDF contiene texto legible y que las claves de API están configuradas.
    """)
    
    st.markdown("---")
    st.markdown("### 📋 Estructura del Informe")
    st.markdown("""
    1. **Análisis del Proyecto**
    2. **Contexto de Mercado**
    3. **Panorama Competitivo**
    4. **Hoja de Ruta TRL**
    """)
