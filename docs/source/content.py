# -*- coding: utf-8 -*-
"""Module body content, m01..m14. Each returns an HTML string."""
from build import flow_svg, loop_svg, spec, diagram, code


def m01():
    return """
<h2 class="sec">What AI Engineering Is</h2>
<p>AI engineering is the discipline of building products on top of pre-trained foundation
models. Unlike classical machine learning, you rarely train a model yourself &mdash; you
compose systems around models that already exist: prompting them, grounding them in your
data, giving them tools, and wrapping them in evaluation and operations so they behave
reliably for real users.</p>
<p>That shift changes the skill set. The centre of gravity moves from datasets and training
loops to <strong>system design</strong>: context construction, retrieval, orchestration,
guardrails, and measurement. Most of this course is about exactly those layers.</p>
""" + diagram(flow_svg(["Model\naccess", "Prompting", "Retrieval\n(RAG)", "Tools &\nagents", "Eval &\nproduction"],
                       height=132, highlight_last=True),
              "Figure 1.1 - the course in one line: each layer wraps the previous one") + """
<h2 class="sec">How It Differs From ML Engineering</h2>
<ul>
<li><strong>Model:</strong> consumed via API or open weights, not trained from scratch.</li>
<li><strong>Data work:</strong> curating context and knowledge bases, not labelled training sets.</li>
<li><strong>Iteration loop:</strong> edit a prompt or pipeline and re-run in seconds, not retrain for days.</li>
<li><strong>Failure modes:</strong> hallucination, prompt injection, drift &mdash; not just accuracy loss.</li>
</ul>
""" + spec("Module 01 &mdash; Key Takeaways", """
<ul>
<li>You build <em>systems around models</em>, not models themselves.</li>
<li>The stack you will assemble: prompting &rarr; retrieval &rarr; tools &rarr; agents &rarr; evaluation &rarr; operations.</li>
<li>Fast iteration is the superpower &mdash; design your workflow so a change can be tested in minutes.</li>
</ul>""")


def m02():
    return """
<h2 class="sec">Next-Token Prediction, Scaled Up</h2>
<p>A large language model is a <strong>transformer</strong> trained on one deceptively simple
objective: given the tokens so far, predict the next one. Trained across trillions of tokens,
that objective forces the network to internalise grammar, facts, style, and a workable
approximation of reasoning &mdash; because all of those help predict what comes next.</p>
<p>Generation is the same trick run in a loop: the model outputs a probability distribution
over its vocabulary, one token is sampled from it, appended to the input, and the process
repeats until a stop condition.</p>
""" + diagram(flow_svg(["Raw text", "Tokenizer", "Transformer\nstack", "Next-token\nprobabilities", "Sampled\ntoken"], height=132),
              "Figure 2.1 - one generation step; the sampled token loops back as input") + """
<h2 class="sec">The Numbers That Matter</h2>
<ul>
<li><strong>Tokens</strong> &mdash; subword chunks (&asymp;4 characters of English each). You are billed and limited in tokens, not words.</li>
<li><strong>Context window</strong> &mdash; the maximum tokens the model can attend to at once (input + output). Everything you want it to know <em>right now</em> must fit here.</li>
<li><strong>Temperature</strong> &mdash; sampling randomness. Low (&asymp;0) for deterministic extraction; higher (&asymp;0.7&ndash;1.0) for creative variety. Some newer models fix or ignore this setting.</li>
<li><strong>Training cutoff</strong> &mdash; the model knows nothing after this date without retrieval.</li>
</ul>
<h2 class="sec">Capability vs. Reliability</h2>
<p>LLMs are probabilistic. The same prompt can produce different outputs; confident prose
can be factually wrong (<em>hallucination</em>). Treat raw model output the way you treat
user input: validate it, constrain it, and never assume correctness. Most of the rest of
this course &mdash; retrieval, tools, evaluation &mdash; exists to convert raw capability
into engineering reliability.</p>
""" + spec("Module 02 &mdash; Key Takeaways", """
<ul>
<li>An LLM predicts tokens; everything else is emergent behaviour on top of that.</li>
<li>Context window is working memory &mdash; finite, priced, and precious.</li>
<li>Design for probabilistic output: validate, constrain, verify.</li>
</ul>""")


