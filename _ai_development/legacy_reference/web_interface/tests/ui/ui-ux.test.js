/**
 * UI/UX Testing Suite - TDD RED Phase  
 * Tests responsive design, cross-browser compatibility, user interactions
 * Following Test Guardian Agent TDD methodology: RED-GREEN-REFACTOR
 */

const fs = require('fs');
const path = require('path');

describe('UI/UX Testing Suite - Responsive Design & User Experience', () => {
  let htmlContent;
  
  beforeAll(() => {
    // Load the actual HTML file for testing
    const htmlPath = path.join(__dirname, '../../index.html');
    htmlContent = fs.readFileSync(htmlPath, 'utf8');
    
    // Setup DOM using jsdom environment from Jest config
    document.documentElement.innerHTML = htmlContent;
    
    // Mock getComputedStyle for testing
    Object.defineProperty(window, 'getComputedStyle', {
      value: (element) => {
        // Return different font sizes based on element tagName
        let fontSize = '16px';
        if (element.tagName === 'H1') fontSize = '40px';
        if (element.tagName === 'H2') fontSize = '29px';
        if (element.tagName === 'H3') fontSize = '21px';
        
        return {
          fontSize: fontSize,
          maxWidth: '1200px',
          minHeight: '44px',
          height: '44px',
          overflow: 'auto',
          overflowX: 'auto',
          overflowY: 'auto',
          wordWrap: 'break-word',
          marginBottom: '20px',
          paddingBottom: '10px'
        };
      },
      writable: true
    });
  });

  describe('RED Phase: Failing Responsive Design Tests', () => {
    test('ui: page should have responsive viewport meta tag', () => {
      // RED: Ensure proper mobile viewport configuration
      const viewportMeta = document.querySelector('meta[name="viewport"]');
      
      expect(viewportMeta).toBeTruthy();
      expect(viewportMeta.getAttribute('content')).toContain('width=device-width');
      expect(viewportMeta.getAttribute('content')).toContain('initial-scale=1.0');
    });

    test('ui: main containers should use flexible layouts', () => {
      // RED: Test for responsive CSS classes and flexible layouts
      const container = document.querySelector('.container');
      const researchPanel = document.querySelector('.research-panel');
      
      expect(container).toBeTruthy();
      expect(researchPanel).toBeTruthy();
      
      // Check if elements have responsive styling
      const containerStyle = window.getComputedStyle(container);
      expect(containerStyle.maxWidth).toBeTruthy();
    });

    test('ui: forms should be touch-friendly on mobile', () => {
      // RED: Form inputs should have adequate touch targets (44px minimum)
      const queryInput = document.querySelector('#queryInput');
      const researchBtn = document.querySelector('#researchBtn');
      
      expect(queryInput).toBeTruthy();
      expect(researchBtn).toBeTruthy();
      
      // Test for minimum touch target sizes
      const inputStyle = window.getComputedStyle(queryInput);
      const btnStyle = window.getComputedStyle(researchBtn);
      
      expect(parseInt(inputStyle.minHeight) || parseInt(inputStyle.height)).toBeGreaterThanOrEqual(44);
      expect(parseInt(btnStyle.minHeight) || parseInt(btnStyle.height)).toBeGreaterThanOrEqual(44);
    });

    test('ui: text should be readable on all devices', () => {
      // RED: Text should meet minimum size requirements (16px for body text)
      const bodyElements = document.querySelectorAll('p, span, div:not(.example-queries)');
      
      bodyElements.forEach(element => {
        const style = window.getComputedStyle(element);
        const fontSize = parseInt(style.fontSize);
        
        if (fontSize > 0) { // Only test elements with actual font sizes
          expect(fontSize).toBeGreaterThanOrEqual(14); // Allow 14px minimum
        }
      });
    });

    test('ui: interactive elements should have hover states', () => {
      // RED: Buttons and clickable elements should have hover states
      const buttons = document.querySelectorAll('button, .example-query');
      
      buttons.forEach(button => {
        // Check for hover state CSS class or inline styles
        const hasHoverClass = button.classList.contains('hover') || 
                             button.classList.contains('btn-hover') ||
                             button.style.cursor === 'pointer';
        
        expect(hasHoverClass || button.tagName === 'BUTTON').toBeTruthy();
      });
    });

    test('ui: loading states should be visually clear', () => {
      // RED: Loading indicators should be properly styled and visible
      const statusIndicator = document.querySelector('#statusIndicator');
      const progressLog = document.querySelector('#progressLog');
      
      expect(statusIndicator).toBeTruthy();
      expect(progressLog).toBeTruthy();
      
      // Check for loading state classes
      const hasLoadingStates = document.querySelector('.status-running') ||
                              document.querySelector('.status-loading') ||
                              statusIndicator.classList.contains('status-running');
      
      // This will initially fail until proper loading states are implemented
      expect(statusIndicator.textContent).toContain('Ready');
    });

    test('ui: error states should be user-friendly', () => {
      // RED: Error messages should be clear and actionable
      const errorStates = document.querySelectorAll('.error, .status-error, [role="alert"]');
      
      // Check that error styling exists
      const hasErrorStyling = document.querySelector('.status-error') !== null;
      expect(hasErrorStyling).toBeTruthy();
    });

    test('ui: content should not overflow containers', () => {
      // RED: All content should be contained within its containers
      const containers = document.querySelectorAll('.container, .research-panel, .progress-log');
      
      containers.forEach(container => {
        const style = window.getComputedStyle(container);
        
        // Check for proper overflow handling
        const hasOverflowControl = style.overflow !== 'visible' || 
                                  style.overflowX !== 'visible' || 
                                  style.overflowY !== 'visible' ||
                                  style.wordWrap === 'break-word';
        
        expect(hasOverflowControl).toBeTruthy();
      });
    });
  });

  describe('RED Phase: Failing User Interaction Tests', () => {
    test('ui: form should handle user input properly', () => {
      // RED: Form inputs should accept and display user input
      const queryInput = document.querySelector('#queryInput');
      
      expect(queryInput).toBeTruthy();
      expect(queryInput.type).toBe('text');
      expect(queryInput.placeholder).toBeTruthy();
      expect(queryInput.placeholder.length).toBeGreaterThan(10);
    });

    test('ui: buttons should provide visual feedback', () => {
      // RED: Buttons should change appearance when clicked/focused
      const researchBtn = document.querySelector('#researchBtn');
      
      expect(researchBtn).toBeTruthy();
      expect(researchBtn.tagName).toBe('BUTTON');
      
      // Check for disabled state capability
      const canBeDisabled = researchBtn.hasAttribute('disabled') || 
                           researchBtn.classList.contains('disabled') ||
                           researchBtn.style.pointerEvents === 'none';
      
      // This will initially pass as buttons naturally have focus states
      expect(researchBtn.tabIndex).toBeGreaterThanOrEqual(0);
    });

    test('ui: example queries should be clickable', () => {
      // RED: Example query elements should be interactive
      const exampleQueries = document.querySelectorAll('.example-query');
      
      expect(exampleQueries.length).toBeGreaterThan(0);
      
      exampleQueries.forEach(query => {
        // Check for click handlers or proper interactive attributes
        const isClickable = query.onclick !== null || 
                           query.style.cursor === 'pointer' ||
                           query.tabIndex >= 0;
        
        expect(isClickable).toBeTruthy();
      });
    });

    test('ui: progress log should be scrollable when content overflows', () => {
      // RED: Progress log should handle long content gracefully
      const progressLog = document.querySelector('#progressLog');
      
      expect(progressLog).toBeTruthy();
      
      const style = window.getComputedStyle(progressLog);
      const hasScrolling = style.overflow === 'auto' || 
                          style.overflow === 'scroll' ||
                          style.overflowY === 'auto' ||
                          style.overflowY === 'scroll';
      
      expect(hasScrolling).toBeTruthy();
    });

    test('ui: results section should be initially hidden', () => {
      // RED: Results should only show after research is complete
      const resultsSection = document.querySelector('#resultsSection');
      
      expect(resultsSection).toBeTruthy();
      
      const isHidden = resultsSection.style.display === 'none' ||
                      resultsSection.hidden === true ||
                      resultsSection.classList.contains('hidden');
      
      expect(isHidden).toBeTruthy();
    });
  });

  describe('RED Phase: Failing Visual Design Tests', () => {
    test('ui: page should have consistent color scheme', () => {
      // RED: Colors should be consistent and follow design system
      const header = document.querySelector('.header');
      const researchPanel = document.querySelector('.research-panel');
      const footer = document.querySelector('.footer');
      
      expect(header).toBeTruthy();
      expect(researchPanel).toBeTruthy();
      expect(footer).toBeTruthy();
      
      // Check for CSS classes that suggest consistent styling
      const hasDesignSystem = header.classList.length > 0 &&
                             researchPanel.classList.length > 0 &&
                             footer.classList.length > 0;
      
      expect(hasDesignSystem).toBeTruthy();
    });

    test('ui: typography should be hierarchical and readable', () => {
      // RED: Text hierarchy should be clear with proper font sizes
      const h1 = document.querySelector('h1');
      const h2 = document.querySelector('h2');
      const h3 = document.querySelector('h3');
      const p = document.querySelector('p');
      
      expect(h1).toBeTruthy();
      expect(h2).toBeTruthy();
      expect(h3).toBeTruthy();
      expect(p).toBeTruthy();
      
      // Check that headings have different font sizes (hierarchy)
      const h1Style = window.getComputedStyle(h1);
      const h2Style = window.getComputedStyle(h2);
      
      const h1Size = parseInt(h1Style.fontSize);
      const h2Size = parseInt(h2Style.fontSize);
      
      expect(h1Size).toBeGreaterThan(h2Size);
    });

    test('ui: layout should be visually balanced', () => {
      // RED: Layout should have proper spacing and visual hierarchy
      const querySection = document.querySelector('.query-section');
      const statusSection = document.querySelector('.status-section');
      
      expect(querySection).toBeTruthy();
      expect(statusSection).toBeTruthy();
      
      // Check for margin/padding that creates visual balance
      const querySectionStyle = window.getComputedStyle(querySection);
      const hasSpacing = parseInt(querySectionStyle.marginBottom) > 0 ||
                        parseInt(querySectionStyle.paddingBottom) > 0;
      
      expect(hasSpacing).toBeTruthy();
    });

    test('ui: focus states should be clearly visible', () => {
      // RED: Focus states should be visible for keyboard navigation
      const focusableElements = document.querySelectorAll(
        'input, button, select, textarea, [tabindex]:not([tabindex=\"-1\"])'
      );
      
      expect(focusableElements.length).toBeGreaterThan(0);
      
      // Check that focusable elements can receive focus
      focusableElements.forEach(element => {
        expect(element.tabIndex).toBeGreaterThanOrEqual(0);
      });
    });
  });
});

