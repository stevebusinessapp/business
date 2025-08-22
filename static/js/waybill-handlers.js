// WAYBILL HANDLERS - Optimized for performance
(function() {
    'use strict';
    
    // Cache DOM elements
    const cache = {
        form: null,
        previewContainer: null,
        templateSelect: null,
        itemsContainer: null,
        addItemBtn: null,
        elements: new Map()
    };
    
    // Get cached element or query and cache it
    function getElement(selector) {
        if (!cache.elements.has(selector)) {
            cache.elements.set(selector, document.querySelector(selector));
        }
        return cache.elements.get(selector);
    }
    
    // Debounce function for performance
    function debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
    
    // Throttle function for performance
    function throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }
    
    // Initialize form handlers
    function initializeFormHandlers() {
        cache.form = getElement('#waybill-form');
        cache.previewContainer = getElement('#preview-content');
        cache.templateSelect = getElement('#template-select');
        
        if (!cache.form) {
            console.error('Waybill form not found');
            return;
        }
        
        setupFormValidation();
        setupPreviewUpdates();
        setupItemManagement();
        setupAutoSave();
    }
    
    // Setup form validation
    function setupFormValidation() {
        const form = cache.form;
        
        form.addEventListener('submit', function(e) {
            if (!validateForm()) {
                e.preventDefault();
                return false;
            }
            
            // Show loading state
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = 'Creating...';
            }
        });
        
        // Real-time validation
        form.addEventListener('input', debounce(function(e) {
            validateField(e.target);
            updatePreview();
        }, 300));
        
        form.addEventListener('change', function(e) {
            validateField(e.target);
            updatePreview();
        });
    }
    
    // Validate individual field
    function validateField(field) {
        const value = field.value.trim();
        const fieldName = field.name;
        
        // Remove existing error styling
        field.classList.remove('is-invalid');
        
        // Basic validation rules
        if (field.hasAttribute('required') && !value) {
            field.classList.add('is-invalid');
            return false;
        }
        
        if (field.type === 'email' && value && !isValidEmail(value)) {
            field.classList.add('is-invalid');
            return false;
        }
        
        if (field.type === 'number' && value && isNaN(value)) {
            field.classList.add('is-invalid');
            return false;
        }
        
        field.classList.add('is-valid');
        return true;
    }
    
    // Validate entire form
    function validateForm() {
        const form = cache.form;
        const fields = form.querySelectorAll('input, select, textarea');
        let isValid = true;
        
        fields.forEach(field => {
            if (!validateField(field)) {
                isValid = false;
            }
        });
        
        return isValid;
    }
    
    // Email validation
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
    
    // Setup preview updates
    function setupPreviewUpdates() {
        const updatePreview = debounce(function() {
            const previewContainer = cache.previewContainer;
            if (!previewContainer) return;
            
            const formData = new FormData(cache.form);
            const previewData = {};
            
            // Collect form data
            for (let [key, value] of formData.entries()) {
                previewData[key] = value;
            }
            
            // Update preview elements
            updatePreviewElements(previewData);
        }, 500);
        
        // Store function for external access
        window.updatePreview = updatePreview;
    }
    
    // Update preview elements
    function updatePreviewElements(data) {
        const previewContainer = cache.previewContainer;
        if (!previewContainer) return;
        
        // Update waybill number
        const waybillNumber = previewContainer.querySelector('.waybill-number');
        if (waybillNumber && data.waybill_number) {
            waybillNumber.textContent = data.waybill_number;
        }
        
        // Update delivery date
        const deliveryDate = previewContainer.querySelector('.delivery-date');
        if (deliveryDate && data.delivery_date) {
            deliveryDate.textContent = formatDate(data.delivery_date);
        }
        
        // Update status
        const status = previewContainer.querySelector('.status');
        if (status && data.status) {
            status.textContent = data.status.charAt(0).toUpperCase() + data.status.slice(1);
        }
        
        // Update custom fields
        updateCustomFields(data);
        
        // Update items table
        updateItemsTable(data);
    }
    
    // Update custom fields in preview
    function updateCustomFields(data) {
        const previewContainer = cache.previewContainer;
        if (!previewContainer) return;
        
        Object.keys(data).forEach(key => {
            if (key.startsWith('custom_')) {
                const previewElement = previewContainer.querySelector(`[data-field="${key}"]`);
                if (previewElement) {
                    previewElement.textContent = data[key];
                }
            }
        });
    }
    
    // Update items table in preview
    function updateItemsTable(data) {
        const previewContainer = cache.previewContainer;
        const itemsTable = previewContainer.querySelector('.items-table tbody');
        
        if (!itemsTable) return;
        
        // Clear existing items
        itemsTable.innerHTML = '';
        
        // Collect item data
        const items = {};
        Object.keys(data).forEach(key => {
            if (key.startsWith('items[')) {
                const match = key.match(/items\[(\d+)\]\[(\w+)\]/);
                if (match) {
                    const index = match[1];
                    const field = match[2];
                    
                    if (!items[index]) {
                        items[index] = {};
                    }
                    items[index][field] = data[key];
                }
            }
        });
        
        // Create table rows
        Object.keys(items).forEach(index => {
            const item = items[index];
            const row = document.createElement('tr');
            
            // Only show items with meaningful data
            const hasData = Object.values(item).some(value => value && value.trim());
            
            if (hasData) {
                row.innerHTML = `
                    <td>${item.description || ''}</td>
                    <td>${item.quantity || ''}</td>
                    <td>${item.weight || ''}</td>
                    <td>${item.dimensions || ''}</td>
                    <td>${item.notes || ''}</td>
                `;
                itemsTable.appendChild(row);
            }
        });
    }
    
    // Setup item management
    function setupItemManagement() {
        let itemIndex = 0;
        
        // Add item button
        document.addEventListener('click', function(e) {
            if (e.target.matches('.add-item-btn')) {
                e.preventDefault();
                addNewItem();
            }
            
            if (e.target.matches('.remove-item-btn')) {
                e.preventDefault();
                removeItem(e.target);
            }
        });
        
        function addNewItem() {
            const container = getElement('#items-container');
            if (!container) return;
            
            const itemHtml = `
                <div class="item-row" data-index="${itemIndex}">
                    <div class="form-group">
                        <label>Description</label>
                        <input type="text" name="items[${itemIndex}][description]" class="form-control">
                    </div>
                    <div class="form-group">
                        <label>Quantity</label>
                        <input type="number" name="items[${itemIndex}][quantity]" class="form-control">
                    </div>
                    <div class="form-group">
                        <label>Weight</label>
                        <input type="text" name="items[${itemIndex}][weight]" class="form-control">
                    </div>
                    <div class="form-group">
                        <label>Dimensions</label>
                        <input type="text" name="items[${itemIndex}][dimensions]" class="form-control">
                    </div>
                    <div class="form-group">
                        <label>Notes</label>
                        <input type="text" name="items[${itemIndex}][notes]" class="form-control">
                    </div>
                    <div class="form-group">
                        <button type="button" class="remove-item-btn">Remove</button>
                    </div>
                </div>
            `;
            
            container.insertAdjacentHTML('beforeend', itemHtml);
            itemIndex++;
            
            // Update preview
            window.updatePreview();
        }
        
        function removeItem(button) {
            const itemRow = button.closest('.item-row');
            if (itemRow) {
                itemRow.remove();
                window.updatePreview();
            }
        }
        
        // Add initial item
        addNewItem();
    }
    
    // Setup auto-save functionality
    function setupAutoSave() {
        const autoSave = debounce(function() {
            const formData = new FormData(cache.form);
            const data = {};
            
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            
            // Save to localStorage
            localStorage.setItem('waybill_draft', JSON.stringify(data));
            
            // Show saved indicator
            showSavedIndicator();
        }, 2000);
        
        // Auto-save on form changes
        cache.form.addEventListener('input', autoSave);
        cache.form.addEventListener('change', autoSave);
        
        // Load draft on page load
        loadDraft();
    }
    
    // Load draft from localStorage
    function loadDraft() {
        const draft = localStorage.getItem('waybill_draft');
        if (!draft) return;
        
        try {
            const data = JSON.parse(draft);
            
            // Fill form fields
            Object.keys(data).forEach(key => {
                const field = cache.form.querySelector(`[name="${key}"]`);
                if (field) {
                    field.value = data[key];
                }
            });
            
            // Update preview
            window.updatePreview();
        } catch (e) {
            console.error('Error loading draft:', e);
        }
    }
    
    // Show saved indicator
    function showSavedIndicator() {
        const indicator = getElement('#saved-indicator');
        if (!indicator) {
            const newIndicator = document.createElement('div');
            newIndicator.id = 'saved-indicator';
            newIndicator.innerHTML = '✓ Draft saved';
            newIndicator.style.cssText = `
                position: fixed;
                top: 20px;
                right: 20px;
                background: #28a745;
                color: white;
                padding: 10px 15px;
                border-radius: 4px;
                z-index: 1000;
                opacity: 0;
                transition: opacity 0.3s;
            `;
            document.body.appendChild(newIndicator);
            
            setTimeout(() => {
                newIndicator.style.opacity = '1';
            }, 10);
            
            setTimeout(() => {
                newIndicator.style.opacity = '0';
                setTimeout(() => {
                    newIndicator.remove();
                }, 300);
            }, 2000);
        }
    }
    
    // Format date for display
    function formatDate(dateString) {
        if (!dateString) return '';
        
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    }
    
    // Clear draft when form is submitted
    function clearDraft() {
        localStorage.removeItem('waybill_draft');
    }
    
    // Export functions for global access
    window.initializeWaybillHandlers = initializeFormHandlers;
    window.clearWaybillDraft = clearDraft;
    
    // Auto-initialize if DOM is already loaded
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeFormHandlers);
    } else {
        initializeFormHandlers();
    }
})();