def m03():
    return """
<h2 class="sec">The Cheapest Lever You Have</h2>
<p>Prompt engineering is directing model behaviour through the input itself. It is the
first tool to reach for because it costs nothing to change and seconds to test. A
well-structured prompt routinely outperforms a mediocre fine-tune.</p>
""" + diagram(flow_svg(["System\nrole", "Task\ninstructions", "Examples\n(few-shot)", "Input\ndata", "Output\nformat"], height=132),
              "Figure 3.1 - anatomy of a production prompt, in the order the model reads it") + """
<h2 class="sec">Techniques That Actually Move the Needle</h2>
<ul>
<li><strong>Be explicit and specific.</strong> State the task, audience, constraints, and what to do in edge cases. Ambiguity in, variance out.</li>
<li><strong>Few-shot examples.</strong> Two or three input&rarr;output pairs teach format and tone faster than paragraphs of description.</li>
<li><strong>Chain of thought.</strong> Asking the model to reason step-by-step before answering measurably improves multi-step tasks.</li>
<li><strong>Structured output.</strong> Demand JSON with a stated schema (or use the API's structured-output mode) so downstream code can parse the result.</li>
<li><strong>Delimiters.</strong> Fence user data in tags like <code class="inline">&lt;input&gt;...&lt;/input&gt;</code> so instructions and data cannot blur together.</li>
</ul>
<h2 class="sec">Prompts Are Code</h2>
<p>Keep prompts in version control, not in a dashboard textbox. Write down expected outputs
for a handful of test inputs, and re-run them after every prompt edit &mdash; this is the
seed of the evaluation habit Module 12 formalises. And never concatenate untrusted user text
straight into instructions: that is how <strong>prompt injection</strong> happens.</p>
""" + spec("Module 03 &mdash; Key Takeaways", """
<ul>
<li>Structure beats cleverness: role, instructions, examples, data, format.</li>
<li>Version prompts and test them like code.</li>
<li>Separate instructions from untrusted data &mdash; always.</li>
</ul>""")


def m04():
    return """
<h2 class="sec">The Shape of Every Call</h2>
<p>Nearly every hosted LLM &mdash; OpenAI, Anthropic, and most others &mdash; exposes the
same core pattern: send an HTTPS request containing a <strong>list of messages</strong>
(each with a role: <code class="inline">system</code>, <code class="inline">user</code>,
or <code class="inline">assistant</code>), receive the model's reply as a new message.
The API is <strong>stateless</strong>: the model remembers nothing between calls, so your
application resends whatever history matters every time.</p>
""" + diagram(flow_svg(["Your app", "HTTPS request\nmessages[]", "Hosted\nmodel", "Response or\ntoken stream"], height=128),
              "Figure 4.1 - stateless request/response; memory lives in your code, not the model") + """
<h2 class="sec">A Minimal Call</h2>
""" + code('<span class="c"># pip install openai</span>\n'
           '<span class="k">import</span> os\n'
           '<span class="k">from</span> openai <span class="k">import</span> OpenAI\n'
           'client = OpenAI()  <span class="c"># reads OPENAI_API_KEY from env</span>\n\n'
           'resp = client.chat.completions.create(\n'
           '    model=os.environ[<span class="s">"CHAT_MODEL"</span>],  <span class="c"># a current model id, kept in config</span>\n'
           '    messages=[\n'
           '        {<span class="s">"role"</span>: <span class="s">"system"</span>, <span class="s">"content"</span>: <span class="s">"You are a concise assistant."</span>},\n'
           '        {<span class="s">"role"</span>: <span class="s">"user"</span>,   <span class="s">"content"</span>: <span class="s">"Explain embeddings in one line."</span>},\n'
           '    ],\n'
           '    temperature=0.2,\n'
           ')\n'
           'print(resp.choices[0].message.content)') + """
<h2 class="sec">Production Concerns From Day One</h2>
<ul>
<li><strong>Streaming</strong> &mdash; request token-by-token output so users see text immediately instead of waiting for the full response.</li>
<li><strong>Errors &amp; retries</strong> &mdash; handle rate limits (HTTP 429) and transient failures with exponential backoff.</li>
<li><strong>Cost</strong> &mdash; you pay per input + output token; log <code class="inline">usage</code> from every response and watch prompt bloat.</li>
<li><strong>Config, not constants</strong> &mdash; providers retire models and change prices. Keep model IDs and rates in configuration.</li>
<li><strong>Secrets</strong> &mdash; API keys live in environment variables or a secret manager, never in code or a browser.</li>
</ul>
""" + spec("Module 04 &mdash; Key Takeaways", """
<ul>
<li>Messages in, message out, no server-side memory &mdash; you own the conversation state.</li>
<li>Stream for UX, retry with backoff, log token usage from the first prototype.</li>
</ul>""")


