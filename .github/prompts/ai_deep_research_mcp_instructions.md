Great. I’ll prepare a complete reference manual and implementation guide for building a self-hosted, AI-powered deep research system similar in spirit to Firecrawl’s Deep Research tier. The guide will be designed for your homelab setup and written as a single markdown file your AI agents (like Claude or Copilot) can execute autonomously.

The document will cover:

* Reverse-engineering Firecrawl’s capabilities
* Deep-dive decomposition of research system components (crawl agents, doc loaders, semantic parsing, retrieval, summarization, RAG pipelines, orchestration, observability, etc.)
* A secure, modular, extensible implementation plan using industry-aligned tools (LangChain, FastAPI, Haystack, etc.)
* Full atomic skill tree for each component
* Detailed hardware/network setup for homelab deployment
* Links to core academic and industrial resources

I’ll let you know when the full reference is ready.


# Building a Self-Hosted AI-Powered Deep Research System

## Introduction

Modern research tasks often require sifting through vast amounts of online information, extracting key insights, and compiling them into coherent reports. This document is a comprehensive reference manual and step-by-step guide for building a **self-hosted, AI-driven deep research system** – one that mirrors the capabilities of Firecrawl’s “Deep Research” tier. Such a system will autonomously crawl the web for academic-grade information, index it semantically, and use retrieval-augmented generation (RAG) to produce detailed answers with source citations. We will design this system to run on a homelab server, enabling local AI agents (like IDE assistants or custom bots) to execute research tasks securely and efficiently without relying on external cloud services.

We will adopt a **recursive decomposition** approach in explaining the system: breaking it down into atomic subsystems and then detailing each component. The guide covers everything from high-level architecture and planning to low-level implementation details. Topics include headless browsing for web scraping, crawler orchestration logic, document parsing and chunking, vector database indexing, intelligent retrievers and rankers, LLM-based summarization, citation insertion, and search heuristics. We will also discuss tooling choices (open-source frameworks and libraries), homelab deployment considerations (networking, rate limits, local LLM options), security best practices, testing and observability, and maintenance workflows. Throughout the guide, we reference academic work and industry resources to ground our approach in proven techniques.

## System Overview: Deep Research Workflow

At a high level, the deep research system acts like an autonomous research analyst that can handle a query end-to-end. It doesn’t just perform a single web search – it **breaks down complex queries into subtopics, iteratively explores multiple sources, and synthesizes the findings into a cohesive report with citations**. In essence, given a user query, the system will:

* **Analyze the query** to identify key themes or sub-questions.
* **Search the web** for each theme and fetch relevant documents (web pages, PDFs, etc.).
* **Parse and index** the content of those documents into a semantic vector store.
* **Iteratively refine** the search if needed, digging deeper based on initial findings (controllable via depth settings).
* **Generate a comprehensive answer** or report using an LLM, *augmented by retrieved facts from the indexed data* to ensure accuracy.
* **Attribute sources** for each fact or quote in the answer, providing a list of references for transparency.

Firecrawl’s own Deep Research API follows a similar pattern. It automatically performs multi-step web exploration and returns a result object containing a *final analysis* (the synthesized answer), the list of *sources* used, and an *activity log* of the research steps. This approach turns a single query into a thorough investigation: *“Think of it as giving your app or workflow a dedicated research analyst — on demand.”*. Unlike a standard search engine which just gives a list of links, a deep research system actively **navigates between sources and composes an informed answer**.

To illustrate the architecture, consider the conceptual data flow in a retrieval-augmented generation system:

&#x20;*Conceptual overview of a retrieval-augmented generation (RAG) pipeline: the system retrieves relevant external knowledge for a user query and feeds it into an LLM, which then produces a fact-based answer (with citations).*

In our design, the “external knowledge” will come from live web content gathered via crawling. By integrating a non-parametric memory (the indexed web content) with the generative model, we ensure the language model can provide up-to-date and verifiable information. This RAG approach is known to improve accuracy and reduce hallucinations by grounding the output in retrieved evidence. It also inherently supports provenance: every claim can be traced back to a source, addressing the critical need for trustworthy and **source-verifiable** answers in research applications.

### Architectural Goals and Constraints

When designing this system, we must keep in mind both functional and non-functional requirements. Functionally, the system must handle complex queries, navigate the web, extract data, and generate answers with cited sources. Non-functional requirements (quality attributes) are equally important: we need **reliability, maintainability, scalability, and security** in the software architecture. Reliability ensures the system behaves consistently (e.g. robust against crawl errors or timeouts), maintainability ensures the codebase can be easily updated (e.g. to support new file types or models), scalability allows the system to handle growing workloads (e.g. larger document sets or concurrent queries), and security is critical since the system interacts with external websites and possibly private data. We will address these qualities through design choices like modular architecture (for maintainability), using proven libraries and sandboxing (for reliability and security), and allowing configurable resource limits (for scalability, e.g. adjusting number of crawler threads or limiting memory usage).

## Core Components and Design

We now break down the system into its core components, describing the role of each and how they interact. The architecture can be thought of as a pipeline or a set of services working in concert. Below is a summary of the main components, each detailed in subsequent sections:

* **1. Query Analyzer & Planner:** Interprets the user’s query and formulates a search strategy (including possible sub-queries or topics to explore).
* **2. Intelligent Web Crawler:** Uses headless browsing to fetch pages. Orchestrates multi-step crawling and adheres to search heuristics (like which links to follow or when to stop).
* **3. Document Loaders & Parsers:** Handle different content types (HTML pages, PDFs, etc.), extracting clean text and metadata from each document.
* **4. Text Chunking & Embedding:** Splits parsed documents into manageable chunks and converts them into vector embeddings for semantic indexing.
* **5. Vector Store (Semantic Index):** Stores embeddings in a database that allows similarity search. This acts as the system’s external knowledge base.
* **6. Retriever & Ranker:** Given a query, retrieves the most relevant chunks from the vector store. May include a ranking step to improve relevance of results.
* **7. Summarizer (LLM Answer Generator):** A large language model that takes the retrieved information and composes a final answer/summary, with references.
* **8. Citation Manager:** Ensures that the answer includes proper source citations and that a list of sources is compiled and returned.
* **9. API Interface & Orchestration:** The runtime layer that ties everything together – coordinating the above components, managing asynchronous tasks, and providing a CLI or API for agents/users to interact with the system.

Each of these components will be designed with modern, open-source tools in mind, and we’ll highlight specific library choices in context. Next, we delve into each component and outline how to implement it step by step.

### 1. Query Analysis and Search Planning

The first step is to break down the initial query into effective search queries and a plan of attack. Complex research questions often contain multiple facets. For example, a query like *“Explain the latest developments in quantum computing and their implications for cryptography”* has at least two facets (quantum computing developments, and impact on cryptography). A good research system will **decompose such multi-part questions into subtopics** so that each can be researched in turn. This is analogous to how a human researcher might outline the aspects of a topic before diving in.

**Techniques for Query Decomposition:** We can employ an LLM prompt or heuristic rules to generate sub-questions from the main query. A chain-of-thought approach can be useful: recent research on *Tree-of-Thought* prompting treats reasoning as a search through a tree of ideas. We can prompt a language model with something like: *“What are the key subtopics or questions one should explore to answer the query X? List 3-5 subtopics.”* The model’s output can guide our search. This aligns with the idea of **recursive decomposition** – tackling a big question by smaller, atomic questions.

Another approach is to generate multiple phrasings of the query to cast a wide net on search. Firecrawl’s Deep Research, for instance, **creates multiple parallel search queries** focusing on different angles of the topic. For example, given a query about “programming memes” (as in Firecrawl’s sample), the system spawned parallel searches like “popular programming memes and their origins,” among others. We can mimic this by prompting an LLM to produce a few alternative search phrases or by using templates (e.g. “What is the history of X?”, “latest research in X”, “benefits and challenges of X”). These variations help ensure we don’t miss relevant information that a single query wording might overlook.

**Search APIs and Tools:** Once we have query variants, the system uses a web search component to get initial results (URLs and snippets). Since our solution is self-hosted, we want to avoid reliance on proprietary search engines if possible. A few options for implementation:

* **Use a Search API:** Leverage an API like Bing Web Search or Google Programmable Search (Custom Search Engine). These provide JSON results for queries. Bing’s API, for example, can return the top N results with titles and snippets, which we can then feed into our crawler. This requires an API key and has call quotas.
* **Self-hosted Meta-Search:** Deploy an open-source metasearch engine like **SearxNG**. SearxNG can aggregate results from multiple search engines and can be self-hosted, giving you a private search endpoint. Your system could send queries to a local SearxNG service and get back a list of result URLs.
* **Direct Web Scraping of a Search Engine:** In principle, one could launch a headless browser to Google or Bing and scrape the results page. This is possible (and some libraries exist for it), but it’s brittle and against most ToS, so using an API or Searx is preferable for reliability.

Whichever method is chosen, we should implement **rate limiting** and polite usage. For example, if using an API, respect the QPS (queries per second) limits. If self-scraping or using Searx, include a small delay between queries to avoid being flagged as a bot. The system should also consider **regional/language settings** if needed (for academic research, often global English results are fine, but this could be configured).

**Search Heuristics:** In planning the search, we can incorporate a few heuristics:

