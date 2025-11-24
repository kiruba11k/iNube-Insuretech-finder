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
    page_title="iNube Solutions - Recent Pain Point Analysis",
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
        
        # Pain points mapping focused on current insurance challenges
        self.pain_points_mapping = {
            "legacy_systems": {
                "keywords": ["legacy system", "outdated technology", "old software", "system modernization", 
                           "technology upgrade", "digital transformation", "modernization challenge"],
                "iNube_solutions": ["policy_administration", "digital_distribution", "claims_management"]
            },
            "manual_processes": {
                "keywords": ["manual process", "paper-based", "manual data entry", "manual workflow",
                           "manual intervention", "manual handling", "manual verification"],
                "iNube_solutions": ["claims_management", "field_operations", "ai_analytics"]
            },
            "customer_experience": {
                "keywords": ["customer satisfaction", "customer churn", "customer retention", 
                           "digital onboarding", "customer experience", "policyholder experience"],
                "iNube_solutions": ["digital_distribution", "embedded_insurance", "policy_administration"]
            },
            "fraud_detection": {
                "keywords": ["insurance fraud", "fraud detection", "false claims", "claims fraud",
                           "fraud prevention", "fraudulent activities"],
                "iNube_solutions": ["claims_management", "ai_analytics"]
            },
            "operational_efficiency": {
                "keywords": ["operational efficiency", "process efficiency", "cost reduction", 
                           "streamline operations", "efficiency improvement", "operational cost"],
                "iNube_solutions": ["policy_administration", "claims_management", "field_operations"]
            },
            "data_analytics": {
                "keywords": ["data analytics", "business intelligence", "predictive analytics",
                           "data-driven decisions", "analytics capability", "data insights"],
                "iNube_solutions": ["ai_analytics", "claims_management"]
            },
            "digital_transformation": {
                "keywords": ["digital transformation", "digital journey", "digital capability",
                           "digital initiative", "technology adoption", "digital strategy"],
                "iNube_solutions": ["digital_distribution", "embedded_insurance", "policy_administration"]
            }
        }
    
    def research_company(self, company_name: str, company_url: str) -> Tuple[Dict, List[Dict]]:
        """Research company using Tavily Search API focusing ONLY on recent pain points (May 2025 to present)"""
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Search queries focused on recent challenges (May 2025 to present)
        recent_queries = [
            f"{company_name} challenges problems issues difficulties 2025",
            f"{company_name} digital transformation legacy systems modernization 2025",
            f"{company_name} operational efficiency cost reduction manual processes 2025",
            f"{company_name} customer experience policyholder satisfaction churn 2025",
            f"{company_name} claims processing fraud detection technology gaps 2025",
            f"{company_name} technology stack IT systems software platforms 2025",
            f"{company_name} financial results operational performance 2025",
            f"{company_name} news updates recent developments technology initiatives 2025",
            f"{company_name} insurance industry challenges 2025",
            f"{company_name} business transformation technology investment 2025"
        ]
        
        all_results = []
        analysis_data = {
            "company_name": company_name,
            "company_url": company_url,
            "sources": [],
            "research_points": [],
            "identified_pain_points": [],
            "recent_sources": []
        }
        
        for query in recent_queries:
            try:
                response = self.client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=5,
                    include_answer=True,
                    # ONLY search from May 2025 to present
                    start_date="2025-05-01",
                    end_date=current_date
                )
                
                if response and 'results' in response:
                    for result in response['results']:
                        source_info = {
                            "title": result.get('title', ''),
                            "url": result.get('url', ''),
                            "content": result.get('content', ''),
                            "query": query,
                            "time_period": f"May 2025 - {datetime.now().strftime('%b %Y')}"
                        }
                        all_results.append(source_info)
                        analysis_data["recent_sources"].append({
                            "title": result.get('title', ''),
                            "url": result.get('url', ''),
                            "content": result.get('content', '')[:500] + "..." if len(result.get('content', '')) > 500 else result.get('content', ''),
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
                            "confidence": "high" if len(context) > 100 else "medium"
                        })
                    break
        
        return pain_points
    
    def _extract_key_points(self, result: Dict, query: str) -> List[Dict]:
        """Extract key points from search results"""
        points = []
        content = result.get('content', '')
        title = result.get('title', '')
        url = result.get('url', '')
        
        categories = {
            "business_model": ["services", "products", "business model", "offering", "solutions", "revenue"],
            "technology": ["technology", "digital", "software", "platform", "AI", "automation", "cloud", "IT"],
            "challenges": ["challenge", "problem", "issue", "limitation", "gap", "difficulty", "bottleneck"],
            "operations": ["operations", "process", "workflow", "efficiency", "cost", "manual", "legacy"],
            "insurance": ["insurance", "policy", "claim", "underwriting", "premium", "risk", "coverage"]
        }
        
        content_lower = content.lower()
        
        for category, keywords in categories.items():
            for keyword in keywords:
                if keyword in content_lower:
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
                    break
        
        return points
    
    def analyze_company_fit(self, research_data: Dict) -> Dict:
        """Analyze company fit for iNube Solutions focusing ONLY on recent pain points"""
        
        analysis = {
            "company_name": research_data["company_name"],
            "industry": "Unknown",
            "validated_pain_points": research_data.get("identified_pain_points", []),
            "potential_iNube_services": [],
            "client_potential_summary": "",
            "recommendation": "",
            "confidence_score": 0,
            "sources": research_data.get("sources", []),
            "recent_sources": research_data.get("recent_sources", [])
        }
        
        pain_point_count = len(analysis["validated_pain_points"])
        
        # Check for insurance industry indicators
        insurance_keywords = ["insurance", "policy", "claim", "underwriting", "premium", "risk", "coverage"]
        insurance_mentions = 0
        
        for point in research_data.get("research_points", []):
            point_text = point["point"].lower()
            if any(keyword in point_text for keyword in insurance_keywords):
                insurance_mentions += 1
                analysis["industry"] = "Insurance"
        
        # Determine potential iNube services based on validated pain points
        all_recommended_services = []
        for pain_point in analysis["validated_pain_points"]:
            all_recommended_services.extend(pain_point["iNube_solutions"])
        
        analysis["potential_iNube_services"] = list(set(all_recommended_services))
        
        # Calculate confidence score based on recent pain points
        pain_point_score = min(80, pain_point_count * 20)
        industry_score = 20 if analysis["industry"] == "Insurance" else 0
        analysis["confidence_score"] = min(100, pain_point_score + industry_score)
        
        # Generate client potential summary
        analysis["client_potential_summary"] = self._generate_client_potential_summary(analysis)
        analysis["recommendation"] = self._generate_recommendation(analysis)
        
        return analysis
    
    def _generate_client_potential_summary(self, analysis: Dict) -> str:
        """Generate comprehensive client potential summary based on recent pain points"""
        pain_points = analysis.get("validated_pain_points", [])
        recent_sources_count = len(analysis.get("recent_sources", []))
        
        if not pain_points:
            return f"Limited client potential identified. No recent pain points found from May 2025 to present. Searched {recent_sources_count} recent sources."
        
        # Group pain points by category
        pain_point_groups = {}
        for pp in pain_points:
            if pp["pain_point_id"] not in pain_point_groups:
                pain_point_groups[pp["pain_point_id"]] = []
            pain_point_groups[pp["pain_point_id"]].append(pp)
        
        current_month_year = datetime.now().strftime("%B %Y")
        summary_parts = []
        
        summary_parts.append(f"## Client Potential Analysis: {analysis['company_name']}")
        summary_parts.append(f"**Timeframe**: May 2025 - {current_month_year}")
        summary_parts.append(f"**Sources Analyzed**: {recent_sources_count} recent sources")
        summary_parts.append("")
        
        summary_parts.append("###  Recent Pain Points Identified")
        summary_parts.append(f"Found {len(pain_points)} validated pain points across {len(pain_point_groups)} key areas:")
        
        for pain_point_id, evidences in pain_point_groups.items():
            pain_point_name = pain_point_id.replace('_', ' ').title()
            source_count = len(evidences)
            
            # Get source URLs for this pain point
            source_links = []
            for i, evidence in enumerate(evidences[:3]):  # Show max 3 sources per pain point
                source_links.append(f"[Source {i+1}]({evidence['source_url']})")
            
            sources_text = ", ".join(source_links)
            summary_parts.append(f"- **{pain_point_name}**: {source_count} evidence sources ({sources_text})")
        
        summary_parts.append("")
        summary_parts.append("###  iNube Solutions Alignment")
        
        if analysis["potential_iNube_services"]:
            solutions = [s.replace('_', ' ').title() for s in analysis["potential_iNube_services"]]
            summary_parts.append(f"**Recommended iNube Solutions**: {', '.join(solutions)}")
            
            # Explain how iNube addresses each pain point
            summary_parts.append("")
            summary_parts.append("**How iNube Can Help**:")
            for pain_point_id in pain_point_groups.keys():
                pain_point_name = pain_point_id.replace('_', ' ').title()
                solutions = self.pain_points_mapping[pain_point_id]["iNube_solutions"]
                solution_names = [s.replace('_', ' ').title() for s in solutions]
                summary_parts.append(f"- **{pain_point_name}**: Addressed with {', '.join(solution_names)}")
        else:
            summary_parts.append("No specific iNube solutions identified for the pain points found.")
        
        summary_parts.append("")
        summary_parts.append("###  Assessment Summary")
        summary_parts.append(f"- **Industry**: {analysis.get('industry', 'Unknown')}")
        summary_parts.append(f"- **Confidence Score**: {analysis.get('confidence_score', 0)}%")
        summary_parts.append(f"- **Pain Points Found**: {len(pain_points)}")
        summary_parts.append(f"- **iNube Solutions Match**: {len(analysis['potential_iNube_services'])} services")
        
        return "\n".join(summary_parts)
    
    def _generate_recommendation(self, analysis: Dict) -> str:
        """Generate recommendation based on recent pain point analysis"""
        
        confidence = analysis["confidence_score"]
        pain_point_count = len(analysis["validated_pain_points"])

        if confidence >= 70 and pain_point_count >= 2:
            return "STRONG POTENTIAL CLIENT - Multiple recent pain points identified with clear iNube solution alignment"
        elif confidence >= 50 and pain_point_count >= 1:
            return "MODERATE POTENTIAL CLIENT - Recent pain points identified with iNube solution opportunities"
        elif confidence >= 30:
            return "WEAK POTENTIAL - Limited recent pain point evidence found"
        else:
            return "NOT A VIABLE PROSPECT - No recent pain points identified from May 2025 to present"

