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

### Sample Chunks

**Chunk 1 — Source: `documents/dataset_rate-my-professors.json` (professor summary)**

```
Professor: Rangachar Kasturi
Department: Computer Science
Overall Rating: 4.2
Difficulty: 3.5
Would Take Again: 100%
Rating Breakdown: Awesome: 7, Great: 2, Good: 0, OK: 0, Awful: 1
```

**Chunk 2 — Source: `documents/dataset_rate-my-professors.json` (professor review)**

```
Professor: Rangachar Kasturi
Course: CDA3201
Quality Rating: 5.0
Tags: Amazing lectures, Caring
Student Review: Doctor Kasturi is one of the best professors I have ever had. His lectures are very clear...
```

**Chunk 3 — Source: `documents/usf_cs_plan.pdf` (page 1)**

```
USF CS Degree Plan (usf_cs_plan) — Page 1
Computer Science B.S.C.S.
4-Year Plan of Study
Potential Entry Level Job Titles: Software Developer, Software Tester, Software Engineer...
```

**Chunk 4 — Source: `documents/github_cop3514_exam1_review.txt`**

```
Study Guide: COP 3514 Program Design - Exam 1 Review (USF CSE Resources)
COP 3514 Program Design - Exam 1 Review
textbook | c compiler
```

**Chunk 5 — Source: `documents/reddit_cop2510.txt` (POST section)**

```
Reddit Thread: COP 2510 Difficulty
POST: I am taking this class next spring with Dr Small... Is getting a minimum of B in this class difficult since you need a B to continue your CS degree
```

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers`, integrated with ChromaDB. It is lightweight, runs locally, and is sufficient for a ~142-chunk corpus of short English text about courses and professors.

**Production tradeoff reflection:** With no cost constraint, I would compare models with longer context windows to reduce chunking artifacts, and domain-tuned or API-hosted embeddings (e.g., OpenAI `text-embedding-3-large`) for better retrieval of course codes and professor names. Tradeoffs include latency (local vs API), hosting cost, multilingual support (not needed here), and accuracy on informal student writing vs formal catalog text. For this corpus size, local MiniLM keeps the pipeline simple and free to run.

---

## Retrieval Tests

Each test shows the query and the top 3 chunks returned by `retrieve()` (cosine distance — lower is more similar).

### Test 1 — Professor query

**Query:** What do students say about Rangachar Kasturi?

| Rank | Distance | Source | Chunk preview |
|------|----------|--------|---------------|
| 1 | 0.333 | `dataset_rate-my-professors.json` — review, CDA3201 | "Student Review: Kasturi is very knowledgeable and a good lecturer, also very friendly..." |
| 2 | 0.336 | `dataset_rate-my-professors.json` — review, CDA3201 | "Student Review: one of the best professors in comp sci... breaks things down..." |
| 3 | 0.355 | `dataset_rate-my-professors.json` — review, CDA3201 | "Student Review: one of the best professors I have ever had. His lectures are very clear..." |

**Why these chunks are relevant:** The query names a specific professor. Each returned chunk is a complete Rate My Professors review where "Rangachar Kasturi" appears in both the text and metadata, so embedding similarity is high. Because ingestion emits one review per document, each chunk contains a full student opinion rather than a fragment.

### Test 2 — Course difficulty query

**Query:** How hard is COP 3514 according to students?

| Rank | Distance | Source | Chunk preview |
|------|----------|--------|---------------|
| 1 | 0.480 | `reddit_cop3514.txt` — COMMENT (Wolverine002) | "I personally had so much struggle in CDA but pass COP without much prep..." |
| 2 | 0.567 | `reddit_cop3514.txt` — COMMENT (vjosa_e_larget) | "As for Computer Organization, that's a class you want to study significantly for..." |
| 3 | 0.571 | `reddit_cop3514.txt` — COMMENT (findingTheWay97) | "Overall they are not very TOUGH courses but there is a very large amount of information..." |

**Why these chunks are relevant:** Course-code boosting pulls chunks from `reddit_cop3514.txt` when the query mentions COP 3514. The top hit is a student comment comparing COP 3514 difficulty to CDA. Hits 2 and 3 are from the same thread and discuss workload and difficulty, though they mix COP and CDA content — a known limitation of this corpus.

### Test 3 — Program opinion query

**Query:** What do students think about the USF CS program overall?

| Rank | Distance | Source | Chunk preview |
|------|----------|--------|---------------|
| 1 | 0.180 | `reddit_program_opinion.txt` — POST | "I was admitted to USF... I am gonna major in CS, I would just love to hear the overall experience..." |
| 2 | 0.232 | `reddit_program_opinion.txt` — COMMENT (Status-Suggestion620) | "USF is not a good school for computer science. It's ranked #422 globally..." |
| 3 | 0.327 | `reddit_program_opinion.txt` — COMMENT (sept27) | "The CS department is a travesty and the quality of the education is extremely subpar..." |

**Why these chunks are relevant:** All three hits come from the same Reddit thread titled "Need your opinion - USF CS Program Experience." The low distances (0.18–0.33) show strong semantic match with a broad program-level question. The comments directly express student opinions about the CS program — both negative rankings and department quality criticism.

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

### Example System Responses (with source attribution)

**Query:** What do students say about Rangachar Kasturi?

**System response:**

> According to the provided documents, students have overwhelmingly positive reviews about Professor Rangachar Kasturi. They describe him as:
>
> - "very knowledgeable and a good lecturer, also very friendly" (Document 1)
> - "one of the best professors in comp sci" (Document 2)
> - "one of the best professors I have ever had" (Document 3)
> - Making complex material "easy to understand" and "interesting" (Documents 2, 3, and 4)
>
> Students also appreciate his teaching style, noting that he "breaks things down to where they make sense" (Document 2), gives "amazing lectures" (Document 3), and has "clear grading criteria" (Document 4).

**Query:** What do students think about the USF CS program overall?

**System response:**

> Based on the provided Reddit thread, "Need your opinion - USF CS Program Experience", opinions about the USF CS program vary among students.
>
> Some students have expressed negative experiences, with one commenter (sept27) stating that the "CS department is a travesty and the quality of the education is extremely subpar." Another commenter (Status-Suggestion620) mentioned that USF is ranked #422 globally for computer science, according to US News.
>
> On the other hand, one student shared a positive experience, stating that they had a great time, got three internships, and worked in two labs during their time at USF. Overall, students have mixed opinions about the USF CS program.

### Out-of-Scope Query (refusal example)

**Query:** What is the best pizza restaurant near USF campus?

**System response:**

> I don't have enough information in the provided sources to answer your question about the best pizza restaurant near USF campus. The context documents only discuss the USF computer science department, professor ratings, and do not mention pizza restaurants.

This shows grounding working correctly — the LLM refuses to answer rather than invent a restaurant recommendation.

---

## Query Interface

The app is a **Gradio web UI** launched with `python app.py` at `http://127.0.0.1:7860`.

