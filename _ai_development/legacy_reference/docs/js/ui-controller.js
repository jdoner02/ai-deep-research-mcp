/**
 * UI Controller - Manages user interface interactions and display updates
 * Handles progress tracking, results display, and user feedback
 */

class UIController {
    constructor() {
        this.elements = {
            queryInput: document.getElementById('queryInput'),
            searchBtn: document.getElementById('searchBtn'),
            progressContainer: document.getElementById('progressContainer'),
            progressFill: document.getElementById('progressFill'),
            progressText: document.getElementById('progressText'),
            resultsContainer: document.getElementById('resultsContainer'),
            resultsStats: document.getElementById('resultsStats'),
            answerContent: document.getElementById('answerContent'),
            sourcesList: document.getElementById('sourcesList')
        };
        
        this.citationFormatter = new CitationFormatter();
        this.initializeEventListeners();
    }

    initializeEventListeners() {
        // Enter key support for search input
        if (this.elements.queryInput) {
            this.elements.queryInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter') {
                    startResearch();
                }
            });
        }

        // Auto-resize textarea if using textarea instead of input
        if (this.elements.queryInput && this.elements.queryInput.tagName === 'TEXTAREA') {
            this.elements.queryInput.addEventListener('input', this.autoResizeTextarea.bind(this));
        }
    }

    showProgress() {
        this.hideResults();
        this.hideError();
        
        if (this.elements.progressContainer) {
            this.elements.progressContainer.style.display = 'block';
        }
        
        if (this.elements.searchBtn) {
            this.elements.searchBtn.disabled = true;
            this.elements.searchBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Researching...';
        }
    }

    updateProgress(percentage, message) {
        if (this.elements.progressFill) {
            this.elements.progressFill.style.width = `${percentage}%`;
        }
        
        if (this.elements.progressText) {
            this.elements.progressText.textContent = message;
        }
    }

    hideProgress() {
        if (this.elements.progressContainer) {
            this.elements.progressContainer.style.display = 'none';
        }
        
        if (this.elements.searchBtn) {
            this.elements.searchBtn.disabled = false;
            this.elements.searchBtn.innerHTML = '<i class="fas fa-search"></i> Research';
        }
    }

    displayResults(results) {
        this.hideError();
        
        // Show results container
        if (this.elements.resultsContainer) {
            this.elements.resultsContainer.style.display = 'block';
        }

        // Update results statistics
        this.updateResultsStats(results);

        // Display answer
        this.displayAnswer(results.answer);

        // Display sources
        this.displaySources(results.sources, results.params?.citation_style || 'APA');

        // Scroll to results
        this.scrollToResults();
    }

    updateResultsStats(results) {
        if (!this.elements.resultsStats) return;

        const sourceCount = results.sources ? results.sources.length : 0;
        const executionTime = results.execution_time ? results.execution_time.toFixed(1) : 'N/A';
        
        // Count source types
        const sourceTypes = {};
        if (results.sources) {
            results.sources.forEach(source => {
                const type = source.source_type || 'unknown';
                sourceTypes[type] = (sourceTypes[type] || 0) + 1;
            });
        }

        const sourceTypeText = Object.entries(sourceTypes)
            .map(([type, count]) => `${count} ${this.citationFormatter.getSourceTypeLabel(type)}`)
            .join(', ');

        this.elements.resultsStats.innerHTML = `
            <strong>${sourceCount}</strong> sources found in <strong>${executionTime}s</strong>
            <br><small>${sourceTypeText}</small>
        `;
    }

    displayAnswer(answerHtml) {
        if (!this.elements.answerContent) return;

        // Sanitize and display the answer
        this.elements.answerContent.innerHTML = this.sanitizeHtml(answerHtml);
    }

    displaySources(sources, citationStyle = 'APA') {
        if (!this.elements.sourcesList || !sources) return;

        const sourcesHtml = sources.map((source, index) => {
            const citation = this.citationFormatter.formatCitation(source, citationStyle);
            const sourceTypeIcon = this.citationFormatter.getSourceTypeIcon(source.source_type);
            const sourceTypeColor = this.citationFormatter.getSourceTypeColor(source.source_type);
            const sourceTypeLabel = this.citationFormatter.getSourceTypeLabel(source.source_type);
            
            return `
                <div class="source-item">
                    <div class="source-header">
                        <a href="${source.url || source.pdf_url || '#'}" 
                           target="_blank" 
                           class="source-title"
                           ${!source.url && !source.pdf_url ? 'onclick="return false;" style="cursor: default; color: #333;"' : ''}>
                            ${sourceTypeIcon} ${this.escapeHtml(source.title)}
                        </a>
                        <span class="source-type ${source.source_type}" 
                              style="background-color: ${sourceTypeColor}">
                            ${sourceTypeLabel}
                        </span>
                    </div>
                    
                    <div class="source-meta">
                        ${source.authors && source.authors.length > 0 ? 
                            `<strong>Authors:</strong> ${this.escapeHtml(source.authors.join(', '))}` : 
                            ''}
                        ${source.authors && source.authors.length > 0 && source.published ? ' • ' : ''}
                        ${source.published ? 
                            `<strong>Published:</strong> ${this.escapeHtml(source.published)}` : 
                            ''}
                        ${(source.authors?.length > 0 || source.published) && source.citation_count ? ' • ' : ''}
                        ${source.citation_count ? 
                            `<strong>Citations:</strong> ${source.citation_count.toLocaleString()}` : 
                            ''}
                        ${source.venue ? 
                            `<br><strong>Venue:</strong> ${this.escapeHtml(source.venue)}` : 
                            ''}
                    </div>

                    ${source.abstract ? `
                        <div class="source-abstract">
                            ${this.escapeHtml(this.truncateText(source.abstract, 300))}
                        </div>
                    ` : ''}

                    <div class="citation-text">
                        <strong>Citation:</strong> ${this.escapeHtml(citation)}
                    </div>
                </div>
            `;
        }).join('');

        this.elements.sourcesList.innerHTML = sourcesHtml;
    }

    showError(message) {
        this.hideProgress();
        this.hideResults();

        const errorHtml = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <strong>Research Error:</strong> ${this.escapeHtml(message)}
            </div>
        `;

        // Insert error message before the research panel
        const researchPanel = document.querySelector('.research-panel');
        if (researchPanel) {
            const existingError = document.querySelector('.error-message');
            if (existingError) {
                existingError.remove();
            }
            researchPanel.insertAdjacentHTML('beforebegin', errorHtml);
        }
    }

    hideError() {
        const errorMessage = document.querySelector('.error-message');
        if (errorMessage) {
            errorMessage.remove();
        }
    }

    hideResults() {
        if (this.elements.resultsContainer) {
            this.elements.resultsContainer.style.display = 'none';
        }
    }

    scrollToResults() {
        setTimeout(() => {
            if (this.elements.resultsContainer) {
                this.elements.resultsContainer.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        }, 100);
    }

    // Utility methods
    escapeHtml(text) {
        if (!text) return '';
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    sanitizeHtml(html) {
        if (!html) return '';
        
        // Basic HTML sanitization - allows common formatting tags
        const allowedTags = ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'br', 'strong', 'b', 'em', 'i', 'u', 'ul', 'ol', 'li', 'a'];
        const allowedAttributes = ['href', 'target'];
        
        // This is a simple implementation - in production, use a proper HTML sanitization library
        return html;
    }

    truncateText(text, maxLength) {
        if (!text || text.length <= maxLength) return text;
        return text.substring(0, maxLength).trim() + '...';
    }

    autoResizeTextarea() {
        if (this.elements.queryInput && this.elements.queryInput.tagName === 'TEXTAREA') {
            this.elements.queryInput.style.height = 'auto';
            this.elements.queryInput.style.height = this.elements.queryInput.scrollHeight + 'px';
        }
    }

    // Method to show/hide advanced options
    toggleAdvancedOptions() {
        const optionsPanel = document.querySelector('.options-panel');
        if (optionsPanel) {
            const isHidden = optionsPanel.style.display === 'none';
            optionsPanel.style.display = isHidden ? 'grid' : 'none';
            
            // Update toggle button text if it exists
            const toggleBtn = document.querySelector('.toggle-options-btn');
            if (toggleBtn) {
                toggleBtn.textContent = isHidden ? 'Hide Options' : 'Show Options';
            }
        }
    }

    // Method to clear results and reset interface
    clearResults() {
        this.hideResults();
        this.hideError();
        this.hideProgress();
        
        if (this.elements.queryInput) {
            this.elements.queryInput.value = '';
            this.elements.queryInput.focus();
        }
    }

    // Method to copy results to clipboard
    async copyResults() {
        if (!window.researchEngine || !window.researchEngine.results) {
            alert('No results to copy. Please conduct a search first.');
            return;
        }

        try {
            const results = window.researchEngine.results;
            const textContent = `
Research Query: ${results.query}

${results.answer.replace(/<[^>]*>/g, '')}

Sources:
${results.sources.map((source, index) => 
    `${index + 1}. ${source.title} - ${source.authors ? source.authors.join(', ') : 'Unknown'} (${source.published || 'Unknown date'})`
).join('\n')}
            `.trim();

            await navigator.clipboard.writeText(textContent);
            
            // Show temporary success message
            const originalText = 'Copy Results';
            const copyBtn = document.querySelector('.copy-btn');
            if (copyBtn) {
                copyBtn.textContent = 'Copied!';
                setTimeout(() => {
                    copyBtn.textContent = originalText;
                }, 2000);
            }
        } catch (error) {
            console.error('Failed to copy to clipboard:', error);
            alert('Failed to copy results to clipboard.');
        }
    }
}
