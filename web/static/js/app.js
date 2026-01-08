document.addEventListener('DOMContentLoaded', () => {
    console.log('Octopus App Initialized');
    
    // Initialize Drag and Drop if available
    if (typeof initDragAndDrop === 'function') {
        initDragAndDrop();
    }

    // Listen for progress update events from HTMX
    document.body.addEventListener('updateProgress', (evt) => {
        const { projectId, progress, goalCount } = evt.detail;
        
        // 1. Update Goal Count
        const countSpan = document.getElementById(`goal-count-${projectId}`);
        if (countSpan) countSpan.textContent = goalCount;
        
        // 2. Update Progress Percent Text
        const percentSpan = document.getElementById(`modal-progress-percent-${projectId}`);
        if (percentSpan) percentSpan.textContent = progress + '%';
        
        // 3. Update Progress Bars & Text Overlays (Animated)
        const containers = [
            document.getElementById(`modal-progress-${projectId}`),
            document.getElementById(`progress-${projectId}`)
        ];
        
        containers.forEach(container => {
            if (container) {
                const bar = container.querySelector('.progress-bar');
                const overlay = container.querySelector('.progress-text-overlay');
                if (bar) bar.style.width = progress + '%';
                if (overlay) overlay.textContent = progress + '%';
            }
        });
    });
});

