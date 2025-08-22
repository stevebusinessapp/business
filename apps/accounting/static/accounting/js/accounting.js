/**
 * Accounting App JavaScript Utilities
 * Handles real-time calculations, form validation, and AJAX operations
 */

class AccountingApp {
    constructor() {
        this.currencySymbol = '₦';
        this.initializeEventListeners();
    }

    /**
     * Initialize all event listeners
     */
    initializeEventListeners() {
        // Currency formatting
        this.setupCurrencyFormatting();
        
        // Real-time calculations
        this.setupRealTimeCalculations();
        
        // Form validation
        this.setupFormValidation();
        
        // Auto-refresh functionality
        this.setupAutoRefresh();
    }

    /**
     * Setup currency input formatting
     */
    setupCurrencyFormatting() {
        const currencyInputs = document.querySelectorAll('input[type="number"][step="0.01"]');
        
        currencyInputs.forEach(input => {
            input.addEventListener('blur', (e) => {
                this.formatCurrencyInput(e.target);
            });
            
            input.addEventListener('input', (e) => {
                this.sanitizeCurrencyInput(e.target);
            });
        });
    }

    /**
     * Format currency input with proper formatting
     */
    formatCurrencyInput(input) {
        let value = input.value.replace(/[^\d.]/g, '');
        
        if (value) {
            const num = parseFloat(value);
            if (!isNaN(num)) {
                input.value = num.toFixed(2);
            }
        }
    }

    /**
     * Sanitize currency input to remove invalid characters
     */
    sanitizeCurrencyInput(input) {
        let value = input.value;
        
        // Remove currency symbols and commas
        value = value.replace(/[₦$€£¥,\s]/g, '');
        
        // Only allow numbers and decimal point
        value = value.replace(/[^\d.]/g, '');
        
        // Ensure only one decimal point
        const parts = value.split('.');
        if (parts.length > 2) {
            value = parts[0] + '.' + parts.slice(1).join('');
        }
        
        input.value = value;
    }

    /**
     * Setup real-time calculations for transaction forms
     */
    setupRealTimeCalculations() {
        const amountInput = document.getElementById('id_amount');
        const taxInput = document.getElementById('id_tax');
        const discountInput = document.getElementById('id_discount');
        const currencySelect = document.getElementById('id_currency');
        const transactionTypeSelect = document.getElementById('id_type');
        
        if (amountInput && taxInput && discountInput) {
            [amountInput, taxInput, discountInput].forEach(input => {
                input.addEventListener('input', () => this.updateCalculations());
                input.addEventListener('blur', () => this.updateCalculations());
            });
            
            if (currencySelect) {
                currencySelect.addEventListener('change', () => this.updateCalculations());
            }
            
            if (transactionTypeSelect) {
                transactionTypeSelect.addEventListener('change', () => this.updateCalculations());
            }
            
            // Initial calculation
            this.updateCalculations();
        }
    }

    /**
     * Update real-time calculations
     */
    updateCalculations() {
        const amountInput = document.getElementById('id_amount');
        const taxInput = document.getElementById('id_tax');
        const discountInput = document.getElementById('id_discount');
        const currencySelect = document.getElementById('id_currency');
        const transactionTypeSelect = document.getElementById('id_type');
        
        if (!amountInput || !taxInput || !discountInput) return;
        
        const amount = parseFloat(amountInput.value) || 0;
        const tax = parseFloat(taxInput.value) || 0;
        const discount = parseFloat(discountInput.value) || 0;
        const currency = currencySelect ? currencySelect.value : this.currencySymbol;
        const transactionType = transactionTypeSelect ? transactionTypeSelect.value : 'income';
        
        const netAmount = amount + tax - discount;
        
        // Update display elements
        this.updateCalculationDisplay(currency, amount, tax, discount, netAmount, transactionType);
        
        // Update currency symbols
        this.updateCurrencySymbols(currency);
    }

