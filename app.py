import streamlit as st
import os
from tavily import TavilyClient
import pandas as pd
import json
from typing import Dict, List, Tuple
import time

# Page configuration
st.set_page_config(
    page_title="iNube Solutions Research Agent",
    page_icon="",
    layout="wide"
)

class TavilyResearchAgent:
    def __init__(self, api_key: str):
        if not api_key:
            st.error("Tavily API key is required")
            return
        self.client = TavilyClient(api_key=api_key)
        self.iNube_services = {
            "policy_administration": "Modular Policy Administration System for Life, Health, General insurance",
            "claims_management": "AI-powered claims processing with fraud detection",
            "digital_distribution": "Digital onboarding and distribution platforms",
            "ai_analytics": "AI and predictive analytics for insurance operations",
            "field_operations": "Mobility suite for field operations and inspections",
            "embedded_insurance": "API-first platforms for embedded insurance partnerships"
        }
    
    def research_company(self, company_name: str, company_url: str) -> Tuple[Dict, List[Dict]]:
        """Research company using Tavily Search API"""
        
        # Perform multiple searches for comprehensive research
        search_queries = [
            f"{company_name} insurance business model services products",
            f"{company_name} technology stack digital transformation IT systems",
            f"{company_name} insurance operations challenges issues",
            f"{company_name} recent news developments 2024 2025",
            f"{company_name} financial performance growth strategy",
            "iNube Solutions insurance technology services"
        ]
        
        all_results = []
        analysis_data = {
            "company_name": company_name,
            "company_url": company_url,
            "sources": [],
            "research_points": []
        }
        
        for query in search_queries:
            try:
                response = self.client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=5,
                    include_answer=True
                )
                
                if response and 'results' in response:
                    for result in response['results']:
                        source_info = {
                            "title": result.get('title', ''),
                            "url": result.get('url', ''),
                            "content": result.get('content', ''),
                            "query": query
                        }
                        all_results.append(source_info)
                        
                        # Extract key points from this source
                        points = self._extract_key_points(result, query)
                        analysis_data["research_points"].extend(points)
                        
                # Add the answer if available
                if response and response.get('answer'):
                    analysis_data["research_points"].append({
                        "point": f"Search analysis: {response['answer']}",
                        "category": "general_analysis",
                        "source_url": f"Query: {query}",
                        "relevance": "high"
                    })
                
                # Add delay to avoid rate limiting
                time.sleep(1)
                        
            except Exception as e:
                st.error(f"Error in search query '{query}': {str(e)}")
                continue
        
        # Extract unique sources
        if all_results:
            analysis_data["sources"] = [{"url": r["url"], "title": r["title"]} for r in all_results]
            analysis_data["sources"] = [dict(t) for t in {tuple(d.items()) for d in analysis_data["sources"]}]
        
        return analysis_data, all_results
    
    def _extract_key_points(self, result: Dict, query: str) -> List[Dict]:
        """Extract key points from search results"""
        points = []
        content = result.get('content', '')
        title = result.get('title', '')
        url = result.get('url', '')
        
        # Define categories and keywords to look for
        categories = {
            "business_model": ["services", "products", "business model", "offering", "solutions", "revenue"],
            "technology": ["technology", "digital", "software", "platform", "AI", "automation", "cloud", "IT"],
            "challenges": ["challenge", "problem", "issue", "limitation", "gap", "difficulty", "bottleneck"],
            "operations": ["operations", "process", "workflow", "efficiency", "cost", "manual", "legacy"],
            "growth": ["growth", "expansion", "market", "customer", "revenue", "premium", "profit"],
            "insurance": ["insurance", "policy", "claim", "underwriting", "premium", "risk", "coverage"]
        }
        
        # Convert content to lowercase for matching
        content_lower = content.lower()
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in content_lower:
                    # Extract context around the keyword
                    start_idx = max(0, content_lower.find(keyword) - 100)
                    end_idx = min(len(content), content_lower.find(keyword) + 200)
                    context = content[start_idx:end_idx].strip()
                    
                    points.append({
                        "point": f"{context}",
                        "category": category,
                        "source_url": url,
                        "source_title": title,
                        "relevance": "medium"
                    })
                    break  # One point per category per source
        
        return points
    
    def analyze_company_fit(self, research_data: Dict) -> Dict:
        """Analyze company fit for iNube Solutions"""
        
        analysis = {
            "company_name": research_data["company_name"],
            "industry": "Unknown",
            "core_business": [],
            "technology_stack": [],
            "identified_challenges": [],
            "digital_maturity": "unknown",
            "potential_iNube_services": [],
            "fit_justification": "",
            "recommendation": "",
            "confidence_score": 0,
            "sources": research_data.get("sources", [])
        }
        
        # Analyze research points to populate the analysis
        tech_keywords = ["legacy", "modernization", "digital", "automation", "AI", "cloud", "technology", "software"]
        challenge_keywords = ["cost", "efficiency", "manual", "slow", "integration", "compliance", "challenge", "problem"]
        insurance_keywords = ["policy", "claim", "underwriting", "premium", "insurance", "risk", "coverage"]
        
        tech_count = 0
        challenge_count = 0
        insurance_count = 0
        
        for point in research_data.get("research_points", []):
            point_text = point["point"].lower()
            
            # Check for insurance industry
            if any(keyword in point_text for keyword in insurance_keywords):
                insurance_count += 1
                analysis["industry"] = "Insurance"
            
            # Check for technology mentions
            if any(keyword in point_text for keyword in tech_keywords):
                tech_count += 1
                if point["point"] not in analysis["technology_stack"]:
                    analysis["technology_stack"].append(point["point"])
            
            # Check for challenges
            if any(keyword in point_text for keyword in challenge_keywords):
                challenge_count += 1
                if point["point"] not in analysis["identified_challenges"]:
                    analysis["identified_challenges"].append(point["point"])
        
        # Determine digital maturity based on technology mentions
        if tech_count > 5:
            analysis["digital_maturity"] = "high"
        elif tech_count > 2:
            analysis["digital_maturity"] = "medium"
        else:
            analysis["digital_maturity"] = "low"
        
        # Determine potential iNube services based on challenges and technology gaps
        if challenge_count > 0 or tech_count < 3:
            # Select relevant services based on identified gaps
            analysis["potential_iNube_services"] = list(self.iNube_services.keys())[:4]
        
        # Calculate confidence score
        total_points = len(research_data.get("research_points", []))
        if total_points > 0:
            analysis["confidence_score"] = min(100, (insurance_count + min(tech_count, 5) + min(challenge_count, 5)) * 10)
        
        # Generate justification and recommendation
        analysis["fit_justification"] = self._generate_justification(analysis, research_data)
        analysis["recommendation"] = self._generate_recommendation(analysis)
        
        return analysis
    
    def _generate_justification(self, analysis: Dict, research_data: Dict) -> str:
        """Generate justification for iNube fit"""
        
        justification_parts = []
        
        if analysis["industry"] == "Insurance":
            justification_parts.append("Company operates in insurance sector, which aligns with iNube's specialization.")
        
        if analysis["digital_maturity"] in ["low", "medium"]:
            justification_parts.append(f"Digital maturity level ({analysis['digital_maturity']}) indicates potential for technology modernization.")
        
        if analysis["identified_challenges"]:
            justification_parts.append(f"Identified {len(analysis['identified_challenges'])} operational challenges that iNube solutions could address.")
        
        if analysis["potential_iNube_services"]:
            services_str = ", ".join([s.replace('_', ' ').title() for s in analysis["potential_iNube_services"]])
            justification_parts.append(f"Recommended iNube services: {services_str}")
        
        return " ".join(justification_parts) if justification_parts else "Limited information available for comprehensive analysis."
    
    def _generate_recommendation(self, analysis: Dict) -> str:
        """Generate recommendation based on analysis"""
        
        confidence = analysis["confidence_score"]
        
        if confidence >= 80:
            return "STRONG RECOMMENDATION - High potential fit with iNube Solutions"
        elif confidence >= 60:
            return "MODERATE RECOMMENDATION - Worth further investigation"
        elif confidence >= 40:
            return "WEAK RECOMMENDATION - Limited evidence of fit"
        else:
            return "INSUFFICIENT DATA - Cannot make reliable recommendation"

