# CEO Brain — 10 AI Modules (TO-BE)

Source-of-truth overview of modules, descriptions, effects, user stories and deadlines.

| # | Module | Description | Effect | Deadline |
|---|--------|-------------|--------|----------|
| 1 | AI Memory | Collects and links context on funds, companies, people, meetings, threads and documents into a single memory. Delivers instant brief with history of touches, related materials, current stage, last touch, probable next step and warm intro paths. | Improved decision quality | 2026-04-29 |
| 2 | Performance | Turns goals into a managed progress-control system. Links goals to fund stages, next actions, blockers and stalled communications. Manages team priorities and load. Highlights risk zones, plan deviations and at-risk-goal signals. | Improved effectiveness | 2026-05-01 |
| 3 | Tasks | Automatically extracts tasks from emails, messages, meetings and summaries; assigns owners, track and due date. Single control loop: status, dependencies, fact of reply, overdue, duplicates, no-owner. | Improved productivity | 2026-05-06 |
| 4 | Notes | Turns transcripts and meeting notes into structured Russian-language summaries with theses, risks, agreements and next steps. Works even without a full transcript. Single standard for notes. Links meeting to follow-up, tasks, owners and fund stage movement. | Context coverage and completeness | 2026-05-08 |
| 5 | Calendar | Runs the operational meeting loop: coordinates slots, tracks unconfirmed bookings, classifies meetings by type, auto-routes fundraising meetings to a separate loop. Delivers upcoming external-meeting list, prep support and CEO-time analytics with optimization tips. | Time optimization | 2026-05-13 |
| 6 | Email | Aggregates signals from email, LinkedIn, WhatsApp, Telegram, Slack and other channels into one stream. Normalizes and classifies each event. Accelerates replies via follow-up, prior threads, templates and personalized drafts under human review for important comms. | Reply coverage, quality and speed | 2026-05-15 |
| 7 | Docs | Determines which document is needed (NDA, one-pager, brief, etc.), picks the right template, builds an action checklist and tracks document workflow status end-to-end. | Doc preparation speed and quality | 2026-05-20 |
| 8 | Tables | Auto-fills and updates trackers, CRM, wishlists and other structured registries. Syncs fields between sources; finds duplicates, gaps and desync; suggests updates. Speeds up fund/participant card assembly, outreach logging and register hygiene. | Table preparation speed and quality | 2026-05-22 |
| 9 | Slides | Assembles presentation materials from notes, docs, trackers and other sources into slide format. Generates one-slide fund summaries, meeting drafts and converts working materials into presentation form. | Slide preparation speed and quality | 2026-05-27 |
| 10 | Reports | Automatically produces regular management reporting on the fundraising process — daily, weekly and monthly status, checklists and owner-process reports. Collects data from meetings, tasks, touches, blockers and fund stages to surface deviations on time. | Timely deviation detection | 2026-05-29 |

## AI Platform

- **Infra**: GCP
- **Data**: PostgreSQL (relational), Cloud Storage (object), Qdrant (vector), Neo4j (graph)
- **Services**: langchain, langgraph, supabase, n8n, MCP, streamlit
- **AI Services**: GPT 5.4, Claude 5.7
- **Clients**: API/MCP, Telegram, Slack, Google Meet

## Strategy link

https://docs.google.com/spreadsheets/d/1QiCLAk5O0tma55ZGNQyAXRNfP-oxS0OC9Y8H_b4SMvo/edit?usp=sharing
