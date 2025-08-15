#!/usr/bin/env python3
"""
Create a PNG architecture diagram for APIM integration
"""

try:
    from PIL import Image, ImageDraw, ImageFont
    import os
    
    # Create a new image
    width, height = 1200, 800
    img = Image.new('RGB', (width, height), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a system font, fallback to default
    try:
        font_title = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 16)
        font_medium = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 12)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 10)
    except:
        font_title = ImageFont.load_default()
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
        font_small = ImageFont.load_default()
    
    # Colors
    colors = {
        'client': '#e3f2fd',
        'apim': '#f3e5f5',
        'container': '#e8f5e8',
        'ai': '#fff3e0',
        'search': '#fff8e1',
        'monitor': '#fce4ec',
        'border': '#333333',
        'text': '#333333',
        'arrow': '#666666'
    }
    
    # Title
    title_text = "Enterprise AI Agent with Azure API Management"
    title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_width) // 2, 20), title_text, fill=colors['text'], font=font_title)
    
    # Draw components
    components = [
        {'name': 'External Clients', 'pos': (50, 100), 'size': (150, 80), 'color': colors['client'], 'details': ['Mobile Apps', 'Web Apps', 'APIs']},
        {'name': 'Azure API Management', 'pos': (300, 80), 'size': (200, 120), 'color': colors['apim'], 'details': ['Subscription Auth', 'Rate Limiting', 'Request Transform', 'Analytics']},
        {'name': 'Container Apps', 'pos': (600, 80), 'size': (200, 120), 'color': colors['container'], 'details': ['FastAPI Backend', 'Auto-scaling', 'Managed Identity', 'React Frontend']},
        {'name': 'Azure AI Services', 'pos': (450, 280), 'size': (180, 100), 'color': colors['ai'], 'details': ['GPT-4o-mini', 'Chat Completion', 'Text Generation']},
        {'name': 'Azure AI Search', 'pos': (700, 280), 'size': (180, 100), 'color': colors['search'], 'details': ['RAG Knowledge', 'Semantic Search', 'Vector Embeddings']},
        {'name': 'Application Insights', 'pos': (950, 80), 'size': (180, 120), 'color': colors['monitor'], 'details': ['Request Tracing', 'Performance Metrics', 'Error Tracking']}
    ]
    
    # Draw component boxes
    for comp in components:
        x, y = comp['pos']
        w, h = comp['size']
        
        # Draw rectangle
        draw.rectangle([x, y, x + w, y + h], fill=comp['color'], outline=colors['border'], width=2)
        
        # Draw component name
        name_bbox = draw.textbbox((0, 0), comp['name'], font=font_large)
        name_width = name_bbox[2] - name_bbox[0]
        draw.text((x + (w - name_width) // 2, y + 10), comp['name'], fill=colors['text'], font=font_large)
        
        # Draw details
        for i, detail in enumerate(comp['details']):
            detail_bbox = draw.textbbox((0, 0), f"• {detail}", font=font_small)
            detail_width = detail_bbox[2] - detail_bbox[0]
            draw.text((x + (w - detail_width) // 2, y + 35 + i * 15), f"• {detail}", fill=colors['text'], font=font_small)
    
    # Draw arrows
    arrows = [
        ((200, 140), (290, 140), 'HTTPS + API Key'),
        ((500, 140), (590, 140), 'Authenticated'),
        ((650, 200), (580, 270), 'AI Query'),
        ((750, 200), (780, 270), 'Search Context'),
        ((500, 120), (940, 120), 'Telemetry'),
        ((800, 140), (940, 140), 'Monitoring')
    ]
    
    for start, end, label in arrows:
        # Draw arrow line
        draw.line([start, end], fill=colors['arrow'], width=2)
        
        # Draw arrowhead
        if end[0] > start[0]:  # Right arrow
            draw.polygon([end, (end[0]-10, end[1]-5), (end[0]-10, end[1]+5)], fill=colors['arrow'])
        
        # Draw label
        mid_x = (start[0] + end[0]) // 2
        mid_y = (start[1] + end[1]) // 2 - 10
        label_bbox = draw.textbbox((0, 0), label, font=font_small)
        label_width = label_bbox[2] - label_bbox[0]
        draw.text((mid_x - label_width // 2, mid_y), label, fill=colors['text'], font=font_small)
    
    # Draw flow steps section
    flow_y = 450
    draw.rectangle([50, flow_y, 1150, flow_y + 300], fill='#ffffff', outline='#dddddd', width=1)
    
    flow_title = "Request Flow with APIM Integration"
    flow_title_bbox = draw.textbbox((0, 0), flow_title, font=font_title)
    flow_title_width = flow_title_bbox[2] - flow_title_bbox[0]
    draw.text(((width - flow_title_width) // 2, flow_y + 20), flow_title, fill=colors['text'], font=font_title)
    
    # Flow steps
    steps = [
        {'num': '1', 'title': 'Client Request', 'desc': 'HTTPS with API Key', 'x': 100},
        {'num': '2', 'title': 'APIM Gateway', 'desc': 'Authentication & Rate Limiting', 'x': 280},
        {'num': '3', 'title': 'FastAPI Processing', 'desc': 'Route to Container App', 'x': 460},
        {'num': '4', 'title': 'Knowledge Search', 'desc': 'Query AI Search for Context', 'x': 640},
        {'num': '5', 'title': 'AI Generation', 'desc': 'GPT-4o-mini Response', 'x': 820},
        {'num': '6', 'title': 'Response & Monitoring', 'desc': 'Return via APIM + Telemetry', 'x': 1000}
    ]
    
    step_y = flow_y + 70
    for i, step in enumerate(steps):
        # Draw circle
        draw.ellipse([step['x']-20, step_y-20, step['x']+20, step_y+20], fill='#1976d2', outline='white', width=2)
        
        # Draw step number
        num_bbox = draw.textbbox((0, 0), step['num'], font=font_large)
        num_width = num_bbox[2] - num_bbox[0]
        draw.text((step['x'] - num_width // 2, step_y - 8), step['num'], fill='white', font=font_large)
        
        # Draw title
        title_bbox = draw.textbbox((0, 0), step['title'], font=font_medium)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text((step['x'] - title_width // 2, step_y + 30), step['title'], fill=colors['text'], font=font_medium)
        
        # Draw description
        desc_bbox = draw.textbbox((0, 0), step['desc'], font=font_small)
        desc_width = desc_bbox[2] - desc_bbox[0]
        draw.text((step['x'] - desc_width // 2, step_y + 50), step['desc'], fill='#666666', font=font_small)
        
        # Draw arrow to next step
        if i < len(steps) - 1:
            next_x = steps[i+1]['x']
            draw.line([(step['x'] + 20, step_y), (next_x - 20, step_y)], fill=colors['arrow'], width=2)
            draw.polygon([(next_x - 20, step_y), (next_x - 30, step_y - 5), (next_x - 30, step_y + 5)], fill=colors['arrow'])
    
    # Add metrics boxes
    metrics_y = flow_y + 150
    metrics = [
        {'title': 'Performance Metrics', 'items': ['Rate Limit: 100/min, 1000/hour', 'Response Time: 3-29ms (health)', 'AI Response: ~6.5s (chat)', 'Success Rate: 100%'], 'x': 70},
        {'title': 'Security Features', 'items': ['Subscription Key Auth', 'Managed Identity', 'HTTPS/TLS Encryption', 'RBAC & Network Security'], 'x': 400},
        {'title': 'Monitoring & Analytics', 'items': ['Real-time Tracing', 'Performance Dashboards', 'Error Tracking & Alerts', 'Usage Analytics'], 'x': 730}
    ]
    
    for metric in metrics:
        # Draw box
        draw.rectangle([metric['x'], metrics_y, metric['x'] + 250, metrics_y + 100], fill='#f5f5f5', outline='#dddddd', width=1)
        
        # Draw title
        title_bbox = draw.textbbox((0, 0), metric['title'], font=font_medium)
        title_width = title_bbox[2] - title_bbox[0]
        draw.text((metric['x'] + (250 - title_width) // 2, metrics_y + 10), metric['title'], fill=colors['text'], font=font_medium)
        
        # Draw items
        for i, item in enumerate(metric['items']):
            draw.text((metric['x'] + 10, metrics_y + 35 + i * 15), f"• {item}", fill='#666666', font=font_small)
    
    # Save the image
    output_path = '/workspaces/get-started-with-ai-agents-with-apim/docs/images/apim-architecture-flow.png'
    img.save(output_path, 'PNG', quality=95)
    print(f"Architecture diagram saved to: {output_path}")
    
except ImportError:
    print("PIL (Pillow) not available. Installing...")
    import subprocess
    subprocess.run(['/workspaces/get-started-with-ai-agents-with-apim/.venv/bin/pip', 'install', 'Pillow'])
    print("Please run the script again after Pillow installation.")
except Exception as e:
    print(f"Error creating PNG diagram: {e}")
    print("The SVG version is available and will work in most modern browsers.")