def main():
    st.title("iNube Solutions - Recent Client Potential Analysis")
    st.markdown("**Analyzing companies for pain points from May 2025 to present**")

    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")

        api_key = st.secrets.get("TAVILY", None)

        if not api_key:
            st.warning("Tavily API key not found in secrets. Please enter it below:")
            api_key = st.text_input("Tavily API Key", type="password")
        else:
            st.success("Tavily API key loaded from secrets")

    #  Initialize agent AFTER reading key
    agent = TavilyResearchAgent(api_key)

    # Now you can safely use agent in sidebar or main page
    with st.sidebar:
        st.markdown("---")
        st.markdown("**iNube Solutions:**")
        for service_id, service_desc in agent.iNube_services.items():
            st.markdown(f"- {service_id.replace('_', ' ').title()}: {service_desc}")
    # Main input section
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Company Information")
        company_name = st.text_input("Company Name", 
                                   placeholder="Enter insurance company name")
        company_url = st.text_input("Company Website URL", 
                                  placeholder="Enter company website URL")
        
        research_button = st.button("Analyze Client Potential", type="primary", disabled=not api_key)
    
    with col2:
        st.subheader("Analysis Focus")
        current_date = datetime.now().strftime("%Y-%m-%d")
        st.markdown(f"""
        This analysis will exclusively search for:
        
        **Timeframe**: May 1, 2025 - {current_date}
        
        **Focus Areas**:
        - Recent business challenges and pain points
        - Technology and operational gaps
        - Digital transformation struggles
        - Customer experience issues
        - Insurance-specific challenges
        
        **Output**: Client potential assessment with iNube solution alignment
        """)
        
        st.warning("Only sources from May 2025 to present will be considered")

    
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
        with st.spinner(f"Researching {company_name} for recent pain points (May 2025 - {current_date})... This may take 2-3 minutes."):
            research_data, detailed_results = agent.research_company(company_name, company_url)
            analysis = agent.analyze_company_fit(research_data)
        
        if analysis and research_data.get("research_points"):
            display_client_analysis(analysis, agent)
        else:
            st.error("Research failed or no recent data found. The company may not have publicly discussed challenges recently.")

