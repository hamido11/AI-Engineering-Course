# -*- coding: utf-8 -*-
"""Lab pages (exercises), one per module, aligned with the code in /labs."""
from build import spec


def ex(eid, tag, title, desc):
    return (f'<h3 class="sub">{eid} &middot; {title} '
            f'<span style="font-family:\'IBM Plex Mono\';font-size:7.6pt;color:#B5502D;">[{tag}]</span></h3>'
            f'<p>{desc}</p>')


def repo(folder):
    return (f'<p style="margin-top:5mm;"><span style="font-family:\'IBM Plex Mono\';font-size:8.6pt;">'
            f'&#9656; Reference code: <strong>{folder}</strong> in the companion repo. '
            f'Try the exercises first, then compare.</span></p>')


def lab_page(n, intro, exercises_html, ship_html, folder):
    return (f'<h2 class="sec">Lab {n:02d} &mdash; Exercises</h2><p>{intro}</p>' + exercises_html +
            spec("Ship It &mdash; Lab Challenge", ship_html) + repo(folder))


def lab01():
    e = (ex("E1", "warm-up", "Map a real product",
            "Pick an AI product you use (a coding assistant, a support bot, a search feature). Identify which layers of the stack from Figure 1.1 it uses, and which it visibly lacks.")
         + ex("E2", "core", "Failure taxonomy",
              "List five realistic ways that product could fail. Classify each as hallucination, retrieval miss, prompt injection, latency/cost, or tooling error. Note which layer would catch it.")
         + ex("E3", "core", "Design your iteration loop",
              "Write down the exact steps to test a prompt change in your own setup. If the loop takes more than five minutes, redesign it until it doesn't &mdash; this loop is your main asset for the rest of the course."))
    ship = ("<p>Write a one-page build spec for a small AI product you will construct across these labs "
            "(examples: a docs Q&amp;A bot, a support triager, a research summarizer). State the user, the task, "
            "the data it needs, and which modules of this course map to which part. Every later lab extends this project.</p>")
    return lab_page(1, "No code yet &mdash; this lab sets up the project and the habits the rest of the course builds on.", e, ship, "labs/01-intro")


def lab02():
    e = (ex("E1", "warm-up", "Count tokens",
            "Use <code class=\"inline\">tiktoken</code> to count tokens for three texts: a tweet, a page of prose, and a code file. Predict the API cost of each at your model's current per-token price.")
         + ex("E2", "core", "Temperature sweep",
              "Send the same prompt at temperature 0, 0.7, and 1.2, three samples each. Record the variance. Decide which setting your Lab-01 project needs and why.")
         + ex("E3", "stretch", "Context-window stress test",
              "Hide one fact (&ldquo;the access code is 7431&rdquo;) inside progressively longer padding documents and ask the model to recall it. Chart recall vs. context length for your model."))
    ship = ("<p>Write a half-page <em>model card summary</em> for the model your project will use: context window, "
            "training cutoff, per-token cost in and out, and the temperature you chose, with one sentence of justification each.</p>")
    return lab_page(2, "Goal: build physical intuition for tokens, sampling, and context before writing any product code.", e, ship, "labs/02-llms")


def lab03():
    e = (ex("E1", "warm-up", "Rewrite a vague prompt",
            "Take &ldquo;summarize this&rdquo; and rebuild it with the Figure 3.1 anatomy: role, explicit instructions, edge-case behaviour, and a required output format.")
         + ex("E2", "core", "Few-shot format lock",
              "Add three input&rarr;output examples to a JSON-extraction prompt. Run it ten times with and without them; measure how often the output parses cleanly in each condition.")
         + ex("E3", "core", "Break in, then lock out",
              "Craft a user input that hijacks your own prompt (&ldquo;ignore previous instructions&hellip;&rdquo;). Then defend: fence user data in delimiters and re-test the same attack."))
    ship = ("<p>Commit your project's prompts as versioned files (<code class=\"inline\">prompts/v1_&hellip;.md</code>) plus a five-case "
            "mini-eval script that runs them and checks outputs. This becomes the seed of Lab 12.</p>")
    return lab_page(3, "Everything here uses the API you'll formalise in Module 04 &mdash; the repo provides a thin helper so you can focus on the prompts.", e, ship, "labs/03-prompt-engineering")


