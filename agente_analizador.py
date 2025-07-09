import os
import streamlit as st
from PyPDF2 import PdfReader
from langchain.agents import create_openai_functions_agent, AgentExecutor
from langchain.tools import Tool
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage, AIMessage
from tavily import TavilyClient
import json

# Configuración de APIs usando variables de entorno
def get_api_keys():
    """Obtiene las claves API desde las variables de entorno"""
    try:
        # Intentar primero desde variables de entorno (Replit Secrets)
        openai_key = os.getenv("OPENAI_API_KEY")
        tavily_key = os.getenv("TAVILY_API_KEY")
        
        # Si no están en variables de entorno, intentar desde Streamlit secrets
        if not openai_key or not tavily_key:
            try:
                openai_key = openai_key or st.secrets["OPENAI_API_KEY"]
                tavily_key = tavily_key or st.secrets["TAVILY_API_KEY"]
            except:
                pass
        
        if not openai_key or not tavily_key:
            st.error("Error: Claves API no encontradas")
            st.error("Por favor, configura las claves OPENAI_API_KEY y TAVILY_API_KEY en los secrets de Replit")
            raise ValueError("Claves API no encontradas")
            
        return openai_key, tavily_key
    except Exception as e:
        st.error(f"Error al obtener las claves API: {str(e)}")
        raise

def extraer_texto_de_pdf(fichero_subido):
    """
    Extrae el texto completo de un archivo PDF subido
    
    Args:
        fichero_subido: Objeto de archivo de Streamlit
        
    Returns:
        str: Texto extraído del PDF
    """
    try:
        # Crear lector PDF
        pdf_reader = PdfReader(fichero_subido)
        
        # Extraer texto de todas las páginas
        texto_completo = ""
        for pagina in pdf_reader.pages:
            texto_completo += pagina.extract_text() + "\n"
        
        # Verificar que se extrajo texto
        if not texto_completo.strip():
            raise ValueError("No se pudo extraer texto del PDF. El archivo podría contener solo imágenes o estar corrupto.")
            
        return texto_completo.strip()
        
    except Exception as e:
        raise Exception(f"Error al extraer texto del PDF: {str(e)}")

def crear_herramienta_busqueda(tavily_key):
    """Crea la herramienta de búsqueda web usando Tavily"""
    
    def buscar_web(query):
        """Realiza búsqueda web usando Tavily"""
        try:
            client = TavilyClient(api_key=tavily_key)
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=5,
                include_domains=["scholar.google.com", "arxiv.org", "ieee.org", "nature.com", "science.org"]
            )
            
            # Formatear resultados
            resultados = []
            for result in response.get('results', []):
                resultados.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'content': result.get('content', '')[:500] + '...' if len(result.get('content', '')) > 500 else result.get('content', '')
                })
            
            return json.dumps(resultados, indent=2)
            
        except Exception as e:
            return f"Error en la búsqueda: {str(e)}"
    
    return Tool(
        name="busqueda_web",
        description="Busca información actual en internet sobre tecnologías, mercados, competidores y tendencias",
        func=buscar_web
    )

