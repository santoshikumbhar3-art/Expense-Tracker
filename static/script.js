/**
 * Expense Tracker — Client-side interactions.
 *
 * Handles: button ripple effects, delete confirmation modal,
 * client-side form validation, and toast auto-dismissal.
 */

document.addEventListener('DOMContentLoaded', () => {
    initRippleEffect();
    initDeleteModal();
    initFormValidation();
    initToastAutoDismiss();
});

/**
 * Adds a Material-style ripple animation to any element with the
 * `.ripple` class when clicked.
 */
function initRippleEffect() {
    document.querySelectorAll('.ripple').forEach((button) => {
        button.addEventListener('click', (event) => {
            const rect = button.getBoundingClientRect();
            const circle = document.createElement('span');
            const size = Math.max(rect.width, rect.height);

            circle.classList.add('ripple-circle');
            circle.style.width = circle.style.height = `${size}px`;
            circle.style.left = `${event.clientX - rect.left - size / 2}px`;
            circle.style.top = `${event.clientY - rect.top - size / 2}px`;

            button.appendChild(circle);
            window.setTimeout(() => circle.remove(), 600);
        });
    });
}

/**
 * Wires up the delete-confirmation modal on the dashboard. Clicking a
 * delete icon opens the modal and points its form at the correct
 * transaction id; the modal never submits without explicit confirmation.
 */
function initDeleteModal() {
    const modal = document.getElementById('deleteModal');
    if (!modal) {
        return;
    }

    const deleteForm = document.getElementById('deleteForm');
    const modalText = document.getElementById('deleteModalText');
    const cancelBtn = document.getElementById('cancelDeleteBtn');

    document.querySelectorAll('[data-delete-id]').forEach((trigger) => {
        trigger.addEventListener('click', () => {
            const expenseId = trigger.getAttribute('data-delete-id');
            const expenseTitle = trigger.getAttribute('data-delete-title');

            deleteForm.setAttribute('action', `/delete/${expenseId}`);
            modalText.textContent = `"${expenseTitle}" will be permanently removed. This action cannot be undone.`;
            modal.classList.add('active');
        });
    });

    const closeModal = () => modal.classList.remove('active');

    cancelBtn.addEventListener('click', closeModal);
    modal.addEventListener('click', (event) => {
        if (event.target === modal) {
            closeModal();
        }
    });
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            closeModal();
        }
    });

    deleteForm.addEventListener('submit', () => {
        showLoadingOverlay();
    });
}

/**
 * Applies elegant, real-time client-side validation to the add/edit
 * expense forms. Mirrors the server-side rules so users see feedback
 * before the request round-trip, while the server remains the source
 * of truth for validation.
 */
function initFormValidation() {
    const form = document.getElementById('expenseForm');
    if (!form) {
        return;
    }

    const titleField = document.getElementById('title');
    const amountField = document.getElementById('amount');
    const dateField = document.getElementById('expense_date');
    const categoryField = document.getElementById('category');
    const descriptionField = document.getElementById('description');

    form.addEventListener('submit', (event) => {
        const validations = [
            validateRequiredText(titleField, 'Title is required.'),
            validatePositiveAmount(amountField),
            validateDate(dateField),
            validateRequiredSelect(categoryField, 'Please select a valid category.'),
            validateMaxLength(descriptionField, 500, 'Description must be under 500 characters.'),
        ];

        const isValid = validations.every(Boolean);

        if (!isValid) {
            event.preventDefault();
            return;
        }

        showLoadingOverlay();
    });

    [titleField, amountField, dateField, categoryField, descriptionField]
        .filter(Boolean)
        .forEach((field) => {
            field.addEventListener('input', () => clearFieldError(field));
            field.addEventListener('change', () => clearFieldError(field));
        });
}

function validateRequiredText(field, message) {
    if (!field) {
        return true;
    }
    if (!field.value.trim()) {
        setFieldError(field, message);
        return false;
    }
    return true;
}

function validatePositiveAmount(field) {
    if (!field) {
        return true;
    }
    const value = parseFloat(field.value);
    if (!field.value.trim() || Number.isNaN(value)) {
        setFieldError(field, 'Amount is required.');
        return false;
    }
    if (value <= 0) {
        setFieldError(field, 'Amount must be greater than zero.');
        return false;
    }
    return true;
}

function validateDate(field) {
    if (!field) {
        return true;
    }
    if (!field.value) {
        setFieldError(field, 'Date is required.');
        return false;
    }
    const selectedDate = new Date(`${field.value}T00:00:00`);
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    if (selectedDate > today) {
        setFieldError(field, 'Date cannot be in the future.');
        return false;
    }
    return true;
}

function validateRequiredSelect(field, message) {
    if (!field) {
        return true;
    }
    if (!field.value) {
        setFieldError(field, message);
        return false;
    }
    return true;
}

function validateMaxLength(field, maxLength, message) {
    if (!field) {
        return true;
    }
    if (field.value.length > maxLength) {
        setFieldError(field, message);
        return false;
    }
    return true;
}

function setFieldError(field, message) {
    field.classList.add('input-error');

    let errorEl = field.parentElement.querySelector('.error-message');
    if (!errorEl) {
        errorEl = document.createElement('span');
        errorEl.className = 'error-message';
        field.parentElement.appendChild(errorEl);
    }
    errorEl.textContent = message;
}

function clearFieldError(field) {
    field.classList.remove('input-error');
    const errorEl = field.parentElement.querySelector('.error-message');
    if (errorEl) {
        errorEl.remove();
    }
}

/**
 * Automatically fades out and removes flash-message toasts after a
 * short delay so the dashboard stays clean on repeat visits.
 */
function initToastAutoDismiss() {
    const toasts = document.querySelectorAll('.toast');
    toasts.forEach((toast, index) => {
        window.setTimeout(() => {
            toast.classList.add('toast-exit');
            window.setTimeout(() => toast.remove(), 400);
        }, 3200 + index * 200);
    });
}

/**
 * Shows a brief loading overlay while a form submission or navigation
 * is in flight, giving the user immediate visual feedback.
 */
function showLoadingOverlay() {
    let overlay = document.querySelector('.loading-overlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.className = 'loading-overlay';
        overlay.innerHTML = '<div class="loading-spinner"></div>';
        document.body.appendChild(overlay);
    }
    overlay.classList.add('active');
}