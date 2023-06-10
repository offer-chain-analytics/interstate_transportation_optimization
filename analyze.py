import pandas as pd
from pulp import *


def analyze(id):
    # Import Costs
    manvar_costs = pd.read_csv('./data_objects/{}/variable_costs.csv'.format(id), index_col=0)
    # Import Costs
    freight_costs = pd.read_csv('./data_objects/{}/freight_costs.csv'.format(id), index_col=0)
    # Variable Costs
    var_cost = freight_costs / 1000 + manvar_costs
    # Import Costs
    fixed_costs = pd.read_csv('./data_objects/{}/fixed_cost.csv'.format(id), index_col=0)
    # Two types of plants: Low Capacity and High Capacity Plant
    cap = pd.read_csv('./data_objects/{}/capacity.csv'.format(id), index_col=0)
    # -- Demand
    demand = pd.read_csv('./data_objects/{}/demand.csv'.format(id), index_col=0)

    countries_reader = open('./data_objects/{}/countries.txt'.format(id), "r")

    # Define Decision Variables
    loc = countries_reader.read().split(',')
    size = ['Low', 'High']

    # Initialize Class
    model = LpProblem("Capacitated Plant Location Model", LpMinimize)

    # Create Decision Variables
    x = LpVariable.dicts("production_", [(i, j) for i in loc for j in loc],
                         lowBound=0, upBound=None, cat='continuous')
    y = LpVariable.dicts("plant_",
                         [(i, s) for s in size for i in loc], cat='Binary')

    # Define Objective Function
    model += (lpSum([fixed_costs.loc[i, s] * y[(i, s)] * 1000 for s in size for i in loc])
              + lpSum([var_cost.loc[i, j] * x[(i, j)] for i in loc for j in loc]))

    # Add Constraints
    for j in loc:
        model += lpSum([x[(i, j)] for i in loc]) == demand.loc[j, 'Demand']
    for i in loc:
        model += lpSum([x[(i, j)] for j in loc]) <= lpSum([cap.loc[i, s] * y[(i, s)] * 1000
                                                           for s in size])
    # Solve Model
    model.solve()

    # Dictionnary
    dict_plant = {}
    dict_prod = {}
    for v in model.variables():
        if 'plant' in v.name:
            name = v.name.replace('plant__', '').replace('_', '')
            dict_plant[name] = int(v.varValue)
            p_name = name
        else:
            name = v.name.replace('production__', '').replace('_', '')
            dict_prod[name] = v.varValue

    # Capacity Plant
    list_low, list_high = [], []
    for l in loc:
        for cap in ['Low', 'High']:
            x = "('{}','{}')".format(l, cap)
            if cap == 'Low':
                list_low.append(dict_plant[x])
            else:
                list_high.append(dict_plant[x])
    df_capacity = pd.DataFrame({'Location': loc, 'Low': list_low, 'High': list_high}).set_index('Location')

    result_json = df_capacity.to_json()

    return result_json