| Field | Type | Description |
|-------|------|-------------|
| **Status** | Text (read-only) | Shows index readiness, e.g. "Index ready — 142 chunks embedded with all-MiniLM-L6-v2." |
| **Your question** | Text input | User types a natural-language question; Enter or the Ask button submits it. |
| **Examples** | Clickable list | Five pre-loaded example questions (COP 3514, Kasturi, electives, COP 2510, program opinion). |
| **Answer** | Markdown | Grounded response from Groq with inline source references. |
| **Retrieved sources** | Markdown | Numbered list of chunks used — label, distance score, URL link, and text preview. |

### Sample Interaction Transcript

```
Status: Index ready — 142 chunks embedded with all-MiniLM-L6-v2.

Your question: What do students say about Rangachar Kasturi?

[User clicks Ask]

Status: Answer generated from retrieved sources.

Answer:
According to the provided documents, students have overwhelmingly positive reviews
about Professor Rangachar Kasturi. They describe him as "very knowledgeable and a
good lecturer, also very friendly" (Document 1) and "one of the best professors
I have ever had" (Document 3). Students appreciate his clear lectures, helpful TAs,
and accessible office hours.

Retrieved sources:
1. Professor review — Rangachar Kasturi (CDA3201) (distance: 0.333)
   Professor: Rangachar Kasturi | Course: CDA3201 | Student Review: Kasturi is very
   knowledgeable and a good lecturer, also very friendly...
2. Professor review — Rangachar Kasturi (CDA3201) (distance: 0.336)
   Student Review: one of the best professors in comp sci...
3. Professor review — Rangachar Kasturi (CDA3201) (distance: 0.355)
   Student Review: one of the best professors I have ever had...
```

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

- *What I gave the AI:* The chunking strategy from planning.md (500 chars / 75 overlap / 800 pass-through), the existing ingest pipeline, Groq API requirements, and the project rubric sections for retrieval tests and grounded generation.
- *What it produced:* `chunk_documents.py`, `retrieval/vector_store.py`, `generation/generate.py`, and `app.py` Gradio UI wiring the full RAG pipeline.
- *What I changed or overrode:* After COP 3514 and electives test failures, I directed the AI to split Reddit threads by comment in `TextAdapter`, add course-code boosting and neighbor expansion in `retrieve()`, and move the sources panel out of a collapsed accordion. I also ran all 5 evaluation questions myself and wrote honest partially-accurate / inaccurate judgments rather than editing results to look perfect.

