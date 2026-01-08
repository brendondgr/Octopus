# Octopus Application Plan

## 1. Project Overview

**Octopus** is a "Project Manager/Organizer" designed to help users manage Projects and Goals with a visual, interactive interface. Its core philosophy is to categorize work into "Projects" containing individual "Goals," all visualized with timelines and deadlines.

## 2. Tech Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML5, Vanilla CSS (Variables-based design system), Vanilla JavaScript
- **Interactivity**: HTMX (for server-side state updates without full reloads)
- **Data & Logic**: Python for business logic and numerical computations (timelines, durations).
- **Database**: SQLite (Simple, file-based persistence recommended for this scale).

## 3. Directory Structure

We will adapt the existing `web/` directory to serve as the main application package.

```text
Octopus/
├── app.py                  # Application Entry Point
├── config.py               # Configuration (Secret keys, DB path)
├── requirements.txt        # Python Dependencies
├── utils/                  # Helper utilities (Date calculations, custom logic)
├── docs/                   # Documentation
│   ├── application.md      # This file
│   ├── plans.md            # Implementation Plans
│   └── ui.md               # UI Design System
└── web/                    # Main Application Package
    ├── __init__.py         # App Factory
    ├── routes.py           # Route definitions
    ├── models.py           # Database models and Logic
    ├── static/
    │   ├── css/
    │   │   ├── variables.css # Defined in ui.md
    │   │   └── main.css      # Core styles
    │   ├── js/
    │   │   ├── app.js        # General interactions
    │   │   └── drag_drop.js  # Drag and drop logic
    │   └── img/
    └── templates/
        ├── base.html       # Base layout
        ├── index.html      # Main Dashboard
        └── components/     # Reusable fragments
            ├── project_card.html
            ├── goal_item.html
            └── modals/
```

## 4. Key Features & Logic

### Data Models

1.  **Project**

    - `id`: Unique Identifier
    - `title`: String
    - `description`: String
    - `status`: Enum (Active, Completed, On-Hold, Abandoned) - _Derived from Goals or set manually? (To be defined in logic)_
    - `date_created`: Timestamp
    - `deadline`: Timestamp (Optional)
    - `order_index`: Integer (For drag-and-drop positioning)

2.  **Goal**
    - `id`: Unique Identifier
    - `project_id`: Foreign Key
    - `title`: String
    - `status`: Enum (Pending, Completed, On-Hold, Abandoned)
    - `date_created`: Timestamp
    - `date_completed`: Timestamp (For duration calculation)
    - `deadline`: Timestamp (Optional)

### Core Logic

- **Duration Calculation**: Python logic to calculate "Days to Complete" based on `date_created` vs `date_completed`.
- **Timeline Visualization**: Calculate weekly breakdowns of completed tasks for the visualization chart.

## 5. UI/UX Strategy

- **Drag-and-Drop**: Implemented via a custom **Pointer Events** system (rather than the native HTML5 API) to ensure "zero-ghosting" and maximum smoothness.
  - **Grip Handle**: Interactions are restricted to a specific `|||` drag-handle on each card to prevent accidental moves.
  - **Physics**: Uses CSS transitions and absolute positioning for high-fidelity "lifting" and "snapping" effects.
- **Status Dashboard**: The interface is divided into **4 separate areas** (Active, Completed, On-Hold, Abandoned).
  - **Visual Clarity**: Each column features a unique, distinct background color and border accent to prevent categorization confusion.
- **HTMX Integration**:
  - Clicking a "Checkmark" sends a POST request to update status and swaps the specific Goal HTML element (Planned).
  - Dragging a card will eventually send a PATCH request to update its status/order in the database.
  - Modals fetch dynamic content via GET requests (Planned).
- **Design System**: Strict adherence to `@docs/ui.md`.
