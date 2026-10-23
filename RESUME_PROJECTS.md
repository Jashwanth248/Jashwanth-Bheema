# Resume-Ready Project Portfolio

These project summaries are designed for resumes, LinkedIn, recruiter review, and technical interviews. Each entry distinguishes implemented features from documented production architecture.

---

## LLM Auditor Platform

**Advanced AI, Data Engineering, and Analytics Platform**

- **Developed a Multi-Agent Verification System:** Built a Google ADK-based orchestration workflow that routes claims to general and geospatial auditing agents, combining grounded evidence with deterministic Haversine calculations instead of relying entirely on LLM-generated answers.
- **Engineered Structured AI Outputs:** Designed FastAPI and Pydantic contracts that return an accuracy verdict, supporting evidence, corrected values, confidence score, risk score, and processing latency in a consistent machine-readable format.
- **Built an Auditable Data Pipeline:** Added event schemas, data-quality gates, SQLite persistence, BigQuery-ready SQL, KPI calculations, and a golden-dataset regression evaluator for measuring accuracy, risk, evidence depth, and latency.
- **Implemented Production Engineering Practices:** Added automated tests, Docker, GitHub Actions, structured logging, Terraform, and a documented Google Cloud architecture using Cloud Run, Pub/Sub, Cloud Storage, BigQuery, Cloud Build, and Vertex AI.
- **Expected Output:** A user submits an AI-generated factual or distance claim and receives a structured verdict such as Accurate or Inaccurate, confidence and risk scores, deterministic corrections when applicable, cited evidence, and an analytics event available for reporting.
- **Technologies:** Python, Google ADK, Gemini, Vertex AI, FastAPI, Pydantic, SQLite, BigQuery SQL, Streamlit, Docker, Terraform, GitHub Actions, Google Cloud.
- **Repository:** [github.com/Jashwanth248/AI_Agets-](https://github.com/Jashwanth248/AI_Agets-)

---

## Airline Operations Command Center

**Real-Time Data Engineering and Business Intelligence System**

- **Designed an End-to-End Analytics Pipeline:** Built Python ingestion and simulation workflows for continuously arriving flight-operation events, including schema validation, business-rule checks, and reproducible event generation.
- **Created an Analytical Warehouse:** Modeled event-grain data in DuckDB and developed SQL/dbt staging layers, tested analytical marts, data contracts, documentation, and reusable operational KPI definitions.
- **Developed an Interactive Operations Dashboard:** Built Streamlit and Plotly views for on-time performance, cancellations, severe delays, route reliability, airport disruption, delay causes, and pipeline freshness.
- **Added Production-Ready Engineering:** Implemented Pytest quality checks, GitHub Actions, Docker, BI-ready CSV/Excel exports, a near-real-time simulator, and a documented cloud mapping using Pub/Sub, Dataflow, BigQuery, and dbt/Dataform.
- **Expected Output:** A decision-ready dashboard and curated analytical tables showing network performance, delay hot spots, unreliable routes, cancellation trends, airport disruption scores, and validated pipeline-health indicators.
- **Technologies:** Python, SQL, pandas, DuckDB, dbt, Streamlit, Plotly, Pytest, Docker, GitHub Actions, Pub/Sub, Dataflow, BigQuery.
- **Repository:** [github.com/Jashwanth248/Data-Analyst-](https://github.com/Jashwanth248/Data-Analyst-)

---

## DocuMind Multimodal RAG

**Source-Aware Multimodal Knowledge Assistant**

- **Developed a Multiformat Ingestion System:** Built workflows that ingest PDFs, Word documents, presentations, spreadsheets, text, code, images, audio, and video through format-aware parsers and Gemini multimodal processing.
- **Implemented Persistent Retrieval:** Created normalized content units, semantic chunking, Gemini embeddings, and a persistent ChromaDB index that supports incremental ingestion without rebuilding the complete knowledge base.
- **Built Grounded Question Answering:** Developed a retrieval-augmented generation pipeline that constrains answers to retrieved content and displays the source files and locations supporting each response.
- **Separated Application Layers:** Implemented FastAPI ingestion and question-answering endpoints, a Streamlit chat and upload interface, watched-folder indexing, automated tests, Docker, and GitHub Actions.
- **Expected Output:** Users upload a mixed collection of documents and media, ask natural-language questions, and receive grounded answers with visible supporting sources while the indexed knowledge remains available after application restarts.
- **Technologies:** Python, Gemini, Google GenAI SDK, FastAPI, Streamlit, ChromaDB, PyMuPDF, python-docx, python-pptx, OpenPyXL, BeautifulSoup, Watchdog, Pytest, Docker, GitHub Actions.
- **Repository:** [github.com/Jashwanth248/DocuMind](https://github.com/Jashwanth248/DocuMind)

---

## Production AI and Data Portfolio

**Five Reproducible Enterprise-Style Data and AI Projects**

- **Built Data Quality at Scale:** Developed configurable batch validation and remediation workflows using Python, SQL patterns, data contracts, idempotent processing, audit trails, and operational observability.
- **Created an AI Data Quality Investigator:** Implemented an evidence-first agent that retrieves supporting information, applies guardrails, records reasoning artifacts, and produces traceable recommendations.
- **Developed ML Anomaly Monitoring:** Engineered features, anomaly scoring, evaluation, thresholding, and drift-monitoring workflows to identify changing data behavior and model risk.
- **Implemented Data Sentinel and Prompt Playground:** Built confidence-aware multi-agent intake with semantic schema retrieval, policy validation, anomaly detection, and human review, plus an LLM evaluation platform with prompt versioning, regression checks, FastAPI, dashboards, Docker, and CI.
- **Expected Output:** Reproducible data-quality reports, evidence-backed investigation results, anomaly and drift alerts, confidence-based human-review decisions, and regression reports comparing LLM releases.
- **Technologies:** Python, SQL, FastAPI, machine learning, agent workflows, semantic retrieval, data contracts, anomaly detection, prompt evaluation, Docker, CI/CD, automated testing.
- **Repository:** [github.com/Jashwanth248/Jashwanth-Bheema](https://github.com/Jashwanth248/Jashwanth-Bheema)

---

## PulseCart DevOps/SRE Platform

**Production-Style Kubernetes and GitOps Platform**

- **Designed a Multi-Service Platform:** Created gateway, order-processing, and worker services backed by PostgreSQL and Redis, with reusable Helm packaging and separate staging and production configurations.
- **Implemented GitOps and Progressive Delivery:** Built CI validation, immutable container workflows, Argo CD synchronization, and Argo Rollouts canary releases with metric-based promotion or rollback.
- **Engineered Reliability and Observability:** Added health probes, resource limits, horizontal scaling, PodDisruptionBudgets, SLOs, Prometheus alerts, OpenTelemetry pipelines, Grafana-ready dashboards, runbooks, and failure drills.
- **Hardened Platform Security:** Applied non-root containers, read-only filesystems, dropped Linux capabilities, NetworkPolicies, Kyverno policies, vulnerability scanning, least-privilege service accounts, and short-lived cloud identity patterns.
- **Expected Output:** A locally runnable commerce system and a production-style deployment design in which Git changes drive controlled Kubernetes releases, telemetry supports SLO monitoring, and failed canaries can be stopped or rolled back.
- **Technologies:** Kubernetes, GKE, Docker, Terraform, Helm, Argo CD, Argo Rollouts, GitHub Actions, PostgreSQL, Redis, OpenTelemetry, Prometheus, Grafana, Kyverno.
- **Repository:** [github.com/Jashwanth248/Devops-](https://github.com/Jashwanth248/Devops-)

---

## Road Friend Personal AI Companion

**Privacy-Oriented Local Voice and Text Assistant**

- **Built a Local-First AI Assistant:** Developed a FastAPI application that supports voice and text interaction, key-free public web research, and natural summarization through optional local Ollama models or Gemini.
- **Implemented Location-Aware Research:** Added permission-based location access, OpenStreetMap/Overpass nearby-place discovery, distance calculation, and optional Google Places and traffic-aware routing.
- **Designed Permission-Based Tool Use:** Required confirmation before browser actions, email or message sending, and private-file access; limited file access to content explicitly selected by the user.
- **Integrated Personal Productivity Features:** Added support for local document reading, Gmail connectivity, nearby-place recommendations, and approved launching of Google Search, Google Maps, YouTube, and Prime Video.
- **Expected Output:** A user speaks or types a request and receives a conversational, evidence-aware response; location and private data are used only with permission, and external actions occur only after confirmation.
- **Technologies:** Python, FastAPI, Ollama, Gemini, OpenStreetMap, Overpass API, Google Maps APIs, browser APIs, speech interfaces, OAuth, Pytest.
- **Repository:** [github.com/Jashwanth248/Road_Friend](https://github.com/Jashwanth248/Road_Friend)

---

## District 8 Maintenance GIS Data Workbench

**Geospatial Data Integration, Quality, and Stewardship Application**

- **Built a Maintenance Data Intake Workflow:** Created a browser-based workbench that loads synthetic IMMS-style CSV data or a local user-selected extract and checks required fields, duplicate work-order IDs, activity/status domains, route formats, coordinates, dates, and acreage values.
- **Implemented Spatial Quality Review:** Added quality-coded map markers, a review extent check, a record queue, and row-level findings so a steward can inspect and correct issues before GIS publication.
- **Prepared Governed GIS Outputs:** Added an editable dataset metadata profile, clean WGS 84 GeoJSON export for rows that pass all checks, annotated CSV review output, and a machine-readable QA report.
- **Kept the Workflow Reproducible:** Built the validation and export logic as dependency-free JavaScript modules with Node.js automated tests and documented schema, data dictionary, quality rules, and production adaptation considerations.
- **Expected Output:** A steward loads a maintenance extract and receives a quality summary, mapped records, actionable data issues, and clearly classified GIS-ready output.
- **Technologies:** JavaScript ES modules, HTML, CSS, Leaflet, CSV, GeoJSON, WGS 84 / CRS84, Node.js test runner.
- **Repository:** [District 8 Maintenance GIS Data Workbench](https://github.com/Jashwanth248/Jashwanth-Bheema/tree/main/06-district-8-maintenance-gis-workbench)

---

## Recommended Resume Selection

A two-page resume should normally include only three projects:

1. **LLM Auditor Platform** for AI/ML Engineer, Data Scientist, and Applied AI roles.
2. **Airline Operations Command Center** for Data Analyst and Data Engineer roles.
3. **DocuMind Multimodal RAG** for AI/ML Engineer and Software Developer roles.

Use **PulseCart** instead of DocuMind when applying for DevOps, Cloud, Platform, or SRE positions. Use **Road Friend** for full-stack, AI application, or agentic-software positions. For GIS Coordinator or geospatial data stewardship roles, prioritize the **District 8 Maintenance GIS Data Workbench** and pair it with the project most relevant to the position's analytics or application duties.