def m05():
    return """
<h2 class="sec">Meaning as Coordinates</h2>
<p>An <strong>embedding</strong> is a fixed-length vector of numbers &mdash; typically a few
hundred to a few thousand dimensions &mdash; produced by a model trained so that
semantically similar text lands close together in that space. &ldquo;Reset my password&rdquo;
and &ldquo;I can't log in&rdquo; share almost no words, but their embeddings sit near each
other; that is what makes semantic search possible where keyword search fails.</p>
""" + diagram(flow_svg(["Text", "Embedding\nmodel", "Vector\n[0.02, -0.41, ...]", "Compare by\ncosine similarity"], height=128),
              "Figure 5.1 - text in, coordinates out; similarity becomes geometry") + """
<h2 class="sec">Working With Embeddings</h2>
<ul>
<li><strong>Similarity metric.</strong> Cosine similarity is the default: 1.0 means same direction (same meaning), near 0 means unrelated.</li>
<li><strong>Chunking.</strong> Long documents are split into passages (commonly a few hundred tokens, often with overlap) and each chunk is embedded separately &mdash; retrieval quality depends heavily on chunk boundaries.</li>
<li><strong>One model per index.</strong> Vectors from different embedding models are incompatible; changing models means re-embedding the corpus.</li>
<li><strong>Beyond search:</strong> clustering, deduplication, recommendation, and classification all fall out of &ldquo;meaning as distance.&rdquo;</li>
</ul>
<h2 class="sec">Where This Slots Into the Build</h2>
<p>Embeddings are infrastructure, not a product feature by themselves. In Module 06 we give
them a home that can search millions of vectors in milliseconds; in Module 07 they become
the retrieval half of RAG.</p>
""" + spec("Module 05 &mdash; Key Takeaways", """
<ul>
<li>Embeddings turn &ldquo;how similar is this?&rdquo; into a distance computation.</li>
<li>Chunking strategy quietly decides your retrieval quality &mdash; treat it as a design choice.</li>
<li>Never mix vectors from different embedding models in one index.</li>
</ul>""")


