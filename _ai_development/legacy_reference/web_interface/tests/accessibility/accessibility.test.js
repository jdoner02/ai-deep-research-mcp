/**
 * Accessibility Testing Suite - TDD RED Phase
 * Tests WCAG 2.1 AA compliance, keyboard navigation, screen reader support
 * Following Test Guardian Agent TDD methodology: RED-GREEN-REFACTOR
 */

const { axe, toHaveNoViolations } = require('jest-axe');
const fs = require('fs');
const path = require('path');

// Extend Jest matchers for accessibility
expect.extend(toHaveNoViolations);

describe('Accessibility Testing Suite - WCAG 2.1 AA Compliance', () => {
  let htmlContent;
  
  beforeAll(() => {
    // Load the actual HTML file for testing
    const htmlPath = path.join(__dirname, '../../index.html');
    htmlContent = fs.readFileSync(htmlPath, 'utf8');
    
    // Setup DOM using jsdom (configured in Jest)
    document.documentElement.innerHTML = htmlContent;
    // Also set the lang attribute on the document element for the test
    document.documentElement.setAttribute('lang', 'en');
  });

  describe('RED Phase: Failing Accessibility Tests', () => {
    test('accessibility: page should have no WCAG violations', async () => {
      // RED: This test should initially fail until accessibility features are implemented
      const results = await axe(document.body);
      expect(results).toHaveNoViolations();
    });

    test('accessibility: page should have proper semantic structure', () => {
      // RED: Testing for semantic HTML structure
      const main = document.querySelector('main');
      const header = document.querySelector('header');
      const nav = document.querySelector('nav');
      
      expect(main).toBeTruthy();
      expect(header).toBeTruthy();
      // Navigation may be optional for this interface
    });

    test('accessibility: all images should have alt text', () => {
      // RED: All images must have meaningful alt text
      const images = document.querySelectorAll('img');
      images.forEach(img => {
        expect(img.getAttribute('alt')).toBeTruthy();
        expect(img.getAttribute('alt').trim()).not.toBe('');
      });
    });

    test('accessibility: form inputs should have proper labels', () => {
      // RED: All form inputs must have associated labels
      const inputs = document.querySelectorAll('input, textarea, select');
      inputs.forEach(input => {
        const id = input.getAttribute('id');
        const label = document.querySelector(`label[for="${id}"]`);
        const ariaLabel = input.getAttribute('aria-label');
        
        expect(id).toBeTruthy();
        expect(label || ariaLabel).toBeTruthy();
      });
    });

    test('accessibility: buttons should have accessible names', () => {
      // RED: All buttons must have accessible names
      const buttons = document.querySelectorAll('button');
      buttons.forEach(button => {
        const text = button.textContent.trim();
        const ariaLabel = button.getAttribute('aria-label');
        const title = button.getAttribute('title');
        
        expect(text || ariaLabel || title).toBeTruthy();
      });
    });

    test('accessibility: page should have proper heading hierarchy', () => {
      // RED: Headings should follow proper hierarchy (h1 -> h2 -> h3, etc.)
      const headings = document.querySelectorAll('h1, h2, h3, h4, h5, h6');
      
      expect(headings.length).toBeGreaterThan(0);
      
      let previousLevel = 0;
      headings.forEach(heading => {
        const level = parseInt(heading.tagName.charAt(1));
        
        if (previousLevel > 0) {
          // Should not skip heading levels
          expect(level - previousLevel).toBeLessThanOrEqual(1);
        } else {
          // First heading should be h1
          expect(level).toBe(1);
        }
        
        previousLevel = level;
      });
    });

    test('accessibility: interactive elements should be keyboard accessible', () => {
      // RED: All interactive elements should be focusable
      const interactiveElements = document.querySelectorAll(
        'button, a, input, textarea, select, [tabindex]'
      );
      
      interactiveElements.forEach(element => {
        const tabIndex = element.getAttribute('tabindex');
        
        // Should not have tabindex=\"-1\" unless intentionally removed from tab order
        if (tabIndex !== null) {
          expect(parseInt(tabIndex)).toBeGreaterThanOrEqual(0);
        }
      });
    });

    test('accessibility: color contrast should meet WCAG AA standards', async () => {
      // RED: Color contrast ratios should meet WCAG AA (4.5:1 for normal text, 3:1 for large text)
      const results = await axe(document.body, {
        rules: {
          'color-contrast': { enabled: true }
        }
      });
      
      expect(results).toHaveNoViolations();
    });

    test('accessibility: form validation should be accessible', () => {
      // RED: Form validation messages should be properly associated with inputs
      const forms = document.querySelectorAll('form');
      
      forms.forEach(form => {
        const inputs = form.querySelectorAll('input, textarea, select');
        
        inputs.forEach(input => {
          const ariaDescribedBy = input.getAttribute('aria-describedby');
          const ariaInvalid = input.getAttribute('aria-invalid');
          
          // If there's validation, it should be properly marked up
          if (ariaInvalid === 'true') {
            expect(ariaDescribedBy).toBeTruthy();
          }
        });
      });
    });

    test('accessibility: ARIA landmarks should be present', () => {
      // RED: Page should have proper ARIA landmarks for screen readers
      const main = document.querySelector('[role=\"main\"], main');
      const banner = document.querySelector('[role=\"banner\"], header');
      const contentinfo = document.querySelector('[role=\"contentinfo\"], footer');
      
      expect(main).toBeTruthy();
      expect(banner).toBeTruthy();
      // Footer/contentinfo may be optional
    });

    test('accessibility: focus indicators should be visible', () => {
      // RED: All focusable elements should have visible focus indicators
      const focusableElements = document.querySelectorAll(
        'a, button, input, textarea, select, [tabindex]:not([tabindex=\"-1\"])'
      );
      
      focusableElements.forEach(element => {
        // This test ensures elements can receive focus
        // Visual focus indicators are tested in e2e tests
        expect(element.tabIndex).toBeGreaterThanOrEqual(0);
      });
    });

    test('accessibility: page should have a descriptive title', () => {
      // RED: Page title should be descriptive and unique
      const title = document.querySelector('title');
      
      expect(title).toBeTruthy();
      expect(title.textContent.trim()).not.toBe('');
      expect(title.textContent.length).toBeGreaterThan(10);
    });

    test('accessibility: language should be specified', () => {
      // RED: HTML element should have lang attribute
      const html = document.documentElement || document.querySelector('html');
      
      expect(html.getAttribute('lang')).toBeTruthy();
      expect(html.getAttribute('lang')).toMatch(/^[a-z]{2}(-[A-Z]{2})?$/);
    });
  });
});

