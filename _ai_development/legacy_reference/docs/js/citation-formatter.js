/**
 * Citation Formatter - Handles academic citation formatting for different styles
 * Supports APA, MLA, Chicago, IEEE, and Web Simple formats
 */

class CitationFormatter {
    constructor() {
        this.styles = {
            'APA': this.formatAPA.bind(this),
            'MLA': this.formatMLA.bind(this),
            'CHICAGO': this.formatChicago.bind(this),
            'IEEE': this.formatIEEE.bind(this),
            'WEB_SIMPLE': this.formatWebSimple.bind(this)
        };
    }

    formatCitation(source, style = 'APA') {
        const formatter = this.styles[style.toUpperCase()];
        if (!formatter) {
            console.warn(`Unknown citation style: ${style}, falling back to APA`);
            return this.formatAPA(source);
        }
        
        return formatter(source);
    }

    formatAPA(source) {
        let citation = '';
        
        // Authors
        if (source.authors && source.authors.length > 0) {
            if (source.authors.length === 1) {
                citation += `${source.authors[0]}. `;
            } else if (source.authors.length <= 6) {
                if (source.authors.length === 2) {
                    citation += `${source.authors[0]} & ${source.authors[1]}. `;
                } else {
                    const allButLast = source.authors.slice(0, -1).join(', ');
                    citation += `${allButLast}, & ${source.authors[source.authors.length - 1]}. `;
                }
            } else {
                citation += `${source.authors[0]} et al. `;
            }
        }
        
        // Year
        const year = this.extractYear(source);
        if (year) {
            citation += `(${year}). `;
        }
        
        // Title
        if (source.source_type === 'web') {
            citation += `${source.title}. `;
        } else {
            citation += `${source.title}. `;
        }
        
        // Venue/Journal
        if (source.venue) {
            citation += `*${source.venue}*. `;
        }
        
        // Special handling for different source types
        if (source.source_type === 'arxiv') {
            const arxivId = this.extractArxivId(source.url);
            citation += `arXiv preprint arXiv:${arxivId}.`;
        } else if (source.url) {
            citation += `Retrieved from ${source.url}`;
        }
        
        return citation.trim();
    }

    formatMLA(source) {
        let citation = '';
        
        // Authors
        if (source.authors && source.authors.length > 0) {
            citation += `${source.authors[0]}`;
            if (source.authors.length > 1) {
                citation += ', et al';
            }
            citation += '. ';
        }
        
        // Title
        citation += `"${source.title}." `;
        
        // Venue
        if (source.venue) {
            citation += `${source.venue}, `;
        }
        
        // Year
        const year = this.extractYear(source);
        if (year) {
            citation += `${year}, `;
        }
        
        // URL
        if (source.url) {
            citation += `${source.url}.`;
        }
        
        return citation.trim();
    }

    formatChicago(source) {
        let citation = '';
        
        // Authors
        if (source.authors && source.authors.length > 0) {
            citation += `${source.authors[0]}`;
            if (source.authors.length > 1) {
                citation += ' et al';
            }
            citation += '. ';
        }
        
        // Title
        citation += `"${source.title}." `;
        
        // Venue
        if (source.venue) {
            citation += `${source.venue} `;
        }
        
        // Year
        const year = this.extractYear(source);
        if (year) {
            citation += `(${year}). `;
        }
        
        // URL
        if (source.url) {
            citation += `Accessed from ${source.url}.`;
        }
        
        return citation.trim();
    }

    formatIEEE(source) {
        let citation = '';
        
        // Authors
        if (source.authors && source.authors.length > 0) {
            citation += `${source.authors[0]}`;
            if (source.authors.length > 1) {
                citation += ' et al';
            }
            citation += ', ';
        }
        
        // Title
        citation += `"${source.title}," `;
        
        // Venue
        if (source.venue) {
            citation += `${source.venue}, `;
        }
        
        // Year
        const year = this.extractYear(source);
        if (year) {
            citation += `${year}, `;
        }
        
        // URL
        if (source.url) {
            citation += `[Online]. Available: ${source.url}`;
        }
        
        return citation.trim();
    }

    formatWebSimple(source) {
        let citation = `${source.title}`;
        
        if (source.venue) {
            citation += ` - ${source.venue}`;
        }
        
        if (source.authors && source.authors.length > 0) {
            citation += ` (by ${source.authors[0]}`;
            if (source.authors.length > 1) {
                citation += ' et al';
            }
            citation += ')';
        }
        
        return citation;
    }

    extractYear(source) {
        if (source.year) {
            return source.year;
        }
        
        if (source.published) {
            const match = source.published.match(/(\d{4})/);
            return match ? match[1] : null;
        }
        
        return null;
    }

    extractArxivId(url) {
        if (!url) return 'unknown';
        
        // Extract arXiv ID from URL
        const match = url.match(/arxiv\.org\/(?:abs|pdf)\/(.+?)(?:\.pdf)?$/);
        return match ? match[1] : 'unknown';
    }

    generateBibliography(sources, style = 'APA') {
        const citations = sources.map(source => this.formatCitation(source, style));
        return citations.sort().join('\n\n');
    }

    getSourceTypeIcon(sourceType) {
        const icons = {
            'arxiv': '📄',
            'scholar': '🎓',
            'semantic_scholar': '🧠',
            'web': '🌐',
            'unknown': '📖'
        };
        
        return icons[sourceType] || icons.unknown;
    }

    getSourceTypeColor(sourceType) {
        const colors = {
            'arxiv': '#e74c3c',
            'scholar': '#3498db', 
            'semantic_scholar': '#9b59b6',
            'web': '#27ae60',
            'unknown': '#95a5a6'
        };
        
        return colors[sourceType] || colors.unknown;
    }

    getSourceTypeLabel(sourceType) {
        const labels = {
            'arxiv': 'arXiv',
            'scholar': 'Google Scholar',
            'semantic_scholar': 'Semantic Scholar',
            'web': 'Web Source',
            'unknown': 'Academic Source'
        };
        
        return labels[sourceType] || labels.unknown;
    }
}