def m06():
    return """
<h2 class="sec">The Problem: Nearest Neighbours at Scale</h2>
<p>Comparing a query vector against ten thousand stored vectors is a simple loop. Against
fifty million, brute force is too slow. A <strong>vector database</strong> solves this with
<em>approximate nearest neighbour</em> (ANN) indexes &mdash; structures like HNSW graphs
that find the closest vectors in milliseconds by accepting a tiny, tunable chance of missing
the exact best match.</p>
""" + diagram(flow_svg(["Documents", "Chunk +\nembed", "ANN index\n(HNSW)", "Query:\ntop-k + filters"], height=128, highlight_last=True),
              "Figure 6.1 - the ingestion and query path every vector store shares") + """
<h2 class="sec">What You Actually Store</h2>
<p>Each record is a triple: the <strong>vector</strong>, the original <strong>text chunk</strong>,
and <strong>metadata</strong> (source, date, tenant, permissions). Metadata matters more than
it looks: real queries are &ldquo;top-5 most similar <em>where product = X and customer =
Y</em>&rdquo;, and filtered search is where engines differ most.</p>
<h2 class="sec">Choosing One</h2>
<ul>
<li><strong>pgvector</strong> &mdash; an extension to PostgreSQL; the right default when your data already lives there and scale is moderate.</li>
<li><strong>Dedicated engines</strong> (Pinecone, Weaviate, Qdrant, Milvus) &mdash; managed scaling, hybrid keyword+vector search, and tenant isolation for larger corpora.</li>
<li><strong>Libraries</strong> (FAISS, Chroma) &mdash; in-process indexes, ideal for prototypes and evaluation harnesses.</li>
</ul>
<p>Whichever you pick, plan for <strong>re-indexing</strong>: content updates, chunking changes,
and embedding-model upgrades all require rebuilding vectors. Treat the index as a derived
artifact of your source data, never the source of truth.</p>
""" + spec("Module 06 &mdash; Key Takeaways", """
<ul>
<li>ANN indexes trade a sliver of recall for orders-of-magnitude speed.</li>
<li>Store text + metadata with every vector; filtered search is the real workload.</li>
<li>The index is derived data &mdash; keep a path to rebuild it from source.</li>
</ul>""")


def m07():
    return """
<h2 class="sec">Closing the Knowledge Gap</h2>
<p><strong>Retrieval-Augmented Generation</strong> connects the two halves you just built.
The model's weights are frozen at its training cutoff and know nothing about your private
data. RAG fixes both limits at answer time: retrieve the most relevant chunks for the user's
question, place them in the prompt, and instruct the model to answer <em>from that context</em>.</p>
""" + diagram(flow_svg(["User\nquery", "Embed\nquery", "Vector\nsearch", "Context +\nquestion", "Grounded\nanswer"], height=132, highlight_last=True),
              "Figure 7.1 - the RAG pipeline: Modules 05 and 06 feeding Module 02") + """
<h2 class="sec">The Prompt Side of RAG</h2>
<p>Retrieval is only half the system. The generation prompt should: fence the retrieved
chunks in clear delimiters, tell the model to answer <strong>only</strong> from the provided
context, require it to say &ldquo;I don't know&rdquo; when the context doesn't contain the
answer, and ask for citations back to chunk identifiers so users can verify claims.</p>
<h2 class="sec">Why RAG Quality Is Retrieval Quality</h2>
<p>When a RAG system answers badly, the cause is usually upstream of the model: the right
chunk wasn't retrieved, was split awkwardly, or was buried under near-duplicates. The
levers that matter, roughly in order:</p>
<ul>
<li><strong>Chunking</strong> &mdash; respect document structure (headings, paragraphs) rather than fixed character counts.</li>
<li><strong>Hybrid search</strong> &mdash; combine vector similarity with keyword matching; exact terms like error codes and product names need lexical search.</li>
<li><strong>Reranking</strong> &mdash; retrieve 20&ndash;50 candidates cheaply, then use a stronger reranker model to pick the best 3&ndash;5 for the prompt.</li>
<li><strong>Freshness</strong> &mdash; re-embed content when it changes; stale indexes produce confidently outdated answers.</li>
</ul>
""" + spec("Module 07 &mdash; Key Takeaways", """
<ul>
<li>RAG = search + prompt discipline; the model is the last step, not the system.</li>
<li>Instruct the model to refuse when context is insufficient &mdash; that is a feature.</li>
<li>Debug retrieval first: most &ldquo;hallucinations&rdquo; are retrieval misses.</li>
</ul>""")


