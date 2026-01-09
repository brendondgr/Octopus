# Logic & Implementation Plans

This document details the step-by-step plans to build **Octopus**. We will follow an iterative approach: **first building the visual "Frontend" with mock data**, then **connecting the "Backend" logic** to make it functional.

## Plan #1: Skeleton, Design System, & Mock Dashboard

**Goal**: Get the application running with the full "Vibrant UI" and interactive "Drag-and-Drop" interface using **mock data**.

1.  **Infrastructure**:
    - Setup Flask app structure (`app.py`, `web/__init__.py`).
    - Create `config.py` and `requirements.txt`.
2.  **Design System**:
    - Implement `web/static/css/variables.css` (Colors/Fonts from `ui.md`).
    - Implement `web/static/css/main.css` (Global styles).
    - Add Google Fonts to `base.html`.
3.  **UI Components (Mock Data)**:
    - Create `project_card.html` template.
    - Create `index.html` route in Flask that passes a list of **Hardcoded Mock Projects** to the template.
    - Render the Dashboard with these mock cards.
4.  **Interactivity**: - Implement `drag_drop.js` to allow dragging cards around (visual only, no saving). - Add the "New Project" button (visual only).
    **Deliverable**: A fully styled, clickable dashboard where you can drag cards, but data resets on reload.

## Plan #2: Project Persistence (The "Projects" Backend)

**Goal**: Replace mock projects with a real Database and implement Project creation.

1.  **Database**:
    - Create `web/models.py` with the **Project** model.
    - Initialize SQLite DB.
2.  **Read**:
    - Update `web/routes.py` to fetch _real_ projects from the DB instead of mock data.
3.  **Create**:
    - Implement the "New Project" Modal.
    - Add logic to save the new project to DB via HTMX.
4.  **Update (Drag & Drop)**: - Connect `drag_drop.js` to a backend route to save the new card order/status.
    **Deliverable**: You can create projects and move them around, and they persist after refresh.

## Plan #3: Goal Logic & Details (The "Goals" Backend)

**Goal**: Make the Project Details Modal functional with Goals.

1.  **Database**:
    - Add **Goal** model to `web/models.py`.
2.  **UI/Interaction**:
    - Create the "Project Details" Modal template (pop-up).
    - Implement the `GET /project/<id>` route to return this modal.
3.  **Goal Management**: - Implement "Add Goal" form (HTMX). - Implement "Toggle Completion" (Checkmark logic with HTMX). - Implement "Delete/Abandon" actions.
    **Deliverable**: Clicking a project opens a modal where you can fully manage its goals.

## Plan #4: Timelines & Numerical Logic

**Goal**: Implement the visualization and deep statistics.

1.  **Logic**:
    - Implement Python logic in `web/models.py` (or `utils/`) to calculate:
      - Task duration (`date_completed` - `date_created`).
      - Weekly completion counts.
2.  **UI/Visualization**: - Create a "Timeline" section on the Dashboard or Modal. - Render a simple chart (CSS-based or lightweight JS) showing "Goals Completed per Week".
    **Deliverable**: Visual feedback on productivity and time tracking.

## Plan #5: Deadlines & Polish

**Goal**: Feature complete & visual refinement.

1.  **Deadlines**:
    - Add `deadline` fields to Models (if not already added) and Forms.
    - Add visual cues (Time remaining, "Overdue" red styling).
2.  **Refinement**: - Review against `docs/ui.md` for any missing polish (Translucency, Shadows). - Ensure mobile responsiveness.
    **Deliverable**: The final, polished "Octopus" application.

## Plan #6: Edit Functionality (Projects & Goals)

**Goal**: Enable full editing capabilities for both Projects and Goals, allowing users to modify all attributes after creation.

1.  **Project Editing**:
    - Add "Edit" button/icon to `project_card.html` template.
    - Create `edit_project.html` modal template (or extend `new_project.html` to handle both create/edit modes).
    - Implement `GET /project/<id>/edit` route to return the edit form with pre-populated data.
    - Implement `POST /project/<id>/edit` route to update project fields (name, description, deadline, status, etc.) in the database.
    - Integrate HTMX for seamless form submission and card refresh without full page reload.
2.  **Goal Editing**:
    - Add "Edit" button/icon to `goal_item.html` template within the Project Details modal.
    - Create inline editing or modal editing for goals (allow editing name, description, deadline, priority, etc.).
    - Implement `GET /goal/<id>/edit` route to return the edit form.
    - Implement `POST /goal/<id>/edit` route to update goal fields in the database.
    - Ensure edited goals refresh in the Project Details modal via HTMX.
3.  **UI/UX Considerations**:
    - Add visual indicators (edit icons, hover states) to show editable elements.
    - Implement form validation for edited fields (match create validation).
    - Add "Cancel" functionality to exit edit mode without saving.
    - Ensure edit modals/forms match the design system from `docs/ui.md`.
4.  **Backend Updates**:
    - Update `web/models.py` methods if needed to support partial updates.
    - Add proper error handling for edit operations (e.g., project/goal not found).
    - Ensure database transactions are handled correctly for updates.
    **Deliverable**: Users can edit any project or goal attribute (name, description, deadline, etc.) with a seamless, intuitive interface that persists changes immediately.