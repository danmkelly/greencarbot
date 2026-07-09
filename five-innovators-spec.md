# GreenCarBot: design specification

> **Team:** The Five Innovators at GreenCarBot
> **Client:** Environmentally-conscious car buyers
> **Brief:** Build a customer-facing AI chatbot ("EcoDrive Advisor") that interviews prospective car buyers about their needs, then recommends the ten most environmentally sound vehicles from the EPA Fuel Economy Guide MY2025 dataset (1,410 vehicles), powered by DeepSeek LLM, delivered in the browser.

---

## Project overview

GreenCarBot (the "EcoDrive Advisor") is an AI-powered conversational environmental car recommendation experience. It interviews prospective car buyers about their needs (passengers, driving habits, budget, charging access, electricity supply type, and must-have features), then merges those requirements with the EPA MY2025 vehicle dataset to return a ranked list of the ten most environmentally sound vehicles. Rankings are based on tailpipe CO2 emissions (g/km), adjusted for electricity grid cleanliness, PHEV electric-driving proportion, and buyer constraints.

GreenCarBot is powered by DeepSeek LLM, runs entirely in the browser, fetches live vehicle data from a local `epa_cars.json` file (the MCP pattern: live data as the single source of truth), routes LLM calls through a Cloudflare Worker proxy for API key security, and persists personalisation data in localStorage with explicit consent. The interface uses a two-panel layout: chat on the left, ranked vehicle results with a filter bar on the right, with bidirectional synchronisation between the two.

---

## Team structure

| Innovator | Handle | Role | Domain ownership |
|-----------|--------|------|-----------------|
| Cormac Quinn | `@Cormac` | Manager / Orchestrator | Task decomposition, specialist dispatch, quality gates, cross-framework synthesis, delivery management |
| Fionn Grogan | `@Fionn` | Researcher / Domain Expert | EPA vehicle data taxonomy, environmental metrics mapping, CO2/powertrain domain knowledge, interview question design |
| Siobhan O'Curran | `@Siobhan` | Designer | Conversational UI design, vehicle card layout, two-panel widget, filter bar design, brand visual identity (green/eco theme), mobile responsiveness |
| Dara Bostwick | `@Dot` | Maker / Engineer | Chatbot conversation engine, MCP integration (epa_cars.json pipeline), structured interview flow, environmental ranking algorithm, keyword extraction, localStorage memory, voice STT/TTS, recovery ladder |
| Niamh O'Brien | `@Niamh` | Backend / Infrastructure | Cloudflare Worker proxy for DeepSeek API key, CORS configuration, secrets management, GitHub Pages deployment, environment security |
| Keelin O'Sullivan | `@Keelin` | QA / Evaluator | Test plan design, bug tracking and triage, academic framework scoring (Taxonomy, CASA, Flow Anatomy, Grice), regression testing |

The scopes are non-overlapping: Fionn never builds, Siobhan never writes conversation logic, Dot never deploys infrastructure, Niamh never designs interfaces, Keelin never modifies features, and Cormac never does specialist work.

---

## Technical architecture

```
Browser (index.html)
  |-- epa_cars.json (MCP live data, EPA Fuel Economy Guide MY2025, 1,410 vehicles)
  |-- Cloudflare Worker proxy (/api/llm)
  |     `-- DeepSeek LLM (api.deepseek.com, key never in browser)
  |-- localStorage (consent-gated: name, visit count, search history, interview responses)
  |-- Web Speech API (STT) and SpeechSynthesis API (TTS)
  `-- GitHub Pages (static hosting)
```

The architecture separates authenticated calls (DeepSeek LLM, through the Worker proxy) from unauthenticated calls (epa_cars.json, served as a static asset). The Worker is a lightweight script that accepts POST requests from the browser, attaches the DeepSeek API key from `env.LLM_KEY`, forwards to `api.deepseek.com`, and returns the response. No key ever enters the browser.

---

## Key features

1. **MCP live data integration:** The bot reads `epa_cars.json` at runtime. Every vehicle surfaced (Make, Model, Vehicle Class, Body Type, Seats, Fuel Type, Battery Capacity, Electric Range, MPG, CO2, Drive Type) comes from the live data. The dataset covers 1,410 MY2025 vehicles (828 gasoline, 574 electric, 8 diesel) processed from the EPA Fuel Economy Guide spreadsheet.

2. **Structured interview flow:** A 6-question guided interview collects buyer needs: (1) how many passengers, (2) city/highway/mixed driving, (3) budget range, (4) home charging access, (5) electricity supply type (green tariff / grid mix / dirty), and (6) must-have features (AWD, SUV, 7+ seats, specific brand). Each question validates the answer before advancing. Users can skip the interview and explore freely.

3. **Environmental ranking algorithm:** Vehicles are scored by tailpipe CO2 emissions (g/km). For EVs, the effective CO2 is adjusted based on the buyer's electricity grid type (green tariff = 0 effective CO2, standard grid = low effective CO2, dirty grid = moderate effective CO2). For PHEVs, the score blends electric and gasoline proportions based on driving mix. Results are ranked and displayed as a top-10 list with gold/silver/bronze badges.

4. **Vehicle search with bidirectional filter sync:** Users can search by Make, Vehicle Class, Body Type, Seats, Fuel Type, Drive Type, MPG range, and CO2 limit. Vehicle cards render in the results panel with fuel-type badges (EV/PHEV/Gasoline/Diesel), key specs, and a CO2 emissions bar. The filter bar stays in sync: typing in chat updates the filter bar, and changing filters updates the chat context.