def main():
    st.title("iNube Solutions Research Agent")
    st.markdown("Comprehensive company analysis using Tavily Search API")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Get API key from secrets or user input
        api_key = st.secrets.get("TAVILY", None)
        
        if not api_key:
            st.warning("Tavily API key not found in secrets. Please enter it below:")
            api_key = st.text_input("Tavily API Key", type="password", 
                                   help="Get your API key from https://tavily.com")
        else:
            st.success("Tavily API key loaded from secrets")
        
        st.markdown("---")
        st.markdown("**How to use:**")
        st.markdown("1. Ensure Tavily API key is set")
        st.markdown("2. Input company details")
        st.markdown("3. Click Research Company")
        st.markdown("4. Review detailed analysis with sources")
        
        st.markdown("---")
        st.markdown("**iNube Solutions Services:**")
        iNube_services = {
            "policy_administration": "Modular Policy Administration System",
            "claims_management": "AI-powered claims processing with fraud detection",
            "digital_distribution": "Digital onboarding and distribution platforms",
            "ai_analytics": "AI and predictive analytics for insurance operations",
            "field_operations": "Mobility suite for field operations",
            "embedded_insurance": "API-first platforms for embedded insurance"
        }
        for service, desc in iNube_services.items():
            st.markdown(f"- **{service.replace('_', ' ').title()}**: {desc}")
    
    # Main input section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Company Information")
        company_name = st.text_input("Company Name", 
                                   value="SHRIRAM GENERAL INSURANCE CO. LTD.",
                                   placeholder="Enter company name")
        company_url = st.text_input("Company Website URL", 
                                  value="https://www.shriramgi.com",
                                  placeholder="Enter company website URL")
        
        research_button = st.button("Research Company", type="primary", disabled=not api_key)
    
    with col2:
        st.subheader("Research Scope")
        st.markdown("""
        The research agent will analyze:
        - Business model and services
        - Technology stack and digital maturity
        - Operational challenges
        - Insurance industry focus
        - Potential iNube Solutions fit
        """)
        
        st.info("Note: Research may take 2-3 minutes to complete as it performs multiple searches for comprehensive analysis.")
    
    if not api_key:
        st.error("Please provide a Tavily API key to begin research")
        return
    
    # Initialize research agent
    try:
        agent = TavilyResearchAgent(api_key)
    except Exception as e:
        st.error(f"Failed to initialize Tavily client: {str(e)}")
        return
    
    if research_button and company_name:
        with st.spinner(f"Researching {company_name} using Tavily Search API... This may take 2-3 minutes."):
            research_data, detailed_results = agent.research_company(company_name, company_url)
            analysis = agent.analyze_company_fit(research_data)
        
        if analysis and research_data.get("research_points"):
            display_comprehensive_analysis(analysis, detailed_results, agent)
        else:
            st.error("Research failed or no data found. Please check the company name and try again.")

