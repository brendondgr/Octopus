/**
 * Timeline.js - Gantt Chart Timeline Renderer
 * Handles rendering and interactivity for Gantt-style timeline visualizations
 */

class TimelineRenderer {
    constructor(containerId, options = {}) {
        this.containerId = containerId;
        this.container = document.getElementById(containerId);
        this.options = {
            barHeight: 24,
            barSpacing: 8,
            labelWidth: 200,
            minBarWidth: 4,
            dayWidth: 40,
            ...options
        };
        this.data = null;
        this.zoomLevels = ['day', 'week', 'month'];
        this.currentZoomIndex = 1; // Start at 'week'
        this.expandedProjects = new Set(); // Track which projects are expanded

        if (this.container) {
            this.init();
        }
    }

    init() {
        this.axisContainer = document.getElementById(`${this.containerId}-axis`);
        this.bodyContainer = document.getElementById(`${this.containerId}-body`);
        this.labelsContainer = document.getElementById(`${this.containerId}-labels`);
        this.tooltipElement = document.getElementById(`${this.containerId}-tooltip`);

        this.attachEventListeners();
    }

    attachEventListeners() {
        // Zoom controls
        const zoomButtons = this.container.querySelectorAll('.btn-zoom');
        zoomButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                const action = e.currentTarget.dataset.action;
                this.handleZoom(action);
            });
        });

        // Filter toggle
        const filterToggle = this.container.querySelector('.btn-filter-toggle');
        if (filterToggle) {
            filterToggle.addEventListener('click', () => this.toggleFilterPanel());
        }

        // Filter checkboxes
        const filterCheckboxes = this.container.querySelectorAll('.gantt-filter-panel input[type="checkbox"]');
        filterCheckboxes.forEach(checkbox => {
            checkbox.addEventListener('change', () => this.handleFilterChange());
        });
    }

    async loadData(endpoint) {
        try {
            const response = await fetch(endpoint);
            if (!response.ok) throw new Error('Failed to fetch timeline data');
            this.data = await response.json();

            // Initialize expanded projects with all project IDs on first load
            if (this.expandedProjects.size === 0 && this.data.items) {
                this.data.items.forEach(item => {
                    if (item.type === 'project') this.expandedProjects.add(item.id.toString());
                });
            }

            this.render();
        } catch (error) {
            console.error('Timeline load error:', error);
            this.showError('Failed to load timeline data');
        }
    }

    render() {
        if (!this.data || !this.data.items || this.data.items.length === 0) {
            this.showEmptyState();
            return;
        }

        this.updateZoomDisplay();
        this.renderDateAxis();
        this.renderItems();
    }

    renderDateAxis() {
        if (!this.axisContainer) return;

        const { dateAxis } = this.data;

        // Calculate axis width based on date range
        const dayWidth = this.getDayWidth();
        const totalDays = this.getTotalDays();
        const axisWidth = totalDays * dayWidth;

        let html = '<div class="gantt-axis-inner" style="width: ' + axisWidth + 'px;">';

        dateAxis.forEach((tick, index) => {
            const position = index * (axisWidth / dateAxis.length);
            html += `<div class="gantt-axis-tick" style="left: ${position}px;">
                <span class="axis-label">${tick.label}</span>
            </div>`;
        });

        html += '</div>';
        this.axisContainer.innerHTML = html;
        this.axisContainer.querySelector('.gantt-axis-inner').style.minWidth = axisWidth + 'px';
    }

    renderItems() {
        if (!this.bodyContainer || !this.labelsContainer) return;

        const { items, minDate, maxDate } = this.data;
        const dayWidth = this.getDayWidth();
        const totalDays = this.getTotalDays();
        const barAreaWidth = totalDays * dayWidth;

        const minDateTime = new Date(minDate).getTime();
        const maxDateTime = new Date(maxDate).getTime();
        const totalMs = maxDateTime - minDateTime;

        let labelsHtml = '';
        let bodyHtml = '';

        // Sort items: projects first, then goals grouped by project
        const sortedItems = this.sortItems(items);

        sortedItems.forEach((item) => {
            const isProject = item.type === 'project';
            const isGoal = item.type === 'goal';

            // Determine visibility based on expansion state
            let isHidden = false;
            if (isGoal && item.project_id) {
                isHidden = !this.expandedProjects.has(item.project_id.toString());
            }

            const hiddenClass = isHidden ? ' hidden' : '';
            const rowClass = (isProject ? 'gantt-row project-row' : 'gantt-row goal-row') + hiddenClass;
            const barClass = this.getBarClass(item);

            // Calculate bar position and width
            const startDate = item.start_date ? new Date(item.start_date) : new Date(minDate);
            const endDate = item.end_date ? new Date(item.end_date) : new Date();

            const startPos = ((startDate.getTime() - minDateTime) / totalMs) * barAreaWidth;
            const endPos = ((endDate.getTime() - minDateTime) / totalMs) * barAreaWidth;
            const barWidth = Math.max(endPos - startPos, this.options.minBarWidth);

            // Labels Column
            labelsHtml += `
                <div class="gantt-label ${isProject ? 'project-label' : 'goal-label'}${hiddenClass}" data-item-id="${item.id}">
                    ${isProject ? `
                        <button class="btn-toggle-expand ${this.expandedProjects.has(item.id.toString()) ? '' : 'collapsed'}" 
                                onclick="timelineManager.toggleExpansion(event, '${this.containerId}', '${item.id}')">
                            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="6 9 12 15 18 9"></polyline>
                            </svg>
                        </button>
                    ` : ''}
                    <span class="label-text" onclick="timelineManager.handleItemClick(event, '${this.containerId}', '${item.id}', '${item.type}')" title="${item.name}">
                        ${this.truncateText(item.name, 25)}
                    </span>
                </div>
            `;

            // Timeline Body
            bodyHtml += `
                <div class="${rowClass}" data-item-id="${item.id}" style="width: ${barAreaWidth}px;">
                    <div class="gantt-bar-area">
                        <div class="${barClass}" 
                             style="left: ${startPos}px; width: ${barWidth}px;"
                             data-item='${JSON.stringify(item)}'
                             onmouseenter="timelineManager.showTooltip(event, '${this.containerId}')"
                             onmouseleave="timelineManager.hideTooltip('${this.containerId}')"
                             onclick="timelineManager.handleItemClick(event, '${this.containerId}', '${item.id}', '${item.type}')">
                            ${isProject ? `<span class="bar-label">${item.name}</span>` : ''}
                        </div>
                    </div>
                </div>
            `;
        });

        this.labelsContainer.innerHTML = labelsHtml;
        this.bodyContainer.innerHTML = bodyHtml || this.getEmptyStateHtml();

        // Set min-width for body rows to ensure scroll works
        this.bodyContainer.querySelectorAll('.gantt-row').forEach(row => {
            row.style.minWidth = barAreaWidth + 'px';
        });
    }

    toggleExpansion(projectId) {
        projectId = projectId.toString();
        if (this.expandedProjects.has(projectId)) {
            this.expandedProjects.delete(projectId);
        } else {
            this.expandedProjects.add(projectId);
        }
        this.renderItems();
    }

    sortItems(items) {
        // Group goals by project
        const projects = items.filter(i => i.type === 'project');
        const goals = items.filter(i => i.type === 'goal');

        const sorted = [];
        projects.forEach(project => {
            sorted.push(project);
            goals.filter(g => g.project_id === project.id).forEach(goal => {
                sorted.push(goal);
            });
        });

        // Add any orphan goals
        goals.filter(g => !projects.find(p => p.id === g.project_id)).forEach(goal => {
            sorted.push(goal);
        });

        return sorted;
    }

    getBarClass(item) {
        let classes = ['gantt-item'];
        const isProject = item.type === 'project';
        classes.push(isProject ? 'gantt-item-project' : 'gantt-item-goal');
        classes.push(`cat-${item.category_color || 'blue'}`);

        // Status classes
        if (item.status === 'Completed') {
            classes.push('gantt-item-completed');
        } else if (item.status === 'Pending') {
            classes.push('gantt-item-pending');
        } else if (item.status === 'On-Hold') {
            classes.push('gantt-item-onhold');
        } else if (item.status === 'Abandoned') {
            classes.push('gantt-item-abandoned');
        }

        return classes.join(' ');
    }

    getDayWidth() {
        const zoomLevel = this.data?.zoomLevel || 'week';
        switch (zoomLevel) {
            case 'day': return 60;
            case 'week': return 40;
            case 'month': return 20;
            default: return 40;
        }
    }

    getTotalDays() {
        if (!this.data) return 30;
        const minDate = new Date(this.data.minDate);
        const maxDate = new Date(this.data.maxDate);
        return Math.max(Math.ceil((maxDate - minDate) / (1000 * 60 * 60 * 24)), 7);
    }

    handleZoom(action) {
        if (action === 'zoom-in' && this.currentZoomIndex > 0) {
            this.currentZoomIndex--;
        } else if (action === 'zoom-out' && this.currentZoomIndex < this.zoomLevels.length - 1) {
            this.currentZoomIndex++;
        } else if (action === 'fit') {
            this.currentZoomIndex = 1; // Default back to week
        }
        this.render();
    }

    getDayWidth() {
        const zoom = this.zoomLevels[this.currentZoomIndex];
        if (zoom === 'day') return 120;
        if (zoom === 'week') return 40;
        if (zoom === 'month') return 10;
        return 40;
    }

    getTotalDays() {
        if (!this.data) return 0;
        const min = new Date(this.data.minDate);
        const max = new Date(this.data.maxDate);
        return Math.ceil((max - min) / (1000 * 60 * 60 * 24)) + 1;
    }

    updateZoomDisplay() {
        const zoomLabel = this.container.querySelector('.zoom-level');
        if (zoomLabel) {
            const zoom = this.zoomLevels[this.currentZoomIndex];
            zoomLabel.textContent = zoom.charAt(0).toUpperCase() + zoom.slice(1);
        }
    }

    toggleFilterPanel() {
        const panel = this.container.querySelector('.gantt-filter-panel');
        if (panel) panel.classList.toggle('hidden');
    }

    handleFilterChange() {
        const checkboxes = this.container.querySelectorAll('.gantt-filter-panel input[type="checkbox"]');
        const filters = {
            status: [],
            type: []
        };

        checkboxes.forEach(cb => {
            if (cb.checked) {
                filters[cb.name].push(cb.value);
            }
        });

        // Trigger filtered data load
        const projectId = this.container.dataset.projectId;
        let url = projectId ? `/api/timeline/project/${projectId}` : '/api/timeline/dashboard';

        // Append filters as query params
        const params = new URLSearchParams();
        if (filters.status.length > 0) params.append('status', filters.status.join(','));
        if (filters.type.length > 0) params.append('type', filters.type.join(','));

        this.loadData(`${url}?${params.toString()}`);
    }

    showEmptyState() {
        if (this.bodyContainer) {
            this.bodyContainer.innerHTML = this.getEmptyStateHtml();
        }
        if (this.labelsContainer) {
            this.labelsContainer.innerHTML = '';
        }
        if (this.axisContainer) {
            this.axisContainer.innerHTML = '';
        }
    }

    getEmptyStateHtml() {
        return `
            <div class="gantt-empty-state">
                <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1">
                    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
                    <line x1="16" y1="2" x2="16" y2="6"></line>
                    <line x1="8" y1="2" x2="8" y2="6"></line>
                    <line x1="3" y1="10" x2="21" y2="10"></line>
                </svg>
                <p>No timeline data available</p>
            </div>
        `;
    }

    showError(message) {
        if (this.bodyContainer) {
            this.bodyContainer.innerHTML = `<div class="gantt-error">${message}</div>`;
        }
    }

    truncateText(text, length) {
        if (text.length <= length) return text;
        return text.substring(0, length) + '...';
    }
}