    /**
     * Update calculation display
     */
    updateCalculationDisplay(currency, amount, tax, discount, netAmount, transactionType) {
        const baseAmountEl = document.getElementById('baseAmount');
        const taxAmountEl = document.getElementById('taxAmount');
        const discountAmountEl = document.getElementById('discountAmount');
        const netAmountEl = document.getElementById('netAmount');
        
        if (baseAmountEl) baseAmountEl.textContent = currency + amount.toFixed(2);
        if (taxAmountEl) taxAmountEl.textContent = currency + tax.toFixed(2);
        if (discountAmountEl) discountAmountEl.textContent = currency + discount.toFixed(2);
        if (netAmountEl) {
            netAmountEl.textContent = currency + netAmount.toFixed(2);
            
            // Update color based on transaction type
            if (transactionType === 'income') {
                netAmountEl.className = 'amount-preview';
            } else {
                netAmountEl.className = 'amount-preview expense';
            }
        }
    }

    /**
     * Update currency symbols in the form
     */
    updateCurrencySymbols(currency) {
        const currencySymbols = document.querySelectorAll('.currency-symbol');
        currencySymbols.forEach(symbol => {
            symbol.textContent = currency;
        });
    }

    /**
     * Setup form validation
     */
    setupFormValidation() {
        const forms = document.querySelectorAll('form');
        
        forms.forEach(form => {
            form.addEventListener('submit', (e) => {
                if (!this.validateForm(form)) {
                    e.preventDefault();
                }
            });
        });
    }

    /**
     * Validate form before submission
     */
    validateForm(form) {
        const amountInput = form.querySelector('#id_amount');
        const titleInput = form.querySelector('#id_title');
        const typeInput = form.querySelector('#id_type');
        
        let isValid = true;
        
        // Validate amount
        if (amountInput) {
            const amount = parseFloat(amountInput.value);
            if (!amount || amount <= 0) {
                this.showError(amountInput, 'Please enter a valid amount greater than zero.');
                isValid = false;
            } else {
                this.clearError(amountInput);
            }
        }
        
        // Validate title
        if (titleInput) {
            const title = titleInput.value.trim();
            if (!title) {
                this.showError(titleInput, 'Please enter a transaction title.');
                isValid = false;
            } else {
                this.clearError(titleInput);
            }
        }
        
        // Validate transaction type
        if (typeInput) {
            const type = typeInput.value;
            if (!type) {
                this.showError(typeInput, 'Please select a transaction type.');
                isValid = false;
            } else {
                this.clearError(typeInput);
            }
        }
        
        return isValid;
    }

    /**
     * Show error message for form field
     */
    showError(input, message) {
        this.clearError(input);
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback d-block';
        errorDiv.textContent = message;
        
        input.parentNode.appendChild(errorDiv);
        input.classList.add('is-invalid');
    }

    /**
     * Clear error message for form field
     */
    clearError(input) {
        const errorDiv = input.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
        input.classList.remove('is-invalid');
    }

    /**
     * Setup auto-refresh functionality
     */
    setupAutoRefresh() {
        // Auto-refresh dashboard data every 30 seconds
        if (window.location.pathname.includes('/accounting/') && 
            !window.location.pathname.includes('/transactions/') &&
            !window.location.pathname.includes('/add/') &&
            !window.location.pathname.includes('/edit/')) {
            
            setInterval(() => {
                this.refreshDashboardData();
            }, 30000);
        }
    }

    /**
     * Refresh dashboard data via AJAX
     */
    refreshDashboardData() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (!csrfToken) return;
        