def display_comprehensive_analysis(analysis: Dict, detailed_results: List[Dict], agent: TavilyResearchAgent):
    """Display comprehensive analysis with sources"""
    
    st.markdown("---")
    st.header(f"Analysis Report: {analysis['company_name']}")
    
    # Key metrics
    st.subheader("Executive Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Industry", analysis.get('industry', 'Unknown'))
    with col2:
        st.metric("Digital Maturity", analysis.get('digital_maturity', 'Unknown').title())
    with col3:
        st.metric("Confidence Score", f"{analysis.get('confidence_score', 0)}%")
    with col4:
        services_count = len(analysis.get('potential_iNube_services', []))
        st.metric("Recommended Services", services_count)
    
    # Research Findings Table
    if detailed_results:
        st.subheader("Detailed Research Findings")
        
        # Create research findings table
        research_table_data = []
        for result in detailed_results:
            research_table_data.append({
                "Source Title": result.get('title', 'N/A'),
                "URL": result.get('url', 'N/A'),
                "Key Content": result.get('content', '')[:200] + "..." if len(result.get('content', '')) > 200 else result.get('content', 'N/A'),
                "Search Query": result.get('query', 'N/A')
            })
        
        research_df = pd.DataFrame(research_table_data)
        st.dataframe(research_df, use_container_width=True)
    
    # Analysis Results Table
    st.subheader("iNube Solutions Fit Analysis")
    
    analysis_table_data = []
    
    # Company Information
    analysis_table_data.append({
        "Category": "Company Information",
        "Aspect": "Company Name",
        "Finding": analysis['company_name'],
        "Source URL": analysis.get('company_url', 'N/A'),
        "Relevance": "High"
    })
    
    analysis_table_data.append({
        "Category": "Company Information",
        "Aspect": "Industry",
        "Finding": analysis.get('industry', 'Unknown'),
        "Source URL": "Multiple sources",
        "Relevance": "High"
    })
    
    analysis_table_data.append({
        "Category": "Company Information", 
        "Aspect": "Digital Maturity",
        "Finding": analysis.get('digital_maturity', 'unknown').title(),
        "Source URL": "Technology analysis",
        "Relevance": "High"
    })
    
    analysis_table_data.append({
        "Category": "Company Information", 
        "Aspect": "Confidence Score",
        "Finding": f"{analysis.get('confidence_score', 0)}%",
        "Source URL": "Analysis metrics",
        "Relevance": "High"
    })
    
    # Core Business (from research points)
    business_points = [p for p in analysis.get('research_points', []) if p.get('category') == 'business_model']
    for i, point in enumerate(business_points[:5]):
        analysis_table_data.append({
            "Category": "Core Business",
            "Aspect": f"Business Area {i+1}",
            "Finding": point['point'][:200] + "..." if len(point['point']) > 200 else point['point'],
            "Source URL": point['source_url'],
            "Relevance": point['relevance'].title()
        })
    
    # Technology Stack
    tech_points = [p for p in analysis.get('research_points', []) if p.get('category') == 'technology']
    for i, point in enumerate(tech_points[:5]):
        analysis_table_data.append({
            "Category": "Technology Stack",
            "Aspect": f"Technology {i+1}",
            "Finding": point['point'][:200] + "..." if len(point['point']) > 200 else point['point'],
            "Source URL": point['source_url'],
            "Relevance": point['relevance'].title()
        })
    
    # Identified Challenges
    challenge_points = [p for p in analysis.get('research_points', []) if p.get('category') == 'challenges']
    for i, point in enumerate(challenge_points[:5]):
        analysis_table_data.append({
            "Category": "Identified Challenges",
            "Aspect": f"Challenge {i+1}",
            "Finding": point['point'][:200] + "..." if len(point['point']) > 200 else point['point'],
            "Source URL": point['source_url'],
            "Relevance": point['relevance'].title()
        })
    
    # Recommended iNube Services
    for service in analysis.get('potential_iNube_services', []):
        analysis_table_data.append({
            "Category": "Recommended Services",
            "Aspect": service.replace('_', ' ').title(),
            "Finding": agent.iNube_services.get(service, ''),
            "Source URL": "iNube Solutions analysis",
            "Relevance": "High"
        })
    
    # Display analysis table
    analysis_df = pd.DataFrame(analysis_table_data)
    st.dataframe(analysis_df, use_container_width=True)
    
    # Justification and Recommendation
    st.subheader("Analysis Justification & Recommendation")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Justification:**")
        st.info(analysis.get('fit_justification', 'No justification available'))
    
    with col2:
        st.markdown("**Final Recommendation:**")
        recommendation = analysis.get('recommendation', 'No recommendation available')
        if "STRONG" in recommendation:
            st.success(recommendation)
        elif "MODERATE" in recommendation:
            st.warning(recommendation)
        else:
            st.error(recommendation)
    
    # Source URLs
    st.subheader("Research Sources")
    sources = analysis.get('sources', [])
    if sources:
        for i, source in enumerate(sources):
            st.markdown(f"{i+1}. **{source.get('title', 'No title')}** - {source.get('url', 'No URL')}")
    else:
        st.info("No sources available")
    
    # Export functionality
    st.subheader("Export Results")
    
    # Create TSV data
    export_df = pd.DataFrame(analysis_table_data)
    tsv_data = export_df.to_csv(sep='\t', index=False)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="Download Analysis TSV",
            data=tsv_data,
            file_name=f"inube_analysis_{analysis['company_name'].lower().replace(' ', '_')}.tsv",
            mime="text/tab-separated-values"
        )
    
    with col2:
        # JSON export
        json_data = json.dumps(analysis, indent=2)
        st.download_button(
            label="Download Full JSON Data",
            data=json_data,
            file_name=f"inube_analysis_full_{analysis['company_name'].lower().replace(' ', '_')}.json",
            mime="application/json"
        )

if __name__ == "__main__":
    main()