def generar_informe_completo(texto_paper):
    """
    Genera el informe completo de análisis de transferencia tecnológica
    
    Args:
        texto_paper (str): Texto extraído del paper científico
        
    Returns:
        str: Informe completo en formato Markdown
    """
    try:
        # Obtener claves API
        openai_key, tavily_key = get_api_keys()
        
        # Inicializar LLM
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        llm = ChatOpenAI(
            model="gpt-4o",
            api_key=openai_key,
            temperature=0.3
        )
        
        # PASO 1: Análisis interno del paper
        st.write("🔍 Paso 1/4: Analizando el contenido del paper...")
        
        prompt_analisis = f"""
        Eres un experto en análisis de investigación científica. Analiza el siguiente paper y extrae:
        
        1. La tecnología o solución principal
        2. El problema específico que aborda
        3. La metodología utilizada
        4. El potencial innovador y disruptivo
        5. Palabras clave técnicas relevantes
        
        Paper a analizar:
        {texto_paper}
        
        Proporciona un análisis estructurado y conciso.
        """
        
        response_analisis = llm.invoke([HumanMessage(content=prompt_analisis)])
        analisis_interno = response_analisis.content
        
        # PASO 2: Búsqueda de tendencias y tecnologías relacionadas
        st.write("🌐 Paso 2/4: Investigando tendencias de mercado...")
        
        # Crear herramienta de búsqueda
        herramienta_busqueda = crear_herramienta_busqueda(tavily_key)
        
        # Crear agente para búsqueda de tendencias
        prompt_tendencias = ChatPromptTemplate.from_messages([
            ("system", """Eres un analista de mercado especializado en tecnología. 
            Basándote en el análisis del paper, genera 2-3 consultas de búsqueda específicas para encontrar:
            1. Tendencias actuales del mercado relacionadas con la tecnología
            2. Tecnologías emergentes en el mismo campo
            3. Aplicaciones comerciales actuales
            
            Usa la herramienta de búsqueda web para investigar y proporciona un resumen consolidado."""),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            ("human", "Análisis del paper: {analisis}\n\nRealiza búsquedas para encontrar tendencias de mercado relevantes.")
        ])
        
        agente_tendencias = create_openai_functions_agent(
            llm=llm,
            tools=[herramienta_busqueda],
            prompt=prompt_tendencias
        )
        
        executor_tendencias = AgentExecutor(
            agent=agente_tendencias,
            tools=[herramienta_busqueda],
            verbose=False
        )
        
        resultado_tendencias = executor_tendencias.invoke({
            "analisis": analisis_interno
        })
        
        # PASO 3: Búsqueda de panorama competitivo
        st.write("🏢 Paso 3/4: Analizando el panorama competitivo...")
        
        prompt_competitivo = ChatPromptTemplate.from_messages([
            ("system", """Eres un analista de inteligencia competitiva. 
            Basándote en el análisis del paper, genera 2-3 consultas de búsqueda para encontrar:
            1. Empresas y startups que trabajen en tecnologías similares
            2. Centros de investigación y universidades en el mismo campo
            3. Posibles socios estratégicos o competidores directos
            
            Usa la herramienta de búsqueda web y proporciona un análisis estructurado."""),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            ("human", "Análisis del paper: {analisis}\n\nBusca información sobre el panorama competitivo.")
        ])
        
        agente_competitivo = create_openai_functions_agent(
            llm=llm,
            tools=[herramienta_busqueda],
            prompt=prompt_competitivo
        )
        
        executor_competitivo = AgentExecutor(
            agent=agente_competitivo,
            tools=[herramienta_busqueda],
            verbose=False
        )
        
        resultado_competitivo = executor_competitivo.invoke({
            "analisis": analisis_interno
        })
        
        # PASO 4: Síntesis y recomendaciones de TRL
        st.write("📊 Paso 4/4: Generando recomendaciones de TRL...")
        
        prompt_final = f"""
        Eres un consultor experto en transferencia tecnológica. Basándote en toda la información recopilada, 
        genera un informe completo siguiendo EXACTAMENTE esta estructura Markdown:

        # Informe de Potencial de Transferencia Tecnológica

        ## 1. Análisis del Proyecto de Investigación

        **Tecnología/Solución Principal:**
        * [Resumen de la tecnología clave identificada en el paper]

        **Problema Abordado:**
        * [Descripción del problema que la investigación busca resolver]

        **Potencial Innovador Intrínseco:**
        * [Análisis sobre la novedad y el carácter disruptivo de la propuesta]

        ---

        ## 2. Contexto de Mercado y Tendencias Actuales

        **Tendencias de Mercado Relevantes:**
        * [Lista de tendencias de mercado identificadas]

        **Tecnologías Relacionadas y Emergentes:**
        * [Lista de otras tecnologías complementarias o en evolución]

        ---

        ## 3. Panorama Competitivo y Posibles Colaboradores

        **Actores Clave en el Mercado (Empresas/Startups):**
        * [Lista de posibles competidores con una breve descripción]

        **Centros de Investigación y Posibles Socios Académicos:**
        * [Lista de otras universidades o centros que investigan en la misma línea]

        ---

        ## 4. Hoja de Ruta Sugerida para Aumentar el TRL

        **Análisis de Madurez Actual (TRL Estimado):**
        * Basado en la descripción, el nivel de madurez tecnológica (TRL) actual se estima en **TRL [X]**.
        * Justificación: [Breve explicación sobre por qué estimas ese TRL].

        **Siguientes Pasos Accionables:**
        1. **Para alcanzar TRL [X+1]:** [Sugerencia concreta]
        2. **Para alcanzar TRL [X+2]:** [Sugerencia concreta]
        3. **Preguntas Clave a Resolver:** [Lista de preguntas que el investigador debería responder para avanzar]

        INFORMACIÓN PARA EL ANÁLISIS:

        Paper Original:
        {texto_paper}

        Análisis Interno:
        {analisis_interno}

        Tendencias de Mercado:
        {resultado_tendencias['output']}

        Panorama Competitivo:
        {resultado_competitivo['output']}

        Genera el informe completo siguiendo exactamente la estructura indicada.
        """
        
        response_final = llm.invoke([HumanMessage(content=prompt_final)])
        informe_final = response_final.content
        
        return informe_final
        
    except Exception as e:
        raise Exception(f"Error al generar el informe: {str(e)}")
