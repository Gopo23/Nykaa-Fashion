---
name: Luxe Pulse
colors:
  surface: '#131313'
  surface-dim: '#131313'
  surface-bright: '#3a3939'
  surface-container-lowest: '#0e0e0e'
  surface-container-low: '#1c1b1b'
  surface-container: '#201f1f'
  surface-container-high: '#2a2a2a'
  surface-container-highest: '#353534'
  on-surface: '#e5e2e1'
  on-surface-variant: '#e4bdc3'
  inverse-surface: '#e5e2e1'
  inverse-on-surface: '#313030'
  outline: '#ab888e'
  outline-variant: '#5b3f45'
  surface-tint: '#ffb1c1'
  primary: '#ffb1c1'
  on-primary: '#66002b'
  primary-container: '#ff4c86'
  on-primary-container: '#590025'
  inverse-primary: '#bb0054'
  secondary: '#c8c6c5'
  on-secondary: '#313030'
  secondary-container: '#4a4949'
  on-secondary-container: '#bab8b7'
  tertiary: '#00dbe9'
  on-tertiary: '#00363a'
  tertiary-container: '#00a0aa'
  on-tertiary-container: '#002f33'
  error: '#ffb4ab'
  on-error: '#690005'
  error-container: '#93000a'
  on-error-container: '#ffdad6'
  primary-fixed: '#ffd9df'
  primary-fixed-dim: '#ffb1c1'
  on-primary-fixed: '#3f0018'
  on-primary-fixed-variant: '#8f003f'
  secondary-fixed: '#e5e2e1'
  secondary-fixed-dim: '#c8c6c5'
  on-secondary-fixed: '#1c1b1b'
  on-secondary-fixed-variant: '#474646'
  tertiary-fixed: '#7df4ff'
  tertiary-fixed-dim: '#00dbe9'
  on-tertiary-fixed: '#002022'
  on-tertiary-fixed-variant: '#004f54'
  background: '#131313'
  on-background: '#e5e2e1'
  surface-variant: '#353534'
typography:
  display-lg:
    fontFamily: Outfit
    fontSize: 48px
    fontWeight: '700'
    lineHeight: 56px
    letterSpacing: -0.02em
  headline-lg:
    fontFamily: Outfit
    fontSize: 32px
    fontWeight: '600'
    lineHeight: 40px
  headline-md:
    fontFamily: Outfit
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '600'
    lineHeight: 16px
    letterSpacing: 0.05em
  data-mono:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '500'
    lineHeight: 20px
    letterSpacing: 0.01em
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 8px
  xs: 4px
  sm: 12px
  md: 24px
  lg: 40px
  xl: 64px
  gutter: 24px
  margin-page: 48px
---

## Brand & Style
The design system embodies a "High-End Data" aesthetic, merging the prestige of luxury fashion with the clinical precision of retail analytics. It is tailored for product strategists who require deep focus and rapid decision-making capabilities.

The visual style is **Glassmorphic-Professional**. It utilizes high-transparency surfaces and deep background blurs to create a sense of physical layering without visual clutter. The interface feels like a high-fidelity control deck: dark, immersive, and responsive. Subtle glowing accents and neon-tinged data points highlight critical conversion metrics, ensuring that the "Action Queues" feel urgent yet sophisticated.

## Colors
The palette is anchored by a deep obsidian background to maximize contrast for data visualization. 

- **Primary (#FC2779):** Reserved for high-priority actions (P0), active states, and critical conversion "hotspots."
- **Secondary (#121212):** Used for card backgrounds and navigation surfaces to provide subtle separation from the base background.
- **Tertiary (#00F0FF):** A "Digital Cyan" used exclusively for secondary data trends, growth indicators, and simulator handles.
- **Surface Layering:** Use `surface_glass_hex` with a `20px` backdrop blur for all modal and floating card elements to maintain the glassmorphic depth.

## Typography
This design system utilizes **Outfit** for all display and heading roles to inject a modern, geometric personality. **Inter** is used for all functional body text and data points to ensure maximum legibility at small scales.

- **Data Emphasis:** Use `data-mono` for all numerical values within simulators and tables to ensure column alignment.
- **Headlines:** Keep `display-lg` reserved for high-level dashboard summaries (e.g., Total Conversion Rate).
- **Labels:** Small labels use uppercase with tracking to differentiate them from interactive body text.

## Layout & Spacing
The layout follows a **12-column fluid grid** with generous internal margins to prevent "dashboard fatigue." 

- **Module Containers:** Cards should be grouped logically with `40px` spacing between major sections and `24px` spacing between related items.
- **Action Queues:** The Kanban-style impact simulator utilizes a `320px` fixed-width column approach with horizontal scrolling on smaller viewports.
- **Density:** Use "Comfortable" padding (`24px`) for P0 priority cards and "Compact" padding (`12px`) for secondary data lists.

## Elevation & Depth
Depth is communicated through **translucency and glow**, rather than traditional heavy shadows.

- **Level 1 (Base):** #0D0D0D (Solid).
- **Level 2 (Cards):** Surface glass with a 1px inner border (10% white) to catch the light.
- **Level 3 (Active/Hover):** Add a subtle outer glow using `primary_color_hex` with a 15px blur at 20% opacity.
- **Level 4 (Modals):** Maximum backdrop blur (40px) with a semi-transparent dark overlay to dim the background content.

## Shapes
The shape language is refined and professional. 
- **Cards & Sections:** Use `rounded-lg` (16px) to maintain a soft but structured appearance.
- **Buttons & Chips:** Use `rounded-xl` (24px) for a more tactile, "app-like" feel.
- **Simulators:** Slider handles and toggle switches should be fully circular (pill-shaped) to invite interaction.

## Components
- **Priority Cards:** P0 cards feature a 2px left-accent border in `primary_color_hex`. P1 cards use a neutral border, and P2 cards are semi-desaturated.
- **Impact Simulators:** Sliders use a `primary_color_hex` track with a glowing white handle. The "Impacted Value" should animate in real-time using `data-mono` typography.
- **Action Queues:** Kanban columns use a vertical stack of "Glass" cards. Dragging a card triggers a `tertiary_color_hex` ghost-state to indicate drop targets.
- **Input Fields:** Use "Underline" style inputs for a cleaner look, where the border only glows when focused.
- **Data Visualizations:** All charts should use gradients of Pink to Cyan. Grid lines should be minimal (opacity 5%) to keep the focus on the data trend.
- **Interactive Toggles:** Large, tactile switches that use a subtle haptic-style animation when activated.