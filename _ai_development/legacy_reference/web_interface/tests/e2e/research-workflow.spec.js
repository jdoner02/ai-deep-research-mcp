/**
 * End-to-End Testing Suite - TDD RED Phase
 * Tests complete user workflows, real-time features, file operations
 * Following Test Guardian Agent TDD methodology: RED-GREEN-REFACTOR
 * 
 * Uses Playwright for cross-browser automation
 */

const { test, expect } = require('@playwright/test');

test.describe('E2E Testing Suite - Complete User Workflows', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to the application
    await page.goto('http://localhost:3000');  // This will fail initially as server isn't running
  });

  test.describe('RED Phase: Failing Research Workflow Tests', () => {
    
    test('e2e: complete research workflow from query to results', async ({ page }) => {
      // RED: Test full user journey from query input to results display
      
      // 1. Verify page loads correctly
      await expect(page.locator('h1')).toContainText('AI Deep Research MCP');
      
      // 2. Enter research query
      const queryInput = page.locator('#queryInput');
      await expect(queryInput).toBeVisible();
      await queryInput.fill('neural networks and deep learning');
      
      // 3. Click research button
      const researchBtn = page.locator('#researchBtn');
      await expect(researchBtn).toBeEnabled();
      await researchBtn.click();
      
      // 4. Verify status changes to running
      const statusIndicator = page.locator('#statusIndicator');
      await expect(statusIndicator).toContainText('Research in Progress', { timeout: 5000 });
      
      // 5. Wait for research completion
      await expect(statusIndicator).toContainText('Research Complete', { timeout: 30000 });
      
      // 6. Verify results section appears
      const resultsSection = page.locator('#resultsSection');
      await expect(resultsSection).toBeVisible({ timeout: 5000 });
      
      // 7. Check that answer content is populated
      const answerContent = page.locator('#answerContent');
      await expect(answerContent).not.toBeEmpty();
    });

    test('e2e: example query selection and execution', async ({ page }) => {
      // RED: Test clicking example queries and running research
      
      // 1. Click on first example query
      const firstExample = page.locator('.example-query').first();
      await expect(firstExample).toBeVisible();
      await firstExample.click();
      
      // 2. Verify query input is populated
      const queryInput = page.locator('#queryInput');
      await expect(queryInput).not.toHaveValue('');
      
      // 3. Start research
      await page.locator('#researchBtn').click();
      
      // 4. Monitor progress log for activity
      const progressLog = page.locator('#progressLog');
      await expect(progressLog).toContainText('Starting research', { timeout: 10000 });
    });

    test('e2e: real-time progress monitoring', async ({ page }) => {
      // RED: Test that progress updates appear in real-time
      
      await page.locator('#queryInput').fill('machine learning algorithms');
      await page.locator('#researchBtn').click();
      
      // Monitor for different progress stages
      const progressLog = page.locator('#progressLog');
      
      // Should see initial startup messages
      await expect(progressLog).toContainText('Research initialized', { timeout: 5000 });
      
      // Should see URL discovery phase
      await expect(progressLog).toContainText('Discovering relevant URLs', { timeout: 15000 });
      
      // Should see document processing
      await expect(progressLog).toContainText('Processing document', { timeout: 25000 });
      
      // Should see completion
      await expect(progressLog).toContainText('Research completed', { timeout: 45000 });
    });

    test('e2e: research configuration options work', async ({ page }) => {
      // RED: Test that max URLs and depth settings affect research
      
      // Set max URLs to 3
      await page.locator('#maxUrls').selectOption('3');
      
      // Set depth to 2
      await page.locator('#maxDepth').selectOption('2');
      
      // Start research
      await page.locator('#queryInput').fill('cybersecurity fundamentals');
      await page.locator('#researchBtn').click();
      
      // Verify configuration is applied (should show in progress log)
      const progressLog = page.locator('#progressLog');
      await expect(progressLog).toContainText('Max URLs: 3', { timeout: 10000 });
      await expect(progressLog).toContainText('Depth: 2', { timeout: 10000 });
    });
  });

  test.describe('RED Phase: Failing Error Handling Tests', () => {
    
    test('e2e: empty query validation', async ({ page }) => {
      // RED: Test that empty queries are handled gracefully
      
      // Try to start research with empty query
      const researchBtn = page.locator('#researchBtn');
      await researchBtn.click();
      
      // Should show error or prevent submission
      const errorIndicator = page.locator('#errorIndicator');
      await expect(errorIndicator).toBeVisible({ timeout: 2000 });
      await expect(errorIndicator).toContainText('Please enter a research query');
    });

    test('e2e: network error handling', async ({ page }) => {
      // RED: Test behavior when backend is unavailable
      
      // Block network requests to simulate server down
      await page.route('**/research', route => route.abort());
      
      await page.locator('#queryInput').fill('test query');
      await page.locator('#researchBtn').click();
      
      // Should show network error
      const statusIndicator = page.locator('#statusIndicator');
      await expect(statusIndicator).toContainText('Connection Error', { timeout: 10000 });
    });

    test('e2e: research timeout handling', async ({ page }) => {
      // RED: Test handling of research that takes too long
      
      // Mock a slow response
      await page.route('**/research', route => {
        setTimeout(() => route.fulfill({ status: 408, body: 'Request Timeout' }), 5000);
      });
      
      await page.locator('#queryInput').fill('timeout test');
      await page.locator('#researchBtn').click();
      
      const statusIndicator = page.locator('#statusIndicator');
      await expect(statusIndicator).toContainText('Request timed out', { timeout: 15000 });
    });
  });

  test.describe('RED Phase: Failing UI Interaction Tests', () => {
    
    test('e2e: responsive behavior on mobile', async ({ page }) => {
      // RED: Test mobile viewport behavior
      
      // Set mobile viewport
      await page.setViewportSize({ width: 375, height: 667 });
      
      // Verify elements are properly sized for mobile
      const queryInput = page.locator('#queryInput');
      const researchBtn = page.locator('#researchBtn');
      
      await expect(queryInput).toBeVisible();
      await expect(researchBtn).toBeVisible();
      
      // Check touch target sizes (minimum 44px)
      const inputBox = await queryInput.boundingBox();
      const buttonBox = await researchBtn.boundingBox();
      
      expect(inputBox.height).toBeGreaterThanOrEqual(44);
      expect(buttonBox.height).toBeGreaterThanOrEqual(44);
    });

    test('e2e: keyboard navigation functionality', async ({ page }) => {
      // RED: Test keyboard-only navigation
      
      // Tab through interactive elements
      await page.keyboard.press('Tab'); // Should focus query input
      await expect(page.locator('#queryInput')).toBeFocused();
      
      await page.keyboard.press('Tab'); // Should focus research button
      await expect(page.locator('#researchBtn')).toBeFocused();
      
      // Test Enter key on button
      await page.keyboard.press('Enter');
      // Should show validation error for empty query
      const errorIndicator = page.locator('#errorIndicator');
      await expect(errorIndicator).toBeVisible({ timeout: 2000 });
    });

    test('e2e: research results display and interaction', async ({ page }) => {
      // RED: Test that results are properly displayed and interactive
      
      // Mock successful research response
      await page.route('**/research', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            answer: 'Test research answer with detailed information.',
            sources: [
              { url: 'https://example1.com', title: 'Source 1' },
              { url: 'https://example2.com', title: 'Source 2' }
            ],
            stats: { documentsProcessed: 5, totalChunks: 25 }
          })
        });
      });
      
      await page.locator('#queryInput').fill('test query');
      await page.locator('#researchBtn').click();
      
      // Wait for results
      await expect(page.locator('#resultsSection')).toBeVisible({ timeout: 10000 });
      
      // Verify answer content
      const answerContent = page.locator('#answerContent');
      await expect(answerContent).toContainText('Test research answer');
      
      // Verify sources are displayed
      const sources = page.locator('.source');
      await expect(sources).toHaveCount(2);
      
      // Verify stats are shown
      const stats = page.locator('#researchStats');
      await expect(stats).toContainText('5 documents');
      await expect(stats).toContainText('25 chunks');
    });
  });

  test.describe('RED Phase: Failing Cross-Browser Tests', () => {
    
    test('e2e: functionality works in all browsers', async ({ page, browserName }) => {
      // RED: Test across different browsers
      
      // Basic functionality test for each browser
      await expect(page.locator('h1')).toBeVisible();
      
      const queryInput = page.locator('#queryInput');
      await queryInput.fill(`${browserName} test query`);
      
      const inputValue = await queryInput.inputValue();
      expect(inputValue).toContain(browserName);
      
      // Browser-specific feature tests
      if (browserName === 'chromium') {
        // Test Chrome-specific features
        await expect(page.locator('.research-btn')).toHaveCSS('cursor', 'pointer');
      }
      
      if (browserName === 'firefox') {
        // Test Firefox-specific behavior
        await expect(page.locator('#queryInput')).toBeEditable();
      }
      
      if (browserName === 'webkit') {
        // Test Safari-specific behavior
        await expect(page.locator('.container')).toBeVisible();
      }
    });
  });
});