* Prefer authoritative domains (for academic info, maybe prioritize Google Scholar, arXiv, Wikipedia, .edu domains, etc.).
* Include the current year or “2025” in a query if recent developments are asked, to get up-to-date results.
* If the query explicitly names a site or source (e.g. “Find information from WHO about...”), then bypass general search and go directly to that site’s search or use a site: query filter.

The outcome of this phase is a set of initial target URLs (and possibly some context like the snippet or the reason we chose them). Now the system moves on to acquiring those pages.

### 2. Intelligent Web Crawling and Browsing

With a list of URLs in hand, the system needs to visit each and extract their content. Web pages today are dynamic and often require rendering. We will use **headless browsing** to ensure we can handle all content (including JavaScript-heavy sites). A headless browser is a web browser without a GUI that can be controlled programmatically – ideal for server environments.

**Headless Browser Choice:** We recommend **Playwright** (Python library) or **Puppeteer** (Node) for this task. Playwright has excellent support for headless Chromium/Firefox/WebKit and can bypass many anti-bot measures by simulating real user behavior. It also allows automation of clicks, scrolling, waiting for network idle, etc., which is helpful if we need to log in or click “Load more” buttons. In our Python-based design, Playwright is a top choice (it’s broadly used in scraping and testing and supports headless Chrome out of the box). Another option is **Selenium** (with headless ChromeDriver) but Selenium is heavier to set up and oriented more towards testing. Playwright’s developer API is quite straightforward for scraping use cases.

Using a browser will handle cookies, dynamic content, and so on. For simpler pages (static HTML), a lightweight approach like `requests` to fetch the HTML might suffice (and be faster). We can implement a **content fetcher** that tries an HTTP GET first, and only if it detects the need for rendering (e.g., the HTML is mostly script tags or the site requires login) does it fall back to the headless browser. This hybrid strategy can improve performance by not using the browser when unnecessary.

**Crawler Orchestration:** The crawler component manages how we traverse not just the initial list of URLs but potentially follow links to go deeper. Firecrawl’s Deep Research allows specifying a `maxDepth` (how many layers of links beyond the initial URLs to follow) and `maxUrls` (cap on total pages). We should implement similar controls. For example, `depth=1` means we only fetch the initial URLs; `depth=2` would mean fetch initial URLs, parse them, and also fetch some of the links found on those pages that appear relevant.

In practice, an **iterative deepening** can be done: after fetching and parsing a page, the system can scan it for new links that might be worth exploring (perhaps those containing certain keywords related to the query). Those go into a queue for crawling if within depth limit. We must be careful to avoid crawling irrelevant or endless links – a heuristic could be to only follow links that stay within the domain of the initial result or that clearly point to additional info (e.g., a link titled "References" or "Related Work"). Another approach is to integrate the search step at each depth: i.e., after reading initial pages, formulate new search queries based on gaps or new terms encountered, then search and fetch those. This becomes a more agent-driven approach where the system alternates between reading and searching.

To keep things manageable, our initial implementation might limit itself to depth 1 or 2. That usually covers the direct search results and maybe one hop (like if a blog post references a research paper link, we fetch the paper too). The orchestration will also **parallelize fetches** for efficiency: since I/O waiting (network and rendering) can be slow, running multiple headless browsers concurrently is useful. Firecrawl’s hosted service, for instance, uses multiple concurrent browser instances to speed up crawling. On a homelab, we can allow perhaps 3–5 parallel page fetches (configurable) to balance speed with resource usage. Playwright can launch multiple browser contexts or we can use a browser pool.

**Anti-bot and Politeness Measures:** When scraping at scale, websites might block frequent requests. Using a **rotating proxy** service or at least cycling through different user-agent strings can help avoid being blocked. Since this is a personal homelab setup, the volume is likely low and targeted (we’re not crawling thousands of pages), so aggressive anti-bot countermeasures are less likely. Still, we should:

* Randomize user-agent and perhaps other client fingerprints.
* Honor `robots.txt` for domains, or at least have a setting to do so for ethical compliance. For academic research, one may choose to bypass `robots.txt` for non-commercial use, but it’s best to have that choice explicit.
* Not hit the same server too rapidly – if our parallel fetches target the same domain, we might serialize those or insert delays (e.g., don’t fetch 5 pages from the same site simultaneously).

**Logging and Progress:** The crawler should log each action (this will feed into our activity log). For example: `[search] Found 15 results`, `[fetch] Crawling URL X`, `[fetch] Completed URL X (size 50KB)`, or `[error] Timeout fetching Y`. Maintaining this log is crucial for transparency and debugging. We can expose this progress in real-time (e.g., streaming to a UI or CLI) so that the user/agent can see what the system is doing. Firecrawl’s Deep Research returns such a timeline of activities for traceability.

At the end of this phase, we will have a collection of raw content (HTML pages, PDFs, etc. in text form) sitting in memory or on disk. Now we move to parsing and understanding that content.

### 3. Document Loading and Parsing

Different sources come in different formats – HTML web pages, PDF files, maybe Word documents, JSON APIs, etc. Our system needs a **document loader** layer that can take a URL or file and output extracted text and metadata in a uniform format (e.g., plain text or Markdown plus source info). This is akin to the “unstructured data ingestion” part of many RAG pipelines.

**HTML Parsing:** For HTML content (the majority of web pages), we should extract the main article or body text and eliminate boilerplate (navigation menus, ads, etc.). Tools like **readability.js** (used in browser reader modes) or Python’s **Goose** or **trafilatura** can do automatic main-content extraction. A simpler approach is to use **BeautifulSoup** to parse the DOM and apply heuristics, such as looking for `<article>` tags or selecting `<p>` text from the largest `<div>` block. There is also the **Unstructured** Python library (from UnstructuredIO) which is specialized for parsing documents (HTML, PDFs, etc.) into clean text segments. We could integrate that library for convenience – for example, `unstructured.partition_html` will give a list of elements (paragraphs, titles, etc.) from an HTML string.

We also capture the **metadata**: at least the page title and the source URL. The title is often in the `<title>` tag or `<meta property="og:title">`. This can later help in labeling sources (e.g., “Source: *Example.com - Guide to X*”).

**PDF and Other Formats:** PDF files might appear in our results (especially for academic content). We should handle them via a PDF parser like **PyMuPDF (fitz)** or **pdfminer.six**. These can extract text from PDFs. Unstructured library also has `partition_pdf` which uses OCR if needed or extracts text layout. For our needs, continuous text is enough, though we should be wary that PDFs often have line breaks mid-sentence. We may need to rejoin lines intelligently or use Unstructured’s output which often handles that.

If the system needs to fetch data from APIs or JSON (for example, a site might provide data via a JSON endpoint), we can incorporate that, but since our focus is academic research, it’s mostly web pages and docs. However, the design should be extensible: e.g., have a loader for JSON that just pretty-prints it or one for CSV if needed.

**Cleaning and Normalization:** Once text is extracted, we normalize it. This includes:

* Removing any duplicate content (navigation repeated on every page, etc.). Readability extraction helps avoid that.
* Removing scripts or any non-text content that slipped through.
* Possibly converting to **Markdown** format, since LLMs often digest Markdown well (and Firecrawl also outputs markdown by default). For instance, if the source had headings, we could keep them or denote them in Markdown. However, for embedding and summarization, plain text is fine; formatting is more relevant if we were preserving structure. We can mostly treat everything as plain text paragraphs, and perhaps mark the title as a heading.

Each parsed document can be represented as an object with fields like: `{ "source": <URL>, "title": <title>, "text": <full cleaned text>, "chunks": [] }`. We leave the `chunks` field for the next step.

We should also record the length of the text and perhaps limit overly large documents. If a page is extremely long (e.g., an entire book or large PDF), it might be wise to impose a limit or at least be mindful during chunking to not overload memory. But generally, chunking will break those up.

At this stage, the system has a collection of texts from various sources. Next, we prepare these texts for efficient semantic search.

### 4. Chunking Strategy and Semantic Embeddings

**Purpose of Chunking:** Language models have context length limits, and vector search works best on reasonably sized text pieces. Therefore, we **split documents into chunks** (also called segments) before embedding them. Chunking ensures that each semantic unit (paragraph or section) is indexed separately, so that a query can retrieve the specific part of a document that’s relevant, rather than an entire document which might dilute relevance.

**Chunk Size:** A typical chunk might be in the range of 200 to 300 words (which is roughly 1000 to 1500 characters, or e.g. 256 tokens if thinking in token units). We want it large enough to contain a complete thought or answer a question, but not so large that irrelevant info pollutes the embedding. Many implementations use \~512 tokens as an upper bound for chunk size. We also often use an **overlap** between chunks (e.g., 20-30% overlap) to avoid cutting important context at boundaries. For example, if chunk1 ends halfway through a paragraph, chunk2 might start a few sentences earlier to provide continuity. This overlap helps the retriever not miss relevant sentences that fell on a boundary.

**Method:** We can use utilities from LangChain (like `CharacterTextSplitter` or `RecursiveTextSplitter`) where you can specify a target chunk size and overlap. The “recursive” splitter will try to split by sections or paragraphs first, preserving structure, but ensure the chunks are below the size limit. Alternatively, a custom script can split by paragraphs and then by sentence if needed to fit size.

**Example:** Suppose we have a 1200-word article. We might split it into 5 chunks of \~240 words each, with a 40-word overlap. Each chunk will carry a reference to the source (e.g., “Doc1 Chunk A”). It’s helpful to also note the position in source (like a page number or paragraph index) in metadata, especially if we want to show snippet context later.

