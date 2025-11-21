import streamlit as st
import os
from groq import Groq
import json
import pandas as pd
from typing import Dict, List

# Page configuration
st.set_page_config(
    page_title="iNube Solutions Research Agent",
    page_icon="",
    layout="wide"
)

class GroqResearchAgent:
    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
    
    def research_company(self, target_company: str, target_company_url: str) -> Dict:
        system_prompt = """You are an expert insurance technology analyst. Analyze companies for iNube Solutions service fit.

Provide JSON with: company_name, industry, core_business, technology_stack, identified_challenges, digital_maturity, potential_iNube_services, fit_justification, recommendation, confidence_score"""

        user_query = f"Research {target_company} ({target_company_url}) and analyze their need for iNube Solutions insurance technology services."
        
        try:
            chat_completion = self.client.chat.completions.create(
                model="openai/gpt-oss-120b",
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

def create_comprehensive_dataframe(analysis: Dict) -> pd.DataFrame:
    """Create comprehensive DataFrame with all analysis data"""
    
    rows = []
    sources_str = "; ".join(analysis.get('sources', []))
    
    # Company Overview
    rows.extend([
        {"Section": "COMPANY OVERVIEW", "Field": "Company Name", "Value": analysis.get('company_name', 'N/A'), "Sources": sources_str},
        {"Section": "COMPANY OVERVIEW", "Field": "Industry", "Value": analysis.get('industry', 'N/A'), "Sources": sources_str},
        {"Section": "COMPANY OVERVIEW", "Field": "Digital Maturity", "Value": analysis.get('digital_maturity', 'N/A'), "Sources": sources_str},
        {"Section": "COMPANY OVERVIEW", "Field": "Confidence Score", "Value": f"{analysis.get('confidence_score', 0)}%", "Sources": sources_str}
    ])
    
    # Core Business
    core_business = analysis.get('core_business', [])
    for i, business in enumerate(core_business):
        rows.append({
            "Section": "CORE BUSINESS", 
            "Field": f"Business Area {i+1}", 
            "Value": business, 
            "Sources": sources_str
        })
    
    # Technology Stack
    tech_stack = analysis.get('technology_stack', [])
    for i, tech in enumerate(tech_stack):
        rows.append({
            "Section": "TECHNOLOGY STACK", 
            "Field": f"Technology {i+1}", 
            "Value": tech, 
            "Sources": sources_str
        })
    
    # Challenges
    challenges = analysis.get('identified_challenges', [])
    for i, challenge in enumerate(challenges):
        rows.append({
            "Section": "IDENTIFIED CHALLENGES", 
            "Field": f"Challenge {i+1}", 
            "Value": challenge, 
            "Sources": sources_str
        })
    
    # Recommended Services
    services = analysis.get('potential_iNube_services', [])
    for i, service in enumerate(services):
        rows.append({
            "Section": "RECOMMENDED SERVICES", 
            "Field": f"Service {i+1}", 
            "Value": service.replace('_', ' ').title(), 
            "Sources": sources_str
        })
    
    # Analysis Results
    rows.extend([
        {"Section": "ANALYSIS RESULTS", "Field": "Recommendation", "Value": analysis.get('recommendation', 'N/A'), "Sources": sources_str},
        {"Section": "ANALYSIS RESULTS", "Field": "Justification", "Value": analysis.get('fit_justification', 'N/A'), "Sources": sources_str}
    ])
    
    return pd.DataFrame(rows)

def main():
    st.title("iNube Solutions Research Agent")
    st.markdown("Analyze companies for potential iNube Solutions service fit")
    
    # Get API key
    api_key = st.secrets.get("GROQ_API_KEY")
    
    if not api_key:
        st.info("Please enter your Groq API key to begin analysis")
        return
    
    agent = GroqResearchAgent(api_key)
    
    # Input section
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
            display_results(analysis)

def display_results(analysis: Dict):
    """Display analysis results in table format with TSV export"""
    
    st.markdown("---")
    st.header(f"Analysis Report: {analysis.get('company_name', 'Unknown Company')}")
    
    # Create comprehensive DataFrame
    df = create_comprehensive_dataframe(analysis)
    
    # Display table
    st.subheader("Detailed Analysis Table")
    
    # Use different background colors for sections
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Section": st.column_config.TextColumn("Section", width="medium"),
            "Field": st.column_config.TextColumn("Field", width="medium"),
            "Value": st.column_config.TextColumn("Value", width="large"),
            "Sources": st.column_config.TextColumn("Source URLs", width="large")
        }
    )
    
    # Quick stats
    st.subheader("Quick Statistics")
    cols = st.columns(4)
    
    with cols[0]:
        st.metric("Industry", analysis.get('industry', 'Unknown'))
    with cols[1]:
        st.metric("Digital Maturity", analysis.get('digital_maturity', 'Unknown').title())
    with cols[2]:
        st.metric("Confidence", f"{analysis.get('confidence_score', 0)}%")
    with cols[3]:
        st.metric("Services Recommended", len(analysis.get('potential_iNube_services', [])))
    
    # Export section
    st.subheader("Export Analysis Results")
    
    # TSV Export
    tsv_data = df.to_csv(sep='\t', index=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="Download TSV File",
            data=tsv_data,
            file_name=f"inube_analysis_{analysis.get('company_name', 'company').lower().replace(' ', '_')}.tsv",
            mime="text/tab-separated-values",
            help="Tab-separated values file for Excel and other applications"
        )
    
    with col2:
        # CSV option for better Excel compatibility
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Download CSV File",
            data=csv_data,
            file_name=f"inube_analysis_{analysis.get('company_name', 'company').lower().replace(' ', '_')}.csv",
            mime="text/csv",
            help="Comma-separated values file for Excel"
        )
    
    # Display source URLs separately
    st.subheader("Research Sources")
    sources = analysis.get('sources', [])
    for source in sources:
        st.markdown(f"- {source}")

if __name__ == "__main__":
    main()
