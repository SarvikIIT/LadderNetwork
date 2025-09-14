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

        # Pre-checks for positive-real realizability with detailed reporting
        import numpy as np

        failures = []

        def degree(arr):
            return len(arr) - 1

        def lowest_degree(arr):
            for i, c in enumerate(arr):
                if abs(c) > 0:
                    return i
            return None

        def rule1_all_real_positive(name, arr):
            ok = True
            for x in arr:
                try:
                    if isinstance(x, complex):
                        ok = False; break
                    xf = float(x)
                    if xf < 0:
                        ok = False; break
                except Exception:
                    ok = False; break
            if not ok:
                failures.append("(1) Coefficients of %s must be real and non-negative." % name)

        def rule5_parity_missing_ok(name, arr):
            if not arr:
                failures.append("(5) %s has no coefficients." % name); return
            hi = len(arr) - 1
            lo = lowest_degree(arr)
            if lo is None:
                failures.append("(5) %s is identically zero." % name); return
            exps = [i for i in range(len(arr)) if abs(arr[i]) > 0]
            if len(exps) <= 1:
                return
            missing_interior = any(abs(arr[k]) == 0 for k in range(lo, hi + 1))
            if missing_interior:
                first_parity = exps[0] % 2
                parity_same = all((e % 2) == first_parity for e in exps)
                if not parity_same:
                    failures.append("(5) Missing interior terms in %s are not of single parity (all-even or all-odd)." % name)

        def rule234_roots(name, arr):
            if not arr or all(abs(x) == 0 for x in arr):
                failures.append("(2)(3)(4) %s is zero or invalid for root checks." % name); return
            poly_desc = list(reversed(arr))
            r = np.roots(poly_desc)
            tol = 1e-8
            # (3) Left-half-plane or on imaginary axis
            if np.any(np.real(r) > tol):
                failures.append("(3) Some roots of %s lie in the right half-plane (Re > 0)." % name)
            # (2) Conjugate pairs
            complex_roots = [z for z in r if abs(np.imag(z)) > tol]
            used = [False] * len(complex_roots)
            for i in range(len(complex_roots)):
                if used[i]:
                    continue
                found = False
                for j in range(i + 1, len(complex_roots)):
                    if used[j]:
                        continue
                    if abs(complex_roots[j] - np.conj(complex_roots[i])) < 1e-6:
                        used[i] = used[j] = True
                        found = True
                        break
                if not found:
                    failures.append("(2) Complex roots of %s do not occur in conjugate pairs." % name)
                    break
            # (4) Simplicity on jω-axis
            imag_axis = [z for z in r if abs(np.real(z)) <= tol]
            taken = [False] * len(imag_axis)
            for i in range(len(imag_axis)):
                if taken[i]:
                    continue
                mult = 1
                for j in range(i + 1, len(imag_axis)):
                    if taken[j]:
                        continue
                    if abs(imag_axis[j] - imag_axis[i]) < 1e-6:
                        taken[j] = True
                        mult += 1
                if mult > 1:
                    failures.append("(4) %s has a multiple root on the imaginary axis (must be simple)." % name)
                    break

        # Apply rules
        rule1_all_real_positive("N(s)", numerator_coeffs)
        rule1_all_real_positive("D(s)", denominator_coeffs)

        deg_n = degree(numerator_coeffs)
        deg_d = degree(denominator_coeffs)
        if abs(deg_n - deg_d) not in (0, 1):
            failures.append("(6) Degree difference between N(s) and D(s) must be 0 or 1.")

        ld_n = lowest_degree(numerator_coeffs)
        ld_d = lowest_degree(denominator_coeffs)
        if ld_n is None or ld_d is None or abs(ld_n - ld_d) > 1:
            failures.append("(7) Lowest-degree terms of N(s) and D(s) must differ by at most 1.")

        rule5_parity_missing_ok("N(s)", numerator_coeffs)
        rule5_parity_missing_ok("D(s)", denominator_coeffs)

        rule234_roots("N(s)", numerator_coeffs)
        rule234_roots("D(s)", denominator_coeffs)

        if failures:
            msg = "Not realizable circuit:\n" + "\n".join(f"- {f}" for f in failures)
            return None, msg

        # Legacy guard (kept but superseded by above)
        if len(numerator_coeffs) > len(denominator_coeffs) + 1:
            return None, "Invalid network: Numerator degree too high for ladder synthesis"

        # Shortcut trivial forms without invoking C++
        # Handle constants and single-term cases robustly
        deg_n = len(numerator_coeffs) - 1
        deg_d = len(denominator_coeffs) - 1

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
        FONT_SIZE = 9
        BUS_DROP = 0.0

        def dec(x: float) -> str:
            try:
                s = f"{x:.3f}"
                s = s.rstrip('0').rstrip('.')
                if s == '-0':
                    s = '0'
                return s
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
                return ('R', f'{dec(1.0/a)}Ω')
            # a*s -> capacitor with C = 1/a F
            if t == 's':
                return ('C', '1F')
            m = re.fullmatch(r'(\d+(?:\.\d+)?)\*?s', t)
            if m:
                a = float(m.group(1))
                if a == 0:
                    return None
                return ('C', f'{dec(a)}F')
            # s/n -> capacitor with C = 1/n F (since Y = C s)
            m = re.fullmatch(r's/(\d+(?:\.\d+)?)', t)
            if m:
                n = float(m.group(1))
                if n == 0:
                    return None
                return ('C', f'{dec(1.0/n)}F')
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

        # Preserve Cauer-I tokens exactly as produced by the core; do not rewrite stages here.

        # Create ladder network
        d = schemdraw.Drawing()
        # Two-port input terminals (left side, initially only Vin+)
        top_port = d.add(elm.Dot().label('Vin+', loc='left'))

        # Start series path from top port to the right
        node = d.add(elm.Line().right().at(top_port.center).length(SERIES_LEN)).end

        bottom_prev = None
        bottom_port_placed = False
        had_shunt = False

        for i in range(len(z_array)):
            z = str(z_array[i]).strip()
            parsed_z = parse_as_plus_b(z)
            # Series element(s) on the top rail (impedance mapping)
            # Pure numeric constant -> series resistor
            if re.fullmatch(r'\d+(?:\.\d+)?', z):
                node = d.add(elm.Resistor().right().at(node).length(SERIES_LEN).label(f'{dec(float(z))}Ω', loc='bottom', fontsize=FONT_SIZE)).end
            elif z == '1':
                node = d.add(elm.Resistor().right().at(node).length(SERIES_LEN).label('1Ω', loc='bottom', fontsize=FONT_SIZE)).end
            elif z == 's':
                node = d.add(elm.Inductor().right().at(node).length(SERIES_LEN).label('1H', loc='bottom', fontsize=FONT_SIZE)).end
            elif z == '1/s':
                node = d.add(elm.Capacitor().right().at(node).length(SERIES_LEN).label('1F', loc='bottom', fontsize=FONT_SIZE)).end
            elif re.fullmatch(r's/(\d+(?:\.\d+)?)', z):
                n = float(re.fullmatch(r's/(\d+(?:\.\d+)?)', z).group(1))
                node = d.add(elm.Inductor().right().at(node).length(SERIES_LEN).label(f'{dec(1.0/n)}H', loc='bottom', fontsize=FONT_SIZE)).end
            elif re.fullmatch(r'(\d+(?:\.\d+)?)/s', z):
                n = float(re.fullmatch(r'(\d+(?:\.\d+)?)/s', z).group(1))
                node = d.add(elm.Capacitor().right().at(node).length(SERIES_LEN).label(f'{dec(1.0/n)}F', loc='bottom', fontsize=FONT_SIZE)).end
            elif parsed_z is not None:
                a, b = parsed_z
                if a > 0:
                    node = d.add(elm.Inductor().right().at(node).length(SERIES_LEN).label(f'{dec(a)}H', loc='bottom', fontsize=FONT_SIZE)).end
                if b > 0:
                    node = d.add(elm.Resistor().right().at(node).length(SERIES_LEN).label(f'{dec(b)}Ω', loc='bottom', fontsize=FONT_SIZE)).end
            else:
                # Fallback: draw a labeled resistor so it renders on all versions
                node = d.add(elm.Resistor().right().at(node).length(SERIES_LEN).label(z, loc='bottom', fontsize=FONT_SIZE)).end

            # Shunt element(s): map Y token(s) to one or multiple vertical components to a bottom bus
            if i < len(y_array):
                y = str(y_array[i]).strip()
                top_of_branch = node
                branch_bottoms = []
                had_shunt = True

                elems = parse_y_sum(y)
                if elems is None:
                    kv = parse_y_monomial(y)
                    if kv is not None:
                        elems = [kv]
                    else:
                        # Fallback as a labeled resistor
                        elems = [('R', y)]

                # Create a single rightward tap from the series node as the shunt entry (even shorter)
                tap = d.add(elm.Line().right().at(top_of_branch).length(SERIES_LEN * 0.12)).end

                # Draw each element with incremental right offsets from the tap, then straight down
                for idx, (kind, val) in enumerate(elems):
                    # Even tighter horizontal separation to further reduce right-side wire
                    at_point = tap if idx == 0 else d.add(elm.Line().right().at(tap).length(SERIES_LEN * 0.3 * idx)).end
                    if kind == 'R':
                        btm = d.add(elm.Resistor().down().at(at_point).length(VERT_LEN).label(val, loc='right', fontsize=FONT_SIZE)).end
                    elif kind == 'L':
                        btm = d.add(elm.Inductor().down().at(at_point).length(VERT_LEN).label(val, loc='right', fontsize=FONT_SIZE)).end
                    elif kind == 'C':
                        btm = d.add(elm.Capacitor().down().at(at_point).length(VERT_LEN).label(val, loc='right', fontsize=FONT_SIZE)).end
                    else:
                        btm = d.add(elm.Resistor().down().at(at_point).length(VERT_LEN).label(val, loc='right', fontsize=FONT_SIZE)).end
                    branch_bottoms.append(btm)

                # If Y is exactly 's/n', it's a single capacitor of value n F (no extra inductor)

                # Tie bottoms together to form a straight local bottom bus
                if len(branch_bottoms) > 1:
                    # Route the bus slightly below element ends to avoid overlapping symbol gaps
                    bus_points = []
                    for btm in branch_bottoms:
                        p = d.add(elm.Line().down().at(btm).length(0.2)).end
                        bus_points.append(p)
                    for j in range(len(bus_points) - 1):
                        d.add(elm.Line().at(bus_points[j]).to(bus_points[j + 1]))
                    local_left = bus_points[0]
                    local_right = bus_points[-1]
                else:
                    local_left = branch_bottoms[0]
                    local_right = branch_bottoms[0]
                # For first branch, create Vin- to the left and connect from local_left
                if not bottom_port_placed:
                    left_point = d.add(elm.Line().left().at(local_left).length(SERIES_LEN)).end
                    d.add(elm.Dot().at(left_point).label('Vin-', loc='left', fontsize=FONT_SIZE))
                    bottom_prev = local_right
                    bottom_port_placed = True
                else:
                    # Extend global bus from previous rightmost to current local_left
                    d.add(elm.Line().at(bottom_prev).to(local_left))
                    bottom_prev = local_right

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

        # Close the mesh only if there were no shunt branches drawn
        if bottom_prev is not None and not had_shunt:
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
            # Professional, structured error response (while preserving `error` for frontend compatibility)
            title = "Not realizable circuit" if error.lower().startswith("not realizable circuit") else "Not realizable circuit with RLC components"
            details = []
            if error.startswith("Not realizable circuit:"):
                # Parse bullet list lines into details array. Support both newline and inline "- " bullets.
                lines = [ln.strip() for ln in error.split("\n")]
                for ln in lines[1:]:
                    if ln.startswith("-"):
                        details.append(ln[1:].strip())
                if not details:
                    # Fallback: split inline bullets after the colon
                    try:
                        body = error.split(":", 1)[1]
                        parts = re.split(r"\s*-\s+", body)
                        for p in parts:
                            p = p.strip()
                            if p:
                                details.append(p)
                    except Exception:
                        pass
            # Build a polished multi-line error string for UIs that only read `error`
            if details:
                pretty_error = title + "\n" + "\n".join(f"• {d}" for d in details)
            else:
                pretty_error = title
            payload = {
                'success': False,
                'error': pretty_error,
                'message': title,
                'details': details,
                'code': 'PR_VALIDATION_FAILED'
            }
            return jsonify(payload), 400
        
        # Optional normalization to present elements in best physical form
        def normalize_tokens(z_list, y_list):
            zl = [str(z) for z in (z_list or [])]
            yl = [str(y) for y in (y_list or [])]
            # For the last Z token, if it's of the form a*s + b with b <= 0, drop the constant b
            if zl:
                t = zl[-1].replace(' ', '')
                m = re.fullmatch(r'(?:(\d+(?:\.\d+)?)\*?s|s)([+-]\d+(?:\.\d+)?)', t)
                if m:
                    a = float(m.group(1)) if m.group(1) else 1.0
                    b = float(m.group(2))
                    if b <= 0:
                        zl[-1] = (f"{dec(a)}s" if abs(a - 1.0) > 1e-12 else 's')
                else:
                    m2 = re.fullmatch(r'(\d+(?:\.\d+)?)[+-](?:(\d+(?:\.\d+)?)\*?s|s)', t)
                    if m2:
                        b = float(m2.group(1))
                        a = float(m2.group(2)) if m2.group(2) else 1.0
                        # If constant first and effectively negative in token, prefer pure inductance
                        if '-' in t:
                            zl[-1] = (f"{dec(a)}s" if abs(a - 1.0) > 1e-12 else 's')
            return zl, yl

        if not error and result:
            result['Z'], result['Y'] = normalize_tokens(result.get('Z'), result.get('Y'))
        
        # Build pretty display strings for Z and Y
        def dec(x: float) -> str:
            try:
                s = ("%g" % x)
            except Exception:
                s = str(x)
            return s

        def pretty_z(tok: str) -> str:
            t = tok.replace(' ', '')
            # Pure numeric -> series resistor
            m = re.fullmatch(r'(\d+(?:\.\d+)?)', t)
            if m:
                k = float(m.group(1))
                return f'R={dec(k)}Ω'
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
            # s/n → C=1/n F
            m = re.fullmatch(r's/(\d+(?:\.\d+)?)', t)
            if m:
                n = float(m.group(1))
                return f'C={dec(1.0/n)}F'
            # a*s + b → parallel C and R
            m = re.fullmatch(r'(?:(\d+(?:\.\d+)?)\*?s|s)\+(\d+(?:\.\d+)?)', t)
            if m:
                a = float(m.group(1)) if m.group(1) else 1.0
                b = float(m.group(2))
                return f'C={dec(a)}F || R={dec(1.0/b)}Ω'
            m = re.fullmatch(r'(\d+(?:\.\d+)?)\+(?:(\d+(?:\.\d+)?)\*?s|s)', t)
            if m:
                b = float(m.group(1))
                a = float(m.group(2)) if m.group(2) else 1.0
                return f'C={dec(a)}F || R={dec(1.0/b)}Ω'
            # a*s
            m = re.fullmatch(r'(\d+(?:\.\d+)?)\*?s', t)
            if m:
                a = float(m.group(1))
                return f'C={dec(a)}F'
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
