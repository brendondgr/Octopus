document.addEventListener('DOMContentLoaded', () => {
    console.log('Octopus App Initialized');

    // Initialize Drag and Drop if available
    if (typeof initDragAndDrop === 'function') {
        initDragAndDrop();
    }

    // Initialize Tabs
    initTabs();

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

    // Re-initialize tabs when modals are loaded via HTMX
    document.body.addEventListener('htmx:afterSwap', (evt) => {
        if (evt.target.id === 'modal-container') {
            initTabs(evt.target);
        }

        // Goal insertion reordering: ensure new goals appear before completed goals
        const goalsList = evt.target.closest?.('.goals-list');
        if (goalsList && evt.detail?.requestConfig?.verb === 'post') {
            const allGoals = goalsList.querySelectorAll('.goal-item');
            if (allGoals.length > 0) {
                const newGoal = allGoals[allGoals.length - 1]; // Last added (appended via beforeend)

                // Only reorder if the new goal is not completed
                if (newGoal && !newGoal.classList.contains('completed')) {
                    // Find first completed goal
                    const firstCompleted = goalsList.querySelector('.goal-item.completed');
                    if (firstCompleted) {
                        goalsList.insertBefore(newGoal, firstCompleted);
                    }
                }
            }
        }
    });
});


/**
 * Initialize tab interfaces
 * @param {HTMLElement} container - Optional container to scope tab init
 */
function initTabs(container = document) {
    const tabInterfaces = container.querySelectorAll('.tab-interface');

    tabInterfaces.forEach(tabInterface => {
        const buttons = tabInterface.querySelectorAll('.tab-button');

        buttons.forEach(button => {
            button.addEventListener('click', (e) => {
                const tabName = e.currentTarget.dataset.tab;
                switchTab(tabName, tabInterface);
            });
        });
    });

    // Restore saved states
    restoreTabStates(container);
}


/**
 * Switch to a specific tab
 * @param {string} tabName - The data-tab value to switch to
 * @param {HTMLElement} tabInterface - The tab interface container
 */
function switchTab(tabName, tabInterface) {
    // For dashboard tabs (likely in header), look in the main content area
    // Otherwise look within the parent (for modals)
    const isDashboard = tabInterface.dataset.group === 'dashboard';
    const contentArea = isDashboard ? document.querySelector('main.container') : tabInterface.parentElement;

    if (!contentArea) return;

    // Update button states
    const buttons = tabInterface.querySelectorAll('.tab-button');
    buttons.forEach(btn => {
        btn.classList.toggle('active', btn.dataset.tab === tabName);
    });

    // Update content visibility
    const contents = contentArea.querySelectorAll('.tab-content');
    contents.forEach(content => {
        const isActive = content.dataset.tab === tabName;
        content.classList.toggle('active', isActive);

        // Load timeline data when switching to timeline tab
        if (isActive && tabName.includes('timeline')) {
            loadTimelineForTab(content);
        }
    });

    // Persist tab state
    sessionStorage.setItem(`tab-${getTabGroupId(tabInterface)}`, tabName);
}


/**
 * Load timeline data for a tab that contains a Gantt container
 * @param {HTMLElement} tabContent - The tab content element
 */
function loadTimelineForTab(tabContent) {
    const ganttContainer = tabContent.querySelector('.gantt-container');
    if (!ganttContainer) return;

    const containerId = ganttContainer.id;
    const projectId = ganttContainer.dataset.projectId;

    // Check if already loaded
    if (ganttContainer.dataset.loaded === 'true') return;

    // Initialize and load
    if (typeof initTimelineOnTabSwitch === 'function') {
        initTimelineOnTabSwitch(containerId, projectId || null);
        ganttContainer.dataset.loaded = 'true';
    }
}


/**
 * Get a unique identifier for a tab group
 * @param {HTMLElement} tabInterface - The tab interface element
 * @returns {string} Unique identifier
 */
function getTabGroupId(tabInterface) {
    if (tabInterface.dataset.group) return tabInterface.dataset.group;

    // Try to get from modal context
    const modal = tabInterface.closest('.modal');
    if (modal) {
        const projectId = modal.querySelector('[data-project-id]')?.dataset.projectId;
        return projectId ? `modal-${projectId}` : 'modal';
    }
    return 'dashboard';
}


/**
 * Restore tab states from sessionStorage
 * @param {HTMLElement} container - Scoped container
 */
function restoreTabStates(container = document) {
    const tabInterfaces = container.querySelectorAll('.tab-interface');
    tabInterfaces.forEach(tabInterface => {
        const groupId = getTabGroupId(tabInterface);
        const savedTab = sessionStorage.getItem(`tab-${groupId}`);
        if (savedTab) {
            switchTab(savedTab, tabInterface);
        }
    });
}

