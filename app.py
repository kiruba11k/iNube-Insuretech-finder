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
            f"{company_name} recent news developments 2025",
            f"{company_name} AI adoption challenges 2025",
            f"{company_name} fraud detection issues 2025",
            f"{company_name} data analytics challenges 2025"
        ]
        
        all_results = []
        analysis_data = {
            "company_name": company_name,
            "company_url": company_url,
            "sources": [],
            "research_points": [],
            "identified_pain_points": [],
            "relevant_sources": [],
            "timeframe_analysis": f"May 2025 to {datetime.now().strftime('%B %Y')}"
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
                                "query": query,
                                "published_date": result.get('published_date', 'Not specified')
                            }
                            all_results.append(source_info)
                            analysis_data["relevant_sources"].append({
                                "title": result.get('title', ''),
                                "url": result.get('url', ''),
                                "content": result.get('content', '')[:300] + "..." if len(result.get('content', '')) > 300 else result.get('content', ''),
                                "query": query,
                                "published_date": result.get('published_date', 'Not specified')
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
        """Analyze company fit for iNube Solutions based on direct source analysis"""
        
        analysis = {
            "company_name": research_data["company_name"],
            "industry": "Insurance",
            "validated_pain_points": research_data.get("identified_pain_points", []),
            "relevant_sources": research_data.get("relevant_sources", []),
            "timeframe_analysis": research_data.get("timeframe_analysis", ""),
            "pain_point_analysis": "",
            "iNube_solutions_alignment": "",
            "client_potential_summary": "",
            "recommendation": "",
            "recent_evidence_count": len(research_data.get("relevant_sources", [])),
            "direct_analysis_summary": ""
        }
        
        pain_points = analysis["validated_pain_points"]
        
        # Group pain points by category
        pain_point_groups = {}
        for pp in pain_points:
            if pp["pain_point_id"] not in pain_point_groups:
                pain_point_groups[pp["pain_point_id"]] = []
            pain_point_groups[pp["pain_point_id"]].append(pp)
        
        # Generate direct analysis based on source URLs and content
        analysis["direct_analysis_summary"] = self._generate_direct_analysis(pain_point_groups, analysis["relevant_sources"])
        
        # Generate dynamic analysis
        analysis["pain_point_analysis"] = self._generate_pain_point_analysis(pain_point_groups, analysis["recent_evidence_count"])
        analysis["iNube_solutions_alignment"] = self._generate_solutions_alignment(pain_point_groups)
        analysis["client_potential_summary"] = self._generate_client_summary(analysis, pain_point_groups)
        analysis["recommendation"] = self._generate_direct_recommendation(analysis, pain_point_groups)
        
        return analysis
    
    def _generate_direct_analysis(self, pain_point_groups: Dict, relevant_sources: List) -> str:
        """Generate direct analysis based on source URLs and content"""
        
        if not pain_point_groups:
            return " **No direct evidence found** in recent sources that matches iNube Solutions capabilities."
        
        analysis_lines = []
        analysis_lines.append("###  Direct Source Analysis")
        analysis_lines.append("**Based on analyzing recent source URLs and content:**\n")
        
        # Analyze each pain point group with specific evidence
        for pain_point_id, evidences in pain_point_groups.items():
            pain_point_name = pain_point_id.replace('_', ' ').title()
            solution_desc = self.pain_points_mapping[pain_point_id]["solution_description"]
            
            analysis_lines.append(f"** {pain_point_name}**")
            analysis_lines.append(f"   - *iNube Solution*: {solution_desc}")
            analysis_lines.append(f"   - *Evidence Found*: {len(evidences)} sources")
            
            # Show top evidence snippets
            for i, evidence in enumerate(evidences[:2]):  # Show top 2 evidence per category
                source_ref = f"[Source {i+1}]({evidence['source_url']})"
                snippet = evidence['evidence'][:150] + "..." if len(evidence['evidence']) > 150 else evidence['evidence']
                analysis_lines.append(f"   - *Evidence {i+1}*: {snippet} ({source_ref})")
            analysis_lines.append("")
        
        return "\n".join(analysis_lines)
    
    def _generate_direct_recommendation(self, analysis: Dict, pain_point_groups: Dict) -> str:
        """Generate final recommendation based on direct analysis of sources and iNube alignment"""
        
        pain_points = analysis["validated_pain_points"]
        relevant_sources = analysis["relevant_sources"]
        
        if not relevant_sources:
            return "❌ **NO RECENT EVIDENCE** - No relevant sources found from May 2025 to present. Cannot assess iNube solution fit."
        
        if not pain_points:
            return "❌ **NO iNUBE MATCH** - Sources found but no specific pain points identified that align with iNube solutions."
        
        # Count unique iNube solutions that can address the identified pain points
        all_solutions = set()
        for pain_point_id in pain_point_groups.keys():
            all_solutions.update(self.pain_points_mapping[pain_point_id]["iNube_solutions"])
        
        unique_solution_count = len(all_solutions)
        total_evidence_count = len(pain_points)
        unique_pain_points = len(pain_point_groups)
        
        # Direct recommendation logic based on source analysis
        if unique_pain_points >= 4 and total_evidence_count >= 6:
            return f" **STRONG iNUBE FIT** - {unique_pain_points} major pain points identified with {total_evidence_count} evidence sources. {unique_solution_count} iNube solutions directly address these challenges."
        
        elif unique_pain_points >= 3 and total_evidence_count >= 4:
            return f" **SOLID iNUBE OPPORTUNITY** - {unique_pain_points} key pain points found with {total_evidence_count} sources. {unique_solution_count} iNube solutions provide direct solutions."
        
        elif unique_pain_points >= 2 and total_evidence_count >= 2:
            return f" **MODERATE iNUBE POTENTIAL** - {unique_pain_points} pain points identified with limited evidence. {unique_solution_count} iNube solutions could address these areas."
        
        elif unique_pain_points >= 1:
            return f" **WEAK iNUBE MATCH** - Only {unique_pain_points} pain point identified with minimal evidence. Limited scope for iNube solutions."
        
        else:
            return " **NO VIABLE iNUBE PROSPECT** - Sources analyzed but no clear alignment with iNube solution capabilities."
    
    def _generate_pain_point_analysis(self, pain_point_groups: Dict, recent_source_count: int) -> str:
        """Generate pain point analysis focusing on recent evidence"""
        if not pain_point_groups:
            return "No recent pain points identified from May 2025 to present."
        
        analysis_lines = []
        analysis_lines.append("###  Recent Pain Points Identified (May 2025 - Present)")
        analysis_lines.append(f"**Analysis based on {recent_source_count} recent sources:**\n")
        
        for pain_point_id, evidences in pain_point_groups.items():
            pain_point_name = pain_point_id.replace('_', ' ').title()
            source_count = len(evidences)
            
            # Get solution alignment
            solutions = self.pain_points_mapping[pain_point_id]["iNube_solutions"]
            solution_names = [s.replace('_', ' ').title() for s in solutions]
            
            analysis_lines.append(f"**🔹 {pain_point_name}**")
            analysis_lines.append(f"   - *Evidence Sources*: {source_count}")
            analysis_lines.append(f"   - *iNube Solutions*: {', '.join(solution_names)}")
        
        return "\n".join(analysis_lines)
    
    def _generate_solutions_alignment(self, pain_point_groups: Dict) -> str:
        """Generate iNube solutions alignment based on recent pain points"""
        if not pain_point_groups:
            return "No iNube solutions alignment identified from recent sources."
        
        # Get all recommended solutions
        all_solutions = set()
        for pain_point_id in pain_point_groups.keys():
            all_solutions.update(self.pain_points_mapping[pain_point_id]["iNube_solutions"])
        
        solution_names = [s.replace('_', ' ').title() for s in all_solutions]
        
        alignment_lines = []
        alignment_lines.append("###  iNube Solutions Alignment")
        alignment_lines.append(f"**Solutions Recommended**: {', '.join(solution_names)}\n")
        
        alignment_lines.append("**Direct Solution Mapping**:")
        for pain_point_id in pain_point_groups.keys():
            pain_point_name = pain_point_id.replace('_', ' ').title()
            solutions = self.pain_points_mapping[pain_point_id]["iNube_solutions"]
            solution_names = [s.replace('_', ' ').title() for s in solutions]
            solution_desc = self.pain_points_mapping[pain_point_id]["solution_description"]
            
            alignment_lines.append(f"- **{pain_point_name}** → {solution_desc}")
        
        return "\n".join(alignment_lines)
    
    def _generate_client_summary(self, analysis: Dict, pain_point_groups: Dict) -> str:
        """Generate client assessment summary focusing on direct analysis"""
        pain_point_count = sum(len(v) for v in pain_point_groups.values())
        unique_pain_points = len(pain_point_groups)
        
        # Calculate iNube solution coverage
        all_solutions = set()
        for pain_point_id in pain_point_groups.keys():
            all_solutions.update(self.pain_points_mapping[pain_point_id]["iNube_solutions"])
        
        summary_lines = []
        summary_lines.append("###  Direct Analysis Summary")
        summary_lines.append(f"- **Company**: {analysis['company_name']}")
        summary_lines.append(f"- **Timeframe**: {analysis.get('timeframe_analysis', '')}")
        summary_lines.append(f"- **Recent Sources Analyzed**: {analysis.get('recent_evidence_count', 0)}")
        summary_lines.append(f"- **Pain Points Identified**: {unique_pain_points} categories, {pain_point_count} total evidence")
        summary_lines.append(f"- **iNube Solutions Match**: {len(all_solutions)} solutions")
        summary_lines.append(f"- **Analysis Method**: Direct source URL and content analysis")
        
        return "\n".join(summary_lines)

def main():
    st.title("iNube Solutions - Client Potential Analysis")
    st.markdown("**Direct analysis of company pain points from May 2025 to present**")
    
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
        
        st.markdown("**Analysis Method:**")
        st.markdown("1. Direct source URL analysis")
        st.markdown("2. Content matching with iNube solutions")
        st.markdown("3. No confidence scores - pure evidence-based")
        st.markdown("4. Recent timeframe focus (May 2025+)")
        
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
        st.subheader("Direct Analysis Method")
        current_date = datetime.now().strftime("%Y-%m-%d")
        st.markdown(f"""
        **Timeframe**: May 1, 2025 - {current_date}
        
        **Direct Analysis Approach**:
        - Source URL and content analysis only
        - No confidence score calculations
        - Direct evidence-to-solution mapping
        - Recent timeframe validation
        
        **Evaluation Criteria**:
        - Number of pain point categories
        - Evidence source count
        - iNube solution alignment
        - Recent source relevance
        """)
        
        st.warning("Recommendations based purely on direct source analysis")

    
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
        with st.spinner(f"Direct analysis of {company_name} (May 2025 - {current_date})..."):
            research_data, detailed_results = agent.research_company(company_name, company_url)
            analysis = agent.analyze_company_fit(research_data)
        
        if analysis and research_data.get("research_points"):
            display_client_analysis(analysis, research_data, agent)
        else:
            st.error("No relevant company-specific pain points found from May 2025 to present.")

def display_client_analysis(analysis: Dict, research_data: Dict, agent: TavilyResearchAgent):
    """Display comprehensive client analysis focusing on direct source analysis"""
    
    st.markdown("---")
    st.header(f"Direct Client Analysis: {analysis['company_name']}")
    
    # Display timeframe info prominently
    st.info(f"**Analysis Timeframe**: {analysis.get('timeframe_analysis', 'May 2025 to Present')}")
    
    # Display direct analysis first
    st.markdown(analysis['direct_analysis_summary'])
    
    st.markdown("---")
    
    # Display main analysis sections
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown(analysis['pain_point_analysis'])
    
    with col2:
        st.markdown(analysis['iNube_solutions_alignment'])
    
    st.markdown("---")
    
    # Assessment Summary and Final Recommendation
    col3, col4 = st.columns([1, 1])
    
    with col3:
        st.markdown(analysis['client_potential_summary'])
    
    with col4:
        st.subheader(" Final Recommendation")
        recommendation = analysis.get('recommendation', 'No recommendation available')
        
        if "STRONG iNUBE FIT" in recommendation:
            st.success(recommendation)
            st.info("**Next Steps**: Immediate engagement recommended. Multiple iNube solutions directly address identified challenges.")
        elif "SOLID iNUBE OPPORTUNITY" in recommendation:
            st.success(recommendation)
            st.info("**Next Steps**: Schedule discovery meeting. Clear alignment with iNube capabilities.")
        elif "MODERATE iNUBE POTENTIAL" in recommendation:
            st.warning(recommendation)
            st.info("**Next Steps**: Further research needed. Limited but viable opportunity.")
        elif "WEAK iNUBE MATCH" in recommendation:
            st.warning(recommendation)
            st.info("**Next Steps**: Low priority. Consider other prospects first.")
        else:
            st.error(recommendation)
            st.info("**Next Steps**: Not recommended for iNube solutions engagement.")
    
    # Detailed Evidence Sources with direct analysis
    st.markdown("---")
    st.subheader(" Recent Evidence Sources (May 2025+)")
    
    relevant_sources = analysis.get("relevant_sources", [])
    if relevant_sources:
        st.info(f"**Direct analysis of {len(relevant_sources)} relevant sources from May 2025 to present**")
        
        # Create a table of sources with direct analysis
        source_data = []
        for i, source in enumerate(relevant_sources):
            # Analyze source for key pain points
            pain_points_in_source = []
            for pp in analysis.get("validated_pain_points", []):
                if pp["source_url"] == source["url"]:
                    pain_points_in_source.append(pp["pain_point_name"])
            
            source_data.append({
                "Source": f"Source {i+1}",
                "Title": source['title'],
                "URL": source['url'],
                "Pain Points": ", ".join(pain_points_in_source) if pain_points_in_source else "None identified",
                "Published Date": source.get('published_date', 'Not specified'),
                "Content Preview": source['content'][:80] + "..." if len(source['content']) > 80 else source['content']
            })
        
        source_df = pd.DataFrame(source_data)
        st.dataframe(source_df, use_container_width=True, hide_index=True)
        
        # Show detailed evidence for each pain point
        st.subheader(" Detailed Pain Point Evidence (Direct Analysis)")
        pain_points = analysis.get("validated_pain_points", [])
        pain_point_groups = {}
        
        for pp in pain_points:
            if pp["pain_point_id"] not in pain_point_groups:
                pain_point_groups[pp["pain_point_id"]] = []
            pain_point_groups[pp["pain_point_id"]].append(pp)
        
        for pain_point_id, evidences in pain_point_groups.items():
            with st.expander(f" {pain_point_id.replace('_', ' ').title()} - {len(evidences)} direct evidence sources"):
                for i, evidence in enumerate(evidences):
                    st.markdown(f"**Evidence {i+1}**")
                    st.markdown(f"**Source**: {evidence['source_title']}")
                    st.markdown(f"**URL**: {evidence['source_url']}")
                    st.markdown(f"**Direct Evidence**: {evidence['evidence']}")
                    st.markdown(f"**iNube Solution Match**: {evidence['solution_description']}")
                    st.markdown("---")
    else:
        st.warning("No relevant sources found for the specified company and timeframe (May 2025+)")
    
    # Export functionality
    st.markdown("---")
    st.subheader(" Export Direct Analysis")
    
    if st.button("Generate Direct Analysis Report"):
        generate_direct_analysis_report(analysis, research_data)

def generate_direct_analysis_report(analysis: Dict, research_data: Dict):
    """Generate a direct analysis report for download"""
    
    report_data = []
    pain_points = analysis.get("validated_pain_points", [])
    
    # Group pain points
    pain_point_groups = {}
    for pp in pain_points:
        if pp["pain_point_id"] not in pain_point_groups:
            pain_point_groups[pp["pain_point_id"]] = []
        pain_point_groups[pp["pain_point_id"]].append(pp)
    
    # Create report data with direct analysis focus
    for pain_point_id, evidences in pain_point_groups.items():
        for evidence in evidences:
            report_data.append({
                "Pain Point Category": pain_point_id.replace('_', ' ').title(),
                "Direct Evidence": evidence["evidence"],
                "Source URL": evidence["source_url"],
                "Source Title": evidence["source_title"],
                "iNube Solutions": ", ".join([s.replace('_', ' ').title() for s in evidence["iNube_solutions"]]),
                "Solution Description": evidence["solution_description"],
                "Analysis Method": "Direct Source Analysis",
                "Timeframe": "May 2025+"
            })
    
    if report_data:
        report_df = pd.DataFrame(report_data)
        csv_data = report_df.to_csv(index=False)
        
        st.download_button(
            label="Download Direct Analysis CSV",
            data=csv_data,
            file_name=f"inube_direct_analysis_{analysis['company_name'].lower().replace(' ', '_')}.csv",
            mime="text/csv",
            type="primary"
        )

if __name__ == "__main__":
    main()
