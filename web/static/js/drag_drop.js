function initDragAndDrop() {
    let activeCard = null;
    let initialX, initialY;
    let cardRect;
    let placeholder = null;
    let dragHandle = null;

    // Use event delegation - attach to body once, works for all current and future cards
    document.body.addEventListener('pointerdown', handleDragStart);

    function handleDragStart(e) {
        if (e.button !== 0) return;

        // 1. Strict Handle Check
        const handle = e.target.closest('.drag-handle');
        if (!handle) return;

        const target = e.target.closest('.project-card');
        if (!target) return;

        activeCard = target;
        dragHandle = handle; // Store for capture release
        cardRect = activeCard.getBoundingClientRect();

        // Add moving class to body to suppress hover effects if needed
        document.body.classList.add('is-moving-card');

        // 2. Calculate Offsets
        initialX = e.clientX - cardRect.left;
        initialY = e.clientY - cardRect.top;

        // 3. Create Placeholder
        placeholder = document.createElement('div');
        placeholder.className = 'card-placeholder';
        placeholder.style.height = `${cardRect.height}px`;
        activeCard.parentNode.insertBefore(placeholder, activeCard);

        // 4. Set Drag State
        activeCard.classList.add('is-dragging');
        activeCard.style.width = `${cardRect.width}px`;
        activeCard.style.height = `${cardRect.height}px`; // Fix height to prevent collapse issues
        activeCard.style.top = `${cardRect.top}px`;
        activeCard.style.left = `${cardRect.left}px`;

        // 5. Global Listeners & Capture
        document.addEventListener('pointermove', handleDragMove);
        document.addEventListener('pointerup', handleDragEnd);
        document.addEventListener('pointercancel', handleDragEnd); // Handle Cancel

        handle.setPointerCapture(e.pointerId);
    }

    function handleDragMove(e) {
        if (!activeCard) return;

        e.preventDefault(); // Prevent scrolling logic implementation for now

        // 1. Move Card
        // Simply follow cursor with offset
        const x = e.clientX - initialX;
        const y = e.clientY - initialY;

        activeCard.style.left = `${x}px`;
        activeCard.style.top = `${y}px`;

        // 2. Hit Test
        // Hide active card to see what's underneath
        activeCard.hidden = true;
        const elemBelow = document.elementFromPoint(e.clientX, e.clientY);
        activeCard.hidden = false;

        if (!elemBelow) return;

        // 3. Find Column
        const column = elemBelow.closest('.status-column');

        if (column) {
            // Logic to move placeholder
            const children = Array.from(column.querySelectorAll('.project-card:not(.is-dragging)'));

            if (children.length === 0) {
                if (placeholder.parentNode !== column) {
                    column.appendChild(placeholder);
                }
            } else {
                // Sort logic
                let closestChild = null;
                let closestOffset = Number.NEGATIVE_INFINITY;

                children.forEach(child => {
                    const box = child.getBoundingClientRect();
                    const offset = e.clientY - box.top - box.height / 2;

                    if (offset < 0 && offset > closestOffset) {
                        closestOffset = offset;
                        closestChild = child;
                    }
                });

                if (closestChild) {
                    if (placeholder.nextElementSibling !== closestChild) {
                        column.insertBefore(placeholder, closestChild);
                    }
                } else {
                    if (placeholder.parentNode !== column || placeholder.nextElementSibling !== null) {
                        column.appendChild(placeholder);
                    }
                }
            }
        }
    }

    function handleDragEnd(e) {
        if (!activeCard) return;

        // Cleanup listeners immediately
        document.removeEventListener('pointermove', handleDragMove);
        document.removeEventListener('pointerup', handleDragEnd);
        document.removeEventListener('pointercancel', handleDragEnd);

        // Release capture
        if (dragHandle) {
            // releasePointerCapture is usually automatic on up, but good for safety
            // dragHandle.releasePointerCapture(e.pointerId); 
            dragHandle = null;
        }

        // 1. Determine Drop Target
        if (placeholder && placeholder.parentNode) {
            const newColumn = placeholder.closest('.status-column');
            if (newColumn) {
                const newStatus = newColumn.dataset.status;

                // Only trigger update if status changed or moved columns
                // (For full reordering, we'd always trigger, but let's start with status)
                const oldStatus = activeCard.dataset.status;
                activeCard.dataset.status = newStatus;

                // Send persistence request
                const projectId = activeCard.dataset.id;

                // We use fetch here for simplicity, or we could trigger an htmx event
                const formData = new FormData();
                formData.append('status', newStatus);

                fetch(`/project/${projectId}`, {
                    method: 'PATCH',
                    body: formData
                }).then(async response => {
                    if (response.ok) {
                        const html = await response.text();
                        // Create a temporary element to parse the HTML
                        const temp = document.createElement('div');
                        temp.innerHTML = html;
                        const newCard = temp.firstElementChild;

                        // Replace the old card with the new one while keeping the reference for animation if needed
                        // Actually, it's safer to wait until animation is done, but the user wants immediate feedback
                        if (activeCard) {
                            activeCard.innerHTML = newCard.innerHTML;
                            activeCard.dataset.status = newCard.dataset.status;
                            // Process HTMX for new content
                            if (window.htmx) htmx.process(activeCard);
                        }

                        // Trigger global timeline update
                        document.body.dispatchEvent(new Event('timeline-updated'));
                    } else {
                        console.error('Update failed');
                    }
                }).catch(err => console.error('Network error', err));
            }
        }

        // 2. Animation & Reset
        const placeholderRect = placeholder.getBoundingClientRect();

        activeCard.style.transition = 'top 0.2s cubic-bezier(0.34, 1.56, 0.64, 1), left 0.2s cubic-bezier(0.34, 1.56, 0.64, 1)';
        activeCard.style.top = `${placeholderRect.top}px`;
        activeCard.style.left = `${placeholderRect.left}px`;
        activeCard.style.transform = 'none';

        // Defined cleanup function
        const performCleanup = () => {
            if (!activeCard) return; // Already cleaned?

            activeCard.classList.remove('is-dragging');
            activeCard.style = ""; // Nuke all inline styles

            // Swap placeholder with real card
            if (placeholder && placeholder.parentNode) {
                placeholder.parentNode.insertBefore(activeCard, placeholder);
                placeholder.remove();
            }

            activeCard = null;
            placeholder = null;
        };

        // 3. Race Condition Safety
        let isCleaned = false;
        const safeCleanup = () => {
            if (isCleaned) return;
            isCleaned = true;
            performCleanup();
            updateColumnCounts(); // Update counts after operation
            document.body.classList.remove('is-moving-card');
        };

        activeCard.addEventListener('transitionend', safeCleanup, { once: true });
        // Fallback if transition fails or is interrupted
        setTimeout(safeCleanup, 250);
    }

    function updateColumnCounts() {
        const columns = document.querySelectorAll('.status-column');
        columns.forEach(col => {
            // Count cards that are not placeholders and not dragging
            const cards = col.querySelectorAll('.project-card:not(.is-dragging)');
            const countBadge = col.querySelector('.column-header .badge-count');
            if (countBadge) {
                countBadge.textContent = cards.length;
            }
        });
    }

    // Listen for external updates (like deletion)
    document.body.addEventListener('project-updated', updateColumnCounts);

    // Run once on init to be safe
    updateColumnCounts();
}