def lab04():
    e = (ex("E1", "warm-up", "Minimal call",
            "Reproduce the module's minimal call, then refactor it into a reusable <code class=\"inline\">ask(messages)</code> helper your later labs will import.")
         + ex("E2", "core", "Streaming",
              "Switch the helper to streaming and print tokens as they arrive. Measure time-to-first-token vs. time-to-full-response for the same request.")
         + ex("E3", "core", "Retries with backoff",
              "Wrap the call in exponential backoff for HTTP 429/5xx (the repo's chaos test shows how to simulate failures). Verify it survives three consecutive simulated failures.")
         + ex("E4", "stretch", "Cost ledger",
              "Log model, input tokens, output tokens, and computed cost for every call to a CSV. Keep model IDs and prices in configuration, not in code."))
    ship = ("<p>Build a tiny CLI chatbot: keeps conversation history, streams responses, retries on failure, and prints "
            "the running cost after each turn. This wrapper is the engine for every later lab.</p>")
    return lab_page(4, "This lab produces the API wrapper the rest of the course runs on &mdash; invest here.", e, ship, "labs/04-openai-api")


def lab05():
    e = (ex("E1", "warm-up", "Similarity ranking",
            "Embed ten sentences (mix two topics). Compute the cosine-similarity matrix and confirm the two topic clusters are visible in the numbers.")
         + ex("E2", "core", "Chunkers, compared",
              "Implement fixed-size and paragraph-aware chunking over the same document. For five test questions, check which chunker's top-3 chunks actually contain the answer.")
         + ex("E3", "stretch", "Near-duplicate detector",
              "Embed a folder of notes and flag pairs above 0.92 similarity. Tune the threshold until false positives disappear."))
    ship = ("<p>Build <em>semantic grep</em>: a CLI that takes a query and a folder, embeds both, and prints the five most "
            "relevant passages with scores. No vector DB yet &mdash; plain arrays are the point.</p>")
    return lab_page(5, "Everything is small enough to run with in-memory arrays &mdash; you'll feel exactly what a vector database automates in Module 06.", e, ship, "labs/05-embeddings")


def lab06():
    e = (ex("E1", "warm-up", "First index",
            "Load the sample docs into Chroma with source and date metadata. Query top-5 for three questions and eyeball the hits.")
         + ex("E2", "core", "Filtered search",
              "Repeat the queries with a metadata filter (<code class=\"inline\">source = &hellip;</code>). Find one query whose answer changes &mdash; that's the filtered-search workload in action.")
         + ex("E3", "stretch", "Recall check",
              "At this small scale you can brute-force exact nearest neighbours. Compare against the index's results and compute recall@5."))
    ship = ("<p>Write an idempotent <code class=\"inline\">reindex.py</code>: wipe and rebuild the collection from source files, "
            "stamping each record with an embedding-model name and content hash. Re-running it twice must produce the identical index.</p>")
    return lab_page(6, "The lab treats the index as derived data from day one &mdash; the rebuild script is the real deliverable.", e, ship, "labs/06-vector-db")


def lab07():
    e = (ex("E1", "warm-up", "Wire it together",
            "Connect Lab 05's chunks, Lab 06's index, and Lab 04's wrapper into one <code class=\"inline\">answer(question)</code> function that cites chunk IDs.")
         + ex("E2", "core", "Honest refusals",
              "Add the &ldquo;answer only from context; say you don't know otherwise&rdquo; instruction. Test with three questions your corpus cannot answer and verify it refuses all three.")
         + ex("E3", "core", "Hybrid retrieval",
              "Add a keyword pre-filter for exact terms (error codes, product names). Find one query where hybrid beats pure vector search.")
         + ex("E4", "stretch", "Rerank",
              "Retrieve 20 candidates, rerank to 5 with a stronger model, and compare answer quality on your test questions."))
    ship = ("<p>Point the pipeline at this course's own PDF: chunk it, index it, and answer five questions about the "
            "course with correct module citations. If it can't cite Module 07 explaining RAG, debug retrieval first.</p>")
    return lab_page(7, "This is the payoff lab &mdash; three modules of infrastructure become one working system.", e, ship, "labs/07-rag")


