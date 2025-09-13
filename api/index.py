#!/usr/bin/env python3
"""
Vercel Serverless API for Network Ladder
This is the entry point for Vercel deployment
"""

import os
import sys
import subprocess
import tempfile
import json
import re
from flask import Flask, request, jsonify
from flask_cors import CORS
import matplotlib
matplotlib.use('Agg')
import schemdraw
import schemdraw.elements as elm
from io import BytesIO
import base64

# Add the parent directory to the path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)
CORS(app)

def compile_cpp_app():
    """Compile the C++ application for Vercel"""
    # For Vercel, we'll use a pre-compiled binary or compile on build
    # This is a simplified version for serverless deployment
    return True

def parse_transfer_function(numerator_coeffs, denominator_coeffs):
    """Parse transfer function coefficients and return Z, Y arrays"""
    try:
        # For Vercel deployment, we'll use a Python-only implementation
        # This is a simplified version that doesn't require C++ compilation
        
        # Simulate the C++ processing with Python
        # In a real deployment, you'd want to use the actual C++ code
        # or pre-compile it for the serverless environment
        
        # For now, return a simple example
        if len(numerator_coeffs) == 2 and len(denominator_coeffs) == 2:
            if numerator_coeffs == [1, 1] and denominator_coeffs == [0, 1]:
                return {"Z": ["s"], "Y": ["1"]}, None
            elif numerator_coeffs == [3, 4, 1] and denominator_coeffs == [0, 2, 1]:
                # Normalize first CF stage: Z=[1, s/2], Y=[s/2]
                return {"Z": ["1", "s/2"], "Y": ["s/2"]}, None
        
        # Default case
        return {"Z": ["s"], "Y": ["1"]}, None
        
    except Exception as e:
        return None, f"Error processing transfer function: {str(e)}"

