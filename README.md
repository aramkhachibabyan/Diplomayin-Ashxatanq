# 🍷 Wine Production Optimization (CVXPY · MIQP)

This repository contains a **Mixed-Integer Quadratic Programming (MIQP)** solver for optimizing wine production using **CVXPY**.  
The model determines the optimal production levels of standard and premium wines while maximizing profit under multiple real-world constraints.

The solver accounts for:

- Revenue generation  
- Market saturation (quadratic diminishing returns)  
- Variable production costs  
- Fixed startup costs for premium wines  
- Resource usage limits  
- Logical constraints via Big-M  
- Integer and binary decision variables  

The entire system is **fully interactive** — all inputs are entered by the user at runtime.

---

## 📌 Features

- ✔️ Mixed Integer Quadratic Programming (MIQP)  
- ✔️ Handles integer production quantities (`X`)  
- ✔️ Handles binary premium-wine decisions (`Y`)  
- ✔️ Big-M based activation constraints  
- ✔️ Resource consumption limits  
- ✔️ Full profit breakdown (revenue, variable cost, fixed cost)  
- ✔️ Resource utilization report  
- ✔️ Automatic solver fallback:
  - GLPK_MI → SCIP → default CVXPY solver  

---

## 🧮 Mathematical Model

### **Decision Variables**

| Variable | Type | Description |
|----------|--------|-------------|
| `X[i]` | Integer | Production quantity of wine *i* |
| `Y[j]` | Boolean | Whether premium wine *j* is produced |

---

### **Objective Function**

Maximize total profit:

\[
\sum_i (A_i X_i - B_i X_i^2 - C_i X_i) - \sum_j (F_j Y_j)
\]

Where:

- \( A_i \) — linear revenue  
- \( B_i \) — quadratic market saturation coefficient  
- \( C_i \) — variable cost  
- \( F_j \) — fixed startup cost for premium wine  

---

### **Constraints**

#### 1. Non-negativity
\[
X_i \ge 0
\]

#### 2. Resource limits  
For each resource type \( k \):

\[
\sum_i r_{k,i} X_i \le R_k
\]

#### 3. Big-M premium logic  
Premium wines can be produced only if their binary decision is active:

\[
X_i \le M \cdot Y_j
\]

---

## 📥 Input Requirements

The program asks the user to input:

- Number of standard wines  
- Number of premium wines  
- Linear revenue coefficients (A)  
- Quadratic coefficients (B)  
- Variable cost coefficients (C)  
- Fixed premium wine costs (F)  
- Number of resource types  
- Resource availability vector (R)  
- Resource consumption matrix (r)  
- Big-M constant  

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/<your-username>/<repo-name>.git
cd <repo-name>
