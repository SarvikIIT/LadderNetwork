import pandas as pd
import schemdraw
import schemdraw.elements as elm

# Read CSV files (force strings)
Z_df = pd.read_csv('Z.csv', header=None, dtype=str)
Y_df = pd.read_csv('Y.csv', header=None, dtype=str)

# Convert to lists of strings
Z = Z_df.iloc[0].astype(str).str.strip().tolist()
Y = Y_df.iloc[0].astype(str).str.strip().tolist()

# Create ladder network

d = schemdraw.Drawing()
start = d.add(elm.SourceV().label('Vin'))
node = start.end

for i in range(len(Z)):
    z = str(Z[i]).strip()
    # Series element
    if z == '1':
        node = d.add(elm.Resistor().right().at(node).label('R')).end
    elif z == 's':
        node = d.add(elm.Inductor().right().at(node).label('L')).end
    elif z == '1/s':
        node = d.add(elm.Capacitor().right().at(node).label('C')).end

    # Shunt element
    if i < len(Y):
        y = str(Y[i]).strip()
        if y == '1':
            shunt = d.add(elm.Resistor().down().at(node).label('R'))
        elif y == 's':
            shunt = d.add(elm.Inductor().down().at(node).label('L'))
        elif y == '1/s':
            shunt = d.add(elm.Capacitor().down().at(node).label('C'))
        # Connect back to main line
        d.add(elm.Line().at(shunt.end).to(node))

# Output

d.add(elm.Line().right().length(1.0).label('Vout'))
d.draw()
d.save('ladder_network.png')
print("Ladder network saved as 'ladder_network.png'")
