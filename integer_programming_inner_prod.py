import gurobipy as gp
from gurobipy import GRB
from itertools import product

def integer_programming_k_cnf(T, clauses, inputs):
    model = gp.Model("k_cnf_ip")

    # Boolean variables F_{t,c} for each t and each clause c
    F = {}
    for t in range(1, T + 1):
        for c in clauses:
            F[t, c] = model.addVar(vtype=GRB.BINARY, name=f"F_{t}_{c}")

    # Boolean variables V_{t,x} for each t and each input vector x
    V = {}
    for t in range(1, T + 1):
        for x in inputs:
            V[t, x] = model.addVar(vtype=GRB.BINARY, name=f"V_{t}_{x}")

    # model.update()
    

    # Constraints for V_{t,x} based on the unsatisfied clauses
    for t in range(1, T + 1):
        for x in inputs:
            unsatisfied_clauses = [c for c in clauses if not clause_satisfied(c, x)]
            # print('this is x:',x)
            
            if unsatisfied_clauses:
                print(unsatisfied_clauses)
                model.addConstr((1 - V[t, x]) * len(unsatisfied_clauses) >= sum(F[t, c] for c in unsatisfied_clauses),
                            name=f"V_{t}_{x}_satisfied")
                # V_{t,x} = 0 if sum(F[t, c] for c in unsatisfied_clauses) > 0
                model.addConstr((1 - V[t, x]) <= sum(F[t, c] for c in unsatisfied_clauses), 
                            name=f"V_{t}_{x}_unsatisfied")
                

    # Additional constraints OR_{t=1,...,T} V_{t,x} = f(x) for all x
    for x in inputs:
        # print('printing inputs!!!!!!!')
        # print(x)
        # print(f(x))
        model.addConstr(gp.quicksum(V[t, x] for t in range(1, T + 1)) >= f(x),
                        name=f"OR_V_{x}_lower_bound")
        model.addConstr(gp.quicksum(V[t, x] for t in range(1, T + 1)) <= T * f(x),
                        name=f"OR_V_{x}_upper_bound")
    model.update()
    # model.display()
    print('*****model*****')

    # Objective function: minimize the total number of clauses used
    model.setObjective(gp.quicksum(F[t, c] for t in range(1, T + 1) for c in clauses), GRB.MINIMIZE)
    model.update()
    model.optimize()

    if model.status == GRB.INFEASIBLE:
        print("Model is infeasible. Computing IIS...")
        model.computeIIS()
        model.write("model.ilp")
        print("IIS written to model.ilp")
        return None, None

    if model.status == GRB.OPTIMAL:
        solution_F = { (t, c): F[t, c].x for t in range(1, T + 1) for c in clauses }
        solution_V = { (t, x): V[t, x].x for t in range(1, T + 1) for x in inputs }
        return solution_F, solution_V
    else:
        print("No optimal solution found.")
        return None, None

def clause_satisfied(clause, x):
    # Implement this function to check if a clause is satisfied by input x
    # This function should return True if the clause is satisfied by x, otherwise False
    # Assuming clause is a tuple representing literals, e.g., (1, -1, 0, 1) for (x1 OR NOT x2 OR x4)
    for i in range(len(clause)):
        if clause[i]==0:
            continue
        elif clause[i]==x[i]:
            return True
    return False

def f(x):
    x = [(i + 1) // 2 for i in x]

    # inner product
    n = len(x)
    n_half = n // 2
    sum_product = sum(x[i] * x[n_half + i] for i in range(n_half))

    return sum_product % 2

    # parity
    # n = len(x)
    # sum_product = sum(x)% 2
    # return sum_product

    # OR
    # sum_product = sum(x)
    # if sum_product>=1:
    #     return 1
    # else:
    #     return 0

def generate_k_clauses(n, k):
    all_clauses = list(product([-1, 0, 1], repeat=n))
    valid_clauses = [clause for clause in all_clauses if sum(1 for x in clause if x != 0) <= k]
    return valid_clauses

# Example usage
T = 7 # Example value for T
n = 8 # Example input length, adjust as needed 
k=2
clauses = generate_k_clauses(n, k)
print('clauses:')
print(clauses)
inputs = list(product([-1, 1], repeat=n))  # All possible input vectors

solution_F, solution_V = integer_programming_k_cnf(T, clauses, inputs)

print(clauses)
print(inputs)

# Print the solutions
# if solution_F and solution_V:
#     print("Solution F:")
#     for key, value in solution_F.items():
#         print(f"F_{key} = {value}")

#     print("Solution V:")
#     for key, value in solution_V.items():
#         print(f"V_{key} = {value}")
# else:
#     print("No solution found.")

# Print the solutions only for F with value 1
if solution_F and solution_V:
    print("Solution F (with value 1):")
    for key, value in solution_F.items():
        if value == 1:
            print(f"F_{key} = {value}")
else:
    print("No solution found.")
