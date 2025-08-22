/**
 * Inventory Currency Handler
 * Handles currency changes specifically for inventory management
 */

class InventoryCurrencyHandler {
    constructor() {
        this.init();
    }

    init() {
        // Listen for currency changes
        this.setupCurrencyChangeListeners();
        
        // Update all inventory currency displays on page load
        this.updateInventoryCurrencyDisplays();
    }

    setupCurrencyChangeListeners() {
        // Listen for currency change events from the currency manager
        document.addEventListener('currencyChanged', (event) => {
            this.handleCurrencyChange(event.detail);
        });

        // Listen for company profile updates
        document.addEventListener('companyProfileUpdated', (event) => {
            this.handleCurrencyChange(event.detail);
        });

        // Listen for manual currency updates
        document.addEventListener('inventoryCurrencyUpdated', (event) => {
            this.handleCurrencyChange(event.detail);
        });
    }

    handleCurrencyChange(currencyData) {
        const { symbol, code } = currencyData;
        
        console.log('Inventory currency change detected:', { symbol, code });
        
        // Update all inventory currency displays
        this.updateInventoryCurrencyDisplays(symbol);
        
        // Update all input fields with currency symbols
        this.updateCurrencyInputFields(symbol);
        
        // Update all calculated totals
        this.updateCalculatedTotals(symbol);
        
        // Update all data attributes
        this.updateCurrencyDataAttributes(symbol, code);
        
        // Trigger recalculation of all inventory items
        this.triggerInventoryRecalculation();
    }

    updateInventoryCurrencyDisplays(symbol = null) {
        const currencySymbol = symbol || this.getCurrentCurrencySymbol();
        
        // Update all elements with currency amounts
        const currencyElements = document.querySelectorAll('[data-currency-amount]');
        currencyElements.forEach(element => {
            const amount = element.dataset.currencyAmount;
            if (amount) {
                element.textContent = this.formatCurrency(amount, currencySymbol);
            }
        });

        // Update specific inventory elements
        this.updateInventorySpecificElements(currencySymbol);
    }

    updateInventorySpecificElements(currencySymbol) {
        // Update unit price displays
        const unitPriceElements = document.querySelectorAll('.unit-price-display, [id*="unit-price"], [id*="price"]');
        unitPriceElements.forEach(element => {
            if (element.textContent.match(/[₦$€£¥₹₿₤₩₪₫₭₮₯₰₱₲₳₴₵₶₷₸₹₺₻₼₽₾₿]/)) {
                const amount = this.extractNumericValue(element.textContent);
                element.textContent = this.formatCurrency(amount, currencySymbol);
            }
        });

        // Update total value displays
        const totalElements = document.querySelectorAll('.total-value-display, [id*="total"], [id*="value"]');
        totalElements.forEach(element => {
            if (element.textContent.match(/[₦$€£¥₹₿₤₩₪₫₭₮₯₰₱₲₳₴₵₶₷₸₹₺₻₼₽₾₿]/)) {
                const amount = this.extractNumericValue(element.textContent);
                element.textContent = this.formatCurrency(amount, currencySymbol);
            }
        });

        // Update grand total
        const grandTotalElement = document.getElementById('grandTotal');
        if (grandTotalElement) {
            const amount = this.extractNumericValue(grandTotalElement.textContent);
            grandTotalElement.textContent = this.formatCurrency(amount, currencySymbol);
        }
    }

    updateCurrencyInputFields(currencySymbol) {
        // Update input group currency symbols
        const inputGroups = document.querySelectorAll('.input-group-text');
        inputGroups.forEach(element => {
            if (element.textContent.match(/[₦$€£¥₹₿₤₩₪₫₭₮₯₰₱₲₳₴₵₶₷₸₹₺₻₼₽₾₿]/)) {
                element.textContent = currencySymbol;
            }
        });

        // Update currency input fields
        const currencyInputs = document.querySelectorAll('input[type="number"], input[data-currency-input]');
        currencyInputs.forEach(input => {
            if (input.dataset.currencyAmount) {
                const amount = input.dataset.currencyAmount;
                input.dataset.currencySymbol = currencySymbol;
            }
        });
    }

    updateCalculatedTotals(currencySymbol) {
        // Update all calculated total cells
        const totalCells = document.querySelectorAll('.total-cell, [data-field="total"]');
        totalCells.forEach(cell => {
            const amount = this.extractNumericValue(cell.textContent);
            cell.textContent = this.formatCurrency(amount, currencySymbol);
        });

        // Update all price cells
        const priceCells = document.querySelectorAll('.price-cell, [data-field="unit_price"]');
        priceCells.forEach(cell => {
            const amount = this.extractNumericValue(cell.textContent);
            cell.textContent = this.formatCurrency(amount, currencySymbol);
        });
    }

