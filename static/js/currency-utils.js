/**
 * Currency Utilities for Multi-Purpose App
 * Handles currency updates and formatting across all pages
 */

class CurrencyManager {
    constructor() {
        this.currentCurrency = {
            code: 'USD',
            symbol: '$'
        };
        this.listeners = [];
        this.init();
    }

    init() {
        // Get current currency from page data or localStorage
        this.loadCurrentCurrency();
        
        // Listen for currency update events
        window.addEventListener('currencyUpdated', (event) => {
            this.handleCurrencyUpdate(event.detail);
        });
        
        // Listen for storage changes (for cross-tab updates)
        window.addEventListener('storage', (event) => {
            if (event.key === 'app_currency') {
                this.handleCurrencyUpdate(JSON.parse(event.newValue));
            }
        });
    }

    loadCurrentCurrency() {
        // Try to get from page data
        const currencyData = document.querySelector('meta[name="currency-data"]');
        if (currencyData) {
            try {
                const data = JSON.parse(currencyData.getAttribute('content'));
                this.currentCurrency = {
                    code: data.code || 'USD',
                    symbol: data.symbol || '$'
                };
            } catch (e) {
                console.warn('Failed to parse currency data from meta tag');
            }
        }
        
        // Fallback to localStorage
        const stored = localStorage.getItem('app_currency');
        if (stored) {
            try {
                this.currentCurrency = JSON.parse(stored);
            } catch (e) {
                console.warn('Failed to parse stored currency data');
            }
        }
    }

    handleCurrencyUpdate(currencyInfo) {
        const oldCurrency = { ...this.currentCurrency };
        this.currentCurrency = {
            code: currencyInfo.currencyCode || currencyInfo.code,
            symbol: currencyInfo.currencySymbol || currencyInfo.symbol
        };

        // Store in localStorage
        localStorage.setItem('app_currency', JSON.stringify(this.currentCurrency));

        // Notify all listeners
        this.notifyListeners(oldCurrency, this.currentCurrency);

        // Update all currency displays on the page
        this.updateCurrencyDisplays();
    }

    updateCurrencyDisplays() {
        // Update currency symbols in stat numbers
        document.querySelectorAll('.stat-number').forEach(element => {
            const text = element.textContent;
            if (this.isCurrencyValue(text)) {
                const numericValue = this.extractNumericValue(text);
                if (numericValue !== null) {
                    element.textContent = this.formatCurrency(numericValue);
                }
            }
        });

        // Update currency symbols in price displays
        document.querySelectorAll('.price-display, .currency-value').forEach(element => {
            const text = element.textContent;
            if (this.isCurrencyValue(text)) {
                const numericValue = this.extractNumericValue(text);
                if (numericValue !== null) {
                    element.textContent = this.formatCurrency(numericValue);
                }
            }
        });

        // Update any elements with data-currency-value attribute
        document.querySelectorAll('[data-currency-value]').forEach(element => {
            const value = element.getAttribute('data-currency-value');
            if (value) {
                element.textContent = this.formatCurrency(parseFloat(value));
            }
        });
    }

    isCurrencyValue(text) {
        // Check if text looks like a currency value
        return /^[^\d]*[\d,]+\.?\d*$/.test(text.trim());
    }

    extractNumericValue(text) {
        // Extract numeric value from currency string
        const match = text.replace(/[^\d.,]/g, '');
        if (match) {
            return parseFloat(match.replace(',', ''));
        }
        return null;
    }

    formatCurrency(value) {
        if (value === null || isNaN(value)) {
            return this.currentCurrency.symbol + '0.00';
        }
        
        // Format with commas and 2 decimal places
        const formatted = value.toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
        
        return this.currentCurrency.symbol + formatted;
    }

    addListener(callback) {
        this.listeners.push(callback);
    }

    removeListener(callback) {
        const index = this.listeners.indexOf(callback);
        if (index > -1) {
            this.listeners.splice(index, 1);
        }
    }

    notifyListeners(oldCurrency, newCurrency) {
        this.listeners.forEach(callback => {
            try {
                callback(oldCurrency, newCurrency);
            } catch (e) {
                console.error('Error in currency listener:', e);
            }
        });
    }

    // AJAX method to update currency on server
    async updateServerCurrency(currencyCode, currencySymbol) {
        try {
            const response = await fetch('/core/update-currency/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    currency_code: currencyCode
                })
            });

            const data = await response.json();
            if (data.success) {
                this.handleCurrencyUpdate({
                    currencyCode: data.currency_code,
                    currencySymbol: data.currency_symbol
                });
                return true;
            } else {
                console.error('Failed to update currency:', data.error);
                return false;
            }
        } catch (error) {
            console.error('Error updating currency:', error);
            return false;
        }
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }
}

// Initialize global currency manager
window.currencyManager = new CurrencyManager();

// Utility function for easy access
window.updateCurrency = function(currencyCode, currencySymbol) {
    return window.currencyManager.updateServerCurrency(currencyCode, currencySymbol);
};

// Export for module systems
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CurrencyManager;
} 