        fetch('/accounting/ajax/update-ledger/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken.value
            },
            body: JSON.stringify({
                month: new Date().getMonth() + 1,
                year: new Date().getFullYear()
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                this.updateDashboardCards(data);
            }
        })
        .catch(error => console.error('Error refreshing dashboard:', error));
    }

    /**
     * Update dashboard summary cards
     */
    updateDashboardCards(data) {
        const incomeCard = document.querySelector('.income-card h3');
        const expenseCard = document.querySelector('.expense-card h3');
        const profitCard = document.querySelector('.profit-card h3');
        
        if (incomeCard) {
            incomeCard.textContent = this.formatCurrency(data.total_income);
        }
        if (expenseCard) {
            expenseCard.textContent = this.formatCurrency(data.total_expense);
        }
        if (profitCard) {
            profitCard.textContent = this.formatCurrency(data.net_profit);
        }
    }

    /**
     * Format currency for display
     */
    formatCurrency(amount) {
        return this.currencySymbol + parseFloat(amount).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    }

    /**
     * Export data functionality
     */
    exportData(type, format, filters = {}) {
        const params = new URLSearchParams({
            type: type,
            format: format,
            ...filters
        });
        
        window.location.href = `/accounting/export/?${params.toString()}`;
    }

    /**
     * Bulk operations for transactions
     */
    bulkOperation(action, transactionIds) {
        if (!transactionIds || transactionIds.length === 0) {
            alert('Please select at least one transaction.');
            return;
        }
        
        if (!confirm(`Are you sure you want to ${action} the selected transactions?`)) {
            return;
        }
        
        const formData = new FormData();
        formData.append('action', action);
        formData.append('transaction_ids', JSON.stringify(transactionIds));
        formData.append('csrfmiddlewaretoken', document.querySelector('[name=csrfmiddlewaretoken]').value);
        
        fetch('/accounting/bulk-operation/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error: ' + data.error);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('An error occurred while processing the request.');
        });
    }

    /**
     * Initialize transaction checkboxes for bulk operations
     */
    setupBulkOperations() {
        const selectAllCheckbox = document.getElementById('select-all');
        const transactionCheckboxes = document.querySelectorAll('.transaction-checkbox');
        const bulkActionSelect = document.getElementById('bulk-action');
        const bulkActionButton = document.getElementById('bulk-action-btn');
        
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => {
                transactionCheckboxes.forEach(checkbox => {
                    checkbox.checked = e.target.checked;
                });
                this.updateBulkActionButton();
            });
        }
        
        transactionCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => {
                this.updateBulkActionButton();
            });
        });
        
        if (bulkActionButton) {
            bulkActionButton.addEventListener('click', () => {
                const selectedIds = this.getSelectedTransactionIds();
                const action = bulkActionSelect.value;
                
                if (action && selectedIds.length > 0) {
                    this.bulkOperation(action, selectedIds);
                }
            });
        }
    }

    /**
     * Get selected transaction IDs
     */
    getSelectedTransactionIds() {
        const checkboxes = document.querySelectorAll('.transaction-checkbox:checked');
        return Array.from(checkboxes).map(checkbox => checkbox.value);
    }

    /**
     * Update bulk action button state
     */
    updateBulkActionButton() {
        const selectedIds = this.getSelectedTransactionIds();
        const bulkActionButton = document.getElementById('bulk-action-btn');
        
        if (bulkActionButton) {
            bulkActionButton.disabled = selectedIds.length === 0;
            bulkActionButton.textContent = `Apply to ${selectedIds.length} transaction(s)`;
        }
    }
}

// Initialize the accounting app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.accountingApp = new AccountingApp();
    
    // Setup bulk operations if on transaction list page
    if (window.location.pathname.includes('/transactions/')) {
        window.accountingApp.setupBulkOperations();
    }
});

// Export utility functions for global use
window.AccountingUtils = {
    formatCurrency: (amount, currency = '₦') => {
        return currency + parseFloat(amount).toLocaleString('en-US', {
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        });
    },
    
    sanitizeAmount: (value) => {
        return value.replace(/[₦$€£¥,\s]/g, '');
    },
    
    validateAmount: (value) => {
        const sanitized = window.AccountingUtils.sanitizeAmount(value);
        const num = parseFloat(sanitized);
        return !isNaN(num) && num > 0;
    }
}; 