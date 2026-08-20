document.addEventListener('DOMContentLoaded', function() {
    const filterSelect = document.getElementById('courseFilter');
    const courseItems = document.querySelectorAll('.course-item');
    const emptyState = document.getElementById('emptyState');

    if (filterSelect) {
        filterSelect.addEventListener('change', function(e) {
            const selectedFilter = e.target.value; // 'all', 'published', or 'draft'
            let visibleCount = 0;

            courseItems.forEach(item => {
                // Get the status we stored in the HTML data attribute
                const courseStatus = item.getAttribute('data-status');

                if (selectedFilter === 'all' || courseStatus === selectedFilter) {
                    item.classList.remove('d-none'); // Show it
                    visibleCount++;
                } else {
                    item.classList.add('d-none'); // Hide it
                }
            });

            // Show or hide the JS empty state if no courses match the filter
            if (visibleCount === 0 && courseItems.length > 0) {
                emptyState.classList.remove('d-none');
            } else {
                emptyState.classList.add('d-none');
            }
        });
    }
});