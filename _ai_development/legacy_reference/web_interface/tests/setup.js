// Test setup configuration for Jest
// Sets up testing environment with DOM testing and accessibility tools

const { configureAxe } = require('jest-axe');
require('@testing-library/jest-dom');

// Configure axe for accessibility testing
const axe = configureAxe({
  rules: {
    // Configure specific accessibility rules
    'color-contrast': { enabled: true },
    'keyboard-navigation': { enabled: true },
    'focus-management': { enabled: true },
    'semantic-html': { enabled: true },
    'aria-usage': { enabled: true }
  }
});

// Global test utilities
global.axe = axe;

// Mock console.error for cleaner test output
const originalError = console.error;
beforeAll(() => {
  console.error = (...args) => {
    if (
      typeof args[0] === 'string' &&
      args[0].includes('Warning: ReactDOM.render is no longer supported')
    ) {
      return;
    }
    originalError.call(console, ...args);
  };
});

afterAll(() => {
  console.error = originalError;
});

// Global test timeout
jest.setTimeout(30000);

// Mock Socket.io for tests
global.io = {
  connect: jest.fn(() => ({
    on: jest.fn(),
    emit: jest.fn(),
    disconnect: jest.fn()
  }))
};

// Mock fetch for API testing
global.fetch = jest.fn();

// Setup DOM environment for testing
if (typeof document !== 'undefined') {
  // Add any additional DOM setup here
  document.body.innerHTML = '';
}
