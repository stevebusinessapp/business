/**
 * Simple and Direct Inventory Real-Time Calculator
 * This script provides immediate real-time calculation functionality
 */

class SimpleInventoryCalculator {
    constructor() {
        this.csrfToken = this.getCSRFToken();
        this.init();
    }

    init() {
        console.log('SimpleInventoryCalculator initialized');
        this.setupEventListeners();
        this.calculateAllTotals();
        
        // Update status indicator
        const statusElement = document.getElementById('calculator-status');
        if (statusElement) {
            statusElement.innerHTML = '<i class="fas fa-check"></i> Ready';
            statusElement.className = 'badge bg-success ms-2';
        }
    }

    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || 
               document.cookie.split('; ').find(row => row.startsWith('csrftoken='))?.split('=')[1] || '';
    }

    setupEventListeners() {
        // Make quantity and price fields editable on click
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('editable-field')) {
                const fieldName = e.target.dataset.field;
                if (fieldName === 'quantity' || fieldName === 'unit_price') {
                this.makeEditable(e.target);
                }
            }
        });

        // Handle input changes for real-time calculation
        document.addEventListener('input', (e) => {
            if (e.target.classList.contains('editable-input')) {
                this.handleRealTimeInput(e.target);
            }
        });

        // Save on blur
        document.addEventListener('blur', (e) => {
            if (e.target.classList.contains('editable-input')) {
                this.saveField(e.target);
            }
        }, true);

        // Save on Enter key
        document.addEventListener('keydown', (e) => {
            if (e.target.classList.contains('editable-input') && e.key === 'Enter') {
                e.preventDefault();
                this.saveField(e.target);
            }
        });
    }

    makeEditable(element) {
        if (element.classList.contains('editing')) return;
        
        const currentValue = element.textContent.trim();
        const fieldName = element.dataset.field;
        
        element.classList.add('editing');
        
        const input = document.createElement('input');
        input.type = 'number';
        input.step = '0.01';
        input.value = this.extractNumber(currentValue) || '';
        input.className = 'form-control form-control-sm editable-input';
        input.dataset.field = fieldName;
        input.dataset.itemId = element.dataset.itemId;
        
        element.innerHTML = '';
        element.appendChild(input);
        input.focus();
        input.select();
    }

    handleRealTimeInput(input) {
        const fieldName = input.dataset.field;
        const row = input.closest('tr');
        const newValue = input.value;
        
        // Update the display immediately
        const fieldElement = input.closest('.editable-field');
        if (fieldElement) {
            let displayValue = newValue;
            if (fieldName === 'unit_price') {
                displayValue = this.formatCurrency(parseFloat(newValue) || 0);
            }
            fieldElement.textContent = displayValue;
        }
        
        // Calculate row total immediately
        this.calculateRowTotal(row);
        
        // Calculate grand total
        this.calculateGrandTotal();
    }

    saveField(input) {
        const fieldName = input.dataset.field;
        const itemId = input.dataset.itemId;
        const newValue = input.value;
        const row = input.closest('tr');
        
        // Update display
        const fieldElement = input.closest('.editable-field');
        fieldElement.classList.remove('editing');
        
        let displayValue = newValue;
        if (fieldName === 'unit_price') {
            displayValue = this.formatCurrency(parseFloat(newValue) || 0);
        }
        fieldElement.textContent = displayValue;
        
        // Send AJAX update
        this.updateFieldAjax(itemId, fieldName, newValue);
        
        // Final calculation
            this.calculateRowTotal(row);
            this.calculateGrandTotal();
    }

    calculateRowTotal(row) {
        const quantityField = row.querySelector('[data-field="quantity"]');
        const priceField = row.querySelector('[data-field="unit_price"]');
        const totalField = row.querySelector('[data-field="total"]');
        
        if (!quantityField || !priceField || !totalField) {
            console.log('Missing fields for calculation');
            return;
        }
        
        const quantity = this.extractNumber(quantityField.textContent) || 0;
        const price = this.extractNumber(priceField.textContent) || 0;
        const total = quantity * price;
        
            totalField.textContent = this.formatCurrency(total);
            totalField.dataset.value = total;
            
                console.log('Row total calculated:', { quantity, price, total });
    }

    calculateAllTotals() {
        const rows = document.querySelectorAll('tbody tr[data-item-id]');
        rows.forEach(row => {
            this.calculateRowTotal(row);
        });
        this.calculateGrandTotal();
    }

    calculateGrandTotal() {
        const totalFields = document.querySelectorAll('[data-field="total"]');
        let grandTotal = 0;
        
        totalFields.forEach(field => {
            const value = this.extractNumber(field.textContent) || 0;
            grandTotal += value;
        });
        
        const grandTotalElement = document.getElementById('grandTotal');
        if (grandTotalElement) {
            grandTotalElement.textContent = this.formatCurrency(grandTotal);
        }
        
            console.log('Grand total calculated:', grandTotal);
    }

    extractNumber(value) {
        if (value === null || value === undefined || value === '') {
            return 0;
        }
        
        // Remove currency symbols and other non-numeric characters
        const cleaned = String(value).replace(/[₦$€£¥₹₿₤₩₪₫₭₮₯₰₱₲₳₴₵₶₷₸₹₺₻₼₽₾₿]/g, '');
        const numeric = cleaned.replace(/[^\d.-]/g, '');
        
        const result = parseFloat(numeric);
        return isNaN(result) ? 0 : result;
    }

    formatCurrency(value) {
        return `₦${parseFloat(value).toLocaleString('en-NG', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }

    updateFieldAjax(itemId, fieldName, value) {
        fetch('/inventory/ajax/update-field/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            },
            body: JSON.stringify({
                item_id: itemId,
                field_name: fieldName,
                value: value,
                field_type: 'number'
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Field updated successfully:', fieldName, value);
            } else {
                console.error('Failed to update field:', data.error);
            }
        })
        .catch(error => {
            console.error('Error updating field:', error);
        });
    }

    updateStatus(select) {
        const itemId = select.dataset.itemId;
        const newStatus = select.value;
        
        fetch('/inventory/ajax/update-status/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': this.csrfToken
            },
            body: JSON.stringify({
                item_id: itemId,
                new_status: newStatus
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                console.log('Status updated successfully:', data);
            } else {
                console.error('Failed to update status:', data.error);
            }
        })
        .catch(error => {
            console.error('Error updating status:', error);
        });
    }
}

// Initialize immediately when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.inventoryCalculator = new SimpleInventoryCalculator();
    });
            } else {
    window.inventoryCalculator = new SimpleInventoryCalculator();
}

// Global functions for testing
window.testCalculations = function() {
    if (window.inventoryCalculator) {
        console.log('Testing calculations...');
        window.inventoryCalculator.calculateAllTotals();
        console.log('Calculations completed');
            } else {
        console.log('Calculator not initialized');
    }
};

window.createTestData = function() {
    const tbody = document.querySelector('tbody');
    if (!tbody) return;
    
    // Create a test row
    const testRow = document.createElement('tr');
    testRow.dataset.itemId = 'test-' + Date.now();
    testRow.innerHTML = `
        <td class="quantity-cell">
            <span class="editable-field" data-field="quantity" data-type="number" data-item-id="${testRow.dataset.itemId}">
                10
            </span>
        </td>
        <td class="price-cell">
            <span class="editable-field" data-field="unit_price" data-type="decimal" data-item-id="${testRow.dataset.itemId}">
                ₦1,500.00
            </span>
        </td>
        <td class="total-cell">
            <span class="editable-field" data-field="total" data-type="calculated" data-item-id="${testRow.dataset.itemId}">
                ₦15,000.00
            </span>
        </td>
        <td class="status-cell">
            <select class="form-select status-select" data-item-id="${testRow.dataset.itemId}" onchange="updateStatus(this)">
                <option value="1">In Stock</option>
                <option value="2">Low Stock</option>
                <option value="3">Out of Stock</option>
            </select>
        </td>
        <td class="actions-cell">
            <div class="btn-group">
                <button class="btn btn-sm btn-info"><i class="fas fa-eye"></i></button>
                <button class="btn btn-sm btn-warning"><i class="fas fa-edit"></i></button>
                <button class="btn btn-sm btn-danger"><i class="fas fa-trash"></i></button>
            </div>
        </td>
    `;
    
    tbody.appendChild(testRow);
    
    // Recalculate totals
    if (window.inventoryCalculator) {
        window.inventoryCalculator.calculateAllTotals();
    }
    
    console.log('Test data created');
};

window.updateStatus = function(select) {
    if (window.inventoryCalculator) {
        window.inventoryCalculator.updateStatus(select);
        } else {
        console.log('Calculator not initialized');
    }
};

window.toggleDebugMode = function() {
    const currentUrl = new URL(window.location);
    if (currentUrl.searchParams.has('debug')) {
        currentUrl.searchParams.delete('debug');
            } else {
        currentUrl.searchParams.set('debug', 'true');
    }
    window.location.href = currentUrl.toString();
}; 