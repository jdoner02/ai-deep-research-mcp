/**
 * API Client - Handles communication with the backend research system
 * In a full implementation, this would make HTTP requests to the Python backend
 */

class APIClient {
    constructor(baseUrl = null) {
        this.baseUrl = baseUrl || this.detectBackendUrl();
        this.timeout = 60000; // 60 seconds
    }

    detectBackendUrl() {
        // In GitHub Pages, there's no backend, so we return null
        // In a full deployment, this would detect the backend service URL
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:8000'; // Local development server
        } else {
            return null; // GitHub Pages - no backend
        }
    }

    async conductResearch(params) {
        if (!this.baseUrl) {
            // GitHub Pages mode - return mock data
            console.log('GitHub Pages mode - using mock data');
            return this.getMockResearchResults(params);
        }

        try {
            const response = await this.makeRequest('/api/research', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    query: params.query,
                    max_sources: params.max_sources,
                    citation_style: params.citation_style,
                    max_depth: params.max_depth,
                    include_web: params.include_web
                })
            });

            if (!response.ok) {
                throw new Error(`API request failed: ${response.status} ${response.statusText}`);
            }

            return await response.json();

        } catch (error) {
            console.error('API request failed:', error);
            
            // Fallback to mock data if API fails
            console.log('Falling back to mock data due to API error');
            return this.getMockResearchResults(params);
        }
    }

    async makeRequest(endpoint, options = {}) {
        const url = `${this.baseUrl}${endpoint}`;
        
        const requestOptions = {
            timeout: this.timeout,
            ...options
        };

        return fetch(url, requestOptions);
    }

    async getMockResearchResults(params) {
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, Math.random() * 2000 + 1000));

        // Generate mock results based on query
        const query = params.query.toLowerCase();
        
        let mockSources = [];

        if (query.includes('machine learning') || query.includes('ai') || query.includes('artificial intelligence')) {
            mockSources = [
                {
                    title: "Attention Is All You Need",
                    authors: ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar", "Jakob Uszkoreit"],
                    abstract: "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks that include an encoder and a decoder. The best performing models also connect the encoder and decoder through an attention mechanism. We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
                    source_type: "arxiv",
                    url: "https://arxiv.org/abs/1706.03762",
                    pdf_url: "https://arxiv.org/pdf/1706.03762.pdf",
                    published: "2017-06-12",
                    citation_count: 45123,
                    venue: "Neural Information Processing Systems (NIPS) 2017"
                },
                {
                    title: "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding",
                    authors: ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee", "Kristina Toutanova"],
                    abstract: "We introduce a new language representation model called BERT, which stands for Bidirectional Encoder Representations from Transformers. Unlike recent language representation models, BERT is designed to pre-train deep bidirectional representations from unlabeled text by jointly conditioning on both left and right context in all layers.",
                    source_type: "semantic_scholar",
                    url: "https://www.semanticscholar.org/paper/BERT%3A-Pre-training-of-Deep-Bidirectional-for-Devlin-Chang/df2b0e26d0599ce3e70df8a9da02e51594e0e992",
                    published: "2018-10-11",
                    citation_count: 32456,
                    venue: "NAACL-HLT 2019"
                },
                {
                    title: "Language Models are Few-Shot Learners",
                    authors: ["Tom B. Brown", "Benjamin Mann", "Nick Ryder", "Melanie Subbiah"],
                    abstract: "Recent work has demonstrated substantial gains on many NLP tasks and benchmarks by pre-training on a large corpus of text followed by fine-tuning on a specific task. While typically task-agnostic in architecture, this method still requires task-specific fine-tuning datasets of thousands or tens of thousands of examples.",
                    source_type: "arxiv",
                    url: "https://arxiv.org/abs/2005.14165",
                    pdf_url: "https://arxiv.org/pdf/2005.14165.pdf",
                    published: "2020-05-28",
                    citation_count: 28789,
                    venue: "Neural Information Processing Systems (NeurIPS) 2020"
                }
            ];
        } else if (query.includes('quantum') || query.includes('cryptography')) {
            mockSources = [
                {
                    title: "Quantum Cryptography: Public Key Distribution and Coin Tossing",
                    authors: ["Charles H. Bennett", "Gilles Brassard"],
                    abstract: "We introduce quantum cryptography protocols that enable two parties to produce a shared random secret key. The security of the key depends on quantum mechanics rather than unproven assumptions about computational complexity.",
                    source_type: "scholar",
                    url: "https://scholar.google.com/citations?view_op=view_citation&citation_for_view=example1",
                    published: "1984-12-01",
                    citation_count: 15234,
                    venue: "Proceedings of IEEE International Conference on Computers, Systems and Signal Processing"
                },
                {
                    title: "Polynomial-Time Algorithms for Prime Factorization and Discrete Logarithms on a Quantum Computer",
                    authors: ["Peter W. Shor"],
                    abstract: "A digital computer is generally believed to be an efficient universal computing device; that is, it is believed able to simulate any physical computing device with an increase in computation time by at most a polynomial factor. This may not be true when quantum mechanics is taken into consideration.",
                    source_type: "arxiv",
                    url: "https://arxiv.org/abs/quant-ph/9508027",
                    pdf_url: "https://arxiv.org/pdf/quant-ph/9508027.pdf",
                    published: "1995-08-23",
                    citation_count: 8945,
                    venue: "SIAM Journal on Computing"
                }
            ];
        } else {
            // Generic academic sources
            mockSources = [
                {
                    title: `Research Perspectives on ${params.query}`,
                    authors: ["Dr. Jane Smith", "Prof. John Doe"],
                    abstract: `This comprehensive review examines current research trends and future directions in ${params.query}. The paper synthesizes findings from multiple studies and proposes new frameworks for understanding this complex topic.`,
                    source_type: "scholar",
                    url: "https://scholar.google.com/citations?view_op=view_citation&citation_for_view=generic1",
                    published: "2023-03-15",
                    citation_count: 156,
                    venue: "Journal of Academic Research"
                },
                {
                    title: `Advances in ${params.query}: A Systematic Analysis`,
                    authors: ["Dr. Alice Johnson", "Prof. Bob Wilson", "Dr. Carol Brown"],
                    abstract: `Recent developments in ${params.query} have opened new avenues for research and application. This paper provides a systematic analysis of current methodologies and their implications for future work.`,
                    source_type: "semantic_scholar",
                    url: "https://www.semanticscholar.org/paper/generic-example",
                    published: "2023-07-20",
                    citation_count: 89,
                    venue: "International Conference on Advanced Research"
                }
            ];
        }

        // Add web sources if enabled
        if (params.include_web) {
            mockSources.push({
                title: `${params.query} - Wikipedia Overview`,
                authors: ["Wikipedia Contributors"],
                abstract: `Wikipedia article providing comprehensive background information and current understanding of ${params.query}. Includes historical context, current applications, and references to academic sources.`,
                source_type: "web",
                url: `https://en.wikipedia.org/wiki/${params.query.replace(/\s+/g, '_')}`,
                published: "2024-01-01",
                citation_count: null,
                venue: "Wikipedia"
            });
        }

        // Limit to requested number of sources
        mockSources = mockSources.slice(0, params.max_sources);

        return {
            query: params.query,
            answer: this.generateMockAnswer(params.query, mockSources.length),
            sources: mockSources,
            execution_time: Math.random() * 25 + 5, // 5-30 seconds
            success: true,
            timestamp: new Date().toISOString(),
            params: params
        };
    }

    generateMockAnswer(query, sourceCount) {
        return `
            <h3>Research Summary: ${query}</h3>
            
            <p>Based on comprehensive analysis of <strong>${sourceCount} academic and scholarly sources</strong>, here are the key findings:</p>
            
            <h4>Key Insights</h4>
            <p>The research reveals significant developments and ongoing discussions in ${query.toLowerCase()}. Current scholarship demonstrates both theoretical advances and practical applications, with increasing interdisciplinary collaboration evident across recent publications.</p>
            
            <h4>Current Research Trends</h4>
            <ul>
                <li><strong>Methodological Innovation:</strong> Researchers are developing new approaches and refining existing methodologies</li>
                <li><strong>Cross-disciplinary Integration:</strong> Increasing collaboration between different fields and research domains</li>
                <li><strong>Practical Applications:</strong> Growing focus on real-world implementation and impact assessment</li>
                <li><strong>Open Questions:</strong> Several important research questions remain actively debated in the literature</li>
            </ul>
            
            <h4>Future Directions</h4>
            <p>The literature suggests several promising avenues for future research, including enhanced methodological approaches, broader application domains, and deeper theoretical understanding. Emerging technologies and changing societal needs continue to drive innovation in this field.</p>
            
            <h4>Implications</h4>
            <p>These findings have important implications for both academic research and practical applications. The convergence of multiple research streams indicates this is an active field with substantial potential for continued development and real-world impact.</p>
        `;
    }

    async healthCheck() {
        if (!this.baseUrl) {
            return { status: 'GitHub Pages Mode', backend: false };
        }

        try {
            const response = await this.makeRequest('/health');
            if (response.ok) {
                const data = await response.json();
                return { status: 'Connected', backend: true, ...data };
            } else {
                return { status: 'Backend Unavailable', backend: false };
            }
        } catch (error) {
            return { status: 'Connection Failed', backend: false, error: error.message };
        }
    }
}
