# The Unofficial Guide — Project 1

> **How to use this template:**
> Complete each section *after* you've built and tested the corresponding part of your system.
> Do not write placeholder text — if a section isn't done yet, leave it blank and come back.
> Every section below is required for submission. One-liners will not receive full credit.

---

## Domain

The Unofficial Guide covers **student-generated knowledge about the USF Computer Science program** — professor reviews, course difficulty, degree planning, and peer advice from Reddit and community study guides.

This knowledge is valuable because official USF pages describe prerequisites and curriculum structure but not how hard a course actually feels, whether a professor is approachable, or which electives students consider low-stress. Students usually learn this through word of mouth, scattered Reddit threads, and Rate My Professors — not through a single searchable source.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
| 1 | Rate My Professors USF CS export | JSON | `documents/dataset_rate-my-professors.json` |
| 2 | Official USF BS in Computer Science page | Web page (saved as text) | `documents/usf_bscs_page.txt` — https://www.usf.edu/ai-cybersecurity-computing/academics/undergraduate/bscs.aspx |
| 3 | r/USF — Program Design COP 3514 | Reddit thread | `documents/reddit_cop3514.txt` — https://www.reddit.com/r/USF/comments/13ewl3y/program_design_cop_3514/ |
| 4 | r/USF — COP 2510 Difficulty | Reddit thread | `documents/reddit_cop2510.txt` — https://www.reddit.com/r/USF/comments/yn7dtp/cop_2510_difficulty/ |
| 5 | USF CS degree flowchart | PDF | `documents/usf_cs_plan.pdf` |
| 6 | r/USF — Need Your Opinion (CS program) | Reddit thread | `documents/reddit_program_opinion.txt` — https://www.reddit.com/r/USF/comments/1rroyo1/need_your_opinion/ |
| 7 | r/USF — Course load while working | Reddit thread | `documents/reddit_course_load.txt` — https://www.reddit.com/r/USF/comments/7bu5tk/how_hard_are_these_classes_will_working_be_too/ |
| 8 | r/USF — Easiest CS Electives | Reddit thread | `documents/reddit_easiest_electives.txt` — https://www.reddit.com/r/USF/comments/7k07b8/easiest_cs_electives/ |
| 9 | USF CSE Resources (GitHub) | GitHub repo | `documents/github_cse_resources.txt`, `documents/github_cop3514_exam1_review.txt` — https://github.com/aeckar/usf-cse-resources |
| 10 | r/USF — CS department experience | Reddit thread | `documents/reddit_cs_experience.txt` — https://www.reddit.com/r/USF/comments/s4ht3j/anyone_here_in_usf_computer_science_department/ |

---

## Chunking Strategy

**Chunk size:** 500 characters, applied only to documents longer than 800 characters (`MAX_WHOLE_CHARS = 800`).

**Overlap:** 75 characters between consecutive chunks when splitting long documents.

**Why these choices fit your documents:** Most documents are already small after ingestion — one professor review (~500 chars), one PDF page, or one Reddit comment. These pass through as a single chunk so retrieval returns a complete review or reply. Longer sources (multi-comment Reddit threads, the USF program page, GitHub study guides) exceed the embedder's effective limit (~256 tokens for `all-MiniLM-L6-v2`), so they are split at 500 characters with 75-char overlap. Splits prefer newline boundaries when past the halfway point of each window. Before chunking, adapters split at natural boundaries: one review per document, one PDF page per document, and one Reddit `POST` or `COMMENT` per document (with long comments further split at paragraph or topic boundaries).

**Final chunk count:** 142 chunks from 128 ingested documents.

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`, integrated with ChromaDB. It is lightweight, runs locally, and is sufficient for a ~142-chunk corpus of short English text about courses and professors.

**Production tradeoff reflection:** With no cost constraint, I would compare models with longer context windows to reduce chunking artifacts, and domain-tuned or API-hosted embeddings (e.g., OpenAI `text-embedding-3-large`) for better retrieval of course codes and professor names. Tradeoffs include latency (local vs API), hosting cost, multilingual support (not needed here), and accuracy on informal student writing vs formal catalog text. For this corpus size, local MiniLM keeps the pipeline simple and free to run.

---

## Grounded Generation

**System prompt grounding instruction:**

```
You are The Unofficial Guide — a helpful assistant for USF Computer Science students.