def m08():
    return """
<h2 class="sec">From Text to Action</h2>
<p><strong>Function calling</strong> lets a model do more than write prose. You describe the
functions your application exposes &mdash; name, purpose, JSON-schema parameters &mdash; and
the model, when it decides a function would help, replies not with text but with a structured
call: <em>which</em> function and <em>what</em> arguments. Crucially, <strong>the model never
executes anything</strong>. Your code runs the function, sends the result back, and the model
composes the final answer.</p>
""" + diagram(flow_svg(["User\nmessage", "Model picks\ntool + args", "Your code\nexecutes", "Result back\nto model", "Final\nanswer"], height=132),
              "Figure 8.1 - the two-round-trip pattern behind every tool-using assistant") + """
<h2 class="sec">Declaring a Tool</h2>
""" + code('tools = [{\n'
           '  <span class="s">"type"</span>: <span class="s">"function"</span>,\n'
           '  <span class="s">"function"</span>: {\n'
           '    <span class="s">"name"</span>: <span class="s">"get_order_status"</span>,\n'
           '    <span class="s">"description"</span>: <span class="s">"Look up the shipping status of an order."</span>,\n'
           '    <span class="s">"parameters"</span>: {\n'
           '      <span class="s">"type"</span>: <span class="s">"object"</span>,\n'
           '      <span class="s">"properties"</span>: {<span class="s">"order_id"</span>: {<span class="s">"type"</span>: <span class="s">"string"</span>}},\n'
           '      <span class="s">"required"</span>: [<span class="s">"order_id"</span>]\n'
           '    }\n'
           '  }\n'
           '}]') + """
<h2 class="sec">Engineering the Boundary</h2>
<ul>
<li><strong>Descriptions are prompts.</strong> The model chooses tools by reading your descriptions &mdash; write them for the model, with when-to-use guidance.</li>
<li><strong>Validate everything.</strong> Treat model-produced arguments as untrusted input: check types, ranges, and permissions before executing.</li>
<li><strong>Gate side effects.</strong> Reads can be automatic; writes, payments, and deletions should require confirmation or run in a sandbox.</li>
<li><strong>Return useful errors.</strong> A clear error string sent back lets the model correct itself on the next attempt.</li>
</ul>
""" + spec("Module 08 &mdash; Key Takeaways", """
<ul>
<li>The model proposes; your code disposes. Execution always stays on your side.</li>
<li>Tool descriptions are part of your prompt surface &mdash; version and test them.</li>
<li>Validate arguments and gate irreversible actions.</li>
</ul>""")


def m09():
    return """
<h2 class="sec">The Integration Explosion</h2>
<p>Function calling works, but every team ends up re-wiring the same integrations &mdash;
one bespoke bridge per app-and-tool pair. The <strong>Model Context Protocol</strong> (MCP),
introduced by Anthropic in 2024 and since adopted broadly across the industry, standardises
that wire: any MCP <em>client</em> (a chat app, an IDE, an agent) can talk to any MCP
<em>server</em> (GitHub, a database, your internal API) without custom glue. Build a server
once; every MCP-capable host can use it.</p>
""" + diagram(flow_svg(["Host app\n(chat / IDE)", "MCP\nclient", "MCP server\n(one per system)", "Tools, resources,\nprompts"], height=128),
              "Figure 9.1 - one protocol between any host and any capability") + """
<h2 class="sec">What a Server Exposes</h2>
<ul>
<li><strong>Tools</strong> &mdash; callable actions, exactly like Module 08's functions, discovered at runtime instead of hard-coded.</li>
<li><strong>Resources</strong> &mdash; readable data (files, records, documents) the host can pull into context.</li>
<li><strong>Prompts</strong> &mdash; reusable, parameterised prompt templates the server ships alongside its tools.</li>
</ul>
<p>The client connects, asks the server what it offers, and presents those capabilities to
the model &mdash; discovery replaces integration code.</p>
<h2 class="sec">The Security Trade</h2>
<p>Plugging third-party capability into a model's context is powerful and risky in equal
measure. A malicious or compromised server can attempt <strong>prompt injection</strong>
through tool results; over-broad servers can exfiltrate data. Treat MCP servers like
dependencies: pin versions, grant least privilege, keep dangerous operations behind human
confirmation, and log every call.</p>
""" + spec("Module 09 &mdash; Key Takeaways", """
<ul>
<li>MCP turns M&times;N custom integrations into M+N standard ones.</li>
<li>Capabilities are discovered at runtime &mdash; hosts don't hard-code tools.</li>
<li>Apply dependency-level scrutiny to any server you connect.</li>
</ul>""")


