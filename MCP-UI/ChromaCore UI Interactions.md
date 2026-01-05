# ChromaCore 3D Visualizer: Interaction Guide

This document outlines the controls and interactive behaviors of the **Semantic Stack Visualizer**. The interface allows users to explore the 3D color geometry, manage the semantic stack, and assign concepts to specific spatial zones.

## 1. 3D Workspace Navigation

The central canvas displays a 10,000-point L*a*b* point cloud representing the available semantic anchors.

- **Rotate View:** Click and drag anywhere in the 3D space to orbit the camera around the center.
  
  - *Horizontal Drag:* Rotates around the azimuth.
  
  - *Vertical Drag:* Adjusts the elevation.

- **Zoom:** Use the mouse scroll wheel to move closer to the core or further out to see the entire shell.

- **Auto-Rotation:** The cloud slowly rotates when idle to visualize depth. Interaction stops this rotation immediately.

## 2. Bi-Directional Highlighting

The system links the sidebar list and the 3D cloud, but with specific directional behaviors to prevent interface "jumping."

- **Sidebar to 3D (Locate):**
  
  - **Action:** Hover your mouse over any row in the **Sidebar List**.
  
  - **Result:** A **white crosshair target** instantly appears on that specific node in the 3D space. This helps you visualize where a specific ID or hashtag lives spatially.

- **3D to Tooltip (Inspect):**
  
  - **Action:** Hover your mouse over any dot in the **3D Cloud**.
  
  - **Result:** A floating tooltip appears next to your cursor displaying the node's **Hashtag** (if assigned), **ID**, **Color**, and **Zone**.
  
  - **Note:** This does **not** auto-scroll the sidebar list. This interaction is purely for inspecting the cloud without losing your place in the list.

## 3. Sidebar: Smart Assigner

Located at the top of the sidebar, the **Quick Assign** panel allows for rapid population of the semantic stack.

- **Zone Selector:** Choose which spatial region to target:
  
  - **Core:** The dense center (Red).
  
  - **Mid:** The habitable region (Green).
  
  - **Outer:** The sparse outlier shell (Blue).

- **Assigning a Tag:**
  
  1. Select a zone (e.g., "Mid").
  
  2. Type a concept name in the input field (e.g., `#python`).
  
  3. Click the **+ button** or press **Enter**.
  
  4. The system automatically finds the **next available empty slot** in that zone, assigns the tag, scrolls the list to that position, and flashes the row to confirm.

## 4. Sidebar: Search & List

The main list manages the 10,000 anchors.

- **Search:** Filter the list by typing an ID (e.g., "500") or a hashtag string (e.g., "py").

- **Visual Status:**
  
  - **Assigned Slots:** Show the hashtag clearly.
  
  - **Empty Slots:** Display a dimmed placeholder.
  
  - **Zone Badges:** Each item is tagged with its zone (CORE, MID, OUT) for quick context.

## 5. Quick Jump Navigation

The bottom **Stats Bar** acts as a rapid navigation tool.

- **Click "● Core":** Instantly jumps the list view to the beginning of the Core zone.

- **Click "● Mid":** Instantly jumps to the start of the Mid Zone (Habitable Zone).

- **Click "● Outer":** Instantly jumps to the start of the Outer Band.

These buttons allow you to traverse the vast 10,000-item dataset instantly without manual scrolling.
