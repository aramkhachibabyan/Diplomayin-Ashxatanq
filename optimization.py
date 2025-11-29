import cvxpy as cp
import numpy as np


def solve_wine_production():
    """
    Wine Production MIQP Solver using CVXPY

    Objective: Maximize Σ(A_i*X_i - B_i*X_i^2 - C_i*X_i) - Σ(F_j*Y_j)

    Much simpler than custom Branch and Bound implementation!
    CVXPY handles all the optimization internally.
    """

    print("=" * 70)
    print("WINE PRODUCTION OPTIMIZATION (CVXPY)")
    print("=" * 70)

    # ==================== DATA INPUT ====================
    n_standard = int(input("\nNumber of standard wines: "))
    n_premium = int(input("Number of premium wines: "))
    n_wines = n_standard + n_premium

    print(f"\nTotal wines: {n_wines} ({n_standard} standard + {n_premium} premium)")

    # Coefficients A (linear revenue)
    print(f"\nEnter linear coefficients A (revenue) for {n_wines} wines:")
    A = np.array([float(input(f"  A[{i + 1}]: ")) for i in range(n_wines)])

    # Coefficients B (quadratic market saturation)
    print(f"\nEnter quadratic coefficients B (market saturation) for {n_wines} wines:")
    B = np.array([float(input(f"  B[{i + 1}]: ")) for i in range(n_wines)])

    # Coefficients C (variable costs)
    print(f"\nEnter variable cost coefficients C (cost per unit) for {n_wines} wines:")
    C = np.array([float(input(f"  C[{i + 1}]: ")) for i in range(n_wines)])

    # Coefficients F (fixed costs for premium wines)
    print(f"\nEnter fixed cost coefficients F (startup cost) for {n_premium} premium wines:")
    F = np.array([float(input(f"  F[{i + 1}] (for premium wine {n_standard + i + 1}): "))
                  for i in range(n_premium)])

    # Resources
    n_resources = int(input("\nNumber of resource types: "))

    print(f"\nEnter total availability for each resource (R_k):")
    R = np.array([float(input(f"  R[{k + 1}]: ")) for k in range(n_resources)])

    # Resource consumption matrix
    print(f"\nEnter resource consumption (r_ki) - {n_resources} resources x {n_wines} wines:")
    r = []
    for k in range(n_resources):
        row = []
        print(f"Resource {k + 1}:")
        for i in range(n_wines):
            val = float(input(f"  r[{k + 1}][{i + 1}]: "))
            row.append(val)
        r.append(row)
    r = np.array(r)

    # Big-M constant
    M = float(input("\nEnter Big-M constant for premium wine constraints: "))

    print("\n" + "=" * 70)
    print("SOLVING USING CVXPY...")
    print("=" * 70 + "\n")

    # ==================== DEFINE CVXPY PROBLEM ====================

    # Decision variables
    X = cp.Variable(n_wines, integer=True)  # Production quantities (INTEGER)
    Y = cp.Variable(n_premium, boolean=True)  # Premium wine production decisions (BINARY)

    # Objective function: Maximize profit
    # Revenue: Σ(A_i*X_i - B_i*X_i^2) - Variable costs: Σ(C_i*X_i) - Fixed costs: Σ(F_j*Y_j)
    revenue = A @ X - cp.sum(cp.multiply(B, cp.square(X)))
    variable_costs = C @ X
    fixed_costs = F @ Y

    objective = cp.Maximize(revenue - variable_costs - fixed_costs)

    # Constraints
    constraints = [X >= 0]

    # 1. Non-negativity: X_i >= 0

    # 2. Resource constraints: Σ(r_ki * X_i) <= R_k
    for k in range(n_resources):
        constraints.append(r[k] @ X <= R[k])

    # 3. Big-M constraints for premium wines: X_i <= M * Y_j
    for j in range(n_premium):
        i = n_standard + j  # Index of premium wine
        constraints.append(X[i] <= M * Y[j])

    # ==================== SOLVE ====================

    problem = cp.Problem(objective, constraints)

    # Solve using GLPK_MI (free) or CPLEX/GUROBI (commercial but better)
    # CVXPY automatically selects available solver
    try:
        result = problem.solve(solver=cp.GLPK_MI, verbose=True)
    except:
        try:
            result = problem.solve(solver=cp.SCIP, verbose=True)
        except:
            try:
                result = problem.solve(verbose=True)  # Use default solver
            except Exception as ex:
                print(f"\nError: Could not solve problem. {ex}")
                print("\nTry installing a MIQP solver:")
                print("  pip install cvxopt")
                print("  or install GLPK, SCIP, or CBC")
                return

    # ==================== DISPLAY RESULTS ====================

    if problem.status not in ["optimal", "optimal_inaccurate"]:
        print(f"\nSolver Status: {problem.status}")
        print("Could not find optimal solution!")
        return

    print("\n" + "=" * 70)
    print("OPTIMAL SOLUTION FOUND")
    print("=" * 70)
    print(f"\nSolver Status: {problem.status}")
    print(f"Maximum Profit: {result:.2f} AMD")

    # Extract solution
    X_opt = X.value
    Y_opt = Y.value

    # Calculate components
    total_revenue = 0
    total_var_cost = 0
    total_fixed_cost = 0

    print("\n" + "-" * 70)
    print("PRODUCTION QUANTITIES:")
    print("-" * 70)

    for i in range(n_wines):
        wine_type = "Standard" if i < n_standard else "Premium"
        x_val = int(round(X_opt[i]))

        revenue = A[i] * x_val - B[i] * x_val ** 2
        var_cost = C[i] * x_val
        net = revenue - var_cost

        total_revenue += revenue
        total_var_cost += var_cost

        print(f"\nWine {i + 1} ({wine_type}):")
        print(f"  Production quantity: {x_val} units")
        print(f"  Revenue (A*X - B*X²): {revenue:>10.2f} AMD")
        print(f"  Variable costs (C*X): {var_cost:>10.2f} AMD")
        print(f"  Net contribution:     {net:>10.2f} AMD")

    print("\n" + "-" * 70)
    print("PREMIUM WINE DECISIONS:")
    print("-" * 70)

    for j in range(n_premium):
        i = n_standard + j
        y_val = int(round(Y_opt[j]))
        x_val = int(round(X_opt[i]))
        status = "PRODUCING" if y_val == 1 else "NOT PRODUCING"
        fixed_cost = F[j] if y_val == 1 else 0
        total_fixed_cost += fixed_cost

        print(f"\nPremium Wine {i + 1}:")
        print(f"  Decision Y[{j + 1}] = {y_val} ({status})")
        print(f"  Quantity X[{i + 1}] = {x_val} units")
        if y_val == 1:
            print(f"  Fixed cost (F*Y): {fixed_cost:>10.2f} AMD")

    print("\n" + "=" * 70)
    print("PROFIT BREAKDOWN:")
    print("=" * 70)
    print(f"Total Revenue (A*X - B*X²):      {total_revenue:>12.2f} AMD")
    print(f"  - Variable Costs (C*X):        {total_var_cost:>12.2f} AMD")
    print(f"  - Fixed Costs (F*Y):           {total_fixed_cost:>12.2f} AMD")
    print(f"  {'=' * 42}")
    print(f"  = NET PROFIT:                  {result:>12.2f} AMD")
    print("=" * 70)

    print("\n" + "-" * 70)
    print("RESOURCE UTILIZATION:")
    print("-" * 70)

    for k in range(n_resources):
        used = sum(r[k][i] * int(round(X_opt[i])) for i in range(n_wines))
        remaining = R[k] - used
        percent = (used / R[k] * 100) if R[k] > 0 else 0

        print(f"\nResource {k + 1}:")
        print(f"  Used:      {used:>10.2f} / {R[k]:.2f} ({percent:>5.1f}%)")
        print(f"  Remaining: {remaining:>10.2f}")

    print("\n" + "=" * 70)

    # Mathematical methods used
    print("\nMATHEMATICAL METHODS USED BY CVXPY:")
    print("-" * 70)
    print("1. Mixed Integer Quadratic Programming (MIQP)")
    print("2. Branch and Bound (internal)")
    print("3. Convex Optimization")
    print("4. LP Relaxation (internal)")
    print("5. Cutting Plane Methods (solver-dependent)")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        solve_wine_production()
    except KeyboardInterrupt:
        print("\n\nProgram interrupted by user.")
    except Exception as e:
        print(f"\nError: {e}")
        import traceback

        traceback.print_exc()