def m10():
    return """
<h2 class="sec">From One Call to a Loop</h2>
<p>Everything so far has been a single round trip. An <strong>agent</strong> wraps the model
in a loop: it plans, takes an action with a tool, observes the result, and decides what to
do next &mdash; repeating until the goal is met or a limit is hit. That loop is what lets a
system handle tasks whose steps can't be enumerated in advance: &ldquo;find the failing
test, fix it, and open a PR&rdquo; rather than &ldquo;answer this question.&rdquo;</p>
""" + diagram(loop_svg(["Plan", "Act\n(call a tool)", "Observe\nresult", "Reflect /\ndecide next"]),
              "Figure 10.1 - the agent loop; exit when the goal is met or budget is spent") + """
<h2 class="sec">Designing the Loop</h2>
<ul>
<li><strong>Bounded autonomy.</strong> Cap iterations, tokens, wall-clock time, and spend. A stuck agent must fail loudly, not loop forever.</li>
<li><strong>Small, sharp toolset.</strong> Five well-described tools beat thirty vague ones; tool confusion is a top failure mode.</li>
<li><strong>State outside the model.</strong> Keep the task list, intermediate results, and history in your application; feed the model only what the next step needs.</li>
<li><strong>Human gates.</strong> Autonomy for reads and drafts; confirmation for anything irreversible.</li>
</ul>
<p>Agents amplify both capability and error: a wrong turn early compounds across every later
step. Start with the simplest workflow that could work &mdash; often a fixed pipeline with
one decision point &mdash; and add autonomy only where it earns its keep.</p>
""" + spec("Module 10 &mdash; Key Takeaways", """
<ul>
<li>Agent = model + tools + loop + stop conditions. The stop conditions are not optional.</li>
<li>Reliability comes from constraints, not from a smarter model.</li>
<li>Escalate to a human at exactly the actions you'd want a junior engineer to ask about.</li>
</ul>""")


