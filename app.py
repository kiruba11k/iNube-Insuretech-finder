import streamlit as st
import os
from tavily import TavilyClient
import pandas as pd
import json
from typing import Dict, List, Tuple
import time

# Page configuration
st.set_page_config(
    page_title="iNube Solutions Pain Point Research Agent",
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
        
        # Enhanced pain points mapping with specific keywords for better detection
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
    
    def research_company(self, company_name: str, company_url: str, include_may_2025: bool = False) -> Tuple[Dict, List[Dict]]:
        """Research company using Tavily Search API with focus on pain points"""
        
        # Base search queries
        base_queries = [
            f"{company_name} challenges problems issues difficulties",
            f"{company_name} digital transformation legacy systems modernization",
            f"{company_name} operational efficiency cost reduction manual processes",
            f"{company_name} customer experience policyholder satisfaction churn",
            f"{company_name} claims processing fraud detection technology gaps",
            f"{company_name} technology stack IT systems software platforms",
            f"{company_name} financial results operational performance investor presentation",
            f"{company_name} news updates recent developments technology initiatives"
        ]
        
        all_results = []
        analysis_data = {
            "company_name": company_name,
            "company_url": company_url,
            "sources": [],
            "research_points": [],
            "identified_pain_points": [],
            "may_2025_sources": []
        }
        
        # First, do general searches without date restriction
        for query in base_queries:
            try:
                response = self.client.search(
                    query=query,
                    search_depth="advanced",
                    max_results=3,  # Reduced to allow for May 2025 searches
                    include_answer=True
                )
                
                if response and 'results' in response:
                    for result in response['results']:
                        source_info = {
                            "title": result.get('title', ''),
                            "url": result.get('url', ''),
                            "content": result.get('content', ''),
                            "query": query,
                            "time_period": "General"
                        }
                        all_results.append(source_info)
                        
                        points = self._extract_key_points(result, query)
                        analysis_data["research_points"].extend(points)
                        
                        pain_points = self._extract_pain_points(result, query)
                        analysis_data["identified_pain_points"].extend(pain_points)
                
                time.sleep(1)
                        
            except Exception as e:
                st.error(f"Error in search query '{query}': {str(e)}")
                continue
        
        # Then, do May 2025 specific searches if requested
        if include_may_2025:
            may_2025_queries = [
                f"{company_name} challenges 2025",
                f"{company_name} technology issues 2025", 
                f"{company_name} digital transformation 2025",
                f"{company_name} operational efficiency 2025",
                f"{company_name} customer experience 2025",
                f"{company_name} insurance challenges 2025"
            ]
            
            for query in may_2025_queries:
                try:
                    response = self.client.search(
                        query=query,
                        search_depth="advanced",
                        max_results=3,
                        include_answer=True,
                        # Set date range for May 2025
                        start_date="2025-05-01",
                        end_date="2025-05-31"
                    )
                    
                    if response and 'results' in response:
                        for result in response['results']:
                            source_info = {
                                "title": result.get('title', ''),
                                "url": result.get('url', ''),
                                "content": result.get('content', ''),
                                "query": query,
                                "time_period": "May 2025"
                            }
                            all_results.append(source_info)
                            analysis_data["may_2025_sources"].append({
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
                    st.error(f"Error in May 2025 search query '{query}': {str(e)}")
                    continue
        
        if all_results:
            analysis_data["sources"] = [{"url": r["url"], "title": r["title"], "time_period": r.get("time_period", "General")} for r in all_results]
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
                            "confidence": "high" if len(context) > 100 else "medium",
                            "time_period": "May 2025" if "2025" in query else "General"
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
            "growth": ["growth", "expansion", "market", "customer", "revenue", "premium", "profit"],
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
                        "relevance": "medium",
                        "time_period": "May 2025" if "2025" in query else "General"
                    })
                    break
        
        return points
    
    def analyze_company_fit(self, research_data: Dict) -> Dict:
        """Analyze company fit for iNube Solutions with focus on pain points"""
        
        analysis = {
            "company_name": research_data["company_name"],
            "industry": "Unknown",
            "core_business": [],
            "technology_stack": [],
            "identified_challenges": [],
            "validated_pain_points": research_data.get("identified_pain_points", []),
            "digital_maturity": "unknown",
            "potential_iNube_services": [],
            "fit_justification": "",
            "recommendation": "",
            "confidence_score": 0,
            "sources": research_data.get("sources", []),
            "pain_point_analysis": "",
            "client_potential_summary": "",
            "may_2025_sources": research_data.get("may_2025_sources", [])
        }
        
        pain_point_count = len(analysis["validated_pain_points"])
        unique_pain_points = set([pp["pain_point_id"] for pp in analysis["validated_pain_points"]])
        
        tech_keywords = ["legacy", "modernization", "digital", "automation", "AI", "cloud", "technology", "software"]
        challenge_keywords = ["cost", "efficiency", "manual", "slow", "integration", "compliance", "challenge", "problem"]
        insurance_keywords = ["policy", "claim", "underwriting", "premium", "insurance", "risk", "coverage"]
        
        tech_count = 0
        challenge_count = 0
        insurance_count = 0
        
        for point in research_data.get("research_points", []):
            point_text = point["point"].lower()
            
            if any(keyword in point_text for keyword in insurance_keywords):
                insurance_count += 1
                analysis["industry"] = "Insurance"
            
            if any(keyword in point_text for keyword in tech_keywords):
                tech_count += 1
                if point["point"] not in analysis["technology_stack"]:
                    analysis["technology_stack"].append(point["point"])
            
            if any(keyword in point_text for keyword in challenge_keywords):
                challenge_count += 1
                if point["point"] not in analysis["identified_challenges"]:
                    analysis["identified_challenges"].append(point["point"])
        
        if tech_count > 5:
            analysis["digital_maturity"] = "high"
        elif tech_count > 2:
            analysis["digital_maturity"] = "medium"
        else:
            analysis["digital_maturity"] = "low"
        
        all_recommended_services = []
        for pain_point in analysis["validated_pain_points"]:
            all_recommended_services.extend(pain_point["iNube_solutions"])
        
        analysis["potential_iNube_services"] = list(set(all_recommended_services))[:6]
        
        if not analysis["potential_iNube_services"] and (challenge_count > 0 or tech_count < 3):
            analysis["potential_iNube_services"] = list(self.iNube_services.keys())[:3]
        
        pain_point_score = min(50, pain_point_count * 15)
        tech_score = min(25, tech_count * 5)
        challenge_score = min(25, challenge_count * 5)
        
        analysis["confidence_score"] = min(100, pain_point_score + tech_score + challenge_score)
        
        analysis["pain_point_analysis"] = self._generate_pain_point_analysis(analysis)
        analysis["client_potential_summary"] = self._generate_client_potential_summary(analysis)
        analysis["fit_justification"] = self._generate_justification(analysis, research_data)
        analysis["recommendation"] = self._generate_recommendation(analysis)
        
        return analysis
    
    def _generate_client_potential_summary(self, analysis: Dict) -> str:
        """Generate comprehensive client potential summary based on pain points"""
        pain_points = analysis.get("validated_pain_points", [])
        
        if not pain_points:
            return "Limited client potential identified. No validated pain points with source evidence found."
        
        # Group pain points by category and time period
        pain_point_groups = {}
        may_2025_count = 0
        
        for pp in pain_points:
            if pp["pain_point_id"] not in pain_point_groups:
                pain_point_groups[pp["pain_point_id"]] = []
            pain_point_groups[pp["pain_point_id"]].append(pp)
            
            if pp.get("time_period") == "May 2025":
                may_2025_count += 1
        
        summary_parts = []
        summary_parts.append(f"Based on our research, {analysis['company_name']} demonstrates strong client potential for iNube Solutions due to validated business challenges across {len(pain_point_groups)} key areas.")
        
        # Highlight May 2025 findings if available
        if may_2025_count > 0:
            summary_parts.append(f" Found {may_2025_count} recent pain point evidence sources from May 2025.")
        
        # Add pain point specific summaries
        for pain_point_id, evidences in pain_point_groups.items():
            pain_point_name = pain_point_id.replace('_', ' ').title()
            source_count = len(evidences)
            may_2025_sources = [ev for ev in evidences if ev.get('time_period') == 'May 2025']
            recent_indicator = " (Recent)" if may_2025_sources else ""
            
            sources_links = ", ".join([f"[Source {i+1}]({ev['source_url']})" for i, ev in enumerate(evidences[:2])])
            
            summary_parts.append(f"\n- **{pain_point_name}**: {source_count} validated evidence sources{recent_indicator} ({sources_links})")
        
        # Add iNube solutions match
        if analysis["potential_iNube_services"]:
            solutions = [s.replace('_', ' ').title() for s in analysis["potential_iNube_services"]]
            summary_parts.append(f"\nThese pain points can be directly addressed by iNube's {', '.join(solutions[:3])} solutions.")
        
        # Add approach recommendation
        if pain_point_groups:
            primary_pain_point = list(pain_point_groups.keys())[0]
            summary_parts.append(f"\nRecommended approach: Focus on {primary_pain_point.replace('_', ' ')} challenges with evidence-based proposals using the source URLs provided.")
        
        return "".join(summary_parts)
    
    def _generate_pain_point_analysis(self, analysis: Dict) -> str:
        """Generate detailed pain point analysis"""
        if not analysis["validated_pain_points"]:
            return "No specific pain points identified with supporting evidence."
        
        pain_point_groups = {}
        may_2025_count = 0
        
        for pp in analysis["validated_pain_points"]:
            if pp["pain_point_id"] not in pain_point_groups:
                pain_point_groups[pp["pain_point_id"]] = []
            pain_point_groups[pp["pain_point_id"]].append(pp)
            
            if pp.get("time_period") == "May 2025":
                may_2025_count += 1
        
        analysis_parts = []
        for pain_point_id, evidences in pain_point_groups.items():
            may_sources = len([ev for ev in evidences if ev.get('time_period') == 'May 2025'])
            recent_indicator = f" ({may_sources} recent)" if may_sources > 0 else ""
            analysis_parts.append(f"{pain_point_id.replace('_', ' ').title()}: {len(evidences)} sources{recent_indicator}")
        
        if may_2025_count > 0:
            analysis_parts.append(f"| May 2025 sources: {may_2025_count}")
            
        return " | ".join(analysis_parts)
    
    def _generate_justification(self, analysis: Dict, research_data: Dict) -> str:
        """Generate justification for iNube fit with pain point focus"""
        
        justification_parts = []
        
        if analysis["industry"] == "Insurance":
            justification_parts.append("Company operates in insurance sector, which aligns with iNube's specialization.")
        
        pain_point_count = len(analysis["validated_pain_points"])
        if pain_point_count > 0:
            may_2025_count = len([pp for pp in analysis["validated_pain_points"] if pp.get('time_period') == 'May 2025'])
            if may_2025_count > 0:
                justification_parts.append(f"Found {pain_point_count} validated pain points ({may_2025_count} from May 2025) with source evidence.")
            else:
                justification_parts.append(f"Found {pain_point_count} validated pain points with source evidence.")
        
        if analysis["digital_maturity"] in ["low", "medium"]:
            justification_parts.append(f"Digital maturity level ({analysis['digital_maturity']}) indicates technology gaps.")
        
        if analysis["potential_iNube_services"]:
            services_str = ", ".join([s.replace('_', ' ').title() for s in analysis["potential_iNube_services"]])
            justification_parts.append(f"iNube can address with: {services_str}")
        
        return " ".join(justification_parts) if justification_parts else "Limited evidence of specific pain points found."

    def _generate_recommendation(self, analysis: Dict) -> str:
        """Generate recommendation based on analysis with pain point focus"""
        
        confidence = analysis["confidence_score"]
        pain_point_count = len(analysis["validated_pain_points"])
        may_2025_count = len([pp for pp in analysis["validated_pain_points"] if pp.get('time_period') == 'May 2025'])

        if confidence >= 70 and pain_point_count >= 2:
            if may_2025_count > 0:
                return "STRONG RECOMMENDATION - Multiple validated pain points found with recent May 2025 source evidence"
            else:
                return "STRONG RECOMMENDATION - Multiple validated pain points found with source evidence"
        elif confidence >= 50 and pain_point_count >= 1:
            if may_2025_count > 0:
                return "MODERATE RECOMMENDATION - Validated pain points identified with recent May 2025 source URLs"
            else:
                return "MODERATE RECOMMENDATION - Validated pain points identified with source URLs"
        elif confidence >= 30:
            return "WEAK RECOMMENDATION - Some challenges identified but limited pain point evidence"
        else:
            return "INSUFFICIENT EVIDENCE - No validated pain points with source proof found"

def main():
    st.title("iNube Solutions Pain Point Research Agent")
    st.markdown("Validate company pain points with source URL evidence for targeted client approach")
    
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
        
        # Date filtering option
        st.subheader("Date Filtering")
        include_may_2025 = st.checkbox(
            "Include May 2025 specific sources", 
            value=True,
            help="Search for pain point evidence from May 1-31, 2025 timeframe using Tavily date range filtering"
        )
        
        st.markdown("How to use:")
        st.markdown("1. Ensure Tavily API key is set")
        st.markdown("2. Input target company details")
        st.markdown("3. Enable May 2025 filtering for recent evidence")
        st.markdown("4. Click Research Company")
        st.markdown("5. Review validated pain points with source URLs")
        st.markdown("6. Use evidence for client approach")
        
        st.markdown("---")
        st.markdown("Pain Points We Detect:")
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
        st.subheader("Target Company Information")
        company_name = st.text_input("Company Name", 
                                   value="SHRIRAM GENERAL INSURANCE CO. LTD.",
                                   placeholder="Enter company name")
        company_url = st.text_input("Company Website URL", 
                                  value="https://www.shriramgi.com",
                                  placeholder="Enter company website URL")
        
        research_button = st.button("Research Pain Points", type="primary", disabled=not api_key)
    
    with col2:
        st.subheader("Research Focus")
        st.markdown("""
        The agent will specifically search for:
        - Validated pain points with source URLs as proof
        - Operational challenges and technology gaps  
        - Digital transformation initiatives and struggles
        - Customer experience issues and retention challenges
        - Evidence-based insights for client approach
        """)
        
        if include_may_2025:
            st.success("May 2025 filtering enabled - Using Tavily date range: 2025-05-01 to 2025-05-31")
        else:
            st.info("Enable May 2025 filtering to get the most recent pain point evidence")
    
    if not api_key:
        st.error("Please provide a Tavily API key to begin research")
        return
    
    try:
        agent = TavilyResearchAgent(api_key)
    except Exception as e:
        st.error(f"Failed to initialize Tavily client: {str(e)}")
        return
    
    if research_button and company_name:
        with st.spinner(f"Researching {company_name} for validated pain points with source evidence... This may take 2-3 minutes."):
            research_data, detailed_results = agent.research_company(
                company_name, 
                company_url, 
                include_may_2025=include_may_2025
            )
            analysis = agent.analyze_company_fit(research_data)
        
        if analysis and research_data.get("research_points"):
            display_pain_point_analysis(analysis, detailed_results, agent, include_may_2025)
        else:
            st.error("Research failed or no data found. Please check the company name and try again.")

def display_pain_point_analysis(analysis: Dict, detailed_results: List[Dict], agent: TavilyResearchAgent, include_may_2025: bool = False):
    """Display comprehensive analysis with focus on pain points and source evidence"""
    
    st.markdown("---")
    st.header(f"Pain Point Analysis Report: {analysis['company_name']}")
    
    # Key metrics with pain point focus
    st.subheader("Executive Summary")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Industry", analysis.get('industry', 'Unknown'))
    with col2:
        st.metric("Validated Pain Points", len(analysis.get('validated_pain_points', [])))
    with col3:
        st.metric("Confidence Score", f"{analysis.get('confidence_score', 0)}%")
    with col4:
        services_count = len(analysis.get('potential_iNube_services', []))
        st.metric("Recommended Solutions", services_count)
    
    # May 2025 Sources Section
    if include_may_2025 and analysis.get('may_2025_sources'):
        st.markdown("---")
        st.header("May 2025 Specific Sources")
        
        st.success(f"Found {len(analysis['may_2025_sources'])} sources from May 2025 timeframe (2025-05-01 to 2025-05-31)")
        
        for i, source in enumerate(analysis['may_2025_sources']):
            with st.expander(f"May 2025 Source {i+1}: {source['title']}", expanded=i==0):
                st.markdown(f"**URL**: {source['url']}")
                st.markdown(f"**Search Query**: {source['query']}")
                st.markdown(f"**Content Preview**: {source['content']}")
                st.markdown("---")
    
    # Client Potential Summary Section
    st.markdown("---")
    st.header("Client Potential Assessment")
    
    if analysis.get('client_potential_summary'):
        st.info(analysis['client_potential_summary'])
    else:
        st.warning("No client potential assessment available.")
    
    # Pain Points Section - Separate May 2025 and general sources
    st.markdown("---")
    st.header("Validated Pain Points with Source Evidence")
    
    pain_points = analysis.get('validated_pain_points', [])
    
    if not pain_points:
        st.warning("No validated pain points found with source evidence.")
    else:
        # Separate May 2025 pain points
        may_2025_pain_points = [pp for pp in pain_points if pp.get('time_period') == 'May 2025']
        general_pain_points = [pp for pp in pain_points if pp.get('time_period') != 'May 2025']
        
        # Display May 2025 pain points first
        if may_2025_pain_points:
            st.subheader("Recent Pain Points (May 2025)")
            st.info(f"Found {len(may_2025_pain_points)} pain point evidence sources from May 2025")
            
            for pain_point in may_2025_pain_points:
                with st.expander(f"RECENT: {pain_point['pain_point_name']} - May 2025 Evidence", expanded=True):
                    if pain_point["iNube_solutions"]:
                        solutions = [s.replace('_', ' ').title() for s in pain_point["iNube_solutions"]]
                        st.success(f"iNube Solutions: {', '.join(solutions)}")
                    
                    st.markdown(f"**Source**: [{pain_point['source_title']}]({pain_point['source_url']})")
                    st.markdown(f"**Evidence**: {pain_point['evidence']}")
                    st.markdown(f"**Keyword Identified**: `{pain_point['keyword_found']}`")
                    st.markdown(f"**Time Period**: {pain_point['time_period']}")
                    st.markdown(f"**Confidence**: {pain_point['confidence'].title()}")
                    st.markdown("---")
        
        # Display general pain points
        if general_pain_points:
            pain_point_groups = {}
            for pp in general_pain_points:
                if pp["pain_point_id"] not in pain_point_groups:
                    pain_point_groups[pp["pain_point_id"]] = []
                pain_point_groups[pp["pain_point_id"]].append(pp)
            
            for pain_point_id, evidences in pain_point_groups.items():
                with st.expander(f"{pain_point_id.replace('_', ' ').title()} - {len(evidences)} evidence source(s)", expanded=len(may_2025_pain_points)==0):
                    
                    if evidences[0]["iNube_solutions"]:
                        solutions = [s.replace('_', ' ').title() for s in evidences[0]["iNube_solutions"]]
                        st.success(f"iNube Solutions: {', '.join(solutions)}")
                    
                    for i, evidence in enumerate(evidences):
                        st.markdown(f"**Evidence #{i+1}**")
                        st.markdown(f"Source: [{evidence['source_title']}]({evidence['source_url']})")
                        st.markdown(f"**Context**: {evidence['evidence']}")
                        st.markdown(f"Keyword identified: {evidence['keyword_found']}")
                        st.markdown("---")

    # Rest of the display functions remain the same...
    if detailed_results:
        st.markdown("---")
        st.subheader("Detailed Research Findings")
        
        research_table_data = []
        for result in detailed_results:
            research_table_data.append({
                "Source Title": result.get('title', 'N/A'),
                "URL": result.get('url', 'N/A'),
                "Time Period": result.get('time_period', 'General'),
                "Key Content": result.get('content', '')[:200] + "..." if len(result.get('content', '')) > 200 else result.get('content', 'N/A'),
                "Search Query": result.get('query', 'N/A')
            })
        
        research_df = pd.DataFrame(research_table_data)
        st.dataframe(research_df, use_container_width=True)
    
    # Justification and Recommendation
    st.markdown("---")
    st.subheader("Analysis Justification & Recommendation")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("**Justification:**")
        st.info(analysis.get('fit_justification', 'No justification available'))
        
        if analysis.get('pain_point_analysis'):
            st.markdown("**Pain Point Analysis:**")
            st.info(analysis['pain_point_analysis'])
    
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
    st.markdown("---")
    st.subheader("Research Sources")
    sources = analysis.get('sources', [])
    if sources:
        # Separate May 2025 and general sources
        may_sources = [s for s in sources if s.get('time_period') == 'May 2025']
        general_sources = [s for s in sources if s.get('time_period') != 'May 2025']
        
        if may_sources:
            st.markdown("**May 2025 Sources:**")
            for i, source in enumerate(may_sources):
                st.markdown(f"{i+1}. {source.get('title', 'No title')} - {source.get('url', 'No URL')}")
        
        if general_sources:
            st.markdown("**General Sources:**")
            for i, source in enumerate(general_sources, start=len(may_sources)+1):
                st.markdown(f"{i}. {source.get('title', 'No title')} - {source.get('url', 'No URL')}")
    else:
        st.info("No sources available")
    
    # Export functionality
    st.markdown("---")
    st.subheader("Export Results")
    
    export_data = []
    
    for pp in pain_points:
        export_data.append({
            "Type": "Pain Point",
            "Category": pp["pain_point_name"],
            "Evidence": pp["evidence"],
            "Source_URL": pp["source_url"],
            "Source_Title": pp["source_title"],
            "Time_Period": pp.get("time_period", "General"),
            "iNube_Solutions": ", ".join([s.replace('_', ' ').title() for s in pp["iNube_solutions"]]),
            "Confidence": pp["confidence"]
        })
    
    export_data.append({
        "Type": "Company Analysis",
        "Category": "Overall Recommendation",
        "Evidence": analysis.get('recommendation', ''),
        "Source_URL": analysis.get('company_url', ''),
        "Source_Title": "Analysis Summary",
        "Time_Period": "Analysis",
        "iNube_Solutions": ", ".join([s.replace('_', ' ').title() for s in analysis.get('potential_iNube_services', [])]),
        "Confidence": f"{analysis.get('confidence_score', 0)}%"
    })
    
    if export_data:
        export_df = pd.DataFrame(export_data)
        csv_data = export_df.to_csv(index=False)
        
        st.download_button(
            label="Download Pain Points Analysis CSV",
            data=csv_data,
            file_name=f"inube_pain_points_{analysis['company_name'].lower().replace(' ', '_')}.csv",
            mime="text/csv",
            type="primary"
        )

if __name__ == "__main__":
    main()
