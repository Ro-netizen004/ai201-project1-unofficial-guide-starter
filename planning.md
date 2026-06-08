# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

The domain of this project is the USF Computer Science Survival Guide (Unofficial Student Knowledge System). It focuses on student-generated and experience-based information about computer science courses, professors, and academic planning at the University of South Florida.

This knowledge is valuable because it helps students make informed decisions about course selection, professor difficulty, and degree planning based on real student experiences rather than official course descriptions. It is difficult to find through official channels because university catalogs and departmental websites only provide formal information such as prerequisites and course objectives, while omitting practical insights like teaching style, workload difficulty, grading patterns, and student experiences.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|------------------|
| 1 | USF CS Professors Dataset (JSON file) | Rate My Professors export for 20 USF CS faculty: aggregate quality and difficulty scores, would-take-again rates, rating distributions, and full student review text tied to specific courses (e.g., CDA3201), plus tags like "Amazing lectures" and "Tough grader" | `documents/dataset_rate-my-professors.json` |
| 2 | Official USF CS program information | USF's authoritative BS in Computer Science page covering admission requirements, degree objectives, core curriculum structure, and formal course expectations—useful as a baseline against which student experiences can be compared | `documents/usf_bscs_page.txt` — https://www.usf.edu/ai-cybersecurity-computing/academics/undergraduate/bscs.aspx |
| 3 | COP3514 Programming Concepts (r/USF) | Thread on COP 3514 (program design) covering perceived difficulty, project workload, exam style, and professor-specific advice from students who have taken the course | `documents/reddit_cop3514.txt` — https://www.reddit.com/r/USF/comments/13ewl3y/program_design_cop_3514/ |
| 4 | COP2510 Difficulty | Thread focused on COP 2510 (introductory programming): how steep the learning curve feels, time commitment, common pitfalls for new CS students, and tips for succeeding in a first coding course | `documents/reddit_cop2510.txt` — https://www.reddit.com/r/USF/comments/yn7dtp/cop_2510_difficulty/ |
| 5 | USF CS Degree Flowchart | Visual degree plan showing prerequisite chains, recommended semester-by-semester course order, gen-ed slots, and elective windows—helps answer "what should I take next?" and "what unlocks what?" | `documents/usf_cs_plan.pdf` |
| 6 | r/USF CS Program Opinion Thread (Need Your Opinion) | Open-ended student opinions on the overall USF CS program: strengths and weaknesses, department culture, internship and career outcomes, and whether the degree feels worth the effort | `documents/reddit_program_opinion.txt` — https://www.reddit.com/r/USF/comments/1rroyo1/need_your_opinion/ |
| 7 | r/USF CS Course Load & Difficulty Discussion | Practical advice on juggling a job with CS coursework, with firsthand difficulty ratings for COP 2513 (programming II) and MAD 2104 (discrete math) and how those courses compare in weekly hours | `documents/reddit_course_load.txt` — https://www.reddit.com/r/USF/comments/7bu5tk/how_hard_are_these_classes_will_working_be_too/ |
| 8 | r/USF “Easiest CS Electives” Thread | Crowdsourced elective picks students consider low-stress, including which upper-level CS courses have lighter workloads, easier grading, or less prerequisite depth | `documents/reddit_easiest_electives.txt` — https://www.reddit.com/r/USF/comments/7k07b8/easiest_cs_electives/ |
| 9 | USF CS Student Study Guides Repository (GitHub) | Community-maintained repo of course-specific study guides, exam reviews, and reference sheets for core CS classes (data structures, discrete math, computer organization, and related topics)—student-authored supplements to lecture material | `documents/github_cse_resources.txt`, `documents/github_cop3514_exam1_review.txt` — https://github.com/aeckar/usf-cse-resources |
| 10 | USF Computer Science Program Student Experience Discussion (r/USF) | Long-form thread from current and alumni CS majors on day-to-day program life: professor quality, course rigor, languages and tools taught, research opportunities, and how well the curriculum prepared them for internships and jobs | `documents/reddit_cs_experience.txt` — https://www.reddit.com/r/USF/comments/s4ht3j/anyone_here_in_usf_computer_science_department/ |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | | |
| 2 | | |
| 3 | | |
| 4 | | |
| 5 | | |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