def m11():
    return """
<h2 class="sec">When the Loop Needs Structure</h2>
<p>A free-running agent loop is hard to debug, resume, or reason about. <strong>LangGraph</strong>
models the workflow instead as an explicit <em>graph</em>: <strong>nodes</strong> are steps
(call a model, run a tool, apply plain code), <strong>edges</strong> define what runs next,
and <strong>conditional edges</strong> branch on the current state. A shared, typed
<strong>state object</strong> flows through the graph and each node returns updates to it.</p>
""" + diagram(flow_svg(["State in", "Node:\nagent step", "Conditional\nedge", "Node: tool /\nnode: finish"], height=128),
              "Figure 11.1 - explicit control flow: the branch decision is code you can read") + """
<h2 class="sec">A Graph in Six Lines</h2>
""" + code('<span class="k">from</span> langgraph.graph <span class="k">import</span> StateGraph, END\n\n'
           'g = StateGraph(AgentState)\n'
           'g.add_node(<span class="s">"agent"</span>, call_model)      <span class="c"># decides: answer or use a tool</span>\n'
           'g.add_node(<span class="s">"tools"</span>, run_tools)       <span class="c"># executes requested tool calls</span>\n'
           'g.add_conditional_edges(<span class="s">"agent"</span>, should_continue,\n'
           '                        {<span class="s">"tools"</span>: <span class="s">"tools"</span>, <span class="s">"end"</span>: END})\n'
           'g.add_edge(<span class="s">"tools"</span>, <span class="s">"agent"</span>)        <span class="c"># loop back after acting</span>\n'
           'app = g.compile()') + """
<h2 class="sec">What the Graph Buys You</h2>
<ul>
<li><strong>Checkpointing</strong> &mdash; state can persist after every node, so long tasks survive restarts and can resume mid-run.</li>
<li><strong>Human-in-the-loop</strong> &mdash; pause the graph at a node, wait for approval, continue: the Module 10 &ldquo;human gate&rdquo; as a first-class primitive.</li>
<li><strong>Observability</strong> &mdash; every node boundary is a natural place to log, trace, and test.</li>
<li><strong>Multi-agent patterns</strong> &mdash; supervisor/worker and other topologies become subgraphs rather than tangles of callbacks.</li>
</ul>
""" + spec("Module 11 &mdash; Key Takeaways", """
<ul>
<li>Graphs make agent control flow explicit, testable, and resumable.</li>
<li>State is a typed object you design &mdash; the model only ever sees a rendered view of it.</li>
<li>Reach for LangGraph when a plain loop stops being explainable.</li>
</ul>""")


def m12():
    return """
<h2 class="sec">Vibes Don't Scale</h2>
<p>Eyeballing a few outputs works for a demo and fails for a product. <strong>Evaluation</strong>
is the practice of measuring quality systematically: a fixed dataset of inputs, a way to
score outputs, and a habit of re-running the whole set on every meaningful change &mdash;
new prompt, new model, new retrieval setting. Without it, you cannot tell an improvement
from a regression.</p>
""" + diagram(flow_svg(["Eval dataset\n(inputs + expected)", "Run\npipeline", "Score\noutputs", "Compare to\nbaseline", "Ship or\niterate"], height=132, highlight_last=True),
              "Figure 12.1 - the eval loop: same dataset, every change, no exceptions") + """
<h2 class="sec">Three Ways to Score</h2>
<ul>
<li><strong>Programmatic checks</strong> &mdash; exact match, contains-string, JSON-schema validity, code that runs. Cheap, deterministic; use whenever the task allows.</li>
<li><strong>LLM-as-judge</strong> &mdash; a strong model grades outputs against a rubric (correctness, groundedness, tone). Scales to open-ended tasks; must itself be spot-checked against human judgment.</li>
<li><strong>Human review</strong> &mdash; the gold standard and the most expensive; spend it calibrating the other two and auditing high-stakes flows.</li>
</ul>
<h2 class="sec">Building the Dataset</h2>
<p>Start small and real: 30&ndash;50 cases drawn from actual usage beat 500 synthetic ones.
Include the ugly cases &mdash; ambiguous phrasing, missing context, adversarial input,
questions whose correct answer is &ldquo;I don't know.&rdquo; Every production failure you
find gets added as a permanent regression test. For RAG, score retrieval separately from
generation (did the right chunks come back?) &mdash; it tells you which half to fix.</p>
""" + spec("Module 12 &mdash; Key Takeaways", """
<ul>
<li>An eval set is to an AI system what a test suite is to code.</li>
<li>Layer scoring: programmatic where possible, LLM-judge where not, humans to calibrate.</li>
<li>Grow the dataset from real failures &mdash; each one becomes a regression test.</li>
</ul>""")


