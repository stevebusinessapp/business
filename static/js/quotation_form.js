// Quotation Form JavaScript - Simplified and Reliable Real-time Calculations
document.addEventListener('DOMContentLoaded', function() {
    console.log('Quotation form JavaScript loaded');
    
    // Get form index with null check
    const managementForm = document.getElementById('id_form-TOTAL_FORMS');
    let formIndex = 0;
    if (managementForm) {
        formIndex = parseInt(managementForm.value) || 0;
    } else {
        console.log('Management form not found, starting with index 0');
    }

    // Smart number extraction function
    function extractNumber(value) {
        if (!value || typeof value !== 'string') return 0;
        
        // Remove all non-numeric characters except decimal point and minus
        let cleaned = value.replace(/[^\d.-]/g, '');
        
        // Handle multiple decimal points (keep only the first one)
        const parts = cleaned.split('.');
        if (parts.length > 2) {
            cleaned = parts[0] + '.' + parts.slice(1).join('');
        }
        
        // Handle multiple minus signs (keep only the first one)
        if (cleaned.startsWith('-')) {
            cleaned = '-' + cleaned.substring(1).replace(/-/g, '');
        } else {
            cleaned = cleaned.replace(/-/g, '');
        }
        
        const numValue = parseFloat(cleaned);
        return isNaN(numValue) ? 0 : numValue;
    }

    // Format number for display
    function formatCurrency(amount) {
        return new Intl.NumberFormat('en-NG', {
            style: 'currency',
            currency: 'NGN',
            minimumFractionDigits: 2,
            maximumFractionDigits: 2
        }).format(amount);
    }

    // Calculate line total for a specific row
    function calculateLineTotal(row) {
        // Try multiple possible selectors for quantity and price fields
        const quantityInput = row.querySelector('input[name*="quantity"], input[name*="0-quantity"], input[name*="1-quantity"], input[name*="2-quantity"]');
        const priceInput = row.querySelector('input[name*="unit_price"], input[name*="0-unit_price"], input[name*="1-unit_price"], input[name*="2-unit_price"]');
        const totalInput = row.querySelector('.line-total');
        
        if (!quantityInput || !priceInput || !totalInput) {
            console.log('Missing inputs for calculation:', {
                quantityInput: !!quantityInput,
                priceInput: !!priceInput,
                totalInput: !!totalInput
            });
            return;
        }
        
        const quantity = extractNumber(quantityInput.value);
        const price = extractNumber(priceInput.value);
        const total = quantity * price;
        
        totalInput.value = total.toFixed(2);
        console.log(`Line total calculated: ${quantity} × ${price} = ${total}`);
        
        // Immediately update totals
        calculateTotals();
    }

    // Calculate all totals
    function calculateTotals() {
        let subtotal = 0;
        
        // Calculate subtotal from line items
        document.querySelectorAll('.line-total').forEach(input => {
            subtotal += extractNumber(input.value);
        });
        
        // Get financial amounts
        const taxInput = document.getElementById('id_total_tax');
        const discountInput = document.getElementById('id_total_discount');
        const shippingInput = document.getElementById('id_shipping_fee');
        const otherInput = document.getElementById('id_other_charges');
        
        const tax = extractNumber(taxInput ? taxInput.value : '0');
        const discount = extractNumber(discountInput ? discountInput.value : '0');
        const shipping = extractNumber(shippingInput ? shippingInput.value : '0');
        const other = extractNumber(otherInput ? otherInput.value : '0');
        
        // Calculate grand total
        const grandTotal = subtotal + tax + shipping + other - discount;
        
        console.log(`Totals calculated: Subtotal=${subtotal}, Tax=${tax}, Discount=${discount}, Shipping=${shipping}, Other=${other}, Grand=${grandTotal}`);
        
        // Update display
        updateTotalsDisplay(subtotal, tax, discount, shipping, other, grandTotal);
    }

    // Update totals display with conditional showing
    function updateTotalsDisplay(subtotal, tax, discount, shipping, other, grandTotal) {
        // Always show subtotal
        const subtotalElement = document.getElementById('subtotal');
        if (subtotalElement) {
            subtotalElement.textContent = formatCurrency(subtotal);
        }
        
        // Show tax only if it's greater than 0
        const taxElement = document.getElementById('tax-amount');
        const taxRow = document.querySelector('.tax-row');
        if (tax > 0) {
            if (taxElement) taxElement.textContent = formatCurrency(tax);
            if (taxRow) taxRow.style.display = 'flex';
        } else {
            if (taxRow) taxRow.style.display = 'none';
        }
        
        // Show discount only if it's greater than 0
        const discountElement = document.getElementById('discount-amount');
        const discountRow = document.querySelector('.discount-row');
        if (discount > 0) {
            if (discountElement) discountElement.textContent = formatCurrency(discount);
            if (discountRow) discountRow.style.display = 'flex';
        } else {
            if (discountRow) discountRow.style.display = 'none';
        }
        
        // Show shipping only if it's greater than 0
        const shippingElement = document.getElementById('shipping-amount');
        const shippingRow = document.querySelector('.shipping-row');
        if (shipping > 0) {
            if (shippingElement) shippingElement.textContent = formatCurrency(shipping);
            if (shippingRow) shippingRow.style.display = 'flex';
        } else {
            if (shippingRow) shippingRow.style.display = 'none';
        }
        
        // Show other charges only if it's greater than 0
        const otherElement = document.getElementById('other-amount');
        const otherRow = document.querySelector('.other-row');
        if (other > 0) {
            if (otherElement) otherElement.textContent = formatCurrency(other);
            if (otherRow) otherRow.style.display = 'flex';
        } else {
            if (otherRow) otherRow.style.display = 'none';
        }
        
        // Always show grand total
        const grandTotalElement = document.getElementById('grand-total');
        if (grandTotalElement) {
            grandTotalElement.textContent = formatCurrency(grandTotal);
        }
    }

    // Add event listeners to existing quantity and price inputs
    function attachEventListeners() {
        console.log('Attaching event listeners...');
        
        // For existing form rows - use multiple selectors to catch all possible field names
        document.querySelectorAll('tr.form-row').forEach(row => {
            // Try multiple possible selectors for quantity and price fields
            const quantityInput = row.querySelector('input[name*="quantity"], input[name*="0-quantity"], input[name*="1-quantity"], input[name*="2-quantity"]');
            const priceInput = row.querySelector('input[name*="unit_price"], input[name*="0-unit_price"], input[name*="1-unit_price"], input[name*="2-unit_price"]');
            
            if (quantityInput) {
                quantityInput.addEventListener('input', () => calculateLineTotal(row));
                quantityInput.addEventListener('change', () => calculateLineTotal(row));
                quantityInput.addEventListener('blur', () => calculateLineTotal(row));
                console.log('Added listeners to quantity input:', quantityInput.name);
            } else {
                console.log('No quantity input found in row');
            }
            
            if (priceInput) {
                priceInput.addEventListener('input', () => calculateLineTotal(row));
                priceInput.addEventListener('change', () => calculateLineTotal(row));
                priceInput.addEventListener('blur', () => calculateLineTotal(row));
                console.log('Added listeners to price input:', priceInput.name);
            } else {
                console.log('No price input found in row');
            }
        });
        
        // For financial fields
        const financialFields = ['id_total_tax', 'id_total_discount', 'id_shipping_fee', 'id_other_charges'];
        financialFields.forEach(fieldId => {
            const field = document.getElementById(fieldId);
            if (field) {
                field.addEventListener('input', calculateTotals);
                field.addEventListener('change', calculateTotals);
                field.addEventListener('blur', calculateTotals);
                console.log('Added listeners to financial field:', fieldId);
            } else {
                console.log('Financial field not found:', fieldId);
            }
        });
    }

    // Add new line item row
    window.addRow = function() {
        console.log('Adding new row...');
        const tbody = document.getElementById('line-items-tbody');
        const managementForm = document.getElementById('id_form-TOTAL_FORMS');
        const newRow = document.createElement('tr');
        newRow.className = 'form-row';
        newRow.id = `form-row-${formIndex}`;
        
        newRow.innerHTML = `
            <td>
                <input type="text" name="form-${formIndex}-product_service" class="form-control" placeholder="Product or service name">
            </td>
            <td>
                <input type="text" name="form-${formIndex}-description" class="form-control" placeholder="Detailed description">
            </td>
            <td>
                <input type="text" name="form-${formIndex}-quantity" class="form-control quantity-input" placeholder="1" value="1">
            </td>
            <td>
                <input type="text" name="form-${formIndex}-unit_price" class="form-control price-input" placeholder="0.00" value="0.00">
            </td>
            <td>
                <input type="text" class="form-control line-total" readonly>
            </td>
            <td>
                <button type="button" class="btn btn-remove-row" onclick="removeRow(this)" title="Remove Item">
                    <i class="fas fa-trash me-1"></i>Remove
                </button>
            </td>
        `;
        
        if (tbody) {
            tbody.appendChild(newRow);
        }
        
        if (managementForm) {
            managementForm.value = formIndex + 1;
        }
        
        formIndex++;
        
        // Add event listeners to new row
        const quantityInput = newRow.querySelector('input[name*="quantity"]');
        const priceInput = newRow.querySelector('input[name*="unit_price"]');
        
        if (quantityInput) {
            quantityInput.addEventListener('input', () => calculateLineTotal(newRow));
            quantityInput.addEventListener('change', () => calculateLineTotal(newRow));
            quantityInput.addEventListener('blur', () => calculateLineTotal(newRow));
        }
        
        if (priceInput) {
            priceInput.addEventListener('input', () => calculateLineTotal(newRow));
            priceInput.addEventListener('change', () => calculateLineTotal(newRow));
            priceInput.addEventListener('blur', () => calculateLineTotal(newRow));
        }
        
        // Initialize calculation for new row
        calculateLineTotal(newRow);
        console.log('New row added with event listeners');
    };

    // Remove line item row
    window.removeRow = function(button) {
        console.log('Removing row...');
        const row = button.closest('tr');
        if (row) {
            row.remove();
            calculateTotals();
        }
    };

    // Initialize everything
    function initialize() {
        console.log('Initializing quotation form...');
        
        // Attach event listeners to existing elements
        attachEventListeners();
        
        // Initialize existing line items
        document.querySelectorAll('.line-item-row').forEach(row => {
            calculateLineTotal(row);
        });
        
        // Calculate initial totals
        calculateTotals();
        
        // Format money inputs on blur
        document.querySelectorAll('.money-input').forEach(input => {
            input.addEventListener('blur', function() {
                const extractedValue = extractNumber(this.value);
                this.value = extractedValue.toFixed(2);
                calculateTotals();
            });
            
            input.addEventListener('input', function() {
                calculateTotals();
            });
        });
        
        console.log('Quotation form initialized successfully');
    }

    // Initialize the form when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeQuotationForm);
    } else {
        initializeQuotationForm();
    }
    
    // Also try to initialize after a short delay to catch any late-loading elements
    setTimeout(initialize, 500);
}); 