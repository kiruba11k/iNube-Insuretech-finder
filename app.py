import streamlit as st
import os
from tavily import TavilyClient
import pandas as pd
import json
from typing import Dict, List, Tuple
import time
from datetime import datetime

# Page configuration
st.set_page_config(
    page_title="iNube Solutions - Client Potential Analysis",
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
        
        self.pain_points_mapping = {
            "legacy_systems": {
                "keywords": ["legacy system", "outdated technology", "old software", "system modernization", 
                           "technology upgrade", "digital transformation", "modernization challenge"],
                "iNube_solutions": ["policy_administration", "digital_distribution", "claims_management"],
                "solution_description": "Replace outdated systems with modern, scalable policy administration platforms"
            },
            "manual_processes": {
                "keywords": ["manual process", "paper-based", "manual data entry", "manual workflow",
                           "manual intervention", "manual handling", "manual verification"],
                "iNube_solutions": ["claims_management", "field_operations", "ai_analytics"],
                "solution_description": "Automate manual workflows with AI-powered claims processing and field operations"
            },
            "customer_experience": {
                "keywords": ["customer satisfaction", "customer churn", "customer retention", 
                           "digital onboarding", "customer experience", "policyholder experience"],
                "iNube_solutions": ["digital_distribution", "embedded_insurance", "policy_administration"],
                "solution_description": "Enhance customer journey with digital distribution and embedded insurance platforms"
            },
            "fraud_detection": {
                "keywords": ["insurance fraud", "fraud detection", "false claims", "claims fraud",
                           "fraud prevention", "fraudulent activities"],
                "iNube_solutions": ["claims_management", "ai_analytics"],
                "solution_description": "Implement AI-powered fraud detection and predictive analytics"
            },
            "operational_efficiency": {
                "keywords": ["operational efficiency", "process efficiency", "cost reduction", 
                           "streamline operations", "efficiency improvement", "operational cost"],
                "iNube_solutions": ["policy_administration", "claims_management", "field_operations"],
                "solution_description": "Streamline operations with integrated policy, claims, and field management"
            },
            "data_analytics": {
                "keywords": ["data analytics", "business intelligence", "predictive analytics",
                           "data-driven decisions", "analytics capability", "data insights"],
                "iNube_solutions": ["ai_analytics", "claims_management"],
                "solution_description": "Leverage AI analytics for data-driven insights and decision making"
            },
            "digital_transformation": {
                "keywords": ["digital transformation", "digital journey", "digital capability",
                           "digital initiative", "technology adoption", "digital strategy"],
                "iNube_solutions": ["digital_distribution", "embedded_insurance", "policy_administration"],
                "solution_description": "Accelerate digital transformation with modern insurance platforms"
            }
        }

    def _extract_key_points(self, result: Dict, query: str) -> List[str]:
    """
    Extract basic key points from search result content to avoid errors.
    """
    content = result.get("content", "")
    if not content:
        return []

    sentences = content.split(".")
    key_points = []

    for s in sentences:
        s = s.strip()
        if len(s) > 40:
            key_points.append(s)
        if len(key_points) >= 3:
            break
    
    return key_points
    def research_company(self, company_name: str, company_url: str) -> Tuple[Dict, List[Dict]]:
        """Research company using Tavily Search API focusing ONLY on relevant recent pain points"""
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # More specific queries to get relevant company-specific pain points
        recent_queries = [
            f"{company_name} business challenges 2025",
            f"{company_name} technology problems 2025",
            f"{company_name} operational issues 2025",
            f"{company_name} digital transformation challenges 2025",
            f"{company_name} customer experience problems 2025",
            f"{company_name} claims processing issues 2025",
            f"{company_name} legacy systems modernization 2025",
            f"{company_name} insurance operations efficiency 2025",
            f"{company_name} financial results challenges 2025",
            f"{company_name} recent news developments 2025"
        ]
        
        all_results = []
        analysis_data = {
            "company_name": company_name,
            "company_url": company_url,
            "sources": [],
            "research_points": [],
            "identified_pain_points": [],
            "relevant_sources": []
        }
        
        for query in recent_queries:
            try:
                response = self.client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=3,
                    include_answer=True,
                    start_date="2025-05-01",
                    end_date=current_date
                )
                
                if response and 'results' in response:
                    for result in response['results']:
                        # Check if the result is actually about the company
                        content = result.get('content', '').lower()
                        title = result.get('title', '').lower()
                        
                        # Filter for company-relevant results
                        if (company_name.lower() in content or company_name.lower() in title):
                            source_info = {
                                "title": result.get('title', ''),
                                "url": result.get('url', ''),
                                "content": result.get('content', ''),
                                "query": query
                            }
                            all_results.append(source_info)
                            analysis_data["relevant_sources"].append({
                                "title": result.get('title', ''),
                                "url": result.get('url', ''),
                                "content": result.get('content', '')[:300] + "..." if len(result.get('content', '')) > 300 else result.get('content', ''),
                                "query": query
                            })
                            
                            points = self._extract_key_points(result, query)
                            analysis_data["research_points"].extend(points)
                            
                            pain_points = self._extract_pain_points(result, query)
                            analysis_data["identified_pain_points"].extend(pain_points)
                    
                    time.sleep(1)
                            
            except Exception as e:
                st.error(f"Error in search query '{query}': {str(e)}")
                continue
        
        if all_results:
            analysis_data["sources"] = [{"url": r["url"], "title": r["title"]} for r in all_results]
            analysis_data["sources"] = [dict(t) for t in {tuple(d.items()) for d in analysis_data["sources"]}]
        
        return analysis_data, all_results
    
    def _extract_pain_points(self, result: Dict, query: str) -> List[Dict]:
        """Extract validated pain points with proof from search results"""
        pain_points = []
        content = result.get('content', '')
        title = result.get('title', '')
        url = result.get('url', '')
        
        content_lower = content.lower()
        
        for pain_point_id, pain_point_data in self.pain_points_mapping.items():
            for keyword in pain_point_data["keywords"]:
                if keyword in content_lower:
                    start_idx = max(0, content_lower.find(keyword) - 150)
                    end_idx = min(len(content), content_lower.find(keyword) + 300)
                    context = content[start_idx:end_idx].strip()
                    
                    if len(context) > 50:
                        pain_points.append({
                            "pain_point_id": pain_point_id,
                            "pain_point_name": pain_point_id.replace('_', ' ').title(),
                            "evidence": context,
                            "source_url": url,
                            "source_title": title,
                            "keyword_found": keyword,
                            "iNube_solutions": pain_point_data["iNube_solutions"],
                            "solution_description": pain_point_data["solution_description"],
                            "confidence": "high" if len(context) > 100 else "medium"
                        })
                    break
        
        return pain_points
    
    def analyze_company_fit(self, research_data: Dict) -> Dict:
        """Analyze company fit for iNube Solutions with dynamic analysis"""
        
        analysis = {
            "company_name": research_data["company_name"],
            "industry": "Insurance",  # Assuming insurance companies for this use case
            "validated_pain_points": research_data.get("identified_pain_points", []),
            "relevant_sources": research_data.get("relevant_sources", []),
            "pain_point_analysis": "",
            "iNube_solutions_alignment": "",
            "client_potential_summary": "",
            "recommendation": "",
            "confidence_score": 0
        }
        
        pain_points = analysis["validated_pain_points"]
        pain_point_count = len(pain_points)
        
        # Group pain points by category
        pain_point_groups = {}
        for pp in pain_points:
            if pp["pain_point_id"] not in pain_point_groups:
                pain_point_groups[pp["pain_point_id"]] = []
            pain_point_groups[pp["pain_point_id"]].append(pp)
        
        # Calculate confidence score
        unique_pain_points = len(pain_point_groups)
        analysis["confidence_score"] = min(100, (unique_pain_points * 15) + (pain_point_count * 2))
        
        # Generate dynamic analysis
        analysis["pain_point_analysis"] = self._generate_pain_point_analysis(pain_point_groups)
        analysis["iNube_solutions_alignment"] = self._generate_solutions_alignment(pain_point_groups)
        analysis["client_potential_summary"] = self._generate_client_summary(analysis, pain_point_groups)
        analysis["recommendation"] = self._generate_recommendation(analysis)
        
        return analysis
    
    def _generate_pain_point_analysis(self, pain_point_groups: Dict) -> str:
        """Generate pain point analysis in table format"""
        if not pain_point_groups:
            return "No recent pain points identified."
        
        analysis_lines = []
        analysis_lines.append("### Recent Pain Points Identified")
        analysis_lines.append(f"Found {sum(len(v) for v in pain_point_groups.values())} validated pain points across {len(pain_point_groups)} key areas:\n")
        
        for pain_point_id, evidences in pain_point_groups.items():
            pain_point_name = pain_point_id.replace('_', ' ').title()
            source_count = len(evidences)
            
            # Get source references
            source_refs = []
            for i, evidence in enumerate(evidences[:3]):  # Show max 3 sources
                source_refs.append(f"Source {i+1}")
            
            sources_text = ", ".join(source_refs)
            analysis_lines.append(f"**{pain_point_name}**: {source_count} evidence sources ({sources_text})")
        
        return "\n".join(analysis_lines)
    
    def _generate_solutions_alignment(self, pain_point_groups: Dict) -> str:
        """Generate iNube solutions alignment in table format"""
        if not pain_point_groups:
            return "No iNube solutions alignment identified."
        
        # Get all recommended solutions
        all_solutions = set()
        for pain_point_id in pain_point_groups.keys():
            all_solutions.update(self.pain_points_mapping[pain_point_id]["iNube_solutions"])
        
        solution_names = [s.replace('_', ' ').title() for s in all_solutions]
        
        alignment_lines = []
        alignment_lines.append("### iNube Solutions Alignment")
        alignment_lines.append(f"**Recommended iNube Solutions**: {', '.join(solution_names)}\n")
        
        alignment_lines.append("**How iNube Can Help**:")
        for pain_point_id in pain_point_groups.keys():
            pain_point_name = pain_point_id.replace('_', ' ').title()
            solutions = self.pain_points_mapping[pain_point_id]["iNube_solutions"]
            solution_names = [s.replace('_', ' ').title() for s in solutions]
            solution_desc = self.pain_points_mapping[pain_point_id]["solution_description"]
            
            alignment_lines.append(f"- **{pain_point_name}**: {solution_desc}")
        
        return "\n".join(alignment_lines)
    
    def _generate_client_summary(self, analysis: Dict, pain_point_groups: Dict) -> str:
        """Generate client assessment summary"""
        pain_point_count = sum(len(v) for v in pain_point_groups.values())
        unique_pain_points = len(pain_point_groups)
        
        summary_lines = []
        summary_lines.append("### Assessment Summary")
        summary_lines.append(f"- **Industry**: {analysis.get('industry', 'Insurance')}")
        summary_lines.append(f"- **Confidence Score**: {analysis.get('confidence_score', 0)}%")
        summary_lines.append(f"- **Pain Points Found**: {pain_point_count}")
        summary_lines.append(f"- **iNube Solutions Match**: {len(set().union(*[self.pain_points_mapping[pp_id]['iNube_solutions'] for pp_id in pain_point_groups.keys()]))} services")
        
        return "\n".join(summary_lines)
    
    def _generate_recommendation(self, analysis: Dict) -> str:
        """Generate final recommendation"""
        confidence = analysis["confidence_score"]
        
        if confidence >= 80:
            return "STRONG POTENTIAL CLIENT - Multiple recent pain points identified with clear iNube solution alignment"
        elif confidence >= 60:
            return "MODERATE POTENTIAL CLIENT - Recent pain points identified with iNube solution opportunities"
        elif confidence >= 40:
            return "WEAK POTENTIAL - Limited recent pain point evidence found"
        else:
            return "NOT A VIABLE PROSPECT - No relevant recent pain points identified"

