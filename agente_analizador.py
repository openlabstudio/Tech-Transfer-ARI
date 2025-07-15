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
from dotenv import load_dotenv


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
            st.error("Error: API keys not found")
            st.error("Please configure OPENAI_API_KEY and TAVILY_API_KEY in Replit secrets")
            raise ValueError("API keys not found")

        return openai_key, tavily_key
    except Exception as e:
        st.error(f"Error getting API keys: {str(e)}")
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
            raise ValueError("Could not extract text from PDF. The file might contain only images or be corrupted.")

        return texto_completo.strip()

    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")

def crear_herramienta_busqueda(tavily_key):
    """Crea la herramienta de búsqueda web usando Tavily"""

    def buscar_web(query):
        """Realiza búsqueda web usando Tavily"""
        try:
            client = TavilyClient(api_key=tavily_key)
            response = client.search(
                query=query,
                search_depth="advanced",
                max_results=8,
                include_domains=["scholar.google.com", "arxiv.org", "ieee.org", "nature.com", "science.org", "reuters.com", "bloomberg.com", "techcrunch.com", "venturebeat.com", "crunchbase.com"]
            )

            # Formatear resultados con más detalles
            resultados = []
            for result in response.get('results', []):
                resultados.append({
                    'title': result.get('title', ''),
                    'url': result.get('url', ''),
                    'content': result.get('content', ''),
                    'score': result.get('score', 0),
                    'published_date': result.get('published_date', ''),
                    'domain': result.get('url', '').split('/')[2] if result.get('url') else ''
                })

            return json.dumps(resultados, indent=2)

        except Exception as e:
            return f"Search error: {str(e)}"

    return Tool(
        name="busqueda_web",
        description="Search current information on internet about technologies, markets, competitors and trends",
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
        st.write("🔍 Step 1/4: Analyzing paper content...")

        prompt_analisis = f"""
        You are an expert in scientific research analysis. Analyze the following paper and extract:

        1. The main technology or solution
        2. The specific problem it addresses
        3. The methodology used
        4. The innovative and disruptive potential
        5. Relevant technical keywords

        Paper to analyze:
        {texto_paper}

        Provide a structured and concise analysis in English.
        """

        response_analisis = llm.invoke([HumanMessage(content=prompt_analisis)])
        analisis_interno = response_analisis.content

        # PASO 2: Búsqueda de tendencias y tecnologías relacionadas
        st.write("🌐 Step 2/4: Researching market trends...")

        # Crear herramienta de búsqueda
        herramienta_busqueda = crear_herramienta_busqueda(tavily_key)

        # Crear agente para búsqueda de tendencias
        prompt_tendencias = ChatPromptTemplate.from_messages([
            ("system", """You are a technology market analyst.
            Based on the paper analysis, generate 3-4 specific search queries to find:
            1. Current market trends related to the technology (include market size, growth, projections)
            2. Specific market data (revenue, investments, valuations, number of companies)
            3. Emerging technologies in the same field
            4. Current commercial applications and use cases

            Use the web search tool to investigate. In your final response, ALWAYS INCLUDE:
            - Clickable links to sources: [Source Title](URL)
            - Specific numerical data when available
            - Publication dates of information
            - Provide a structured consolidated summary in English."""),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            ("human", "Paper analysis: {analisis}\n\nSearch for relevant market trends with specific data and sources.")
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
        st.write("🏢 Step 3/4: Analyzing competitive landscape...")

        prompt_competitivo = ChatPromptTemplate.from_messages([
            ("system", """You are a competitive intelligence analyst.
            Based on the paper analysis, generate 3-4 search queries to find:
            1. Companies and startups working on similar technologies (include funding data, valuation, employees if available)
            2. Research centers and universities in the same field (include recent publications, funding)
            3. Potential strategic partners or direct competitors
            4. Related patents or intellectual property

            Use the web search tool. In your final response, ALWAYS INCLUDE:
            - Clickable links to sources: [Company/Institution Name](URL)
            - Specific data about funding, size, location when available
            - Relevant information dates
            - Provide a structured analysis in English."""),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
            ("human", "Paper analysis: {analisis}\n\nSearch for detailed information about the competitive landscape with specific data and sources.")
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
        st.write("📊 Step 4/4: Generating TRL recommendations...")

        prompt_final = f"""
        You are an expert technology transfer consultant. Based on all the information collected,
        generate a comprehensive report following EXACTLY this Markdown structure:

        # Technology Transfer Potential Report

        ## 1. Research Project Analysis

        **Main Technology/Solution:**
        * [Summary of the key technology identified in the paper]

        **Problem Addressed:**
        * [Description of the problem the research aims to solve]

        **Intrinsic Innovation Potential:**
        * [Analysis of the novelty and disruptive nature of the proposal]

        ---

        ## 2. Market Context and Current Trends

        **Relevant Market Trends:**
        * [List of identified market trends WITH SPECIFIC DATA such as market size, growth rates, projections]
        * [INCLUDE clickable links to sources: [Title](URL)]

        **Specific Market Data:**
        * [Concrete figures on market size, investments, number of companies, etc.]
        * [INCLUDE clickable links to sources: [Title](URL)]

        **Related and Emerging Technologies:**
        * [List of other complementary or evolving technologies]
        * [INCLUDE clickable links to sources: [Title](URL)]

        ---

        ## 3. Competitive Landscape and Potential Collaborators

        **Key Market Players (Companies/Startups):**
        * [List of potential competitors with specific data: funding, valuation, employees, location]
        * [INCLUDE clickable links: [Company Name](URL)]

        **Research Centers and Potential Academic Partners:**
        * [List of universities/centers with data on recent publications, funding, projects]
        * [INCLUDE clickable links: [Center Name](URL)]

        **Intellectual Property Analysis:**
        * [Information about relevant patents if found]
        * [INCLUDE clickable links to sources: [Title](URL)]

        ---

        ## 4. Suggested Roadmap to Increase TRL

        **Current Maturity Analysis (Estimated TRL):**
        * Based on the description, the current Technology Readiness Level (TRL) is estimated at **TRL [X]**.
        * Justification: [Brief explanation of why you estimate that TRL].

        **Actionable Next Steps:**
        1. **To reach TRL [X+1]:** [Concrete suggestion]
        2. **To reach TRL [X+2]:** [Concrete suggestion]
        3. **Key Questions to Resolve:** [List of questions the researcher should answer to advance]

        ---

        ## 5. Sources and References

        **Consulted Sources:**
        * [Complete list of all sources with clickable links used in the analysis]
        * [Include consultation date when possible]

        IMPORTANT INSTRUCTIONS:
        - ALWAYS include clickable links in format [Text](URL)
        - Prioritize specific numerical data when available
        - Include publication dates of information
        - Verify that all links work correctly
        - Write the entire report in English

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