Rules:
1. Answer ONLY using the context documents provided below.
2. If the context does not contain enough information to answer, say clearly that you do not have enough information in the provided sources.
3. Do not use outside knowledge, guess, or invent facts.
4. When possible, cite where information comes from (professor name, course code, thread title, degree plan page, etc.).
5. Be concise and practical — write like you're advising a fellow student.
```

Retrieved chunks are formatted as numbered context blocks (`[Document 1 — Professor review — Kasturi (CDA3201)]`) and passed in the user message alongside the question. The LLM (`llama-3.3-70b-versatile` via Groq) receives no other context. Temperature is set to 0.2 to reduce creative guessing.

**How source attribution is surfaced in the response:** The LLM is instructed to cite professor names, course codes, and thread titles in its answer. The Gradio UI also shows a **Retrieved sources** panel listing each hit with a human-readable label (e.g., "Professor review — Kasturi (CDA3201)"), similarity distance, optional URL link, chunk position, and a text preview.

---

## Evaluation Report

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | How hard is COP 3514 according to students? | Manageable if you know C/C++; not extremely tough; pointers/linked lists and projects matter; want a B or better. | Described mixed student opinions; mentioned Wolverine002 found COP easier than CDA; partially conflated CDA difficulty with COP 3514. | Partially relevant | Partially accurate |
| 2 | What do students say about Rangachar Kasturi? | Very positive: clear lectures, caring, among the best CS professors, high ratings. | Correctly summarized strong praise from multiple reviews — knowledgeable, friendly, breaks concepts down well. | Relevant | Accurate |
| 3 | What are some of the easiest CS electives at USF? | Software Systems Development, Software Engineering, Software Testing named as easy electives. | Said it did not have enough information; retrieved the thread title and POST but not the comment with elective names in the top context sent to the LLM. | Partially relevant | Inaccurate |
| 4 | What is the workload like for COP 2510? | Doable with effort; office hours help; Dr. Small teaches well; B achievable for beginners. | Gave general advice about putting in effort and using office hours; did not give specific workload hours but directionally reasonable. | Relevant | Partially accurate |
| 5 | What do students think about the USF CS program overall? | Mixed: some say doable with curving; others criticize advisors, job market, and professor inconsistency. | Captured mixed opinions including negative comments about department quality and rankings; noted variation among students. | Relevant | Accurate |

**Retrieval quality:** Relevant / Partially relevant / Off-target  
**Response accuracy:** Accurate / Partially accurate / Inaccurate

---

## Failure Case Analysis

**Question that failed:** What are some of the easiest CS electives at USF?

**What the system returned:** The LLM said it did not have enough information, even though `reddit_easiest_electives.txt` contains student comments naming Software Systems Development, Software Engineering, and Software Testing.

**Root cause (tied to a specific pipeline stage):** At the **retrieval** stage, the top-4 vector hits included the thread's original POST (which only asks for elective suggestions) and unrelated degree-plan chunks. The actual answer comments (`COMMENT (chainy)`, etc.) ranked lower in embedding similarity because the POST repeats phrases like "CS electives" more closely than the query. Those answer chunks were not included in the context sent to the LLM, so **generation** correctly refused to invent an answer.

**What you would change to fix it:** Boost comment sections over POST sections when a thread's POST is a question with no answer text; increase top-k for broad recommendation queries; or add keyword/hybrid retrieval so comment bodies containing course names rank higher.

---

## Spec Reflection

**One way the spec helped you during implementation:**

The planning document's document table and chunking numbers gave concrete targets for each pipeline stage — I knew to emit one review per professor document, split long Reddit threads before embedding, and keep chunks under ~800 characters for MiniLM. The architecture diagram also made it clear which module owned which responsibility, which kept ingestion, chunking, retrieval, and generation in separate folders instead of one monolithic script.

**One way your implementation diverged from the spec, and why:**

The original spec described simple pass-through chunking for small documents, but testing showed long Reddit threads still failed even after character-level splits because the original question post outranked student answer comments in embedding search. I added comment-level splitting in `TextAdapter`, neighbor chunk expansion, and course-code boosting in `retrieve()` — none of which were in the initial spec but were needed to get usable answers for course-specific questions like COP 3514.

---

## AI Usage

**Instance 1**

- *What I gave the AI:* The professor JSON structure, the `BaseAdapter` contract, and the requirement to emit one document per review (not one per professor).
- *What it produced:* `ProfessorJSONAdapter` with `_build_review_text`, `_build_summary_text`, metadata fields, and `_append_line` to skip null values.
- *What I changed or overrode:* Added null stripping in `BaseAdapter.build_document()` for all adapters (required by ChromaDB), and verified review text omits lines like `Grade Received: None` instead of printing nulls literally.

**Instance 2**

- *What I gave the AI:* The chunking strategy from planning.md (500 chars / 75 overlap / 800 pass-through), the existing ingest pipeline, and the project requirement for ChromaDB + Gradio.
- *What it produced:* `chunk_documents.py`, `vector_store.py`, `generate.py`, and `app.py` wiring ingest → chunk → embed → retrieve → Groq → UI.
- *What I changed or overrode:* After COP 3514 test failures, I directed the AI to split Reddit threads by comment, add course-code boosting at retrieval time, and move the sources panel out of a collapsed accordion so retrieved chunks are visible during evaluation.