def display_client_analysis(analysis: Dict, agent: TavilyResearchAgent):
    """Display focused client potential analysis"""
    
    st.markdown("---")
    
    # Client Potential Summary
    st.markdown(analysis['client_potential_summary'])
    
    st.markdown("---")
    
    # Final Recommendation
    st.subheader(" Final Recommendation")
    recommendation = analysis.get('recommendation', 'No recommendation available')
    if "STRONG" in recommendation:
        st.success(recommendation)
    elif "MODERATE" in recommendation:
        st.warning(recommendation)
    else:
        st.error(recommendation)
    
    # Recent Sources
    st.markdown("---")
    st.subheader(" Recent Sources Analyzed")
    
    recent_sources = analysis.get('recent_sources', [])
    if recent_sources:
        st.info(f"Analyzed {len(recent_sources)} sources from May 2025 to present")
        
        for i, source in enumerate(recent_sources):
            with st.expander(f"Source {i+1}: {source['title']}", expanded=i<2):
                st.markdown(f"**URL**: {source['url']}")
                st.markdown(f"**Content Preview**: {source['content']}")
                st.markdown("---")
    else:
        st.warning("No recent sources found from May 2025 to present")
    
    # Export functionality
    st.markdown("---")
    st.subheader("Export Results")
    
    export_data = []
    pain_points = analysis.get('validated_pain_points', [])
    
    for pp in pain_points:
        export_data.append({
            "Pain Point": pp["pain_point_name"],
            "Evidence": pp["evidence"],
            "Source_URL": pp["source_url"],
            "Source_Title": pp["source_title"],
            "iNube_Solutions": ", ".join([s.replace('_', ' ').title() for s in pp["iNube_solutions"]]),
            "Confidence": pp["confidence"]
        })
    
    if export_data:
        export_df = pd.DataFrame(export_data)
        csv_data = export_df.to_csv(index=False)
        
        st.download_button(
            label="Download Pain Points Analysis",
            data=csv_data,
            file_name=f"inube_client_analysis_{analysis['company_name'].lower().replace(' ', '_')}.csv",
            mime="text/csv",
            type="primary"
        )

if __name__ == "__main__":
    main()