**Embedding the Chunks:** Once we have chunks, we generate vector embeddings for each. An embedding is a numerical representation of the text’s meaning. We will use a **pre-trained embedding model**. Since we aim for a self-hosted solution, an open-source model is preferable to calling an API like OpenAI’s. Some options by 2025:

* **Sentence Transformers (SBERT)** models (e.g., `all-MiniLM-L6-v2` or newer). These are fast and give 384-dimensional embeddings suitable for semantic search.
* **Hugging Face’s InstructorXL** or **GPT4All-J embedding** models – there are models specialized for embeddings which might be larger but more accurate.
* **Local LLM embedding**: if we already have a local model like Llama 2 running, we could use a smaller version fine-tuned for embeddings or use the LLM’s embedding API (if available). For instance, some LLM runtimes allow extracting the last hidden state as an embedding. However, it’s simpler to use a dedicated embedding model for speed and quality.

We’ll proceed assuming we use a smaller transformer specifically for embedding. We load that model at startup (using a library like HuggingFace’s `transformers` or the `sentence_transformers` package). Then for each text chunk, we compute the embedding vector. This typically results in a vector of length a few hundred (the model defines that).

**Vector Store Selection:** Now we store these vectors in a vector database. Two popular open-source choices:

* **Chroma DB:** an easy-to-use, embedded vector store (it can run in-memory or persist to disk). It has a Python API and can perform similarity search (kNN) with cosine or Euclidean distance. Chroma is great for a lightweight setup and can scale to millions of embeddings on a single node.
* **Weaviate:** a standalone vector database that can run as a container. It offers advanced features (like hybrid search, filtering by metadata, GraphQL queries) and can scale distributed, but it’s heavier than Chroma. Running Weaviate on a homelab is feasible (with Docker), but for simplicity you might start with Chroma or even a local **FAISS** index.
* Other options: **FAISS** (Facebook AI Similarity Search) is a library (no server) that LangChain can use under the hood. **Milvus** or **Pinecone** are others, but Pinecone is cloud-hosted (not self-hosted unless using their enterprise).

Let’s assume we use **Chroma** for our design (as it’s Pythonic and simple to integrate). We initialize a Chroma collection, configure it to use cosine similarity on the embeddings. We store each chunk’s vector with metadata: source ID, source URL, chunk text (could store or at least a reference to it), maybe chunk title or section if available.

**Indexing step:** At runtime, after crawling and parsing, we’ll feed all chunks to the vector store. This is the **indexing** phase where we populate our knowledge index for the query. In a persistent setup, one might keep indices across queries, but typically for a one-off deep research session, we create a fresh index per query (unless you expect repeated queries on similar topics and want to reuse data, which is a possible extension – e.g., cache vectors for popular URLs).

Now we have a semantic index of the gathered knowledge. The next component will query this index to pull out the information relevant to answering the user’s question.

### 5. Retrieval and Ranking of Relevant Information

Once the knowledge base is built, the system must **retrieve** the most relevant pieces of information to feed into the answer generator. This step is critical: if the retriever fails to fetch an important fact, the final answer might be incomplete or incorrect. Our retriever will use the vector store to get similarity matches for the query.

**Query Embedding:** We take the original user query (or a refined version of it) and obtain its embedding using the same model used for documents. This gives us a query vector in the same semantic space as the chunk vectors.

**Similarity Search:** Using the vector DB (Chroma), we perform a similarity search with the query vector to find the top *k* most similar chunks. We might choose *k* around 5 or 10 initially – enough to have substantial info but not too many to overwhelm the LLM context. The search returns those chunks and their metadata. Each chunk likely corresponds to a particular source and section.

This process essentially implements the *retriever* in retrieval-augmented generation. The quality of retrieval depends on the embedding model and how well the query was phrased. Sometimes a user query might be broad, and the top results might all be from one source. It’s often a good idea to enforce some diversity (e.g., at most 2 chunks from the same source in the top results) to ensure the answer can draw from multiple viewpoints. We can implement that by post-processing the retrieved set: if too many chunks are from one article, consider taking the top 2 from that and then skip to the next distinct source for the others.

**Ranking or Filtering:** In addition to raw similarity, some systems apply a secondary **re-ranking** using a more precise model. For instance, Microsoft’s Orqa or Facebook’s DPR are advanced, but even simpler: we could use a small cross-encoder model that takes the query and each retrieved chunk and outputs a relevance score, then sort by that. This can slightly improve precision at the cost of more compute. In our homelab scenario, this might be optional. Alternatively, a cheap heuristic filter: if a chunk’s similarity score is below a certain threshold, maybe it’s not actually relevant and we drop it. Or if the query contains a keyword that none of the chunk’s text contains, that chunk might be a false positive from embedding similarity (rare but possible with semantic search). A hybrid search approach combines keyword and vector methods to mitigate this, but implementing a full hybrid might be overkill. Simpler: we could ensure that each retrieved chunk shares at least one significant keyword with the query (stopwords excluded), as a sanity check.

**Example:** If the query is *“quantum computing developments 2024 cryptography”*, we expect chunks that mention those terms or synonyms. If a retrieved chunk is about “quantum entanglement experiment in 2019” and doesn’t mention cryptography, it might be less useful unless it’s providing background. We could still include it if our aim is comprehensive, but if we have many more directly relevant chunks, we’d prioritize those.

At the end of retrieval, we have a set of relevant text snippets with source references. Now it’s time to generate the final answer using these.

### 6. Answer Synthesis with LLM (Retrieval-Augmented Generation)

This is where the **Large Language Model (LLM)** comes into play, using the retrieved information to compose a final answer or report. Our goal is to have the LLM integrate the facts from the sources and produce a well-structured answer in Markdown (including sections, bullet points, etc., as appropriate), with citations referencing the sources.

**Choosing an LLM:** Since we want a self-hosted solution, we’ll consider running an open or locally hosted model:

* If powerful hardware (GPU) is available in the homelab, a fine-tuned large model like **Llama 2 70B** or **GPT-JT** could be used. There are also instruction-tuned smaller models (13B or 30B) that might be sufficient for many tasks.
* If no GPU and limited CPU, one might opt for optimized 7B-13B models (like those quantized to 4-bit running on CPU, e.g. via LLama.cpp). They might not be as fluent or factual as GPT-4, but could do a decent job with the right prompt and when grounded with real data.
* Another approach is to use an on-premise API solution like **Ollama** or **OpenWebAI** which can serve models efficiently. For example, **Ollama** can run Llama 2 or other models and provides an HTTP API to stream responses. This abstracts a lot of the complexity of directly interfacing with the model.
* The user mention of *Claude or VSCode Copilot agents* suggests perhaps using a closed model by proxy (Claude’s API could be called if one has a key, or Copilot’s underlying model if available). However, to keep strictly self-hosted, we won’t rely on those. Instead, ensure our architecture can swap in a local model or an API. We’ll design our system such that the LLM interface is modular – e.g., an `LLMClient` that could either call a local server (like Ollama’s endpoint) or call OpenAI/Anthropic if configured.

**Prompt Construction:** We need to feed the LLM the question and the retrieved data, and ask it to produce a cited answer. A common prompt format for RAG is:

```
SYSTEM: You are a helpful research assistant that provides answers with citations.
USER: Question: "<user query>"

We have gathered the following information:
[1] "<source 1 text snippet>"
[2] "<source 2 text snippet>"
...
[n] "<source n snippet>"

Using only the information above, write a comprehensive answer to the question. Cite the sources in square brackets (e.g., [1], [2]) next to the facts. If the information is insufficient, say you couldn't find the answer.
ASSISTANT:
```

We provide the model a numbered list of source excerpts. By enumerating them \[1], \[2], etc., we make it easy for the model to cite. This technique is used by many QA systems to enforce citation usage. It’s important to instruct the model to **only use the provided info** – this mitigates hallucinations. The model should not make up new facts; it should ideally stick to what’s in \[1]…\[n]. If our retrieval worked well, those snippets contain the needed facts.

We should also include the source **titles or context** if possible in the snippets to give the model more cues. For example, instead of raw snippet text, it might be beneficial to prepend something like “\[1] (Source: *Nature 2024 article*) … snippet text …”. However, too much might clutter the context window.

**Controlling Output Format:** We want the final output in Markdown, possibly with sections if it’s a long report. We can hint at structure in the prompt if needed (like “Provide a summary with an Introduction, key points, and a Conclusion.”). Since our user is an AI agent or developer, a well-structured Markdown output is desired (with appropriate headings, lists, etc.). We should test the prompt to see how well the model follows formatting instructions. We may also instruct: “Use clear headings and bullet points where relevant, and ensure the answer is in Markdown format.”

**Generation Process:** We will call the LLM with the constructed prompt. If using a library or API that supports streaming (both OpenAI API and local servers like Ollama do), we can stream the tokens of the answer back to the client application so that the user can see it unfold (and possibly cancel if needed). This improves UX. In a CLI scenario, streaming just means printing as it comes. In a web UI (like Streamlit or a browser app), it could mean updating a text box incrementally.

**Citation Embedding in Text:** As the LLM generates text, it should include citations like “\[1]” referencing the sources we labeled. We will need to post-process or interpret those. Specifically, after generation, the system can map “\[1]” to the actual source URL or reference info from our stored metadata. For the final output, we may choose to append a references section: e.g.:

**References:**

1. Source 1 Title – URL
2. Source 2 Title – URL

