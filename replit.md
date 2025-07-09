# Asistente de Análisis para Transferencia Tecnológica

## Overview

This is a Streamlit-based AI assistant designed for AR+I (Andorra Recerca + Innovació) researchers to analyze the market potential of their scientific research and receive recommendations for increasing their Technology Readiness Level (TRL). The application allows researchers to upload scientific papers in PDF format and generates comprehensive reports about market opportunities, competitive landscape, and next steps for technology transfer.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

The application follows a clean separation of concerns with a frontend-backend architecture:

- **Frontend**: Streamlit web interface (`app.py`)
- **Backend Logic**: Python module with AI agent functionality (`agente_analizador.py`)
- **AI Processing**: LangChain-based agentic workflow with OpenAI GPT-4o
- **Web Search**: Tavily API for market research and competitive analysis
- **Document Processing**: PyPDF2 for PDF text extraction
- **Deployment**: Streamlit Community Cloud

## Key Components

### 1. User Interface (`app.py`)
- File upload component for PDF documents
- Action button for report generation
- Loading spinner during processing
- Results display with formatted markdown output
- Error handling for file processing issues

### 2. AI Agent Module (`agente_analizador.py`)
- PDF text extraction functionality
- Multi-step agentic workflow implementation
- Integration with OpenAI and Tavily APIs
- Report generation logic

### 3. Agentic Workflow (Planned)
The system implements a 4-step sequential process:
1. **Internal Paper Analysis**: LLM analysis of uploaded document
2. **Market Trends Research**: Tavily-powered web search for related technologies
3. **Competitive Landscape Analysis**: Research on similar companies and organizations
4. **Report Generation**: Comprehensive output with actionable recommendations

## Data Flow

1. **Input**: User uploads PDF research paper
2. **Processing**: 
   - Extract text from PDF using PyPDF2
   - Analyze content with GPT-4o
   - Perform web searches using Tavily
   - Generate structured insights
3. **Output**: Formatted report with market analysis and recommendations

## External Dependencies

### APIs
- **OpenAI API**: GPT-4o for text analysis and reasoning
- **Tavily API**: Web search capabilities for market research

### Python Libraries
- `streamlit`: Web interface framework
- `langchain`: AI agent orchestration
- `langchain-openai`: OpenAI integration
- `tavily-python`: Web search integration
- `pypdf2`: PDF text extraction
- `python-dotenv`: Environment variable management

### Security
- API keys managed through Streamlit secrets (`st.secrets`)
- No hardcoded credentials in source code

## Deployment Strategy

- **Platform**: Streamlit Community Cloud
- **Configuration**: Uses Streamlit's built-in secrets management
- **Dependencies**: All requirements specified in `requirements.txt`
- **Scalability**: Single-user processing model suitable for research team usage

### Environment Setup
Required secret keys:
- `OPENAI_API_KEY`: OpenAI API access
- `TAVILY_API_KEY`: Tavily search API access

## Technical Considerations

### Current State
- Complete PDF upload and text extraction implemented
- Streamlit UI foundation established
- API key management configured for both Replit Secrets and Streamlit Secrets
- Complete agentic workflow implementation with 4-step process
- Enhanced reporting with clickable links and market data integration
- Improved web search capabilities with more data sources

### Architecture Decisions
- **Streamlit Choice**: Rapid prototyping and deployment, ideal for research users
- **LangChain Integration**: Provides robust agent framework for complex workflows
- **Tavily for Search**: Specialized web search API for research applications
- **Sequential Processing**: Linear workflow suitable for report generation task

### Recent Enhancements (January 2025)
- Complete 4-step agentic workflow implemented
- Enhanced web search with expanded data sources (financial, tech news, academic)
- Clickable links and source attribution in reports
- Market data integration with specific metrics
- Improved error handling and API key management for both Replit and Streamlit environments
- Added comprehensive source references section to reports

### Future Enhancements
- Caching for improved performance
- Multi-language support for international markets
- Advanced patent search integration
- Report export in multiple formats (PDF, Word)
- Collaborative features for team analysis