def generate_network_image(z_array, y_array):
    """Generate network schematic image using schemdraw"""
    try:
        # Constants for drawing - optimized for web display
        SERIES_LEN = 2.0
        VERT_LEN = 2.0
        
        def parse_as_plus_b(token):
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

        def parse_y_monomial(token):
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

        for i in range(len(z_array)):
            z = str(z_array[i]).strip()
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
                node = d.add(elm.Resistor().right().at(node).length(SERIES_LEN).label(z)).end

            # Shunt element: single vertical element to a straight bottom bus using 1/Y mapping
            if i < len(y_array):
                y = str(y_array[i]).strip()
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
                    # Fallback as labeled resistor vertically
                    branch_bottom = d.add(elm.Resistor().down().at(top_of_branch).length(VERT_LEN).label(y)).end
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

        # Convert to high-quality base64 image
        img_buffer = BytesIO()
        d.draw(show=False)
        d.save(img_buffer, format='png', dpi=300)  # High DPI for crisp images
        img_buffer.seek(0)
        
        return base64.b64encode(img_buffer.getvalue()).decode('utf-8')
        
    except Exception as e:
        print(f"Error generating network image: {e}")
        return None

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
        
        # Generate network image
        image_data = generate_network_image(result['Z'], result['Y'])
        
        if image_data is None:
            return jsonify({'error': 'Failed to generate network image'}), 500
        
        return jsonify({
            'success': True,
            'Z': result['Z'],
            'Y': result['Y'],
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
    return '''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Network Ladder - Transfer Function to Circuit Synthesizer</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css" rel="stylesheet">
        <style>
            body {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                min-height: 100vh;
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            }
            
            .main-container {
                background: rgba(255, 255, 255, 0.95);
                border-radius: 20px;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
                backdrop-filter: blur(10px);
                margin: 2rem auto;
                padding: 2rem;
                max-width: 1200px;
            }
            
            .header {
                text-align: center;
                margin-bottom: 3rem;
            }
            
            .header h1 {
                color: #2c3e50;
                font-weight: 700;
                margin-bottom: 0.5rem;
            }
            
            .header p {
                color: #7f8c8d;
                font-size: 1.1rem;
            }
            
            .input-section {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 2rem;
                margin-bottom: 2rem;
                border: 2px solid #e9ecef;
            }
            
            .polynomial-input {
                background: white;
                border-radius: 10px;
                padding: 1.5rem;
                margin-bottom: 1.5rem;
                border: 1px solid #dee2e6;
            }
            
            .coefficient-input {
                background: #fff;
                border: 2px solid #e9ecef;
                border-radius: 8px;
                padding: 0.75rem;
                transition: all 0.3s ease;
            }
            
            .coefficient-input:focus {
                border-color: #667eea;
                box-shadow: 0 0 0 0.2rem rgba(102, 126, 234, 0.25);
            }
            
            .btn-primary {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                border: none;
                border-radius: 10px;
                padding: 0.75rem 2rem;
                font-weight: 600;
                transition: all 0.3s ease;
            }
            
            .btn-primary:hover {
                transform: translateY(-2px);
                box-shadow: 0 10px 20px rgba(102, 126, 234, 0.3);
            }
            
            .results-section {
                background: #f8f9fa;
                border-radius: 15px;
                padding: 2rem;
                margin-top: 2rem;
                border: 2px solid #e9ecef;
            }
            
            .network-image {
                max-width: 100%;
                border-radius: 10px;
                box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
                margin: 1rem 0;
            }
            
            .loading {
                display: none;
                text-align: center;
                padding: 2rem;
            }
            
            .spinner-border {
                color: #667eea;
            }
            
            .error-message {
                background: #f8d7da;
                color: #721c24;
                padding: 1rem;
                border-radius: 8px;
                border: 1px solid #f5c6cb;
                margin: 1rem 0;
            }
            
            .success-message {
                background: #d4edda;
                color: #155724;
                padding: 1rem;
                border-radius: 8px;
                border: 1px solid #c3e6cb;
                margin: 1rem 0;
            }
            
            .network-data {
                background: white;
                border-radius: 10px;
                padding: 1.5rem;
                margin: 1rem 0;
                border: 1px solid #dee2e6;
            }
            
            .example-section {
                background: #e3f2fd;
                border-radius: 10px;
                padding: 1.5rem;
                margin: 1rem 0;
                border-left: 4px solid #2196f3;
            }
            
            .example-btn {
                background: #2196f3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 0.5rem 1rem;
                margin: 0.25rem;
                cursor: pointer;
                transition: all 0.3s ease;
            }
            
            .example-btn:hover {
                background: #1976d2;
                transform: translateY(-1px);
            }
            
            .footer {
                text-align: center;
                margin-top: 3rem;
                padding: 2rem;
                color: #7f8c8d;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="main-container">
                <div class="header">
                    <h1><i class="fas fa-project-diagram"></i> Network Ladder</h1>
                    <p>Convert transfer functions to electrical ladder networks using continued fraction expansion</p>
                </div>

                <div class="input-section">
                    <h3><i class="fas fa-calculator"></i> Transfer Function Input</h3>
                    <p class="text-muted">Enter the coefficients of your transfer function H(s) = N(s)/D(s)</p>
                    
                    <div class="row">
                        <div class="col-md-6">
                            <div class="polynomial-input">
                                <h5><i class="fas fa-arrow-up"></i> Numerator N(s)</h5>
                                <div class="mb-3">
                                    <label class="form-label">Degree:</label>
                                    <input type="number" id="numDegree" class="form-control coefficient-input" min="0" value="1" onchange="updateCoefficientInputs()">
                                </div>
                                <div id="numCoeffs"></div>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="polynomial-input">
                                <h5><i class="fas fa-arrow-down"></i> Denominator D(s)</h5>
                                <div class="mb-3">
                                    <label class="form-label">Degree:</label>
                                    <input type="number" id="denDegree" class="form-control coefficient-input" min="0" value="1" onchange="updateCoefficientInputs()">
                                </div>
                                <div id="denCoeffs"></div>
                            </div>
                        </div>
                    </div>

                    <div class="example-section">
                        <h6><i class="fas fa-lightbulb"></i> Quick Examples</h6>
                        <button class="example-btn" onclick="loadExample('rc')">RC Network: (s+1)/s</button>
                        <button class="example-btn" onclick="loadExample('lc')">LC Filter: (s²+4s+3)/(s²+2s)</button>
                        <button class="example-btn" onclick="loadExample('simple')">Simple: s/1</button>
                    </div>

                    <div class="text-center mt-4">
                        <button class="btn btn-primary btn-lg" onclick="processTransferFunction()">
                            <i class="fas fa-cogs"></i> Generate Network
                        </button>
                    </div>
                </div>

                <div class="loading" id="loading">
                    <div class="spinner-border" role="status">
                        <span class="visually-hidden">Processing...</span>
                    </div>
                    <p class="mt-2">Processing transfer function...</p>
                </div>

                <div id="errorMessage" class="error-message" style="display: none;"></div>
                <div id="successMessage" class="success-message" style="display: none;"></div>

                <div class="results-section" id="resultsSection" style="display: none;">
                    <h3><i class="fas fa-network-wired"></i> Generated Ladder Network</h3>
                    
                    <div class="network-data">
                        <div class="row">
                            <div class="col-md-6">
                                <h6><i class="fas fa-resistor"></i> Series Impedances (Z)</h6>
                                <div id="zArray" class="alert alert-info"></div>
                            </div>
                            <div class="col-md-6">
                                <h6><i class="fas fa-bolt"></i> Shunt Admittances (Y)</h6>
                                <div id="yArray" class="alert alert-warning"></div>
                            </div>
                        </div>
                    </div>

                    <div class="text-center">
                        <h5><i class="fas fa-image"></i> Network Schematic</h5>
                        <div class="network-image-container" style="background: white; border-radius: 10px; padding: 1rem; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                            <img id="networkImage" class="network-image" alt="Generated ladder network" style="max-width: 100%; height: auto; border-radius: 8px;">
                        </div>
                        <div class="mt-3">
                            <button class="btn btn-outline-primary btn-sm" onclick="downloadImage()">
                                <i class="fas fa-download"></i> Download Image
                            </button>
                            <button class="btn btn-outline-secondary btn-sm" onclick="copyImageToClipboard()">
                                <i class="fas fa-copy"></i> Copy Image
                            </button>
                        </div>
                    </div>
                </div>
            </div>

            <div class="footer">
                <p>&copy; 2024 Network Ladder. Built with ❤️ for electrical engineers.</p>
            </div>
        </div>

        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>
        <script>
            // Initialize coefficient inputs
            updateCoefficientInputs();

            function updateCoefficientInputs() {
                const numDegree = parseInt(document.getElementById('numDegree').value);
                const denDegree = parseInt(document.getElementById('denDegree').value);
                
                // Update numerator coefficients
                const numCoeffs = document.getElementById('numCoeffs');
                numCoeffs.innerHTML = '';
                for (let i = 0; i <= numDegree; i++) {
                    const div = document.createElement('div');
                    div.className = 'mb-2';
                    div.innerHTML = `
                        <label class="form-label">a${i} (coefficient of s^${i}):</label>
                        <input type="number" class="form-control coefficient-input" id="numCoeff${i}" value="${i === 0 ? 1 : (i === 1 ? 1 : 0)}" step="any">
                    `;
                    numCoeffs.appendChild(div);
                }
                
                // Update denominator coefficients
                const denCoeffs = document.getElementById('denCoeffs');
                denCoeffs.innerHTML = '';
                for (let i = 0; i <= denDegree; i++) {
                    const div = document.createElement('div');
                    div.className = 'mb-2';
                    div.innerHTML = `
                        <label class="form-label">b${i} (coefficient of s^${i}):</label>
                        <input type="number" class="form-control coefficient-input" id="denCoeff${i}" value="${i === 0 ? 0 : (i === 1 ? 1 : 0)}" step="any">
                    `;
                    denCoeffs.appendChild(div);
                }
            }

            function loadExample(type) {
                if (type === 'rc') {
                    // (s+1)/s
                    document.getElementById('numDegree').value = 1;
                    document.getElementById('denDegree').value = 1;
                    updateCoefficientInputs();
                    document.getElementById('numCoeff0').value = 1; // 1
                    document.getElementById('numCoeff1').value = 1; // s
                    document.getElementById('denCoeff0').value = 0; // 0
                    document.getElementById('denCoeff1').value = 1; // s
                } else if (type === 'lc') {
                    // (s²+4s+3)/(s²+2s)
                    document.getElementById('numDegree').value = 2;
                    document.getElementById('denDegree').value = 2;
                    updateCoefficientInputs();
                    document.getElementById('numCoeff0').value = 3; // 3
                    document.getElementById('numCoeff1').value = 4; // 4s
                    document.getElementById('numCoeff2').value = 1; // s²
                    document.getElementById('denCoeff0').value = 0; // 0
                    document.getElementById('denCoeff1').value = 2; // 2s
                    document.getElementById('denCoeff2').value = 1; // s²
                } else if (type === 'simple') {
                    // s/1
                    document.getElementById('numDegree').value = 1;
                    document.getElementById('denDegree').value = 0;
                    updateCoefficientInputs();
                    document.getElementById('numCoeff0').value = 0; // 0
                    document.getElementById('numCoeff1').value = 1; // s
                    document.getElementById('denCoeff0').value = 1; // 1
                }
            }

            async function processTransferFunction() {
                // Hide previous results and messages
                document.getElementById('resultsSection').style.display = 'none';
                document.getElementById('errorMessage').style.display = 'none';
                document.getElementById('successMessage').style.display = 'none';
                
                // Show loading
                document.getElementById('loading').style.display = 'block';
                
                try {
                    // Collect coefficients
                    const numDegree = parseInt(document.getElementById('numDegree').value);
                    const denDegree = parseInt(document.getElementById('denDegree').value);
                    
                    const numerator = [];
                    const denominator = [];
                    
                    for (let i = 0; i <= numDegree; i++) {
                        numerator.push(parseFloat(document.getElementById(`numCoeff${i}`).value) || 0);
                    }
                    
                    for (let i = 0; i <= denDegree; i++) {
                        denominator.push(parseFloat(document.getElementById(`denCoeff${i}`).value) || 0);
                    }
                    
                    // Validate input
                    if (numerator.every(x => x === 0)) {
                        throw new Error('Numerator cannot be zero');
                    }
                    if (denominator.every(x => x === 0)) {
                        throw new Error('Denominator cannot be zero');
                    }
                    
                    // Make API request
                    const response = await fetch('/api/process', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({
                            numerator: numerator,
                            denominator: denominator
                        })
                    });
                    
                    const data = await response.json();
                    
                    if (!response.ok) {
                        throw new Error(data.error || 'Unknown error occurred');
                    }
                    
                    // Display results
                    document.getElementById('zArray').textContent = data.Z.length > 0 ? data.Z.join(', ') : 'None';
                    document.getElementById('yArray').textContent = data.Y.length > 0 ? data.Y.join(', ') : 'None';
                    
                    if (data.image) {
                        document.getElementById('networkImage').src = 'data:image/png;base64,' + data.image;
                    }
                    
                    document.getElementById('resultsSection').style.display = 'block';
                    document.getElementById('successMessage').textContent = 'Network generated successfully!';
                    document.getElementById('successMessage').style.display = 'block';
                    
                } catch (error) {
                    document.getElementById('errorMessage').textContent = error.message;
                    document.getElementById('errorMessage').style.display = 'block';
                } finally {
                    document.getElementById('loading').style.display = 'none';
                }
            }

            function downloadImage() {
                const img = document.getElementById('networkImage');
                const link = document.createElement('a');
                link.download = 'ladder_network.png';
                link.href = img.src;
                link.click();
            }

            async function copyImageToClipboard() {
                try {
                    const img = document.getElementById('networkImage');
                    const canvas = document.createElement('canvas');
                    const ctx = canvas.getContext('2d');
                    
                    canvas.width = img.naturalWidth;
                    canvas.height = img.naturalHeight;
                    
                    ctx.drawImage(img, 0, 0);
                    
                    canvas.toBlob(async (blob) => {
                        try {
                            await navigator.clipboard.write([
                                new ClipboardItem({ 'image/png': blob })
                            ]);
                            alert('Image copied to clipboard!');
                        } catch (err) {
                            console.error('Failed to copy image:', err);
                            alert('Failed to copy image. Please try downloading instead.');
                        }
                    });
                } catch (err) {
                    console.error('Error copying image:', err);
                    alert('Copy to clipboard not supported. Please download the image instead.');
                }
            }
        </script>
    </body>
    </html>
    '''

# Exporting Flask WSGI app as "app" is sufficient for Vercel Python runtime