This way, the user can click or inspect sources. Firecrawl’s Deep Research returns a structured list of sources with titles and URLs, which is analogous to our approach. The presence of inline citations makes the answer trustworthy, as the user can verify each claim.

We must be prepared that the model might make a citation mistake (like citing \[3] when we only gave \[1] and \[2]). We can minimize this by clearly enumerating and maybe not giving more than, say, 5 sources to reduce confusion. If it does happen, a post-processing step could catch an invalid citation and correct or remove it (e.g., if “\[3]” appears but we only have 1-2, we might replace it with the closest or remove it). Logging these occurrences is good for debugging.

**Ensuring Accuracy:** While the LLM is guided by the sources, we should still manually or programmatically verify critical facts. The system can be configured in a “verification mode” where after generation, it cross-checks the answer’s sentences against the source texts (e.g., using a simple search to see if the sentence is present in source). However, this might be beyond initial scope. At least, the inclusion of citations means a user can do the verification themselves. (In a highly rigorous setting, you’d highlight any statements not backed by provided sources, but that’s an advanced feature.)

**Multi-Pass Answer Refinement:** We could enhance the answer by having a second LLM pass or agent. For example, the **first pass** provides a direct answer. A **second pass** (maybe a different prompt or even different model) could take that answer and “edit” or “expand” it, maybe improving clarity or adding an “Introduction” and “Conclusion” around it. In the Unwind AI tutorial, they used a two-agent approach (one to gather info, another to elaborate). In our design, this is optional. It can be as simple as taking the final answer draft and prompting an LLM: “Polish the above answer, ensuring it is well-structured. Keep the citations as they are.” This might yield a more readable result. We must be careful that a second pass doesn’t break or hallucinate citations. Likely, it should not add new info, just reorganize or clarify. This can be considered if the initial output quality is not satisfactory. For now, a single-pass generation with a decent model should work.

By the end of this stage, we have the answer content ready. The final step is to wrap up and return results, including making sure the sources are properly referenced.

### 7. Source Attribution and Citation Management

A hallmark of an academic-level research system is proper citation of sources. We have already baked citation mentions (“\[1]”, “\[2]”, etc.) into the answer. Now we focus on **managing the source references** to accompany the answer. The system should output not only the answer text but also a structured list of all sources used, with identifiers matching the citations.

**Compiling the Source List:** We have metadata for each chunk in the vector store, including the source URL and possibly the title. We should consolidate this at the document level. For example, if chunk1 and chunk2 both come from the same source URL, they correspond to one source in the final list. So, we can collect unique source URLs from all retrieved chunks that were fed into the answer. Ideally, we use the *titles* of those pages as the reference titles in the bibliography.

We then sort them by the numbering we assigned in the prompt (which likely corresponds to relevance order or so). In our prompt, we labeled source excerpts \[1..n] arbitrarily – presumably \[1] was the most relevant chunk’s source, \[2] the next, etc. We should maintain that same numbering when listing the references to avoid confusion.

**Formatting References:** In Markdown, a simple way is to list as:

