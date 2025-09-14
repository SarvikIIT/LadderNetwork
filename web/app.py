#!/usr/bin/env python3
"""
Network Ladder Web Application Backend
Flask API server that processes transfer functions and generates ladder networks
"""

import os
import subprocess
import tempfile
import json
import re
from flask import Flask, request, jsonify, send_file, render_template
from flask_cors import CORS
import matplotlib
matplotlib.use('Agg')
import schemdraw
import schemdraw.elements as elm
from io import BytesIO
import base64

app = Flask(__name__, template_folder=os.path.join(os.path.dirname(__file__), '..', 'templates'), static_folder=os.path.join(os.path.dirname(__file__), '..', 'static'))
CORS(app)

# Configuration
CXX_COMPILER = "g++"
CXX_FLAGS = "-std=c++17 -O2"
SOURCE_FILES = [
    "main.cpp", "Polynomial.cpp", "ContinuedFraction.cpp", 
    "CSVMaker.cpp", "NetworkUtils.cpp"
]

def compile_cpp_app():
    """Compile the C++ application if not already compiled"""
    exe_name = "app.exe" if os.name == 'nt' else "app"
    if not os.path.exists(exe_name):
        try:
            # Source files are now in src/ directory
            source_files = [
                "src/main.cpp", "src/Polynomial.cpp", "src/ContinuedFraction.cpp", 
                "src/CSVMaker.cpp", "src/NetworkUtils.cpp"
            ]
            cmd = [CXX_COMPILER] + CXX_FLAGS.split() + ["-o", exe_name] + source_files
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print("C++ application compiled successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"Compilation failed: {e.stderr}")
            return False
    return True

def parse_transfer_function(numerator_coeffs, denominator_coeffs):
    """Parse transfer function coefficients and return Z, Y arrays"""
    try:
        # Validate input
        if not numerator_coeffs or not denominator_coeffs:
            return None, "Empty coefficient arrays"
        
        if all(x == 0 for x in numerator_coeffs):
            return None, "Invalid network: Numerator cannot be zero"
        
        if all(x == 0 for x in denominator_coeffs):
            return None, "Invalid network: Denominator cannot be zero"
        
        # Normalize by trimming trailing zeros to get actual degrees
        def trim_trailing_zeros(arr):
            i = len(arr) - 1
            while i > 0 and abs(arr[i]) == 0:
                i -= 1
            return arr[: i + 1]

        numerator_coeffs = trim_trailing_zeros(list(numerator_coeffs))
        denominator_coeffs = trim_trailing_zeros(list(denominator_coeffs))

        # Normalize overall sign so that leading denominator coefficient is positive
        def leading_coeff(arr):
            return arr[-1] if arr else 0
        if leading_coeff(denominator_coeffs) < 0:
            numerator_coeffs = [ -x for x in numerator_coeffs ]
            denominator_coeffs = [ -x for x in denominator_coeffs ]

        # Basic degree realizability: |deg(N) - deg(D)| <= 1 for passive RLC driving-point Z(s)
        deg_n = len(numerator_coeffs) - 1
        deg_d = len(denominator_coeffs) - 1
        if abs(deg_n - deg_d) > 1:
            return None, "Not realizable as passive RLC: |deg(N) - deg(D)| must be <= 1"

        # Coefficient sanity: require all finite reals and nonnegative after normalization
        def has_invalid_coeffs(arr):
            for v in arr:
                if v is None:
                    return True
                try:
                    _ = float(v)
                except Exception:
                    return True
            return False
        if has_invalid_coeffs(numerator_coeffs) or has_invalid_coeffs(denominator_coeffs):
            return None, "Invalid coefficients: must be real numbers"

        if any(x < 0 for x in numerator_coeffs) or any(x < 0 for x in denominator_coeffs):
            return None, "Not realizable as passive RLC: negative coefficients detected"

        # Denominator must be Hurwitz (all poles in LHP). Use Routh-Hurwitz test.
        def is_hurwitz_stable(coeffs_asc):
            # Convert ascending [a0, a1, ..., an] to descending [an, ..., a0]
            a = list(reversed(coeffs_asc))
            # All coefficients strictly positive
            if any(c <= 0 for c in a):
                return False
            n = len(a) - 1
            # Build Routh table
            rows = n + 1
            cols = (n // 2) + 1
            table = [[0.0 for _ in range(cols)] for _ in range(rows)]
            # First two rows
            table[0][:] = [a[i] for i in range(0, len(a), 2)] + [0.0] * (cols - len(a[0::2]))
            table[1][:] = [a[i] for i in range(1, len(a), 2)] + [0.0] * (cols - len(a[1::2]))
            # Fill remaining rows
            for r in range(2, rows):
                for c in range(cols - 1):
                    top_left = table[r - 2][0]
                    if abs(top_left) < 1e-12:
                        # epsilon substitution to avoid division by zero; this indicates a marginal case
                        top_left = 1e-12
                    table[r][c] = ((table[r - 2][0] * table[r - 1][c + 1]) - (table[r - 1][0] * table[r - 2][c + 1])) / top_left
            # Stable if first column all positive
            first_col = [table[r][0] for r in range(rows)]
            return all(x > 0 for x in first_col if isinstance(x, (int, float)))

        if not is_hurwitz_stable(denominator_coeffs):
            return None, "Not realizable/stable: denominator is not Hurwitz (poles not in LHP)"

        # Check for invalid network conditions
        if len(numerator_coeffs) > len(denominator_coeffs) + 1:
            return None, "Invalid network: Numerator degree too high for ladder synthesis"

        # Shortcut trivial forms without invoking C++
        # Handle constants and single-term cases robustly

        def is_zero_poly(poly):
            return all(abs(x) == 0 for x in poly)

        def safe_div(a, b):
            try:
                return a / b
            except Exception:
                return None

        if not is_zero_poly(denominator_coeffs):
            a0 = numerator_coeffs[0] if len(numerator_coeffs) > 0 else 0
            a1 = numerator_coeffs[1] if len(numerator_coeffs) > 1 else 0
            b0 = denominator_coeffs[0] if len(denominator_coeffs) > 0 else 0
            b1 = denominator_coeffs[1] if len(denominator_coeffs) > 1 else 0

            # H(s) = (a1 s + a0) / (b1 s + b0)
            # Constant: a1=0, b1=0 -> Z = [k]
            if deg_n <= 1 and deg_d <= 1:
                if abs(a1) == 0 and abs(b1) == 0 and abs(b0) > 0:
                    k = safe_div(a0, b0)
                    if k is not None:
                        return {"Z": [f"{k}"], "Y": []}, None
                # Pure integrator: a0>0, b1>0, a1=0, b0=0 -> Z = [(a0/b1)/s]
                if abs(a1) == 0 and abs(b0) == 0 and abs(b1) > 0:
                    scale = safe_div(a0, b1)
                    if scale is None:
                        scale = 0
                    if scale <= 0:
                        return None, "Not realizable as passive RLC: negative or zero capacitance implied"
                    # If scale == 1: token '1/s', else 'scale/s'
                    if abs(scale - 1) < 1e-12:
                        return {"Z": ["1/s"], "Y": []}, None
                    else:
                        return {"Z": [f"{scale}/s"], "Y": []}, None
                # Pure differentiator: a1>0, b0>0, a0=0, b1=0 -> Z = [s/(b0/a1)]
                if abs(b1) == 0 and abs(a0) == 0 and abs(b0) > 0 and abs(a1) > 0:
                    scale = safe_div(b0, a1)
                    if scale is None:
                        scale = 0
                    if scale <= 0:
                        return None, "Not realizable as passive RLC: negative or zero inductance implied"
                    if abs(scale - 1) < 1e-12:
                        return {"Z": ["s"], "Y": []}, None
                    else:
                        return {"Z": [f"s/{scale}"], "Y": []}, None
        
        # Create temporary input file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            # Write numerator: degree coefficients
            f.write(f"{len(numerator_coeffs)-1}")
            for coeff in numerator_coeffs:
                f.write(f" {coeff}")
            f.write("\n")
            
            # Write denominator: degree coefficients  
            f.write(f"{len(denominator_coeffs)-1}")
            for coeff in denominator_coeffs:
                f.write(f" {coeff}")
            f.write("\n")
            
            input_file = f.name

        # Check if C++ app exists
        cpp_app = "./app.exe" if os.name == 'nt' else "./app"
        if not os.path.exists(cpp_app):
            # Try to compile it
            if not compile_cpp_app():
                return None, "C++ application not available and compilation failed"
            cpp_app = "./app.exe" if os.name == 'nt' else "./app"

        # Run the C++ application
        with open(input_file, 'r') as f:
            result = subprocess.run(
                [cpp_app], 
                stdin=f, 
                capture_output=True, 
                text=True, 
                cwd=os.getcwd(),
                timeout=30  # 30 second timeout
            )
        
        # Clean up
        os.unlink(input_file)
        
        if result.returncode != 0:
            error_msg = result.stderr.strip() if result.stderr.strip() else "Unknown C++ application error"
            if "Invalid network" in error_msg:
                return None, f"Invalid network: {error_msg}"
            return None, f"C++ application error: {error_msg}"
        
        # Parse output
        output_lines = result.stdout.strip().split('\n')
        z_line = None
        y_line = None
        
        for line in output_lines:
            if line.startswith("Z = ["):
                z_line = line
            elif line.startswith("Y = ["):
                y_line = line
        
        # Extract Z and Y arrays
        z_array = []
        y_array = []
        
        if z_line:
            z_content = z_line[z_line.find('[')+1:z_line.rfind(']')]
            if z_content.strip():
                z_array = [item.strip() for item in z_content.split(',')]
        
        if y_line:
            y_content = y_line[y_line.find('[')+1:y_line.rfind(']')]
            if y_content.strip():
                y_array = [item.strip() for item in y_content.split(',')]
        
        # Validate that we have at least one element; fallback for trivial unity if needed
        if not z_array and not y_array:
            # As a last resort, attempt to interpret H(s) as a constant ratio
            if deg_n == 0 and deg_d == 0 and abs(denominator_coeffs[0]) > 0:
                k = safe_div(numerator_coeffs[0], denominator_coeffs[0])
                if k is not None:
                    return {"Z": [f"{k}"], "Y": []}, None
            return None, "Invalid network: No valid network elements generated"

        # Validate synthesized tokens are realizable with nonnegative passive components
        def token_is_linear_positive(tok):
            t = str(tok).replace(' ', '')
            # Reject explicit powers beyond 1
            if re.search(r's\^\d+', t) or re.search(r'/s\^\d+', t):
                return False
            # Reject negatives anywhere
            if '-' in t:
                return False
            # Allowed simple forms
            if re.fullmatch(r'\d+(?:\.\d+)?', t):
                return float(t) >= 0
            if t in ('1', 's', '1/s'):
                return True
            if re.fullmatch(r's/(\d+(?:\.\d+)?)', t):
                return float(re.fullmatch(r's/(\d+(?:\.\d+)?)', t).group(1)) > 0
            if re.fullmatch(r'(\d+(?:\.\d+)?)/s', t):
                return float(re.fullmatch(r'(\d+(?:\.\d+)?)/s', t).group(1)) > 0
            # Linear a*s + b or b + a*s
            if re.fullmatch(r'(?:(\d+(?:\.\d+)?)\*?s|s)\+(\d+(?:\.\d+)?)', t):
                return True
            if re.fullmatch(r'(\d+(?:\.\d+)?)\+(?:(\d+(?:\.\d+)?)\*?s|s)', t):
                return True
            # For Y, we might receive sums like "a"+"b*s"; this will be handled elementwise below
            return False

        # Validate Z tokens
        for zt in z_array:
            if not token_is_linear_positive(zt):
                return None, f"Not realizable/supported term in Z: {zt}"

        # Validate Y tokens (allow '+' sums of allowed monomials)
        for yt in y_array:
            t = str(yt).replace(' ', '')
            parts = t.split('+') if '+' in t else [t]
            ok = True
            for p in parts:
                if not token_is_linear_positive(p):
                    ok = False
                    break
            if not ok:
                return None, f"Not realizable/supported term in Y: {yt}"
        
        return {"Z": z_array, "Y": y_array}, None
        
    except subprocess.TimeoutExpired:
        return None, "Processing timeout: Transfer function too complex"
    except Exception as e:
        return None, f"Error processing transfer function: {str(e)}"

def generate_network_image(z_array, y_array):
    """Generate network schematic image using schemdraw. Returns (b64, error_str)."""
    try:
        # Constants for drawing - optimized for web display
        SERIES_LEN = 2.0
        VERT_LEN = 2.0

        def dec(x: float) -> str:
            try:
                return ("%g" % x)
            except Exception:
                return str(x)
        
        def parse_as_plus_b(token):
            t = token.replace(' ', '')
            m = re.match(r'^(?:(\d+(?:\.\d+)?)\*?s|s)(?:\+(\d+(?:\.\d+)?))?$', t)
            if m:
                a = float(m.group(1)) if m.group(1) else 1.0
                b = float(m.group(2)) if m.group(2) else 0.0
                return a, b
            m = re.match(r'^(\d+(?:\.\d+)?)\+(?:(\d+(?:\.\d+)?)\*?s|s)$', t)
            if m:
                b = float(m.group(1))
                a = float(m.group(2)) if m.group(2) else 1.0
                return a, b
            return None

        def parse_y_monomial(token):
            t = token.replace(' ', '')
            # a (constant admittance) -> series resistor with value 1/a Ω
            m = re.fullmatch(r'\d+(?:\.\d+)?', t)
            if m:
                a = float(t)
                if a == 0:
                    return None
                return ('R', f'1/{a}Ω')
            # a*s -> capacitor with C = 1/a F
            if t == 's':
                return ('C', '1F')
            m = re.fullmatch(r'(\d+(?:\.\d+)?)\*?s', t)
            if m:
                a = float(m.group(1))
                if a == 0:
                    return None
                return ('C', f'1/{a}F')
            # s/n -> capacitor with C = n F (since Y = C s)
            m = re.fullmatch(r's/(\d+(?:\.\d+)?)', t)
            if m:
                n = float(m.group(1))
                if n == 0:
                    return None
                return ('C', f'{n}F')
            # 1/(a*s) or 1/s -> inductor with L = a H
            if t == '1/s':
                return ('L', '1H')
            m = re.fullmatch(r'1/(\d+(?:\.\d+)?)\*?s', t)
            if m:
                a = float(m.group(1))
                return ('L', f'{a}H')
            return None

        def parse_y_sum(token):
            """Parse sums like '2s+3' or '3+2s' into a list of (kind,label)."""
            t = token.replace(' ', '')
            if '+' not in t:
                return None
            parts = t.split('+')
            elems = []
            for part in parts:
                kv = parse_y_monomial(part)
                if kv is None:
                    return None
                elems.append(kv)
            return elems

        # Optional CF normalization for first section: if initial Z is 's' and first Y is linear 'a s + b',
        # transform to Z=['1', 's/a'] and Y=['s/a'] as per requested CF form.
        if len(z_array) >= 1 and len(y_array) >= 1:
            z0 = str(z_array[0]).strip()
            m_lin = re.fullmatch(r"\s*(?:(\d+(?:\.\d+)?)\*?s|s)\s*\+\s*(\d+(?:\.\d+)?)\s*", str(y_array[0]))
            if z0 == 's' and m_lin:
                a = float(m_lin.group(1)) if m_lin.group(1) else 1.0
                # b is m_lin.group(2), but it is absorbed in the CF normalization to a leading '1'
                z_array = ['1', f's/{a}'] + list(z_array[1:])
                y_array = [f's/{a}'] + list(y_array[1:])

        # Create ladder network
        d = schemdraw.Drawing()
        # Two-port input terminals (left side, initially only Vin+)
        top_port = d.add(elm.Dot().label('Vin+', loc='left'))

        # Start series path from top port to the right
        node = d.add(elm.Line().right().at(top_port.center).length(SERIES_LEN)).end

        bottom_prev = None
        bottom_port_placed = False

        for i in range(len(z_array)):
            z = str(z_array[i]).strip()
            parsed_z = parse_as_plus_b(z)
            # Series element(s) on the top rail (impedance mapping)
            # Pure numeric constant -> series resistor
            if re.fullmatch(r'\d+(?:\.\d+)?', z):
                node = d.add(elm.Resistor().right().at(node).length(SERIES_LEN).label(f'{dec(float(z))}Ω', loc='bottom')).end
            elif z == '1':
                node = d.add(elm.Resistor().right().at(node).length(SERIES_LEN).label('1Ω', loc='bottom')).end
            elif z == 's':
                node = d.add(elm.Inductor().right().at(node).length(SERIES_LEN).label('1H', loc='bottom')).end
            elif z == '1/s':
                node = d.add(elm.Capacitor().right().at(node).length(SERIES_LEN).label('1F', loc='bottom')).end
            elif re.fullmatch(r's/(\d+(?:\.\d+)?)', z):
                n = float(re.fullmatch(r's/(\d+(?:\.\d+)?)', z).group(1))
                node = d.add(elm.Inductor().right().at(node).length(SERIES_LEN).label(f'{dec(1.0/n)}H', loc='bottom')).end
            elif re.fullmatch(r'(\d+(?:\.\d+)?)/s', z):
                n = float(re.fullmatch(r'(\d+(?:\.\d+)?)/s', z).group(1))
                node = d.add(elm.Capacitor().right().at(node).length(SERIES_LEN).label(f'{dec(1.0/n)}F', loc='bottom')).end
            elif parsed_z is not None:
                a, b = parsed_z
                if a > 0:
                    node = d.add(elm.Inductor().right().at(node).length(SERIES_LEN).label(f'{dec(a)}H', loc='bottom')).end
                if b > 0:
                    node = d.add(elm.Resistor().right().at(node).length(SERIES_LEN).label(f'{dec(b)}Ω', loc='bottom')).end
            else:
                # Fallback: draw a labeled resistor so it renders on all versions
                node = d.add(elm.Resistor().right().at(node).length(SERIES_LEN).label(z, loc='bottom')).end

            # Shunt element(s): map Y token(s) to one or multiple vertical components to a bottom bus
            if i < len(y_array):
                y = str(y_array[i]).strip()
                top_of_branch = node
                branch_bottoms = []

                elems = parse_y_sum(y)
                if elems is None:
                    kv = parse_y_monomial(y)
                    if kv is not None:
                        elems = [kv]
                    else:
                        # Fallback as a labeled resistor
                        elems = [('R', y)]

                # Draw each element with small horizontal offsets if multiple
                for idx, (kind, val) in enumerate(elems):
                    at_point = top_of_branch
                    if idx > 0:
                        at_point = d.add(elm.Line().right().at(top_of_branch).length(SERIES_LEN * 0.5 * idx)).end
                    if kind == 'R':
                        btm = d.add(elm.Resistor().down().at(at_point).length(VERT_LEN).label(val, loc='right')).end
                    elif kind == 'L':
                        btm = d.add(elm.Inductor().down().at(at_point).length(VERT_LEN).label(val, loc='right')).end
                    elif kind == 'C':
                        btm = d.add(elm.Capacitor().down().at(at_point).length(VERT_LEN).label(val, loc='left')).end
                    else:
                        btm = d.add(elm.Resistor().down().at(at_point).length(VERT_LEN).label(val, loc='right')).end
                    branch_bottoms.append(btm)

                # If Y is exactly 's/n', it's a single capacitor of value n F (no extra inductor)

                # Tie bottoms together for a single local bottom node at this section
                if len(branch_bottoms) > 1:
                    for j in range(len(branch_bottoms) - 1):
                        d.add(elm.Line().at(branch_bottoms[j]).to(branch_bottoms[j + 1]))

                # Representative bottom for bus chaining is the rightmost one
                branch_bottom = branch_bottoms[-1]
                # For first branch, create Vin- to the left and connect horizontally
                if not bottom_port_placed:
                    left_point = d.add(elm.Line().left().at(branch_bottoms[0]).length(SERIES_LEN)).end
                    d.add(elm.Dot().at(left_point).label('Vin-', loc='left'))
                    bottom_prev = branch_bottom
                    bottom_port_placed = True
                else:
                    # Extend horizontal bottom bus between branch bottoms
                    d.add(elm.Line().at(bottom_prev).to(branch_bottom))
                    bottom_prev = branch_bottom

        # If no shunts, still close the loop: add Vin- below Vin+ and connect right end down to the bottom
        if not bottom_port_placed:
            tmp = d.add(elm.Line().down().at(top_port.center).length(VERT_LEN)).end
            d.add(elm.Dot().at(tmp).label('Vin-', loc='left'))
            # Connect the final top node down, then tie to Vin- horizontally
            down_seg = d.add(elm.Line().down().at(node).length(VERT_LEN))
            down_end = down_seg.end
            d.add(elm.Line().at(tmp).to(down_end))
            # Prevent duplicate closure below
            bottom_prev = None

        # Close the mesh at the right end by connecting the last top node down to the bottom bus
        if bottom_prev is not None:
            down_seg = d.add(elm.Line().down().at(node).length(VERT_LEN))
            down_end = down_seg.end
            d.add(elm.Line().at(bottom_prev).to(down_end))

        # Convert to high-quality base64 image using a temporary file (more reliable on Windows)
        d.draw(show=False)
        tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
        tmp_file_path = tmp_file.name
        tmp_file.close()
        try:
            d.save(tmp_file_path, dpi=300)
            with open(tmp_file_path, 'rb') as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')
            return encoded, None
        finally:
            try:
                os.unlink(tmp_file_path)
            except Exception:
                pass
        
    except Exception as e:
        print(f"Error generating network image: {e}")
        return None, str(e)

@app.route('/api/process', methods=['POST'])
def process_transfer_function():
    """Process transfer function and return network data"""
    try:
        data = request.get_json()
        
        if not data or 'numerator' not in data or 'denominator' not in data:
            return jsonify({'error': 'Missing numerator or denominator coefficients'}), 400
        
        numerator = data['numerator']
        denominator = data['denominator']
        
        if not isinstance(numerator, list) or not isinstance(denominator, list):
            return jsonify({'error': 'Coefficients must be arrays'}), 400
        
        if len(numerator) == 0 or len(denominator) == 0:
            return jsonify({'error': 'Coefficients arrays cannot be empty'}), 400
        
        # Process the transfer function
        result, error = parse_transfer_function(numerator, denominator)
        
        if error:
            return jsonify({'error': error}), 400
        
        # Build pretty display strings for Z and Y
        def dec(x: float) -> str:
            try:
                s = ("%g" % x)
            except Exception:
                s = str(x)
            return s

        def pretty_z(tok: str) -> str:
            t = tok.replace(' ', '')
            if t == '1':
                return 'L=1H'
            if t == 's':
                return 'L=1H'
            if t == '1/s':
                return 'C=1F'
            m = re.fullmatch(r's/(\d+(?:\.\d+)?)', t)
            if m:
                n = float(m.group(1))
                return f'L={dec(1.0/n)}H'
            m = re.fullmatch(r'(\d+(?:\.\d+)?)/s', t)
            if m:
                n = float(m.group(1))
                return f'C={dec(1.0/n)}F'
            m = re.fullmatch(r'(?:(\d+(?:\.\d+)?)\*?s|s)\+(\d+(?:\.\d+)?)', t)
            if m:
                a = float(m.group(1)) if m.group(1) else 1.0
                b = float(m.group(2))
                return f'L={dec(a)}H, R={dec(b)}Ω'
            m = re.fullmatch(r'(\d+(?:\.\d+)?)\+(?:(\d+(?:\.\d+)?)\*?s|s)', t)
            if m:
                b = float(m.group(1))
                a = float(m.group(2)) if m.group(2) else 1.0
                return f'L={dec(a)}H, R={dec(b)}Ω'
            return tok

        def pretty_y(tok: str) -> str:
            t = tok.replace(' ', '')
            # s/n → C=n F || L=1/n H (per requested CF rendering)
            m = re.fullmatch(r's/(\d+(?:\.\d+)?)', t)
            if m:
                n = float(m.group(1))
                return f'C={dec(n)}F || L={dec(1.0/n)}H'
            # a*s + b → parallel C and R
            m = re.fullmatch(r'(?:(\d+(?:\.\d+)?)\*?s|s)\+(\d+(?:\.\d+)?)', t)
            if m:
                a = float(m.group(1)) if m.group(1) else 1.0
                b = float(m.group(2))
                return f'C={dec(1.0/a)}F || R={dec(1.0/b)}Ω'
            m = re.fullmatch(r'(\d+(?:\.\d+)?)\+(?:(\d+(?:\.\d+)?)\*?s|s)', t)
            if m:
                b = float(m.group(1))
                a = float(m.group(2)) if m.group(2) else 1.0
                return f'C={dec(1.0/a)}F || R={dec(1.0/b)}Ω'
            # a*s
            m = re.fullmatch(r'(\d+(?:\.\d+)?)\*?s', t)
            if m:
                a = float(m.group(1))
                return f'C={dec(1.0/a)}F'
            if t == 's':
                return 'C=1F'
            # constant b
            m = re.fullmatch(r'(\d+(?:\.\d+)?)', t)
            if m:
                b = float(m.group(1))
                return f'R={dec(1.0/b)}Ω'
            # 1/(a*s)
            m = re.fullmatch(r'1/(\d+(?:\.\d+)?)\*?s', t)
            if m:
                a = float(m.group(1))
                return f'L={dec(a)}H'
            if t == '1/s':
                return 'L=1H'
            return tok

        Z_display = [pretty_z(z) for z in result['Z']]
        Y_display = [pretty_y(y) for y in result['Y']]

        # Generate network image
        image_data, img_err = generate_network_image(result['Z'], result['Y'])
        
        if image_data is None:
            return jsonify({'error': f"Failed to generate network image: {img_err}"}), 500
        
        return jsonify({
            'success': True,
            'Z': result['Z'],
            'Y': result['Y'],
            'Z_display': Z_display,
            'Y_display': Y_display,
            'image': image_data
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'}), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'healthy', 'message': 'Network Ladder API is running'})

@app.route('/', methods=['GET'])
def serve_frontend():
    """Serve the main frontend page"""
    return render_template('index.html')

if __name__ == '__main__':
    # Compile C++ application on startup
    if not compile_cpp_app():
        print("Warning: C++ application compilation failed. Some features may not work.")
    
    print("Starting Network Ladder Web Application...")
    print("Visit http://localhost:5000 to use the application")
    app.run(debug=True, host='0.0.0.0', port=5000)
