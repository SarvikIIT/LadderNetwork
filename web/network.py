import matplotlib
matplotlib.use('Agg')

import re
import pandas as pd
import schemdraw
import schemdraw.elements as elm

# Read CSV files (force strings)
Z_df = pd.read_csv('Z.csv', header=None, dtype=str)
Y_df = pd.read_csv('Y.csv', header=None, dtype=str)

# Convert to lists of strings
Z = Z_df.iloc[0].astype(str).str.strip().tolist()
Y = Y_df.iloc[0].astype(str).str.strip().tolist()


SERIES_LEN = 1.6
VERT_LEN = 1.6


def parse_as_plus_b(token: str):
    t = token.replace(' ', '')
    m = re.match(r'^(?:(\d+)\*?s|s)(?:\+(\d+))?$', t)
    if m:
        a = int(m.group(1)) if m.group(1) else 1
        b = int(m.group(2)) if m.group(2) else 0
        return a, b
    m = re.match(r'^(\d+)\+(?:(\d+)\*?s|s)$', t)
    if m:
        b = int(m.group(1))
        a = int(m.group(2)) if m.group(2) else 1
        return a, b
    return None


def parse_y_monomial(token: str):
    t = token.replace(' ', '')
    # a (constant admittance) -> series resistor with value 1/a Ω
    m = re.fullmatch(r'\d+', t)
    if m:
        a = int(t)
        if a == 0:
            return None
        return ('R', f'1/{a}Ω')
    # a*s -> capacitor with C = 1/a F
    if t == 's':
        return ('C', '1F')
    m = re.fullmatch(r'(\d+)\*?s', t)
    if m:
        a = int(m.group(1))
        if a == 0:
            return None
        return ('C', f'1/{a}F')
    # 1/(a*s) or 1/s -> inductor with L = a H
    if t == '1/s':
        return ('L', '1H')
    m = re.fullmatch(r'1/(\d+)\*?s', t)
    if m:
        a = int(m.group(1))
        return ('L', f'{a}H')
    return None

# Create ladder network

d = schemdraw.Drawing()
# Two-port input terminals (left side, initially only Vin+)
top_port = d.add(elm.Dot().label('Vin+', loc='left'))

# Start series path from top port to the right
node = d.add(elm.Line().right().at(top_port.center).length(SERIES_LEN)).end

bottom_prev = None
bottom_port_placed = False

for i in range(len(Z)):
    z = str(Z[i]).strip()
    parsed_z = parse_as_plus_b(z)
    # Series element(s) on the top rail (impedance mapping)
    if z == '1':
        node = d.add(elm.Resistor().right().at(node).length(SERIES_LEN).label('1Ω')).end
    elif z == 's':
        node = d.add(elm.Inductor().right().at(node).length(SERIES_LEN).label('1H')).end
    elif z == '1/s':
        node = d.add(elm.Capacitor().right().at(node).length(SERIES_LEN).label('1F')).end
    elif parsed_z is not None:
        a, b = parsed_z
        if a > 0:
            node = d.add(elm.Inductor().right().at(node).length(SERIES_LEN).label(f'{a}H')).end
        if b > 0:
            node = d.add(elm.Resistor().right().at(node).length(SERIES_LEN).label(f'{b}Ω')).end
    else:
        node = d.add(elm.Box().right().at(node).length(SERIES_LEN).label(z)).end

    # Shunt element: single vertical element to a straight bottom bus using 1/Y mapping
    if i < len(Y):
        y = str(Y[i]).strip()
        kind_val = parse_y_monomial(y)
        top_of_branch = node
        if kind_val is not None:
            kind, val = kind_val
            if kind == 'R':
                branch_bottom = d.add(elm.Resistor().down().at(top_of_branch).length(VERT_LEN).label(val)).end
            elif kind == 'L':
                branch_bottom = d.add(elm.Inductor().down().at(top_of_branch).length(VERT_LEN).label(val)).end
            elif kind == 'C':
                branch_bottom = d.add(elm.Capacitor().down().at(top_of_branch).length(VERT_LEN).label(val)).end
        else:
            # Fallback as labeled box vertically
            branch_bottom = d.add(elm.Box().down().at(top_of_branch).length(VERT_LEN).label(y)).end
        # For first branch, create Vin- to the left and connect horizontally
        if not bottom_port_placed:
            left_point = d.add(elm.Line().left().at(branch_bottom).length(SERIES_LEN)).end
            d.add(elm.Dot().at(left_point).label('Vin-', loc='left'))
            bottom_prev = branch_bottom
            bottom_port_placed = True
        else:
            # Extend horizontal bottom bus between branch bottoms
            d.add(elm.Line().at(bottom_prev).to(branch_bottom))
            bottom_prev = branch_bottom

# If no shunts, place Vin- unconnected below Vin+ to indicate terminals (not shorted)
if not bottom_port_placed:
    tmp = d.add(elm.Line().down().at(top_port.center).length(VERT_LEN)).end
    d.add(elm.Dot().at(tmp).label('Vin-', loc='left'))

# Render and save

d.draw(show=False)
d.save('ladder_network.png')
print("Ladder network saved as 'ladder_network.png'")