def m13():
    return """
<h2 class="sec">Contact With Reality</h2>
<p>A pipeline that works in a notebook meets latency budgets, cost ceilings, hostile inputs,
and provider outages the moment real users arrive. <strong>Production AI</strong> is the
layer of engineering that absorbs those shocks without changing what the system does.</p>
""" + diagram(flow_svg(["Request", "Input guards\n+ auth", "Cache\ncheck", "Model call\n(w/ fallback)", "Output checks\n+ response"], height=132),
              "Figure 13.1 - a production request path; the model is one hop among five") + """
<h2 class="sec">The Four Budgets</h2>
<ul>
<li><strong>Latency</strong> &mdash; stream tokens to cut perceived wait; route simple requests to small fast models; parallelise retrieval and pre-work.</li>
<li><strong>Cost</strong> &mdash; cache aggressively (identical and semantically-similar requests), trim prompt bloat, and use the cheapest model that passes your evals per route.</li>
<li><strong>Reliability</strong> &mdash; retries with backoff, timeouts, circuit breakers, and a fallback model or degraded mode for provider outages.</li>
<li><strong>Safety</strong> &mdash; validate inputs against prompt injection, moderate outputs, scope every tool credential to least privilege, and log enough to reconstruct any incident.</li>
</ul>
<h2 class="sec">Shipping Changes Safely</h2>
<p>Treat every prompt, model, and retrieval change like a deploy: run the Module 12 eval
suite offline, then canary to a small slice of traffic, compare live metrics against the
control, and keep one-click rollback. Model upgrades are not drop-in &mdash; behaviour
shifts even between minor versions of the &ldquo;same&rdquo; model family.</p>
""" + spec("Module 13 &mdash; Key Takeaways", """
<ul>
<li>Wrap the model: guards in front, checks behind, cache beside, fallback beneath.</li>
<li>Route by difficulty &mdash; most traffic doesn't need your biggest model.</li>
<li>Evals offline + canary online = the only safe way to change anything.</li>
</ul>""")


def m14():
    return """
<h2 class="sec">Keeping It Alive</h2>
<p><strong>MLOps</strong> &mdash; and its LLM-era sibling often called <em>LLMOps</em> &mdash;
is the operational discipline that keeps an AI system healthy over months, not demos.
Classical MLOps centres on training pipelines and model registries; in an AI-engineering
stack the same rigour applies to a different set of artifacts: <strong>prompts, retrieval
indexes, eval datasets, model versions, and configuration</strong>.</p>
""" + diagram(loop_svg(["Version\neverything", "Deploy\n(canary)", "Monitor\n+ trace", "Detect drift,\nfeed back"]),
              "Figure 14.1 - the operations loop; monitoring feeds the next iteration") + """
<h2 class="sec">The Practices That Matter</h2>
<ul>
<li><strong>Version everything together.</strong> A release is a pinned tuple: model ID + prompt version + index snapshot + config. Any answer in production must be reproducible from its tuple.</li>
<li><strong>Trace end-to-end.</strong> For each request, record the full chain &mdash; input, retrieved chunks, tool calls, output, latency, token cost &mdash; so any bad answer can be replayed and diagnosed.</li>
<li><strong>Monitor quality, not just uptime.</strong> Sample live traffic through your LLM-judge rubrics; watch refusal rates, groundedness, and user feedback alongside p95 latency and cost per request.</li>
<li><strong>Watch for drift.</strong> User behaviour shifts, documents go stale, providers silently update models. Scheduled eval runs against production snapshots catch decay before users do.</li>
</ul>
<p>The loop closes where the course began: monitoring surfaces failures, failures become
eval cases, eval cases drive the next prompt or pipeline change &mdash; and the build
continues.</p>
""" + spec("Module 14 &mdash; Key Takeaways", """
<ul>
<li>Reproducibility = versioned tuple of model, prompt, index, and config.</li>
<li>Tracing turns &ldquo;the bot said something weird&rdquo; into a replayable bug report.</li>
<li>Quality monitoring is continuous evaluation &mdash; the loop never finishes.</li>
</ul>""")


BODIES = [m01, m02, m03, m04, m05, m06, m07, m08, m09, m10, m11, m12, m13, m14]