def main():
    st.title("iNube Solutions - Client Potential Analysis")
    st.markdown("**Analyzing company-specific pain points from May 2025 to present**")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        
        api_key = st.secrets.get("TAVILY", None)
        
        if not api_key:
            st.warning("Tavily API key not found in secrets. Please enter it below:")
            api_key = st.text_input("Tavily API Key", type="password", 
                                   help="Get your API key from https://tavily.com")
        else:
            st.success("Tavily API key loaded from secrets")
        
        st.markdown("---")
        
        current_month_year = datetime.now().strftime("%B %Y")
        st.info(f"**Search Range**: May 2025 - {current_month_year}")
        
        st.markdown("**How to use:**")
        st.markdown("1. Ensure Tavily API key is set")
        st.markdown("2. Input target company details")
        st.markdown("3. Click Research Company")
        st.markdown("4. Review company-specific pain points and iNube alignment")
        
        st.markdown("---")
        st.markdown("**Pain Points Detected:**")
        pain_points = {
            "legacy_systems": "Outdated technology infrastructure",
            "manual_processes": "Inefficient manual workflows", 
            "customer_experience": "Poor customer satisfaction",
            "fraud_detection": "Ineffective fraud prevention",
            "operational_efficiency": "High operational costs",
            "data_analytics": "Lack of data-driven insights",
            "digital_transformation": "Slow digital adoption"
        }
        for pp_id, pp_desc in pain_points.items():
            st.markdown(f"- {pp_id.replace('_', ' ').title()}: {pp_desc}")

    # Main input section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Company Information")
        company_name = st.text_input("Company Name", 
                                   value="SHRIRAM GENERAL INSURANCE CO. LTD.",
                                   placeholder="Enter insurance company name")
        company_url = st.text_input("Company Website URL", 
                                  value="https://www.shriramgi.com",
                                  placeholder="Enter company website URL")
        
        research_button = st.button("Analyze Client Potential", type="primary", disabled=not api_key)
    
    with col2:
        st.subheader("Analysis Focus")
        current_date = datetime.now().strftime("%Y-%m-%d")
        st.markdown(f"""
        **Timeframe**: May 1, 2025 - {current_date}
        
        **Analysis Includes**:
        - Company-specific pain point identification
        - Dynamic iNube solutions alignment
        - Client potential assessment
        - Actionable recommendations
        
        **Filters Applied**:
        - Only company-relevant sources
        - Recent evidence only (May 2025+)
        - Insurance industry focus
        """)
        
        st.warning("Only relevant, company-specific sources from May 2025+ will be analyzed")

    
    if not api_key:
        st.error("Please provide a Tavily API key to begin analysis")
        return
    
    try:
        agent = TavilyResearchAgent(api_key)
    except Exception as e:
        st.error(f"Failed to initialize Tavily client: {str(e)}")
        return
    
    if research_button and company_name:
        current_date = datetime.now().strftime("%Y-%m-%d")
        with st.spinner(f"Researching {company_name} for relevant pain points (May 2025 - {current_date})..."):
            research_data, detailed_results = agent.research_company(company_name, company_url)
            analysis = agent.analyze_company_fit(research_data)
        
        if analysis and research_data.get("research_points"):
            display_client_analysis(analysis, research_data, agent)
        else:
            st.error("No relevant company-specific pain points found from May 2025 to present.")

