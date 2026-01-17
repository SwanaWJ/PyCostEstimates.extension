# PyCostEstimates (pyRevit Extension)

**PyCostEstimates** is a **pyRevit extension** that automates **quantity takeoff, material costing, and Bill of Quantities (BOQ) generation** directly inside **Autodesk Revit**.

Instead of relying on manual takeoff, schedules, and spreadsheets, costs are **calculated directly from the model**, kept **consistent**, and **exported in a single workflow**.

![Demo GIF](assets/PyCostEstimates_Demo.gif)

---

## What This Extension Does (In Simple Terms)

- Adds a **PyCostEstimates** tab to the Revit ribbon
- Reads quantities directly from the model
- Applies material and unit costs automatically
- Generates BOQs and material schedules ready for tendering and procurement
- Keeps family and material costs consistent across the project

---

## PyCostEstimates Ribbon Overview

After installation, you will see a new ribbon tab:

**PyCostEstimates**

The tools are grouped into logical panels:

### 1. Setup and Validation
- **Create Parameters**
- **Type Consistency Check**

### 2. Cost Definition
- **Edit Material Unit Costs**
- **Edit Material Buildup**
- **Rename Family Types**
- **Search Family Type**

### 3. Cost Calculation
- **Apply Rate**
- **Compute Amount**

### 4. BOQ and Export
- **BOQ Description**
- **Export BOQ**
- **Preview Total**
- **Export Material Schedule**

---

## Recommended Workflow (End-to-End)

Follow these steps **in order** for best results.

---

## Step 1 - Create Required Parameters

**Button:** Create Parameters

This creates all shared parameters required for costing, such as:
- Unit Rate
- Amount
- Material Cost
- BOQ Description

> Run this **once per project** (or when loading new families).

---

## Step 2 - Ensure Family Type Consistency

**Button:** Type Consistency Check

This tool:
- Checks that families follow naming and typing rules
- Prevents duplicate or mismatched cost entries
- Avoids BOQ errors later

> Strongly recommended before applying costs.

---

## Step 3 - Edit Material Unit Costs

**Button:** Edit Material Unit Costs

This opens the CSV-based pricing database.

### How it works
- Each material has a unit rate (m^2 / m^3 / No.)
- Costs are stored in CSV files
- Families are mapped to materials by name

Edit the CSV -> Save -> Re-run cost tools.

---

## Step 4 - Define Composite Costs (Material Buildup)

**Button:** Edit Material Buildup

This is where **recipes** live.

### Example: Concrete

Concrete is calculated from:
- Cement
- Quarry dust
- Crushed stones
- Water
- Labor

You define these once, and the extension calculates the **final composite rate automatically**.

> This is the key feature that eliminates manual rate analysis.

---

## Step 5 - Rename and Manage Family Types (Optional but Powerful)

- **Rename Family Types** - standardize naming for cost matching
- **Search Family Type** - quickly locate families across the project

This ensures:
- CSV material names match Revit families
- Costs apply correctly without manual overrides

---

## Step 6 - Apply Rates to the Model

**Button:** Apply Rate

This step:
- Reads material and recipe data
- Writes unit rates into the model
- Applies rates per category (walls, slabs, columns, etc.)

No schedules required.

---

## Step 7 - Compute Amounts

**Button:** Compute Amount

This step:
- Multiplies **quantity x unit rate**
- Writes final amounts into parameters
- Prepares the model for BOQ export

> This is where the actual money gets calculated.

---

## Step 8 - Generate BOQ and Totals

### BOQ Description
Adds readable descriptions per item.

### Export BOQ
Exports a clean Excel BOQ containing:
- Item
- Description
- Unit
- Quantity
- Rate
- Amount

### Preview Total
Shows the grand total cost directly in Revit.

### Export Material Schedule
Exports material-level schedules for auditing or procurement.

---

## Quick Start (Sample Project)

1. Open:
assets/Sample test project.rvt

2. Run the tools in this order:
1. Create Parameters
2. Apply Rate
3. Compute Amount
4. Export BOQ

Your BOQ is generated in **minutes, not hours**.

---

## Supported Revit Categories

| Category               | Unit    |
|------------------------|---------|
| Structural Foundations | m^3     |
| Structural Columns     | m^3 / m |
| Structural Framing     | m       |
| Structural Rebar       | m       |
| Blockwork Walls        | m^2     |
| Roofs                  | m^2     |
| Wall Finishes          | m^2     |
| Floor Finishes         | m^2     |
| Doors                  | No.     |
| Windows                | No.     |
| Electrical             | No. / m |
| Plumbing               | No. / m |

---

## Installation

1. Install **pyRevit**  
https://github.com/eirannejad/pyRevit/releases

2. Download this repository:  
https://github.com/SwanaWJ/pyrevit-CostEstimates/archive/refs/heads/main.zip

3. In Revit -> **pyRevit tab** -> left-most drop-down  
4. Open **Settings**  
5. Click **Add Folder** -> select `pyrevit-CostEstimates`  
6. Click **Save Settings** -> **Reload**

You will now see **PyCostEstimates** in the Revit ribbon.

---

## License

MIT License (c) 2025 Swana WJ