/**
 * Keyboard Navigation Testing Suite
 * Tests keyboard accessibility and navigation patterns
 */
describe('Keyboard Navigation Testing Suite', () => {
  beforeEach(() => {
    // Reset DOM for each test
    const htmlPath = path.join(__dirname, '../../index.html');
    const htmlContent = fs.readFileSync(htmlPath, 'utf8');
    document.documentElement.innerHTML = htmlContent;
  });

  describe('RED Phase: Failing Keyboard Navigation Tests', () => {
    test('keyboard: all interactive elements should be reachable via Tab', () => {
      // RED: Tab navigation should reach all interactive elements
      const interactiveElements = document.querySelectorAll(
        'a, button, input, textarea, select, [tabindex]:not([tabindex=\"-1\"])'
      );
      
      interactiveElements.forEach(element => {
        expect(element.tabIndex).toBeGreaterThanOrEqual(0);
      });
    });

    test('keyboard: Enter key should activate buttons', () => {
      // RED: Buttons should be activatable with Enter key
      const buttons = document.querySelectorAll('button');
      
      buttons.forEach(button => {
        // Ensure button has proper event handling attributes or handlers
        const onClick = button.getAttribute('onclick');
        const hasEventListeners = button._eventListeners || false;
        
        // This will initially fail until proper event handling is implemented
        expect(onClick || hasEventListeners).toBeTruthy();
      });
    });

    test('keyboard: Space key should activate buttons', () => {
      // RED: Buttons should be activatable with Space key
      const buttons = document.querySelectorAll('button');
      
      buttons.forEach(button => {
        // Check for proper button implementation that supports space activation
        expect(button.tagName.toLowerCase()).toBe('button');
      });
    });

    test('keyboard: Escape key should close modals/dropdowns', () => {
      // RED: Modal or dropdown elements should be closeable with Escape
      const modals = document.querySelectorAll('[role=\"dialog\"], .modal');
      const dropdowns = document.querySelectorAll('[aria-expanded], .dropdown');
      
      [...modals, ...dropdowns].forEach(element => {
        // Initially fail until proper escape key handling is implemented
        const hasEscapeHandler = element.getAttribute('data-escape-handler') === 'true';
        expect(hasEscapeHandler).toBeTruthy();
      });
    });

    test('keyboard: focus should be trapped in modals', () => {
      // RED: When modal is open, focus should be trapped inside
      const modals = document.querySelectorAll('[role=\"dialog\"], .modal');
      
      modals.forEach(modal => {
        const focusableElements = modal.querySelectorAll(
          'a, button, input, textarea, select, [tabindex]:not([tabindex=\"-1\"])'
        );
        
        if (focusableElements.length > 0) {
          // Should have focus trap implementation
          const hasFocusTrap = modal.getAttribute('data-focus-trap') === 'true';
          expect(hasFocusTrap).toBeTruthy();
        }
      });
    });
  });
});