def display_client_analysis(analysis: Dict, research_data: Dict, agent: TavilyResearchAgent):
    """Display comprehensive client analysis in table format"""
    
    st.markdown("---")
    st.header(f"Client Potential Analysis: {analysis['company_name']}")
    
    # Display main analysis sections
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(analysis['pain_point_analysis'])
    
    with col2:
        st.markdown(analysis['iNube_solutions_alignment'])
    
    st.markdown("---")
    
    # Assessment Summary
    col3, col4 = st.columns([1, 1])
    
    with col3:
        st.markdown(analysis['client_potential_summary'])
    
    with col4:
        st.subheader("Final Recommendation")
        recommendation = analysis.get('recommendation', 'No recommendation available')
        if "STRONG" in recommendation:
            st.success(recommendation)
        elif "MODERATE" in recommendation:
            st.warning(recommendation)
        else:
            st.error(recommendation)
    
    # Detailed Evidence Sources
    st.markdown("---")
    st.subheader("Evidence Sources")
    
    relevant_sources = analysis.get("relevant_sources", [])
    if relevant_sources:
        st.info(f"Found {len(relevant_sources)} relevant sources from May 2025 to present")
        
        # Create a table of sources
        source_data = []
        for i, source in enumerate(relevant_sources):
            source_data.append({
                "Source": f"Source {i+1}",
                "Title": source['title'],
                "URL": source['url'],
                "Content Preview": source['content'][:100] + "..." if len(source['content']) > 100 else source['content']
            })
        
        source_df = pd.DataFrame(source_data)
        st.dataframe(source_df, use_container_width=True, hide_index=True)
        
        # Show detailed evidence for each pain point
        st.subheader("Detailed Pain Point Evidence")
        pain_points = analysis.get("validated_pain_points", [])
        pain_point_groups = {}
        
        for pp in pain_points:
            if pp["pain_point_id"] not in pain_point_groups:
                pain_point_groups[pp["pain_point_id"]] = []
            pain_point_groups[pp["pain_point_id"]].append(pp)
        
        for pain_point_id, evidences in pain_point_groups.items():
            with st.expander(f"{pain_point_id.replace('_', ' ').title()} - {len(evidences)} evidence sources"):
                for i, evidence in enumerate(evidences):
                    st.markdown(f"**Evidence {i+1}**")
                    st.markdown(f"**Source**: {evidence['source_title']}")
                    st.markdown(f"**URL**: {evidence['source_url']}")
                    st.markdown(f"**Evidence**: {evidence['evidence']}")
                    st.markdown(f"**iNube Solution**: {evidence['solution_description']}")
                    st.markdown("---")
    else:
        st.warning("No relevant sources found for the specified company and timeframe")
    
    # Export functionality
    st.markdown("---")
    st.subheader("Export Analysis")
    
    if st.button("Generate Comprehensive Report"):
        generate_comprehensive_report(analysis, research_data)