5. **Voice input/output:** Web Speech API for STT (microphone button with listening state animation) and SpeechSynthesis for TTS (speaker icon on each bot message, cancel on re-click, auto-speak after voice input).

6. **Memory and personalisation:** localStorage stores user name, visit count, search history, interview responses, and consent status -- all gated by an explicit consent flow (Yes/No prompt before any write). A "Clear memory" button gives full transparency and control.

7. **Recovery ladder:** A gibberish counter tracks consecutive unrecognised inputs. At failures 1-2 the bot rewords the question. At failures 3-4 it offers constrained suggestion chips and the human handoff path. At failure 4+ it auto-forces human handoff. Register shifts from helpful to concerned to definitive.

8. **Human handoff:** The "Prefer a real human?" bar is persistently visible at the bottom of the chat panel. The contact modal provides information about the tool's limitations and contact details.

---

## Academic frameworks applied

Four frameworks from the Customer Engagement and AI module are embedded in the chatbot's design, build, and evaluation:

| Framework | Source | Application | Domain owner |
|-----------|--------|-------------|-------------|
| Seven-Dimension Chatbot Taxonomy | Adamopoulou & Moussiades (2020) | Quality-gate checklist: knowledge domain (EPA MY2025 vehicles), service (environmental recommendation), goals (rank by CO2), response generation (hybrid LLM + data), channel (two-panel + voice), human-aid, permissions | Fionn (domain, service scope); Dot (goals, response gen); Niamh (human-aid, permissions); Siobhan (channel presentation) |
| CASA (Computers Are Social Actors) | Reeves & Nass (1996) | Trust and ethics guardrail: disclosure, fake-human cues, register-capability alignment, frustration handling, chummy data extraction | Siobhan (disclosure design); Dot (frustration handling); Niamh (data governance); Fionn (register alignment); Keelin (CASA audit) |
| Conversation Flow Anatomy | Adamopoulou & Moussiades (2020) | Structural completeness: Opener (identity + capability), Intent (environmental recommendation), Slots (6 interview questions collected sequentially), Recovery (gibberish ladder), Closer (ranked results + next-step chips) | Dot (recovery ladder, slots, intents); Siobhan (opener/closer UI); Cormac ("design the unexpected first") |
| Gricean Maxims | Grice (1975) | Conversation quality: Quantity (2-4 sentence responses), Quality (every CO2, MPG, and range value from epa_cars.json), Relation (environmental domain only, no financial advice), Manner (clear, brief, no em dashes) | Dot (Quantity, Quality); Fionn (Relation); Siobhan (Manner) |

Keelin owns the cross-framework scoring rubric and produces a weighted design score.

---

## Design principles

1. **Interview-first:** The bot leads with a structured interview to collect needs before making recommendations. Free-form chat is available as a fallback and exploration mode. The interview is skippable.

2. **Environmental transparency:** Every recommendation includes CO2 emissions, fuel type, and efficiency metrics. The ranking algorithm is transparent: users understand why vehicles are ordered as they are. The electricity grid adjustment is explained, not hidden.

3. **Recovery-first:** Failure paths are designed and scheduled before happy paths. Every phase plan starts with "what happens when epa_cars.json fails to load?" and "what happens when the user types gibberish during the interview?"

4. **Mobile-responsive:** The two-panel layout (chat left, results right) stacks vertically at 768px. Touch targets meet a 42px minimum. The results panel scrolls independently on mobile. Filter chips and vehicle cards are thumb-friendly.

5. **Live data as truth:** `epa_cars.json` is the single source of truth. Every vehicle surfaced, every CO2 value, every MPG figure must match the live data exactly. The bot does not hallucinate vehicle specifications or environmental metrics.

6. **Human-always-reachable:** The handoff path is available from every conversational state, including error states and proxy failure -- the handoff display is pure frontend HTML and survives Worker downtime.

---

## Data source

- **Dataset:** EPA Fuel Economy Guide MY2025 (1,410 passenger vehicles)
- **Processed from:** EPA Excel workbook "20250814 MY25 ICE,EV,PHEV For DOE R2public.xlsx"
- **Preprocessing:** Three-sheet extraction (FEguide/ICE, EV, PHEV), CO2 conversion (g/mi to g/km), electric range conversion (miles to km), body type normalisation, non-consumer vehicle exclusion, seat-count enrichment via vehicle-class heuristic with 50+ model-specific overrides
- **Fields:** Make, Model, Vehicle Class, Body Type, Seats, Fuel Type, Battery Capacity (kWh), Electric Range (km), City MPG, Highway MPG, Combined MPG, CO2 Emissions (g/km), Drive Type
- **Filter dimensions:** Make, Vehicle Class, Body Type, Seats, Fuel Type (Electricity/Gasoline/Diesel), Drive Type, MPG, CO2

---

## Delivery pattern

Cormac runs the following handoff sequence:

```
Fionn (EPA data taxonomy + environmental metrics + interview questions)
  -> Siobhan (interface design + vehicle cards + filter bar + green brand)
    -> Dot (conversation engine + interview flow + ranking algorithm + MCP pipeline)
      -> Niamh (Cloudflare Worker proxy + secrets + deployment)
        -> Keelin (test plan + bug register + academic scoring)
          -> Cormac (synthesis + final deliverable)
```

Each handoff includes a contract: input (what the specialist receives), output format (what they deliver), success criteria (how it is judged), and handoff destination (who receives it next). Quality gates are mandatory at every stage.

---

*GreenCarBot: designed and delivered by the Five Innovators team for the Customer Engagement and Artificial Intelligence module.*
