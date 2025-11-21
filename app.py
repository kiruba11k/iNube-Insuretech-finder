import streamlit as st
import os
from groq import Groq
import json
from typing import Dict

# Page configuration
st.set_page_config(
    page_title="iNube Solutions Research Agent",
    page_icon="🔍",
    layout="wide"
)

class GroqResearchAgent:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.iNube_capabilities = {
            "policy_administration": "Modular Policy Administration System for Life, Health, General insurance",
            "claims_management": "AI-powered claims processing with fraud detection",
            "digital_distribution": "Digital onboarding and distribution platforms", 
            "ai_analytics": "AI and predictive analytics for insurance operations",
            "field_operations": "Mobility suite for field operations and inspections",
            "embedded_insurance": "API-first platforms for embedded insurance partnerships"
        }
    
    def research_company(self, target_company: str, target_company_url: str) -> Dict:
        system_prompt = """You are an expert insurance technology analyst. Analyze companies for iNube Solutions service fit.

Provide JSON with: company_name, industry, core_business, technology_stack, identified_challenges, digital_maturity, potential_iNube_services, fit_justification, recommendation, confidence_score"""

        user_query = f"Research {target_company} ({target_company_url}) and analyze their need for iNube Solutions insurance technology services."
        
        try:
            chat_completion = self.client.chat.completions.create(
                model="mixtral-8x7b-32768",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_query}
                ],
                temperature=0.3,
                max_tokens=4000,
            )
            
            response_content = chat_completion.choices[0].message.content
            return self._parse_response(response_content, target_company, target_company_url)
            
        except Exception as e:
            st.error(f"Research error: {e}")
            return None
    
    def _parse_response(self, response_content: str, company_name: str, company_url: str) -> Dict:
        try:
            start_idx = response_content.find('{')
            end_idx = response_content.rfind('}') + 1
            if start_idx >= 0 and end_idx > start_idx:
                json_str = response_content[start_idx:end_idx]
                data = json.loads(json_str)
            else:
                data = {"error": "Could not parse response"}
            
            data["sources"] = [company_url]
            data["company_name"] = company_name
            return data
            
        except json.JSONDecodeError:
            return {
                "company_name": company_name,
                "industry": "Unknown",
                "core_business": [],
                "technology_stack": [],
                "identified_challenges": [],
                "digital_maturity": "unknown",
                "potential_iNube_services": [],
                "fit_justification": "Analysis completed but parsing failed",
                "recommendation": "Review manually",
                "confidence_score": 0,
                "sources": [company_url]
            }

def main():
    st.title("iNube Solutions Research Agent")
    st.markdown("Analyze companies for potential iNube Solutions service fit")
    
    # Get API key from environment variable (set in Streamlit Cloud)
    api_key = os.environ.get("GROQ_API_KEY")
    
    if not api_key:
        st.error("GROQ_API_KEY environment variable not set. Please configure it in Streamlit Cloud secrets.")
        return
    
    agent = GroqResearchAgent(api_key)
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Company Information")
        company_name = st.text_input("Company Name", placeholder="e.g., ABC Insurance Company")
        company_url = st.text_input("Company Website URL", placeholder="e.g., https://www.example.com")
        
        analyze_button = st.button("Analyze Company", type="primary")
    
    with col2:
        st.subheader("iNube Solutions Services")
        st.markdown("""
        - Policy Administration Systems
        - Claims Management with AI
        - Digital Distribution Platforms
        - AI and Predictive Analytics
        - Field Operations Solutions
        - Embedded Insurance Platforms
        """)
    
    if analyze_button and company_name and company_url:
        with st.spinner(f"Researching {company_name}..."):
            analysis = agent.research_company(company_name, company_url)
        
        if analysis:
            display_report(analysis, agent)

def display_report(analysis: Dict, agent: GroqResearchAgent):
    st.markdown("---")
    st.header(f"Analysis Report: {analysis.get('company_name', 'Unknown')}")
    
    # Key metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Industry", analysis.get('industry', 'Unknown'))
    with col2:
        st.metric("Digital Maturity", analysis.get('digital_maturity', 'Unknown').title())
    with col3:
        st.metric("Confidence", f"{analysis.get('confidence_score', 0)}%")
    
    # Core sections
    sections = [
        ("Core Business Areas", "core_business"),
        ("Technology Stack", "technology_stack"), 
        ("Identified Challenges", "identified_challenges")
    ]
    
    for title, key in sections:
        st.subheader(title)
        items = analysis.get(key, [])
        if items:
            for item in items:
                st.markdown(f"- {item}")
        else:
            st.info(f"No {title.lower()} identified")
    
    # Recommended services
    st.subheader("Recommended iNube Services")
    services = analysis.get('potential_iNube_services', [])
    if services:
        for service in services:
            if service in agent.iNube_capabilities:
                st.markdown(f"**{service.replace('_', ' ').title()}**: {agent.iNube_capabilities[service]}")
    else:
        st.info("No specific services recommended")
    
    # Final sections
    st.subheader("Analysis Justification")
    st.write(analysis.get('fit_justification', 'No justification provided'))
    
    st.subheader("Recommendation")
    st.info(analysis.get('recommendation', 'No recommendation provided'))
    
    st.subheader("Sources")
    for source in analysis.get('sources', []):
        st.markdown(f"- {source}")

if __name__ == "__main__":
    main()