def generate_comprehensive_report(analysis: Dict, research_data: Dict):
    """Generate a comprehensive report for download"""
    
    report_data = []
    pain_points = analysis.get("validated_pain_points", [])
    
    # Group pain points
    pain_point_groups = {}
    for pp in pain_points:
        if pp["pain_point_id"] not in pain_point_groups:
            pain_point_groups[pp["pain_point_id"]] = []
        pain_point_groups[pp["pain_point_id"]].append(pp)
    
    # Create report data
    for pain_point_id, evidences in pain_point_groups.items():
        for evidence in evidences:
            report_data.append({
                "Pain Point Category": pain_point_id.replace('_', ' ').title(),
                "Evidence": evidence["evidence"],
                "Source URL": evidence["source_url"],
                "Source Title": evidence["source_title"],
                "iNube Solutions": ", ".join([s.replace('_', ' ').title() for s in evidence["iNube_solutions"]]),
                "Solution Description": evidence["solution_description"],
                "Confidence": evidence["confidence"].title()
            })
    
    if report_data:
        report_df = pd.DataFrame(report_data)
        csv_data = report_df.to_csv(index=False)
        
        st.download_button(
            label="Download Comprehensive Analysis CSV",
            data=csv_data,
            file_name=f"inube_analysis_{analysis['company_name'].lower().replace(' ', '_')}.csv",
            mime="text/csv",
            type="primary"
        )

if __name__ == "__main__":
    main()