// Global Timeline Management
const timelineManager = {
    renderers: new Map(),

    initTimeline(containerId, options = {}) {
        if (!this.renderers.has(containerId)) {
            const renderer = new TimelineRenderer(containerId, options);
            this.renderers.set(containerId, renderer);

            // Initial data load
            const container = document.getElementById(containerId);
            const projectId = container?.dataset.projectId;
            const endpoint = projectId ? `/api/timeline/project/${projectId}` : '/api/timeline/dashboard';
            renderer.loadData(endpoint);

            // Sync vertical scroll between labels and body
            this.setupScrollSync(containerId);
        }
    },

    setupScrollSync(containerId) {
        const labelsBody = document.getElementById(`${containerId}-labels`);
        const scrollContainer = document.querySelector(`#${containerId} .gantt-scroll-container`);

        if (labelsBody && scrollContainer) {
            scrollContainer.addEventListener('scroll', () => {
                labelsBody.scrollTop = scrollContainer.scrollTop;
            });
            labelsBody.addEventListener('scroll', () => {
                scrollContainer.scrollTop = labelsBody.scrollTop;
            });
        }
    },

    toggleExpansion(event, containerId, projectId) {
        event.stopPropagation();
        const renderer = this.renderers.get(containerId);
        if (renderer) {
            renderer.toggleExpansion(projectId);
        }
    },

    showTooltip(event, containerId) {
        const renderer = this.renderers.get(containerId);
        if (!renderer || !renderer.tooltipElement) return;

        const itemStr = event.currentTarget.dataset.item;
        if (!itemStr) return;
        const item = JSON.parse(itemStr);
        const tooltip = renderer.tooltipElement;

        // Use custom formatting for dates and durations
        const startDate = this.formatDateEST(item.start_date);
        const endDate = item.end_date ? this.formatDateEST(item.end_date) : 'Ongoing';
        const durationText = this.formatDuration(item);

        tooltip.querySelector('.tooltip-type').textContent = item.type.toUpperCase();
        tooltip.querySelector('.tooltip-name').textContent = item.name;
        tooltip.querySelector('.tooltip-start').textContent = startDate;
        tooltip.querySelector('.tooltip-end').textContent = endDate;
        tooltip.querySelector('.tooltip-duration').textContent = durationText;
        tooltip.querySelector('.tooltip-status').textContent = item.status;

        // Show tooltip early to calculate its dimensions
        tooltip.style.display = 'block';
        tooltip.classList.add('visible');

        const containerRect = renderer.container.getBoundingClientRect();
        const tooltipRect = tooltip.getBoundingClientRect();

        let left = event.clientX - containerRect.left + 15;
        let top = event.clientY - containerRect.top + 15;

        // Clipping Prevention: Horizontal
        if (left + tooltipRect.width > containerRect.width) {
            left = event.clientX - containerRect.left - tooltipRect.width - 15;
        }

        // Clipping Prevention: Vertical
        if (event.clientY + tooltipRect.height > window.innerHeight) {
            top = event.clientY - containerRect.top - tooltipRect.height - 15;
        }

        // Ensure it doesn't go off the top of the container
        if (top < 0) top = 10;

        tooltip.style.left = `${left}px`;
        tooltip.style.top = `${top}px`;
    },

    formatDateEST(dateString) {
        if (!dateString) return 'N/A';
        try {
            const date = new Date(dateString);
            return date.toLocaleString('en-US', {
                timeZone: 'America/New_York',
                year: 'numeric',
                month: '2-digit',
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit',
                hour12: true
            }).replace(',', ':');
        } catch (e) {
            return dateString;
        }
    },

    formatDuration(item) {
        const start = new Date(item.start_date);
        const end = item.end_date ? new Date(item.end_date) : new Date();
        const diffMs = end - start;

        if (isNaN(diffMs) || diffMs < 0) return '0 hours';

        const diffHours = diffMs / (1000 * 60 * 60);
        const diffDays = diffHours / 24;
        const diffMonths = diffDays / 30.44; // Average month length
        const diffYears = diffDays / 365.25;

        // Scaling logic per user request:
        // Pass 24 months (2 years) -> Years
        if (diffMonths >= 24) {
            return `${diffYears.toFixed(1)} years`;
        }
        // Pass 60 days (2 months) -> Months
        if (diffDays >= 60) {
            return `${Math.floor(diffMonths)} months`;
        }
        // Pass 48 hours (2 days) -> Days
        if (diffHours >= 48) {
            return `${Math.floor(diffDays)} days`;
        }
        // Under 48 hours -> Hours
        return `${Math.floor(diffHours)} hours`;
    },

    hideTooltip(containerId) {
        const renderer = this.renderers.get(containerId);
        if (renderer && renderer.tooltipElement) {
            renderer.tooltipElement.classList.remove('visible');
            renderer.tooltipElement.style.display = 'none';
        }
    },

    handleItemClick(event, containerId, itemId, itemType) {
        event.stopPropagation();

        if (itemType === 'project') {
            // Use HTMX to open project details modal
            const tempBtn = document.createElement('button');
            tempBtn.setAttribute('hx-get', `/project/${itemId}/details`);
            tempBtn.setAttribute('hx-target', '#modal-container');
            tempBtn.setAttribute('hx-swap', 'innerHTML');
            document.body.appendChild(tempBtn);
            htmx.process(tempBtn);
            tempBtn.click();
            tempBtn.remove();
        } else if (itemType === 'goal') {
            // Find the parent project and open its details
            const renderer = this.renderers.get(containerId);
            if (renderer && renderer.data && renderer.data.items) {
                const item = renderer.data.items.find(i => i.id == itemId && i.type == 'goal');
                if (item && item.project_id) {
                    this.handleItemClick(event, containerId, item.project_id, 'project');
                }
            }
        }
    }
};

// Legacy support for app.js
function initTimelineOnTabSwitch(containerId, projectId = null) {
    timelineManager.initTimeline(containerId);
}