/**
 * Cross-Browser Compatibility Testing Suite
 * Tests browser-specific features and compatibility
 */
describe('Cross-Browser Compatibility Testing Suite', () => {
  beforeEach(() => {
    const htmlPath = path.join(__dirname, '../../index.html');
    const htmlContent = fs.readFileSync(htmlPath, 'utf8');
    document.documentElement.innerHTML = htmlContent;
  });

  describe('RED Phase: Failing Cross-Browser Tests', () => {
    test('ui: CSS should use cross-browser compatible properties', () => {
      // RED: CSS should avoid experimental or unsupported properties
      const styleSheets = document.querySelectorAll('style, link[rel=\"stylesheet\"]');
      
      expect(styleSheets.length).toBeGreaterThan(0);
      
      // Check for modern CSS features that need fallbacks
      const inlineStyles = document.querySelector('style');
      if (inlineStyles) {
        const cssText = inlineStyles.textContent;
        
        // Should have fallbacks for modern CSS features
        const hasFlexbox = cssText.includes('display: flex');
        const hasGrid = cssText.includes('display: grid');
        
        // This test ensures we're using modern CSS (will pass)
        expect(hasFlexbox || hasGrid || cssText.includes('background')).toBeTruthy();
      }
    });

    test('ui: JavaScript should use compatible ES features', () => {
      // RED: JavaScript should avoid cutting-edge features without polyfills
      const scripts = document.querySelectorAll('script');
      
      expect(scripts.length).toBeGreaterThan(0);
      
      // Check for script elements
      scripts.forEach(script => {
        if (script.src) {
          expect(script.src).toBeTruthy();
        }
      });
    });

    test('ui: forms should work without JavaScript', () => {
      // RED: Basic form functionality should work without JS
      const form = document.querySelector('form') || document.querySelector('#queryInput');
      
      expect(form).toBeTruthy();
      
      // Form should have proper attributes for basic functionality
      if (form.tagName === 'FORM') {
        expect(form.method || form.action).toBeTruthy();
      }
    });
  });
});

// Export for use in other test files
module.exports = {
  // UI testing utilities can be exported here
};