    updateCurrencyDataAttributes(symbol, code) {
        // Update body data attributes
        document.body.dataset.currencySymbol = symbol;
        document.body.dataset.currencyCode = code;

        // Update meta tags
        const symbolMeta = document.querySelector('meta[name="currency-symbol"]');
        const codeMeta = document.querySelector('meta[name="currency-code"]');
        
        if (symbolMeta) symbolMeta.setAttribute('content', symbol);
        if (codeMeta) codeMeta.setAttribute('content', code);
    }

    triggerInventoryRecalculation() {
        // Trigger recalculation for all inventory items
        const inventoryRows = document.querySelectorAll('tr[data-item-id]');
        inventoryRows.forEach(row => {
            const itemId = row.dataset.itemId;
            this.recalculateItemTotals(itemId);
        });

        // Update grand total
        this.calculateGrandTotal();
    }

    recalculateItemTotals(itemId) {
        const row = document.querySelector(`tr[data-item-id="${itemId}"]`);
        if (!row) return;

        const quantityField = row.querySelector('[data-field="quantity"]');
        const priceField = row.querySelector('[data-field="unit_price"]');
        const totalField = row.querySelector('[data-field="total"]');

        if (quantityField && priceField && totalField) {
            const quantity = this.extractNumericValue(quantityField.textContent);
            const price = this.extractNumericValue(priceField.textContent);
            const total = quantity * price;

            totalField.textContent = this.formatCurrency(total);
            totalField.dataset.value = total;
        }
    }

    calculateGrandTotal() {
        const totalFields = document.querySelectorAll('[data-field="total"]');
        let grandTotal = 0;

        totalFields.forEach(field => {
            const value = this.extractNumericValue(field.textContent);
            grandTotal += value;
        });

        const grandTotalElement = document.getElementById('grandTotal');
        if (grandTotalElement) {
            grandTotalElement.textContent = this.formatCurrency(grandTotal);
        }
    }

    formatCurrency(amount, symbol = null) {
        const currencySymbol = symbol || this.getCurrentCurrencySymbol();
        const numericAmount = parseFloat(amount) || 0;
        
        return `${currencySymbol}${numericAmount.toLocaleString('en-US', { 
            minimumFractionDigits: 2, 
            maximumFractionDigits: 2 
        })}`;
    }

    extractNumericValue(currencyString) {
        if (!currencyString) return 0;
        
        // Remove all currency symbols
        const cleaned = String(currencyString).replace(/[₦$€£¥₹₿₤₩₪₫₭₮₯₰₱₲₳₴₵₶₷₸₹₺₻₼₽₾₿]/g, '');
        
        // Remove commas and other formatting
        const numeric = cleaned.replace(/[^\d.-]/g, '');
        
        const result = parseFloat(numeric);
        return isNaN(result) ? 0 : result;
    }

    getCurrentCurrencySymbol() {
        return document.body.dataset.currencySymbol || '$';
    }

    // Method to update currency via AJAX
    async updateCurrency(currencyCode, currencySymbol) {
        try {
            const response = await fetch('/inventory/ajax/update-currency/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken(),
                },
                body: JSON.stringify({
                    currency_code: currencyCode,
                    currency_symbol: currencySymbol
                })
            });

            const data = await response.json();
            
            if (data.success) {
                // Trigger currency change event
                const event = new CustomEvent('inventoryCurrencyUpdated', {
                    detail: { symbol: currencySymbol, code: currencyCode }
                });
                document.dispatchEvent(event);
                
                // Show success message
                this.showMessage('Currency updated successfully!', 'success');
                
                return data;
            } else {
                this.showMessage('Error updating currency: ' + data.error, 'error');
                return null;
            }
        } catch (error) {
            console.error('Error updating currency:', error);
            this.showMessage('Error updating currency. Please try again.', 'error');
            return null;
        }
    }

    getCSRFToken() {
        const token = document.querySelector('[name=csrfmiddlewaretoken]');
        return token ? token.value : '';
    }

    showMessage(message, type = 'info') {
        // Create a simple message display
        const messageDiv = document.createElement('div');
        messageDiv.className = `alert alert-${type === 'error' ? 'danger' : type} alert-dismissible fade show`;
        messageDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        
        // Insert at the top of the content area
        const contentArea = document.querySelector('.container-fluid');
        if (contentArea) {
            contentArea.insertBefore(messageDiv, contentArea.firstChild);
            
            // Auto-remove after 5 seconds
            setTimeout(() => {
                if (messageDiv.parentNode) {
                    messageDiv.remove();
                }
            }, 5000);
        }
    }
}

// Initialize inventory currency handler when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.inventoryCurrencyHandler = new InventoryCurrencyHandler();
});

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = InventoryCurrencyHandler;
} 