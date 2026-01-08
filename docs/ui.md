# User Interface & Design System

This document outlines the **"Vibrant UI"** design system used across the application. The interface is designed to be modern, high-energy, and premium, balancing functional data density with a playful, interactive aesthetic.

## 🎨 Color Palette

The application uses a carefully curated color system defined in `variables.css`.

### Brand Colors

- **Primary (Electric Coral):** `#FF6B6B` — Main buttons, primary actions, and brand highlights.
- **Secondary (Deep Indigo):** `#4C3BCF` — Navigation, info states, and secondary focus.
- **Tertiary (Vivid Teal):** `#00D9C0` — Success states and teal accents.

### Neutral Base

- **Background:** `#FEFBF6` (Warm Off-White) — Avoids clinical white for a softer feel.
- **Surface:** `#FFF8F0` (Soft Cream) — Used for cards and secondary panels.
- **Elevated:** `#FFFFFF` — Pure white used for modals and floating elements.

### Categorization Tones

The application features 16 predefined color sets used for classifying various data types or categories. Each category follows a consistent three-tone implementation:

1.  **Low-opacity Background:** For the main container area.
2.  **Saturated Border:** For clear visual categorization.
3.  **High-contrast Text:** For maximum legibility.

| Name              | Background (HEX) | Border/Accent (HEX) | Text (HEX) |
| :---------------- | :--------------- | :------------------ | :--------- |
| **Yellow Orange** | `#fef3c7`        | `#f59e0b`           | `#78350f`  |
| **Yellow**        | `#fef9c3`        | `#eab308`           | `#713f12`  |
| **Orange**        | `#ffedd5`        | `#f97316`           | `#7c2d12`  |
| **Red**           | `#fee2e2`        | `#ef4444`           | `#7f1d1d`  |
| **Blue**          | `#dbeafe`        | `#3b82f6`           | `#1e3a8a`  |
| **Purple**        | `#f3e8ff`        | `#a855f7`           | `#581c87`  |
| **Teal**          | `#ccfbf1`        | `#14b8a6`           | `#134e4a`  |
| **Light Purple**  | `#ede9fe`        | `#8b5cf6`           | `#4c1d95`  |
| **Light Blue**    | `#e0f2fe`        | `#0ea5e9`           | `#0c4a6e`  |
| **Green**         | `#d1fae5`        | `#10b981`           | `#064e3b`  |
| **Black**         | `#1f2937`        | `#111827`           | `#ffffff`  |
| **Muted Gray**    | `#e2e8f0`        | `#64748b`           | `#0f172a`  |
| **Brown**         | `#fde68a`        | `#b45309`           | `#78350f`  |
| **Light Pink**    | `#fce7f3`        | `#f472b6`           | `#831843`  |
| **Kiwi**          | `#ecfccb`        | `#84cc16`           | `#365314`  |
| **Rose**          | `#ffe4e6`        | `#f43f5e`           | `#881337`  |

---

## ✨ Design Philosophy & Style Choices

### 1. Modern Typography

- **Headings:** `Space Grotesk` — A geometric typeface that provides a modern, high-tech personality.
- **Body:** `DM Sans` — Chosen for high legibility in information-dense views.
- **Mono:** `JetBrains Mono` — Used for labels, numerical values, and metadata to emphasize the data-driven focus of the interface.

### 2. Modular Glassmorphism

The app makes extensive use of transparency and depth to feel "layered":

- **Glass headers:** Uses `backdrop-filter: blur(12px)` to allow underlying content to blur beautifully as it scrolls underneath.
- **Themed Glows:** Interactive elements like the Primary Button use themed glows (e.g., `rgba(255, 107, 107, 0.3)`) on hover, making the UI feel "alive."

### 3. Soft Geometry

- **Border Radii:** Generous rounding is applied throughout (`6px` to `24px`). Modals and segmented controls use high radii to soften the technical nature of the grid.
- **Elevation:** A 5-step shadow system (`xs` to `xl`) creates clear spatial hierarchy for overlapping components like tooltips, dropdowns, and modals.

### 4. Interactive Fidelity

- **Micro-animations:** Segmented controls and toggles use "spring" bezier curves (`cubic-bezier(0.34, 1.56, 0.64, 1)`) for a snappy, responsive feel.
- **Interactive Cards:** Component cards feature a hover lift effect (`translateY(-2px)`) and a slight scale up (`1.01x`) to provide immediate feedback.

---

## 📱 Responsive Strategy

The design uses a mobile-first approach:

- **Dynamic Layouts:** Complex structures persist across breakpoints, but container minimum widths are enforced with horizontal scrolling to maintain legibility.
- **Component Swapping:** Small icon-only variants replace labelled components on smaller screens to preserve space.
- **Responsive Sizing:** CSS variables are manipulated via scripts to adjust interface density based on device width.
