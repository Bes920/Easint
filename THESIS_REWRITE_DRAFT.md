# EASINT: An AI-Enhanced Open-Source Intelligence Platform With Real-Time Threat Analysis

## Preliminary Pages

### Title Page
THE ICT UNIVERSITY  
Faculty of Information and Communication Technology  

A thesis presented and submitted in partial fulfillment of the requirement for the degree of a Bachelor of Science in Cybersecurity  

**EASINT: AN AI-ENHANCED OPEN-SOURCE INTELLIGENCE PLATFORM WITH REAL-TIME THREAT ANALYSIS**

By  
TANYI BESONG BRYAN MAURICE  
Matricule: ICTU20234375  
Email: tanyibesong.bryanmauirce@ictuniversity.edu.cm  
Supervised by: Engr. Moune  
July 2026

### Declaration
I declare that the work entitled "EASINT: An AI-Enhanced Open-Source Intelligence Platform With Real-Time Threat Analysis" is my own original work, conceived and presented in partial fulfillment of the requirement for the degree of a Bachelor of Science in Cybersecurity at ICT University. This work has not been submitted for any degree or examination in any other university, and all sources used or quoted have been indicated and acknowledged in the references.

### Certification
This work entitled "EASINT: An AI-Enhanced Open-Source Intelligence Platform With Real-Time Threat Analysis" has been submitted for examination with my approval as the Research Supervisor.

### Dedication
To my beloved parents, whose sacrifices, love, and encouragement sustained this journey.  
To my teachers at ICT University, whose guidance and commitment to excellence shaped my academic development.

### Acknowledgments
I am sincerely grateful to my supervisor, Engr. Moune, for guidance, correction, and encouragement throughout this project. I also acknowledge the lecturers and staff of the ICT University Faculty of Information and Communication Technology for the academic foundation that made this work possible. Special appreciation goes to my internship supervisor, Engr. Njilla Donald, for practical mentorship and exposure to real-world cybersecurity work. I further thank my classmates and the open-source community whose tools and documentation supported the development of Easint.

### Abstract
This dissertation presents Easint, an AI-enhanced Open-Source Intelligence (OSINT) platform designed to centralize several intelligence-gathering workflows within a unified web application. The implementation in the repository is a Flask-based system that provides OSINT capabilities for IP reputation checking, file hash analysis, file metadata extraction, Google dork generation, Shodan search, reverse IP lookup, comprehensive email OSINT, Wayback Machine checking, cryptocurrency tracking, MAC address lookup, WHOIS lookup, email breach checking, username search, subdomain enumeration, DNS lookup, SSL certificate inspection, IP geolocation, and phone number lookup.

The platform persists investigation records and tool outputs in Supabase-backed tables through a service layer, and it provides a dashboard for investigation management, filtering, result review, and status updates. The system also includes AI-powered analysis through Gemini and Mistral-backed services, including conversational chat about an investigation and automated investigation summary generation. A D3.js-based network graph visualizes entity relationships extracted from investigation results.

The project demonstrates how a modular Flask application can combine multiple OSINT functions, automated saving of results, and AI-assisted interpretation into a practical investigation workspace. The dissertation also documents the limits of the implementation, including the absence of a full authentication stack, the lack of persisted graph tables, and the fact that several originally claimed thesis features are not present in the current codebase.

Keywords: OSINT, Open-Source Intelligence, Artificial Intelligence, Flask, Supabase, Threat Analysis, Network Visualization, D3.js, Cybersecurity

## Table of Contents
Preliminary Pages  
Chapter 1: Introduction  
Chapter 2: Literature Review  
Chapter 3: Methodology  
Chapter 4: Analysis, Design, Implementation, and Findings  
Chapter 5: Summary, Conclusions, Discussion, and Recommendations  
References  
Annexes

## Chapter 1: Introduction

### 1.1 Background to the Problem
The modern cybersecurity environment is characterized by an expanding attack surface, faster incident cycles, and a constant flow of public digital traces that can be used for reconnaissance and analysis. Security professionals frequently rely on Open-Source Intelligence, or OSINT, to examine publicly available information such as IP reputation data, breach exposure records, domain registration data, DNS records, usernames, file hashes, and other digital artifacts. When handled systematically, OSINT supports incident response, threat analysis, attribution work, and pre-engagement reconnaissance.