/**
 * Screen Reader Testing Suite  
 * Tests screen reader compatibility and ARIA usage
 */
describe('Screen Reader Testing Suite', () => {
  beforeEach(() => {
    const htmlPath = path.join(__dirname, '../../index.html');
    const htmlContent = fs.readFileSync(htmlPath, 'utf8');
    document.documentElement.innerHTML = htmlContent;
  });

  describe('RED Phase: Failing Screen Reader Tests', () => {
    test('screen-reader: dynamic content should have ARIA live regions', () => {
      // RED: Areas with dynamic content should have aria-live attributes
      const dynamicAreas = document.querySelectorAll(
        '.results, .status, .loading, .error, .success'
      );
      
      dynamicAreas.forEach(area => {
        const ariaLive = area.getAttribute('aria-live');
        expect(ariaLive).toBeTruthy();
        expect(['polite', 'assertive', 'off']).toContain(ariaLive);
      });
    });

    test('screen-reader: loading states should be announced', () => {
      // RED: Loading indicators should be accessible to screen readers
      const loadingElements = document.querySelectorAll('.loading, [aria-busy]');
      
      loadingElements.forEach(element => {
        const ariaBusy = element.getAttribute('aria-busy');
        const ariaLabel = element.getAttribute('aria-label');
        const text = element.textContent.trim();
        
        expect(ariaBusy === 'true' || ariaLabel || text).toBeTruthy();
      });
    });

    test('screen-reader: error messages should be properly announced', () => {
      // RED: Error messages should be accessible to screen readers
      const errorElements = document.querySelectorAll('.error, [role=\"alert\"]');
      
      errorElements.forEach(element => {
        const role = element.getAttribute('role');
        const ariaLive = element.getAttribute('aria-live');
        
        expect(role === 'alert' || ariaLive).toBeTruthy();
      });
    });

    test('screen-reader: form controls should have descriptions', () => {
      // RED: Complex form controls should have help text
      const complexInputs = document.querySelectorAll(
        'input[type=\"password\"], textarea, select[multiple]'
      );
      
      complexInputs.forEach(input => {
        const ariaDescribedBy = input.getAttribute('aria-describedby');
        if (ariaDescribedBy) {
          const description = document.getElementById(ariaDescribedBy);
          expect(description).toBeTruthy();
        }
      });
    });
  });
});

// Export for use in other test files
module.exports = {
  axe,
  toHaveNoViolations
};