def lab08():
    e = (ex("E1", "warm-up", "Declare a tool",
            "Write the JSON schema for <code class=\"inline\">get_order_status(order_id)</code> backed by the repo's fake order table. Make the description say when <em>not</em> to use it.")
         + ex("E2", "core", "The two-round-trip loop",
              "Implement the full cycle: model requests the call, your code executes, result returns, model answers. Log each leg. Cap the number of rounds.")
         + ex("E3", "core", "Hostile arguments",
              "Have the model call your tool with an order ID that doesn't exist, then with a malformed one. Validate, return structured errors, and confirm the model recovers gracefully.")
         + ex("E4", "stretch", "Gate a dangerous tool",
              "Add <code class=\"inline\">issue_refund</code> but require a typed confirmation before execution. The model may draft; only a human may fire."))
    ship = ("<p>Assemble a support bot with both tools: statuses answered automatically, refunds drafted but gated. "
            "Demonstrate one full conversation of each kind.</p>")
    return lab_page(8, "The theme is the trust boundary: the model proposes, your code validates and disposes.", e, ship, "labs/08-function-calling")


def lab09():
    e = (ex("E1", "warm-up", "Speak the protocol",
            "Run the repo's minimal MCP server under the MCP Inspector (or any MCP-capable host). List its tools and call one &mdash; note that you wrote zero integration code on the client side.")
         + ex("E2", "core", "Serve your own tools",
              "Wrap Lab 08's order tools in an MCP server. Connect from an MCP-capable host and use them from chat.")
         + ex("E3", "stretch", "Threat-model a server",
              "You're evaluating a third-party MCP server for production. Write the one-page review: what it can read, what it can do, how a poisoned tool result could inject instructions, and your three mitigations."))
    ship = ("<p>Publish your Lab 08 tools as an MCP server with a README covering scopes, dangerous operations, and "
            "logging &mdash; written for the security reviewer, not the user.</p>")
    return lab_page(9, "One protocol, two sides: first consume it, then provide it.", e, ship, "labs/09-mcp")


def lab10():
    e = (ex("E1", "warm-up", "Bound the loop",
            "Run the repo's agent with max-iterations, token budget, and wall-clock caps. Prove each cap triggers by setting it absurdly low.")
         + ex("E2", "core", "Fail loudly",
              "Give the agent an impossible task. Acceptable outcome: a clear failure report within budget. Unacceptable: silent looping. Fix the loop until the acceptable outcome is guaranteed.")
         + ex("E3", "core", "Add reflection",
              "Insert a &ldquo;critique your last step before acting&rdquo; stage. Measure the change in steps-to-completion across five tasks.")
         + ex("E4", "stretch", "Human gate",
              "Any file-writing action must print a preview and wait for y/n. Reads stay autonomous."))
    ship = ("<p>Build a file-organizer agent for a sandbox folder: it plans a re-organisation, shows the full move plan "
            "(dry-run), and executes only after approval &mdash; within budget, every time.</p>")
    return lab_page(10, "Every exercise here is about the constraints, not the intelligence &mdash; that's the module's thesis in practice.", e, ship, "labs/10-agents")


def lab11():
    e = (ex("E1", "warm-up", "Loop &rarr; graph",
            "Rebuild Lab 10's loop as a LangGraph <code class=\"inline\">StateGraph</code> with agent and tool nodes. Confirm identical behaviour on the same tasks.")
         + ex("E2", "core", "Branch explicitly",
              "Add a conditional edge routing easy questions straight to answer and hard ones through tools. The routing function is plain Python &mdash; unit-test it.")
         + ex("E3", "core", "Kill it and resume",
              "Enable checkpointing, kill the process mid-run, restart, and watch it resume from the last node instead of the beginning.")
         + ex("E4", "stretch", "Interrupt for approval",
              "Replace Lab 10's y/n prompt with a graph interrupt before the tool node &mdash; approval becomes part of the graph itself."))
    ship = ("<p>A resumable research assistant: given a topic, it searches your Lab 07 index, drafts notes, pauses for "
            "review, and finishes after approval &mdash; surviving a restart at any point.</p>")
    return lab_page(11, "The deliverable is the same agent as Lab 10 &mdash; the point is what the graph makes visible, testable, and resumable.", e, ship, "labs/11-langgraph")