/**
 * File Upload/Download Testing Suite
 * Tests file operations and document handling
 */
test.describe('E2E File Operations Testing Suite', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:3000');
  });

  test.describe('RED Phase: Failing File Operation Tests', () => {
    
    test('e2e: research results can be downloaded', async ({ page }) => {
      // RED: Test downloading research results as file
      
      // Mock research completion
      await page.route('**/research', route => {
        route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            answer: 'Downloadable research results',
            sources: [{ url: 'https://test.com', title: 'Test Source' }]
          })
        });
      });
      
      await page.locator('#queryInput').fill('download test');
      await page.locator('#researchBtn').click();
      
      // Wait for results
      await expect(page.locator('#resultsSection')).toBeVisible({ timeout: 10000 });
      
      // Look for download button (should exist)
      const downloadBtn = page.locator('#downloadBtn');
      await expect(downloadBtn).toBeVisible();
      
      // Test download functionality
      const [download] = await Promise.all([
        page.waitForEvent('download'),
        downloadBtn.click()
      ]);
      
      expect(download.suggestedFilename()).toContain('research_results');
    });

    test('e2e: progress log can be exported', async ({ page }) => {
      // RED: Test exporting progress log
      
      await page.locator('#queryInput').fill('export test');
      await page.locator('#researchBtn').click();
      
      // Wait for some progress
      await page.waitForTimeout(3000);
      
      // Look for export log button
      const exportBtn = page.locator('#exportLogBtn');
      await expect(exportBtn).toBeVisible();
      
      const [download] = await Promise.all([
        page.waitForEvent('download'),
        exportBtn.click()
      ]);
      
      expect(download.suggestedFilename()).toContain('progress_log');
    });
  });
});

// Export test utilities for other test files
module.exports = {
  // Utility functions can be exported here
};
