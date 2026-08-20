document.addEventListener('DOMContentLoaded', function() {
    
    // --- 1. LIVE PREVIEW LOGIC ---
    // Django generates IDs like 'id_title', 'id_category', etc.
    const titleInput = document.getElementById('id_title');
    const categoryInput = document.getElementById('id_category');
    const descriptionInput = document.getElementById('id_description');
    const levelInput = document.getElementById('id_level');
    const durationInput = document.getElementById('id_duration');
    const imageInput = document.getElementById('id_image');

    const previewTitle = document.getElementById('previewTitle');
    const previewCategory = document.getElementById('previewCategory');
    const previewDescription = document.getElementById('previewDescription');
    const previewLevel = document.getElementById('previewLevel');
    const previewDuration = document.getElementById('previewDuration');
    const imagePreview = document.getElementById('imagePreview');

    if (titleInput) {
        titleInput.addEventListener('input', (e) => {
            previewTitle.textContent = e.target.value || 'Course Title';
        });
    }

    if (categoryInput) {
        categoryInput.addEventListener('change', (e) => {
            const selectedText = e.target.options[e.target.selectedIndex].text;
            previewCategory.textContent = selectedText !== '---------' ? selectedText : 'Category';
        });
    }

    if (descriptionInput) {
        descriptionInput.addEventListener('input', (e) => {
            // Limit preview description length
            const text = e.target.value;
            previewDescription.textContent = text ? (text.length > 100 ? text.substring(0, 100) + '...' : text) : 'Course description will appear here.';
        });
    }

    if (levelInput) {
        levelInput.addEventListener('change', (e) => {
            previewLevel.textContent = e.target.value || '-';
        });
    }

    if (durationInput) {
        durationInput.addEventListener('input', (e) => {
            previewDuration.textContent = e.target.value || '-';
        });
    }

    // Handle Image Preview
    if (imageInput) {
        imageInput.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imagePreview.innerHTML = `<img src="${e.target.result}" alt="Course Preview" class="img-fluid rounded" style="object-fit: cover; height: 100%; width: 100%;">`;
                }
                reader.readAsDataURL(file);
            } else {
                imagePreview.innerHTML = '<i class="bi bi-image fs-1 text-muted"></i>';
            }
        });
    }


    // --- 2. DYNAMIC INPUTS: OUTCOMES & REQUIREMENTS ---
    const addOutcomeBtn = document.getElementById('addOutcome');
    const outcomesContainer = document.getElementById('outcomesContainer');
    
    const addRequirementBtn = document.getElementById('addRequirement');
    const requirementsContainer = document.getElementById('requirementsContainer');

    // Add new Outcome
    if (addOutcomeBtn) {
        addOutcomeBtn.addEventListener('click', () => {
            const newField = document.createElement('div');
            newField.className = 'input-group mb-2';
            newField.innerHTML = `
                <input type="text" name="outcomes[]" class="form-control outcome" placeholder="Example: Learn Python fundamentals">
                <button type="button" class="btn btn-outline-danger remove-outcome">
                    <i class="bi bi-trash"></i>
                </button>
            `;
            outcomesContainer.appendChild(newField);
        });
    }

    // Add new Requirement
    if (addRequirementBtn) {
        addRequirementBtn.addEventListener('click', () => {
            const newField = document.createElement('div');
            newField.className = 'input-group mb-2';
            newField.innerHTML = `
                <input type="text" name="requirements[]" class="form-control requirement" placeholder="Example: Basic computer knowledge">
                <button type="button" class="btn btn-outline-danger remove-requirement">
                    <i class="bi bi-trash"></i>
                </button>
            `;
            requirementsContainer.appendChild(newField);
        });
    }

    // Event Delegation for Remove Buttons
    document.addEventListener('click', function(e) {
        if (e.target.closest('.remove-outcome')) {
            e.target.closest('.input-group').remove();
        }
        if (e.target.closest('.remove-requirement')) {
            e.target.closest('.input-group').remove();
        }
    });

});