Despite the value of OSINT, many investigations still require analysts to move between separate tools and manually correlate outputs that are presented in different formats. This creates delays and increases the chance of missing relationships between entities such as domains, IP addresses, email addresses, usernames, and infrastructure indicators. The need for a single environment that can collect, organize, and interpret these findings remains practical and relevant.

Artificial intelligence now adds another useful layer to OSINT workflows. Large language models can summarize results, explain relationships, and help analysts interpret complex output more quickly. In the Easint repository, this capability is implemented through AI services that support investigation chat and auto-analysis. The platform therefore aims to reduce manual consolidation effort while preserving the analyst's ability to review the underlying source data.

### 1.2 Problem Statement
The main problem addressed by this project is the fragmentation of OSINT workflows. Analysts often use separate tools for IP checks, DNS analysis, WHOIS lookups, breach checking, file inspection, and social or platform enumeration. These tools work independently and produce data that must be manually assembled into a coherent investigation.

This fragmented workflow is inefficient, especially when investigations involve several indicators that need to be compared quickly. It also makes it harder to preserve investigation context over time, track results, and review what has already been tested. Although commercial platforms exist, they are often expensive or overly complex for individual researchers and small teams.

Easint addresses this problem by implementing a unified Flask application that exposes multiple OSINT functions, stores results in Supabase, provides an investigation dashboard, and adds AI-assisted interpretation and visualization. The current codebase supports a practical prototype of that workflow, but it does not implement the full authentication and database isolation architecture described in the original thesis draft.

### 1.3 Objectives

#### 1.3.1 General Objective
The general objective of this study is to design and develop a modular AI-enhanced OSINT platform that centralizes multiple investigation capabilities in a single web-based environment for cybersecurity analysis.

#### 1.3.2 Specific Objectives
The specific objectives of Easint are:
- To implement a Flask-based OSINT platform that provides multiple investigation tools from a single interface.
- To persist investigation records and tool outputs in a Supabase-backed data store.
- To provide an investigation dashboard for viewing, filtering, updating, and deleting investigations.
- To integrate AI services for conversational analysis and investigation summaries.
- To generate a graph-based visual representation of relationships found in investigation results.
- To support automated result saving and export-oriented workflows.

### 1.4 Research Questions
This study is guided by the following research questions:
- How can several heterogeneous OSINT capabilities be combined into a single modular application?
- How can investigation results be stored and retrieved in a way that preserves context across sessions?
- How can AI assistance improve the interpretation of OSINT results in a practical investigation workflow?
- How can entity extraction and graph visualization improve relationship analysis across investigation results?

### 1.5 Scope of Research
The scope of this research covers the Easint repository as implemented in the current codebase. The system includes a Flask application, Supabase-backed persistence, investigation management routes, AI routes, a dashboard interface, and several OSINT tool endpoints for network, email, domain, identity, and file-related analysis.

The study focuses on implemented features only. It does not assume the presence of a complete login and registration system, server-side authentication middleware, or persistent graph storage tables, because these are not present in the repository. It also does not claim support for tools or integrations that are described in the original thesis draft but absent from the code.

### 1.6 Significance of the Study
This project is significant for three reasons.

First, it demonstrates how a small-to-medium Flask application can be structured as a modular OSINT workspace with service-based persistence and analysis layers.

Second, it shows how AI can be integrated into OSINT workflows in a way that supports both direct questioning and automated investigation summaries.

Third, it provides a practical prototype that can be extended by future researchers who want to add authentication, stronger access control, richer graph persistence, or additional intelligence sources.

### 1.7 Limitations of the Study
The current implementation has several limitations.

- It does not implement the full Supabase Auth workflow described in the original thesis draft.
- It does not include the `require_auth` middleware claimed in the thesis.
- It does not persist network graph nodes and edges in dedicated tables.
- Several tools described in the thesis draft are not present in the repository, while several implemented tools are not described in the draft.
- The availability and quality of external OSINT results depend on third-party APIs and environment variables.

### 1.8 Organization of the Study
This dissertation is organized into five chapters. Chapter 1 introduces the problem, objectives, scope, significance, and limitations. Chapter 2 reviews relevant literature on OSINT, AI-assisted analysis, threat intelligence, and graph visualization. Chapter 3 describes the methodology and implementation approach. Chapter 4 presents the system analysis, design, implementation, and findings. Chapter 5 summarizes the work, states the conclusions, and provides recommendations for future improvement.