1. **Title of Source 1** – [https://source1.url](https://source1.url)
2. **Title of Source 2** – [https://source2.url](https://source2.url)

This is human-readable. Since our answer is likely consumed by an AI agent or developer, clickable links (if in a rendered environment) are useful. Another format could be footnote style, but enumerated list is straightforward.

If some sources don’t have a clear title (maybe for PDFs, we might only have the filename or a snippet as title), we could use the domain or a brief description. It’s important to include enough detail so the user can identify it. Firecrawl’s API returns for each source: the URL, title, and a short description if available. We can try to extract meta description tags from HTML to serve as a description if needed.

**Citation Integrity:** The system should double-check that every `[number]` in the answer corresponds to a source in the list. It’s possible the LLM output cited \[1] and \[2], but maybe also \[3] which it hallucinated. We can detect that because we know how many sources we provided. If an out-of-range citation is found, one approach is to replace it with a “(?)” or footnote indicating missing source. But ideally, with careful prompt and not giving too many sources at once, this is rare. If the model cites something incorrectly (e.g., puts \[2] where \[1] would’ve been correct for that fact), it’s harder to detect automatically. Manual review is the best guard. Future improvements might include using the activity log to highlight which source was used for which sentence.

**Output Example:** The final answer might look like:

> **Q:** What are the latest developments in quantum computing and their implications for cryptography?
> **A:** *... (answer paragraphs) ... quantum computers have achieved stable 127-qubit operations as of 2024, breaking previous records. This progress has led experts to believe that quantum factoring of 2048-bit RSA is feasible within a decade. Consequently, research into post-quantum cryptography has accelerated, focusing on lattice-based algorithms resistant to quantum attacks. ... (more content with \[2], \[3] etc.) ...*
>
> **References:**
>
> 1. *Quantum Computing Breakthroughs of 2024* – example.com/quantum-2024-news
> 2. *Post-Quantum Cryptography Report, NIST (2025)* – nist.gov/PQC-report-2025.pdf
> 3. *Cryptography in the Quantum Era (Blog)* – securityblog.com/quantum-crypto

*(The above is an illustrative style – the actual content would depend on sources.)*

In that example, the bracketed numbers in the text match the reference list. The user or agent reading this can follow those links to verify each claim.

This citation-focused approach aligns with academic writing standards and ensures **traceability** of information. It transforms the LLM from a black-box oracle into a tool that *shows its work* – crucial for trust in a research assistant. As Nicholas Camara (CTO of Firecrawl) noted, source attribution is a key feature of automated research to allow manual verification of critical information.

### 8. Iterative Deepening and Multi-Hop Research (Optional)

*(This section is optional for initial implementation, but outlines how the system can go “deeper” if one round of research is not enough.)*

If the user’s query is very broad or if the initial answers seem shallow, the system can loop back for another iteration of research. This is controlled by a parameter (like `maxDepth` or a toggle for “deep dive”). Firecrawl’s API allows a `maxDepth` up to 5, meaning it will perform up to 5 rounds of searching and analysis. In our system, after producing an answer draft, we could analyze if there are unanswered aspects or follow-up questions, and then feed those as new queries.

For instance, our answer might say “XYZ is an open problem (sources cited)”. The system could detect the phrase “open problem” and decide a follow-up query: “What are current attempts to solve XYZ?”. This requires an agent-like capability to generate new queries based on content gaps. We could employ the LLM in a reflective mode: *“Based on the assembled answer, is further research needed on any subtopic? If yes, output the next question to investigate, otherwise output 'no further research'.”* This prompt might yield a follow-up question if the model identifies something. If we trust that, we then run another iteration: search that question, gather new info, and either integrate it into the existing answer or produce a supplement.

Alternatively, we can simply allow the user to request deeper research on a subtopic manually (like they could click on a sub-question or ask a follow-up). Since our focus is an autonomous system, the fully automated multi-hop might be experimental. To keep things stable, the default could be one iteration, with an option to manually trigger more.

If implementing multi-iteration, make sure to **merge the new information** with the old. Perhaps maintain the vector index across iterations (so it grows with new info) and then regenerate the answer considering all knowledge. Or produce a separate section for new findings. This can get complex, so for now, we acknowledge the capability but not dive too deep.

## Technology Choices and Implementation Strategy

Having described the design in abstract, we now map each component to concrete, modern open-source tools and outline how to implement the system step-by-step. The guiding principle is to use **secure, well-maintained libraries** and keep the system modular (each component can be developed and tested in isolation). We also aim for reproducibility – using containerization and version control to capture the environment.

Below is a summary of recommended tech stack components for this project:

* **Programming Language:** Python (due to its rich ecosystem for AI and web scraping, and the availability of LangChain, etc.). Python will host our orchestrator, retrieval logic, and possibly the web API (FastAPI).

* **Headless Browser:** Playwright for Python. This requires installing the browser drivers (Playwright can do it via `playwright install`). We will run it in headless mode. We might also use `pyppeteer` or Selenium if needed, but Playwright is preferred for reliability with modern sites.

* **Web Scraping Utilities:** `requests` for simple GET requests (with fake headers) for sites that don’t need JS. `BeautifulSoup4` for HTML parsing if we need fine control (although Unstructured can handle parsing too).

* **Document Parsing:** Unstructured’s `partition` functions for PDFs, HTML, etc., to get clean text. Alternatively, `readability-lxml` to parse HTML main content. We should evaluate a few on test pages.

* **Embeddings:** HuggingFace Transformers or SentenceTransformers to load a model like `sentence-transformers/all-MiniLM-L6-v2`. This requires downloading model weights (which we can do once and cache). If using a GPU, a larger model like `multi-qa-MiniLM-cos-v1` or others could be chosen for slightly better quality.

* **Vector Store:** **ChromaDB** (can be added via `pip install chromadb`). It can run in-memory or use an SQLite persistence. For our usage, either is fine. If we want persistence (to reuse data between runs), we can point it to a database file. Chroma can also be integrated with LangChain easily as a `VectorStore` object.

* **Language Model:** If using a local model, one convenient way is to run **Ollama** on the homelab. For example, `ollama pull llama2:13b` to get the model, then our Python code can do `requests.post("http://localhost:11434/generate", json={"model": "llama2:13b", "prompt": prompt})` to get a streamed response. If not Ollama, we could use the `transformers` library in Python to directly run a model with `generate` (but hosting a large model in Python might be heavy; frameworks like `lit-gpt` or `vLLM` could help for performance). Alternatively, since the user specifically mentioned **LM Studio**, one could run LM Studio which provides a local UI for models and possibly an API (it wasn’t primarily an API server, but it does have a “local server” mode). **Open WebUI** is another – it supports running as a web server and even multi-user. However, integrating with those might require their specific protocols (OpenWebUI can work with an extension to expose a socket or HTTP).

* **Frameworks:** We can either assemble these components manually (which gives fine-grained control) or leverage a framework like **LangChain** or **Haystack**. LangChain, for example, can manage chains of tools and has integrations for web scraping (via Playwright), for vector stores (Chroma, FAISS, etc.), and LLMs. Haystack (by Deepset) is a dedicated RAG framework with similar capabilities (crawlers, readers, etc.). An advantage of LangChain is a large community and many ready-made modules. For instance, LangChain could allow us to define a custom tool that searches and scrapes (like a tool that uses Playwright to get content) and an agent that decides when to use it. That starts leaning into an autonomous agent architecture (like AutoGPT style). Given our design, it might be straightforward enough to implement without a heavy framework, but adopting LangChain could accelerate development and ensure we follow best practices. Notably, Firecrawl itself integrates with LangChain and LlamaIndex, implying these frameworks mesh well with the concept.

* **API Layer:** **FastAPI** is an excellent choice to expose our system via HTTP endpoints on the homelab. We can create an endpoint `/research` that accepts a query and parameters (depth, etc.) and returns a JSON with the answer and sources. FastAPI also easily supports streaming responses via Server-Sent Events (SSE) if we want to stream tokens or logs. If we anticipate using this from a VS Code extension or other local tools, having an HTTP API is convenient. Additionally, a simple CLI interface can be built (even just running the script from terminal with the query as argument).

* **Data Storage:** If we want to cache results or store previous research sessions, we could use a relational DB (PostgreSQL) or a simple local SQLite. For example, storing past queries and their answers, or storing the contents of pages we’ve crawled before (to avoid re-crawling the same URL again). This can be an optimization: a local *content cache*. We could key it by URL and store the parsed text and embeddings. Then if that URL is encountered again, skip crawling and use cached text. For initial version, this is not essential but nice to consider for efficiency and offline capability (e.g., if a source disappears or internet is down, you still have it cached).

Now, let’s outline the **step-by-step implementation plan** incorporating these tools:

**Setup and Environment:**

1. **System Environment:** Prepare the homelab server with necessary system dependencies. Install Python 3.10+ (for compatibility with latest libs). Ensure you have Docker installed (for any services like Weaviate or to containerize the app itself later). Also, install Chrome or Chromium (Playwright will actually handle this automatically when you first run it, by downloading a browser binary). If using GPU for ML, ensure CUDA drivers are in place.

2. **Python Environment:** Create a virtual environment and install required Python packages:

   ```bash
   pip install playwright bs4 requests chromadb sentence-transformers fastapi uvicorn transformers unstructured
   ```

   * `playwright` for headless browsing.
   * `bs4` (BeautifulSoup) for HTML parsing fallback.
   * `requests` for HTTP requests.
   * `chromadb` for vector store.
   * `sentence-transformers` to easily load embedding models.
   * `fastapi` and `uvicorn` for the API server.
   * `transformers` for possibly running the LLM or embedding model.
   * `unstructured` for document parsing.
   * Also, if using LangChain, `pip install langchain` (and maybe `openai` if you plan to use OpenAI’s models for testing). If using Haystack, `pip install farm-haystack`.

   Additionally, run `playwright install` to set up the browsers.

3. **Project Structure:** Organize the code into modules for clarity (this also aids maintainability):

   * `crawler.py`: functions to perform web search and crawling (using Playwright/requests).
   * `parser.py`: functions to parse fetched content (HTML, PDF, etc. -> text).
   * `embedder.py`: functions to chunk text and generate embeddings.
   * `vectorstore.py`: initialize and manage the Chroma (or chosen DB) index.
   * `retriever.py`: functions for querying the index.
   * `generator.py`: logic to construct LLM prompt and call the LLM for answer generation.
   * `server.py`: FastAPI app definitions (endpoints) that tie it all together.
   * `cli.py`: optional CLI entrypoint that parses command-line args and calls the main routine (could use `argparse`).
   * `utils.py`: shared helpers (e.g., a function to clean text or to format citations).

   Having this separation means each module can be unit-tested individually. For example, you can test `parser.py` on known HTML files to see if it extracts correctly.

4. **API Keys and Config:** If using any external API (like an OpenAI model or Bing Search), keep those keys in a `.env` file or environment variables. Provide a config file or use environment variables for things like maximum depth, number of parallel browsers, model names, etc. This allows easy tuning without changing code. Since everything is local in our plan, keys might not be needed except possibly a Bing key if we go that route. Ensure not to hardcode keys in code (security best practice).

**Development Steps:**

5. **Implement Search Querying:** In `crawler.py`, implement a `web_search(query)` function. If using an API like Bing:

   ```python
   def web_search(query, count=5):
       url = f"https://api.bing.microsoft.com/v7.0/search?q={urllib.parse.quote(query)}&count={count}"
       headers = {"Ocp-Apim-Subscription-Key": BING_API_KEY}
       resp = requests.get(url, headers=headers, timeout=10)
       resp.raise_for_status()
       data = resp.json()
       results = []
       for web_res in data.get("webPages", {}).get("value", []):
           results.append({
               "title": web_res["name"],
               "url": web_res["url"],
               "snippet": web_res.get("snippet", "")
           })
       return results
   ```

   If using Searx, you might do a similar GET to your instance’s search endpoint. If purely local offline and you have no search, you could skip this and rely on user-provided URLs (less ideal).

   Test this function standalone to verify you get results. This is an area that can fail if API keys are wrong or quota exceeded, so include proper error handling and meaningful messages (e.g., if no results returned, maybe try a different approach or inform the user).

6. **Implement Page Fetching:** In `crawler.py`, implement `fetch_page(url)` that returns the raw content (HTML text or file bytes). Use Playwright for this:

   ```python
   async def fetch_page_playwright(url):
       browser = await playwright.chromium.launch()
       page = await browser.new_page()
       await page.goto(url, wait_until="load", timeout=15000)
       content = await page.content()
       # Optionally, if PDF or something, you might detect content type.
       await browser.close()
       return content
   ```

   Since Playwright is async, you either run it in an event loop or use `asyncio.run`. Alternatively, use `requests.get` if the URL is likely a PDF or simpler page (you can check `url.endswith(".pdf")` and handle that by direct download).

   You might also want to implement logic to handle PDF links: e.g., if the URL or the response Content-Type indicates PDF, save the bytes to a file or memory and then use PDF parser.

   Because using Playwright for each page can be heavy, consider a **PagePool**: launch one browser, open multiple pages/tabs for each URL (Playwright can handle many contexts). This is a bit more advanced to coordinate async tasks. Libraries like **gather** or **trio** can manage concurrent fetches. Perhaps simpler: use `asyncio.gather` on a list of fetch tasks. Limit concurrency to, say, 3 at a time to not overload.

   Don’t forget to include timeouts and exception catching. If a page fails (due to 404 or script error), log it and continue with others.

7. **Implement Parsing:** In `parser.py`, write functions like `parse_html(html_content)` and `parse_pdf(pdf_bytes)`. For `parse_html`, use Unstructured:

   ```python
   from unstructured.partition.html import partition_html
   def parse_html(html_content):
       elements = partition_html(text=html_content)
       text = "\n".join([el.text for el in elements if el.text])
       return text
   ```

   This gives a raw text. You might improve it by handling the title: perhaps use BeautifulSoup to get `<title>` tag separately. For PDFs:

   ```python
   from unstructured.partition.pdf import partition_pdf
   def parse_pdf(file_path):
       elements = partition_pdf(filename=file_path)
       text = "\n".join([el.text for el in elements if el.text])
       return text
   ```

   Unstructured might require the file from disk (not just bytes), so you’ll need to save the PDF bytes to a temp file (maybe use Python’s `tempfile` module). Make sure to clean up temp files after.

   If Unstructured is too slow or heavy, an alternative is to use BeautifulSoup for HTML and PyMuPDF for PDF:

   ```python
   import fitz
   def parse_pdf_bytes(pdf_bytes):
       doc = fitz.open(stream=pdf_bytes, filetype="pdf")
       text = ""
       for page in doc:
           text += page.get_text()
       doc.close()
       return text
   ```

   Either way, after extraction, do some normalization: e.g., collapse multiple newlines, strip whitespace.

   Test the parser on a sample HTML file and PDF to ensure it extracts correctly.

8. **Implement Chunking and Embedding:** In `embedder.py`, load the embedding model at module import or via an initializer function:

   ```python
   from sentence_transformers import SentenceTransformer
   model = SentenceTransformer('all-MiniLM-L6-v2')
   ```

   Then a function `chunk_and_embed(text, source_id)` that splits the text and returns list of (embeddings, metadata):

   ```python
   from textwrap import wrap
   def chunk_and_embed(text, source, overlap=50, chunk_size=200):
       # A simple approach: split by sentences or every ~200 words.
       words = text.split()
       chunks = []
       i = 0
       while i < len(words):
           chunk_words = words[i:i+chunk_size]
           chunk_text = " ".join(chunk_words)
           chunks.append(chunk_text)
           i += chunk_size - overlap  # move with overlap
       # Now embed all chunks
       embeddings = model.encode(chunks)  # returns a list of vectors
       results = []
       for emb, chunk_text in zip(embeddings, chunks):
           results.append({
               "embedding": emb,
               "meta": {"source": source, "text": chunk_text}
           })
       return results
   ```

   (In practice, better splitting by sentence boundaries using `nltk` or `re` to avoid cutting mid-sentence. LangChain’s `RecursiveCharacterTextSplitter` can do this more systematically, considering punctuation and newlines.)

   We call this for each document we parsed. Assign each document a source ID or use the URL as an ID.

9. **Initialize Vector Store:** In `vectorstore.py`, set up Chroma:

   ```python
   import chromadb
   client = chromadb.Client()
   collection = client.create_collection("research_data")
   ```

   To add documents:

   ```python
   def add_chunks(chunks):
       # chunks: list of {"embedding": emb, "meta": {...}}
       ids = [str(uuid.uuid4()) for _ in chunks]  # unique ids for each chunk
       embeddings = [c["embedding"] for c in chunks]
       metadatas = [c["meta"] for c in chunks]
       collection.add(documents=[c["meta"]["text"] for c in chunks],
                      embeddings=embeddings,
                      ids=ids,
                      metadatas=metadatas)
   ```

   You might wonder why store the text in the vector DB too – Chroma allows storing the document text which is convenient for retrieval output. We definitely store at least the metadata with source and maybe an identifier. The `ids` can be random or you could compose from source+index.

   After adding all chunks from all sources, the vector index is ready.

10. **Implement Retrieval:** In `retriever.py`, write:

    ```python
    def retrieve_relevant_chunks(query, top_k=5):
        q_emb = embedder.model.encode(query)
        results = vectorstore.collection.query(query_embeddings=[q_emb], n_results=top_k, include=['metadatas', 'documents', 'distances'])
        # results is a dict with keys 'ids', 'documents', 'metadatas', etc.
        found = []
        if results.get('documents'):
            for text, meta, dist in zip(results['documents'][0], results['metadatas'][0], results['distances'][0]):
                found.append({"text": text, "source": meta['source'], "score": dist})
        return found
    ```

    Chroma returns nearest neighbors; note that `distances` might actually be **distance** (so lower is better if it’s Euclidean) or 1-cosine similarity. We can convert it to a similarity score if needed. But we can mostly treat the first items as most relevant.

    Here, each `found` item contains a chunk text and its source URL. If we also had title in meta, include that.

    We may do a little post-filter: for example, ensure unique sources if desired. Or if multiple chunks from one source appear, maybe combine them or indicate that in the final answer (though the model can handle multiple citations from the same doc).

11. **LLM Generation Implementation:** In `generator.py`, decide how to call the LLM. Two main paths:

    * **Using a Local API (Ollama/OpenWebUI)**: If using Ollama, ensure an instance is running and model is ready. Then do HTTP request as described. If using OpenAI’s API (for testing or if allowed), use `openai` package and call the model with the prompt.
    * **Using transformers directly:** e.g., load an `AutoModelForCausalLM` in 4-bit and call `generate`. This requires managing tokenization and might be complex to get right with long contexts. Many open models have 2048 or 4096 token limits which should suffice for a handful of chunks plus query.

    For clarity, let’s assume we use a local model via an API (to decouple model serving from our main app). We will implement a function `generate_answer(prompt)` that sends the prompt to the model and streams or returns the output. Example with OpenAI:

    ```python
    import openai
    def generate_answer(prompt):
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            stream=True  # to stream
        )
        answer = ""
        for chunk in response:
            if 'content' in chunk['choices'][0]['delta']:
                piece = chunk['choices'][0]['delta']['content']
                answer += piece
                yield piece  # stream out
        return answer
    ```

    But for local, it depends on the interface. Suppose we have Ollama:

    ```python
    def generate_answer(prompt):
        res = requests.post("http://localhost:11434/generate", json={"model": "llama2", "prompt": prompt, "system":"", "max_tokens": 1000, "stop": []}, stream=True)
        answer_text = ""
        for line in res.iter_lines():
            if line:
                data = json.loads(line.decode())
                token = data.get('response')
                if token is not None:
                    answer_text += token
                    yield token
        return answer_text
    ```

    This streams token by token. We accumulate and also yield each token to the caller.

    The function is a generator, so the FastAPI route or CLI can output as it comes.

    Constructing the **prompt**: We craft the string as described in the previous section:

    ```python
    def build_prompt(query, retrieved_chunks):
        prompt = "You are an AI research assistant. Use the given sources to answer the question.\n"
        prompt += f"Question: {query}\n"
        prompt += "Sources:\n"
        for idx, item in enumerate(retrieved_chunks, start=1):
            snippet = item["text"].strip().replace('\n',' ')
            prompt += f"[{idx}] {snippet}\n"
        prompt += ("\nWrite a comprehensive answer to the question using the sources above. "
                   "Cite each statement with the source number in square brackets. "
                   "If information is insufficient, say you cannot find the answer.\nAnswer:\n")
        return prompt
    ```

    This is a straightforward approach. We might refine it after testing, but it gives the model the context it needs.

12. **Orchestrator / Main Logic:** Now combine everything. In `server.py` (or a main script function), implement the workflow:

    ```python
    async def deep_research(query, max_depth=1):
        log = []  # collect activities for debugging/log
        results = []
        try:
            # Step 1: Query analysis (for now, we’ll just use the query as is or maybe one rephrase)
            subqueries = [query]
            log.append({"type": "search", "message": f"Generated {len(subqueries)} subqueries for \"{query}\""})
            # Step 2: Web search for each subquery
            all_urls = []
            for sq in subqueries:
                search_results = web_search(sq)
                log.append({"type": "search", "message": f"Search for \"{sq}\" returned {len(search_results)} results"})
                for res in search_results:
                    all_urls.append(res['url'])
            # Deduplicate URLs
            all_urls = list(dict.fromkeys(all_urls))
            if not all_urls:
                raise Exception("No search results found")
            # Step 3: Crawl initial URLs (with concurrency)
            contents = await fetch_urls_concurrently(all_urls[:10])  # limit e.g. 10 for scope
            # contents is list of (url, content_bytes_or_str)
            parsed_docs = []
            for url, content in contents:
                if content is None:
                    continue
                # determine type
                if isinstance(content, bytes):
                    # likely PDF or similar
                    text = parse_pdf_bytes(content)
                else:
                    text = parse_html(content)
                if not text.strip():
                    continue
                parsed_docs.append({"url": url, "text": text})
                log.append({"type": "fetch", "message": f"Fetched and parsed {url[:60]}..., {len(text.split())} words"})
            # Step 4: Chunk and embed docs
            all_chunks = []
            for doc in parsed_docs:
                source = doc["url"]
                chunk_data = chunk_and_embed(doc["text"], source)
                all_chunks.extend(chunk_data)
            add_chunks(all_chunks)
            log.append({"type": "index", "message": f"Indexed {len(all_chunks)} chunks from {len(parsed_docs)} documents"})
            # Step 5: Retrieve relevant chunks for answer
            top_chunks = retrieve_relevant_chunks(query, top_k=5)
            log.append({"type": "retrieve", "message": f"Retrieved {len(top_chunks)} relevant chunks for answering"})
            # Step 6: Generate answer
            prompt = build_prompt(query, top_chunks)
            answer_text = ""
            async for token in generate_answer_stream(prompt):
                answer_text += token
                # (Here we could also yield the token to API client if streaming API)
            log.append({"type": "synthesis", "message": "Generated final answer"})
            # Step 7: Prepare sources list
            sources_list = []
            for idx, chunk in enumerate(top_chunks, start=1):
                src_url = chunk["source"]
                title = get_title_from_cache_or_web(src_url)  # we might have stored titles earlier
                sources_list.append({"number": idx, "title": title or src_url, "url": src_url})
            results = {"answer": answer_text, "sources": sources_list, "log": log}
        except Exception as e:
            log.append({"type": "error", "message": str(e)})
            results = {"error": str(e), "log": log}
        return results
    ```

    This pseudocode covers the main steps. In reality, we’ll refine each part and handle asynchronous calls properly. Notably, `fetch_urls_concurrently` would wrap `fetch_page` in tasks.

    We also see an example of an activity log being built. This log can be extremely useful for observability – it can be returned (maybe only in a debug mode or to the developer) to see what the system did at each step, similar to Firecrawl’s `activities`.

    The log entries might look like:

    * `[search] Generated 1 subquery for "quantum computing cryptography"`
    * `[search] Search for "quantum computing cryptography" returned 10 results`
    * `[fetch] Fetched and parsed https://example.com/quantum-news..., 800 words`
    * `[index] Indexed 40 chunks from 5 documents`
    * `[retrieve] Retrieved 5 relevant chunks for answering`
    * `[synthesis] Generated final answer`
      This gives transparency.

13. **FastAPI Endpoints:** With the main logic in place, expose it in an API. For example:

    ```python
    app = FastAPI()

    @app.post("/deep_research")
    async def deep_research_endpoint(request: ResearchRequest):  # define a Pydantic model for input if needed
        result = await deep_research(request.query, max_depth=request.max_depth)
        return result
    ```

    We might also add a GET for simple testing, or a websocket/SSE for streaming (Advanced: FastAPI can push events for each token or log entry).

    If building a CLI, just parse sys.argv and call `deep_research(query)` and print the formatted answer and sources.

14. **Testing the Pipeline:** Before deploying widely, test each part:

    * Unit test the search function with a simple query (maybe stub the API to not waste calls).
    * Test crawling on a known URL (maybe one with predictable content).
    * Test parsing on some saved HTML/PDF files.
    * Test the embedding and retrieval by creating a small dummy corpus and querying it.
    * Finally, run the `deep_research` function end-to-end with a straightforward query and see the output and logs. You might use a query where you already know the answer to judge it.

    Ensure that the system successfully cites sources. Check that the citations \[1], \[2] in the answer correspond correctly to the sources. Evaluate if the answer is coherent and addresses the question fully. This might involve tweaking the prompt or the number of retrieved chunks.

    It’s advisable to test with queries of varying difficulty (factual questions, open-ended analytical questions, etc.) to see how the system handles them.

15. **Performance Tuning:** On a homelab, resources are finite. If using a large LLM model, generation will be the slowest step. The crawling could also be slow for many URLs. We should set sensible timeouts: e.g., maybe a total time budget of say 3 minutes (180 seconds) for the whole operation, similar to Firecrawl’s defaults. If that time is exceeded, we stop and return whatever we have (perhaps a partial answer or an error). We can expose a `timeLimit` param in the API for users to adjust.

    Memory: The vector store with all chunks might consume memory, but if it’s just tens or hundreds of chunks, it’s trivial. The LLM context memory is more critical – feeding 5 chunks of \~200 words each + query might be \~1000 tokens, which most models can handle. If we try to feed, say, 30 chunks, that could be 6000+ tokens and might hit limits or slow down generation, so limiting to the top few is both efficient and usually sufficient. If the user explicitly wants a very comprehensive report, we might include more, but chunk selection is key.

16. **Network and Security Setup:** Since this will run on a server possibly accessible on a network, secure it:

    * If exposing FastAPI beyond localhost, consider enabling HTTPS (maybe behind a reverse proxy like Nginx with certs) or at least require an API token in requests.
    * If this is purely for personal use on local network, at minimum use a firewall to block external access.
    * The system will be making outbound requests to arbitrary websites. This is a potential vector for malicious content. Running the headless browser in a container or with restricted privileges is wise. Playwright’s browser runs with a sandbox by default (on Linux, ensure user namespaces are enabled or use `--no-sandbox` if needed, though no-sandbox is less secure). We can also run the entire application inside a Docker container that has limited file system access, to mitigate any harm if a malicious page tries to exploit the browser.
    * Keep the system and browser updated. For example, regularly update Playwright (which updates the browser engine) to patch security issues.
    * You might also implement basic sanitization on outputs, e.g., if a page’s text includes some script or weird Unicode that could mess with our terminal or UI, maybe strip non-printable chars.
    * Monitor the logs for any failed requests or unexpected redirects (like if a site blocked us or asked for CAPTCHA, etc.).

17. **Cybersecurity Considerations:** If this system might access sensitive internal documents in addition to web, ensure that when it indexes internal data, that data is not exposed in the final answer beyond what’s asked (our design doesn’t really differentiate, but if hooking up internal knowledge, that might come later). Also be cautious with prompts to the LLM so that it doesn’t reveal the entire content of sources unless needed (we mostly instruct it to synthesize, not list raw text, so that’s fine).

    Another angle: since this is an autonomous agent of sorts running code, be careful with prompt injection if users provide queries. In our case, the user is likely the owner, but if it were a public service, a malicious query could try to get the LLM to output something it shouldn’t (like system file content). However, our LLM has no direct file system access, only the retrieved web content. So the main risk is the model could be tricked to ignore instructions. We mitigate that by keeping a strong system prompt that it must cite sources and by not letting it run arbitrary tools beyond what we coded.

18. **Deployment on Homelab:** We can use **Docker Compose** to run components:

    * One service for our FastAPI app (which will run Uvicorn server).

    * Possibly a service for Weaviate (if we used that instead of Chroma). If Chroma in-memory is fine, no need.

    * If using a separate LLM server (like Ollama or OpenWebUI), that runs as another service or on the host. For example, Ollama runs on macOS/Linux directly, not via Docker (though one could containerize it).

    * We could also containerize Playwright with the app, but Playwright needs some OS dependencies (fonts, possibly Chrome dependencies). There are base images like `mcr.microsoft.com/playwright/python` that have everything needed. Starting from one of those could save effort. For instance:

      ```Dockerfile
      FROM mcr.microsoft.com/playwright/python:latest
      WORKDIR /app
      COPY requirements.txt .
      RUN pip install -r requirements.txt
      COPY . .
      CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]
      ```

      This image would have Chrome installed for Playwright. Ensure to not run as root in container for security.

    * If we incorporate these into one compose file, ensure to define network settings (maybe host mode if accessing other servers on host, or use docker internal network for contacting a containerized weaviate/llm, etc.).

19. **Observability & Monitoring:** Incorporate logging (the `log` we built can also be output to console or a file). We could use Python’s `logging` module to log info and debug messages to a file for later analysis. This can be helpful to see how often searches fail or how long steps take. For more advanced tracing, one could integrate OpenTelemetry to trace a “research session” across the functions, but that might be overkill. At minimum, timing each major step and logging it is useful:

    ```python
    start = time.time()
    # do search
    log.append({"type":"timing", "message": f"Search took {time.time()-start:.2f}s"})
    ```

    etc. This helps in identifying bottlenecks (maybe crawling is taking 80% of time, etc.).

    If running long-term, consider monitoring memory/CPU usage (maybe via docker stats or an external tool) to ensure the process doesn’t leak memory or consume too much CPU over time. LLM inference will use CPU/GPU heavily while generating, which is expected.

20. **Maintenance:** Keep track of versions of all components (maybe freeze `requirements.txt` with exact versions that you tested). Write tests for new features to avoid regressions (for example, if you change the chunk size logic, test that retrieval still finds known answers). Since this is a personal system, maintenance mostly means updating the LLM model if a better one comes out (just swap the model in config), updating libraries occasionally for security patches, and monitoring any changes needed if source websites or search APIs change formats.

By following this plan, an AI agent (or an engineer) could implement the system from start to finish. The design emphasizes modularity, so each piece can be improved independently. For example, one could upgrade the vector store to Weaviate for larger scale, or swap out the embedding model for a more powerful one, or integrate a new LLM, without overhauling the entire system.

Throughout development, keep the **end-user (or end-agent) in mind**: the output should be easy to parse by an AI (hence structured Markdown and JSON) and the system should fail gracefully (if something goes wrong, return an error message rather than hanging indefinitely).

## Homelab Deployment and Local AI Integration

Deploying on a homelab means we should account for the environment specifics:

* **Network Design:** Likely, the server will sit behind your home router. If you need to access it externally (e.g., you're on the go and want to query it), set up a VPN into your network or a secure tunnel rather than exposing the API port to the open internet. If you do expose it, use HTTPS and some auth. For internal LAN use (e.g., from your PC or an IDE on the same network), it might be fine to run it on `0.0.0.0:8000` and connect by IP.

* **Local Agent Usage:** If using VS Code Copilot or ChatGPT plugins, they might allow making HTTP requests. For example, Copilot Labs or other extensions might call local services. You can have an extension that when you ask a question, it triggers a call to `http://homelab:8000/deep_research` and then formats the response. GitHub’s Copilot cannot be self-hosted, but OpenAI’s functions or LangChain agents can call our API. We could also integrate this system with a voice assistant or other interfaces, but that’s beyond scope. At minimum, a developer can query it via HTTP or CLI and get a Markdown answer with citations which they can then use or edit.

* **Local LLM Options:** We touched on this, but to enumerate:

  * **Open WebUI:** An interface to manage models. If it's running on the homelab, ensure it’s on a secured port. It supports multiple models, which is nice if you want to quickly switch between, say, a smaller model for quick responses and a bigger one for heavy queries.
  * **LM Studio:** This is more of a desktop app, but it has a “local server” feature where it can expose the model for API usage (I believe via an HTTP or gRPC). If the homelab has a GUI, LM Studio could run, but on a server likely not. It’s more likely one would use something like text-generation-webui (another popular local UI) which also offers an API. That or **llama.cpp** with an HTTP front.
  * **Ollama:** Very convenient on macOS and now Linux – it downloads models easily and runs them efficiently with quantization. Running `ollama serve` will start a local service. You then call it as shown. It's designed for this kind of usage (with support for streaming).
  * If one has a GPU with sufficient VRAM, running a model with HuggingFace `transformers` in 8-bit or 4-bit mode is possible. For example, using bitsandbytes to load a 13B model in 8-bit would require \~16GB RAM. That might just fit on a high-end GPU or can use CPU with lots of RAM (slower). It’s a trade-off between performance and cost (of using an API like OpenAI). Given this is a self-hosted project, let’s assume we prefer to keep everything local even if it’s a bit slower.

* **Scaling Down or Up:** The architecture is modular to allow replacing parts. If the homelab is very low-power (like a Raspberry Pi), running an LLM might be infeasible – one could then use an online API for the LLM while still doing crawling locally. Conversely, if the homelab is a powerful server, one could scale components: e.g., use multiple threads or processes for crawling to go deeper faster, allocate more memory to store large numbers of documents, etc. Docker deployment makes it easier to move the setup to a bigger machine if needed.

* **API Rate-Limiting:** Since this is local, you might not worry about abuse, but it’s good to guard against accidental overload (say an agent script goes into a loop hitting the API). We can implement a simple rate limit – e.g., only allow one deep research job at a time, or queue them if multiple requests come. Firecrawl’s free tier mentions low rate limits; for our use, we define what’s acceptable (maybe one query at a time per user). FastAPI could integrate with a limiter or we can handle concurrency by semaphore. Also keep an eye on the browser: too many concurrent pages could saturate CPU/RAM, so it’s wise to enforce a cap at the application level.

* **Data Privacy:** All data stays within your homelab. The content from the web is presumably public, but if you ever mix in private documents to augment the research, those would also be processed locally. Just ensure if you do use any cloud-based services (like an external search API or a cloud LLM) that you’re not sending anything sensitive there.

* **Maintaining the System:** Version control your code (git). Possibly set up CI tests if you push to GitHub (even just for the non-browser parts, since browser tests in CI are tricky without a display or in a container, but one could use xvfb for headless). Keep dependencies updated but tested – for instance, if a new Playwright or new LLM model comes out, test the system with it.

* **Future Improvements:** (Just to note, not necessarily to implement immediately)

  * Implement a knowledge-graph or ontology builder to connect concepts found (could use something like Neo4j to store relationships between entities found in text). This could help the system reason about which areas to explore next.
  * Integrate a question generator to ask follow-up questions automatically (like an agent that probes the initial answer for gaps).
  * Add a UI: A simple Streamlit or React front-end where you input a question and it shows the answer with collapsible source texts, etc. This would make it more user-friendly (similar to how Perplexity.ai or other engines present results). Since the user mentioned VS Code, one could even make a VS Code extension panel that hits the API and displays the markdown answer inside the editor, allowing the developer to incorporate it into notes or code comments.
  * Multi-user support: if multiple people/agents query it simultaneously, you’d want to isolate their sessions (each maybe with its own index and process). This would involve some kind of session management.

* **Academic References and Inspirations:** It’s worth noting that our design stands on shoulders of prior work. The concept of retrieval-augmented generation comes from research by Facebook AI and others, which showed that combining parametric knowledge of LMs with retrieved documents yields better factual accuracy. Our approach also mirrors systems like **Haystack’s Finder** or **Microsoft’s Orqa** in combining search with QA. Firecrawl’s Deep Research itself is an example of applying these ideas in a developer-friendly API. We also applied principles of **systems thinking** – considering how each part (crawler, index, LLM) influences the whole and how to balance trade-offs. For instance, optimizing for speed (maybe smaller model) versus accuracy (bigger model) is a trade-off to decide based on homelab capabilities. In architecture terms, we applied **modularity and separation of concerns** (each component has a clear role), which is a key approach to managing complexity.

Finally, building such a system is an iterative engineering process: start simple, get the basic end-to-end flow working (even if using smaller data or a slower model), then refine each part. Use the logs and tests to identify where improvements are most needed (maybe the parser missed some content or the LLM formatting needed tweaks) and address those. Over time, this system can evolve into a powerful personal research assistant, and because it’s self-hosted, you retain full control and flexibility to adapt it to your needs – whether that’s doing literature reviews, competitive intel, or just satisfying personal curiosity with well-sourced answers.

## Conclusion and Further Resources

We have outlined a complete architecture and implementation plan for a deep research system, touching on everything from web crawling to answer generation. By following this guide, an engineer or an AI agent (given the appropriate tools and permissions) can build the system from scratch, and developers can deploy it on homelab hardware for private use.

This project integrates knowledge and techniques from multiple domains: web scraping, natural language processing, information retrieval, and software architecture. For further reading and validation of these concepts, you may consult the following references:

* **Retrieval-Augmented Generation (RAG) Paper (Lewis et al., 2020):** Introduces the core idea of combining an LLM with a retrieved document index for knowledge-intensive QA. This is the foundational idea behind our system’s design.
* **Firecrawl Blog – Deep Research API Announcement:** Provides insight into the goals and capabilities of Firecrawl’s approach, which we mirrored (multi-step web exploration, source attribution, etc.).
* **OpenAI Function Calling & Agents:** OpenAI’s documentation on building agents (though not fully open-source, the concepts of tool use by LLMs influenced our approach). Also, the *OpenAI’s Agents SDK* tutorial by Unwind AI shows a multi-agent research setup which is similar in spirit, and worth reviewing for ideas on multi-agent coordination.
* **LangChain Documentation:** If using LangChain, their docs on web research agents, vector stores, and evaluation might be useful. LangChain’s abstractions can simplify some parts (like chunking and calling LLMs with callbacks for streaming).
* **Haystack by Deepset:** An open-source RAG framework with examples of building QA systems over documents. It’s a more specialized tool than LangChain and can serve as an alternative approach. They also have a tutorial for a question-answering pipeline that parallels what we built.
* **Academic Paper on “Tree of Thoughts”:** Yao et al., 2023 (if available) on tree-of-thought prompting can provide deeper understanding of why breaking down problems can enhance LLM reasoning.
* **Software Architecture References:** Since we also care about maintainability and quality, resources like *ISO/IEC 25010* for quality attributes or the *Architecture Tradeoff Analysis Method (ATAM)* can be useful to ensure our system meets its quality goals. While those are broader, they remind us to consider things like reliability (e.g., what if a site is down? do we fail gracefully), or security (we addressed running browsers in sandbox, etc.).
* **Security in Web Scraping:** Papers or blogs about scraping ethically and safely (avoiding legal issues, respecting robots.txt where appropriate). There’s also community knowledge on handling anti-bot measures that could be useful if one scales this up.
* **Vector Database Literature:** To fine-tune our retrieval, looking at blogs from Pinecone, Qdrant, or Chroma on handling large-scale vector search, hybrid retrieval, and optimizing query speed could be helpful if our dataset grows.

By building this system, one gains practical experience in full-stack AI system development – from front-end (if you add an interface) to back-end crawling and ML inference. It is a solid project for a cybersecurity or computer engineering student to learn modern software architecture and to appreciate how AI can be integrated into complex workflows in a modular, controlled manner. We have emphasized a design that is **modular** (each component could be swapped with another implementation), **secure** (keeping data local, sandboxing, and avoiding external dependencies when possible), and **transparent** (with logs and citations for every action and piece of information). These qualities are important in professional environments where trust and maintainability are paramount.

With the reference implementation in hand, you can now proceed to code and assemble the system. Start the engine, and let your self-hosted AI researcher dig deep into the web’s knowledge – delivering answers you can trust, complete with the evidence to back them up. Good luck, and happy building!

**References:**

1. Lewis, Patrick, et al. *"Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks."* NeurIPS 33 (2020): 9459-9474. (Introduces RAG model combining an LLM with a dense retriever for improved factual accuracy)

2. Firecrawl Dev Blog. *"Introducing Deep Research API – AI-powered web research on any topic."* (2025) – Describes the Deep Research methodology (query breakdown, iterative search, synthesis, source attribution) and provides examples.

3. Firecrawl Dev Blog. *"Building a Local Deep Research Application with Firecrawl and Streamlit."* Bex Tuychiev, March 2025 – An open-source tutorial that inspired parts of our design, showing how Firecrawl’s deep research endpoint can be used in a custom app.

4. Unwind AI Tutorial. *"Build a Deep Research Agent with OpenAI Agents SDK and Firecrawl."* Saboo & Gupta, March 2025 – Demonstrates a multi-agent system (research agent + elaboration agent) and a Streamlit UI, providing insight into multi-step agent orchestration in a research context.

5. Qdrant Tech Blog. *"What is RAG: Understanding Retrieval-Augmented Generation."* (2024) – Provides an accessible overview of RAG pipelines and components (retriever, vector store, generator) along with diagrams for indexing and retrieval processes.

6. B. Tuychiev, Firecrawl Blog. *"Top 9 Browser Automation Tools for Web Testing and Scraping in 2025."* (2025) – Reviews tools like Playwright, Selenium, Scrapy, etc., noting that headless browsers (Playwright/Puppeteer) are ideal for scraping dynamic sites in server environments.

7. ISO/IEC 25010 Standard (2011). *"Systems and software Quality Requirements and Evaluation (SQuaRE) – System and software quality models."* – Defines quality attributes such as reliability, maintainability, performance efficiency, which we considered in architecture design.

8. LangChain Documentation – *Modules on Retrieval QA, VectorStores, Tools and Agents* (2023-2025) – Useful for implementation reference if using LangChain to build the pipeline (e.g., `VectorStoreRetriever`, `LLMMathChain`, etc.).

9. *Chain-of-Thought and Tree-of-Thought Papers:* Kojima et al. (2022) *"Large Language Models are Zero-Shot Reasoners"* and Yao et al. (2023) *"Tree of Thoughts: Deliberate Problem Solving with Large Language Models"* – underpin the idea of prompting models to decompose problems, which inspired our query analysis approach.

10. K2View Blog. *"RAG Architecture: The generative AI enabler."* (2025) – Discusses enterprise RAG applications and diagrams data flow from user query to LLM response, reinforcing the architecture we built with retrieval in the loop.

These resources, along with the step-by-step plan provided, should equip you to successfully implement and refine your deep research system. By iterating on this framework, you can create a robust tool that brings you the power of an autonomous research analyst – one that tirelessly scours the digital world and delivers reasoned, evidence-backed insights at your fingertips. Good luck on your implementation journey!
