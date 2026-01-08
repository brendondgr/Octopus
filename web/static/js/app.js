document.addEventListener('DOMContentLoaded', () => {
    console.log('Octopus App Initialized');
    
    // Initialize Drag and Drop if available
    if (typeof initDragAndDrop === 'function') {
        initDragAndDrop();
    }
});