def lab12():
    e = (ex("E1", "warm-up", "Harvest real cases",
            "Collect ten real inputs from your project's usage so far &mdash; include two ugly ones and one whose correct answer is &ldquo;I don't know.&rdquo; Write expected outcomes for each.")
         + ex("E2", "core", "Programmatic scorers",
              "Write checkers for what can be checked mechanically: JSON validity, must-contain strings, correct refusals. Run the set and print a pass rate.")
         + ex("E3", "core", "LLM-as-judge, calibrated",
              "Write a grading rubric, have a strong model score each output 1&ndash;5, then score five yourself. If you and the judge disagree by more than a point on average, fix the rubric, not your opinion.")
         + ex("E4", "stretch", "Prove it catches regressions",
              "Deliberately break your prompt (delete the refusal instruction). The eval must visibly fail. If it doesn't, your dataset has a hole &mdash; add the missing case."))
    ship = ("<p>One command &mdash; <code class=\"inline\">python run_eval.py</code> &mdash; that runs the dataset, prints pass rate and "
            "per-case results vs. the last baseline, and exits non-zero on regression. Wire it into the habit loop from Lab 01.</p>")
    return lab_page(12, "From here on, no prompt or pipeline change lands without this lab's script passing.", e, ship, "labs/12-evaluation")


def lab13():
    e = (ex("E1", "warm-up", "Cache layer",
            "Add exact-match response caching to your Lab 04 wrapper. Replay a day of test traffic and report the hit rate and cost saved.")
         + ex("E2", "core", "Survive an outage",
              "Simulate provider failure (the repo's <code class=\"inline\">CHAOS=1</code> flag). Verify the fallback path engages, the user gets an answer, and the incident is logged.")
         + ex("E3", "core", "Guard the door",
              "Add an input check for prompt-injection patterns ahead of your RAG bot, and an output check that citations actually exist in the retrieved set.")
         + ex("E4", "stretch", "Canary a change",
              "Route 10% of eval traffic to a new prompt version. Compare pass rates and cost side by side before promoting to 100%."))
    ship = ("<p>Wrap your Lab 07 bot with all four budgets &mdash; guards in front, checks behind, cache beside, fallback "
            "beneath &mdash; and print a one-screen ops report: p50/p95 latency, cache hit rate, fallbacks.</p>")
    return lab_page(13, "Same bot as Lab 07 &mdash; now it can take a punch.", e, ship, "labs/13-production")


def lab14():
    e = (ex("E1", "warm-up", "Stamp the tuple",
            "Attach a version tuple &mdash; model ID, prompt version, index content-hash, config hash &mdash; to every answer your bot produces. Any answer must be traceable to its exact build.")
         + ex("E2", "core", "Trace and replay",
              "Log every request end-to-end (input, retrieved chunks, output, latency) as JSONL. Add a replay command (the reference code uses <code class=\"inline\">python trace.py &lt;trace_id&gt;</code>) that re-runs any past request against the current build and reports which part of the tuple changed.")
         + ex("E3", "core", "Schedule the evals",
              "Write the cron/CI job that runs Lab 12 nightly against the production tuple and alerts on regression. Dry-run it manually.")
         + ex("E4", "stretch", "Drift drill",
              "Swap in a different model version without telling your eval suite. Confirm the nightly run catches the behaviour change within one cycle."))
    ship = ("<p>Write the two documents every on-call engineer needs: a release checklist (what must pass before any "
            "tuple change ships) and a one-page incident runbook (bad answer reported &rarr; trace &rarr; replay &rarr; diagnose &rarr; add eval case). "
            "That closes the loop &mdash; and the course.</p>")
    return lab_page(14, "The final lab turns your project from a demo into something you could hand to another engineer.", e, ship, "labs/14-mlops")


LABS = [lab01, lab02, lab03, lab04, lab05, lab06, lab07,
        lab08, lab09, lab10, lab11, lab12, lab13, lab14]
