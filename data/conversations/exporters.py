"""
Conversation Exporters - Export conversations in various formats
"""

import json
import csv
from typing import List, Dict, Any
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

class ConversationExporter:
    """Export conversations in different formats"""
    
    @staticmethod
    async def export_to_json(conversations: List[Dict[str, Any]], session_id: str) -> str:
        """Export to JSON format"""
        export_data = {
            "session_id": session_id,
            "export_date": datetime.now().isoformat(),
            "total_messages": len(conversations),
            "conversations": conversations
        }
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    @staticmethod
    async def export_to_txt(conversations: List[Dict[str, Any]], session_id: str) -> str:
        """Export to plain text format"""
        lines = [
            "=" * 60,
            f"JARVIS Conversation Export",
            f"Session ID: {session_id}",
            f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Total Messages: {len(conversations)}",
            "=" * 60,
            ""
        ]
        
        for msg in conversations:
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")
            
            lines.append(f"[{timestamp}] {role}:")
            lines.append(content)
            lines.append("-" * 40)
            lines.append("")
        
        return "\n".join(lines)
    
    @staticmethod
    async def export_to_csv(conversations: List[Dict[str, Any]], session_id: str) -> str:
        """Export to CSV format"""
        import io
        
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["Timestamp", "Role", "Content", "ID"])
        
        # Write data
        for msg in conversations:
            writer.writerow([
                msg.get("timestamp", ""),
                msg.get("role", ""),
                msg.get("content", ""),
                msg.get("id", "")
            ])
        
        return output.getvalue()
    
    @staticmethod
    async def export_to_html(conversations: List[Dict[str, Any]], session_id: str) -> str:
        """Export to HTML format"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>JARVIS Conversation Export - {session_id}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            max-width: 900px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            margin-bottom: 20px;
        }}
        .message {{
            margin-bottom: 15px;
            padding: 15px;
            border-radius: 10px;
            animation: fadeIn 0.5s ease;
        }}
        .user {{
            background: #e3f2fd;
            border-left: 4px solid #2196f3;
        }}
        .assistant {{
            background: #f3e5f5;
            border-left: 4px solid #9c27b0;
        }}
        .timestamp {{
            font-size: 11px;
            color: #666;
            margin-bottom: 5px;
        }}
        .role {{
            font-weight: bold;
            margin-bottom: 8px;
        }}
        .content {{
            line-height: 1.5;
        }}
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 JARVIS Conversation Export</h1>
        <p>Session ID: {session_id}</p>
        <p>Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Total Messages: {len(conversations)}</p>
    </div>
"""
        
        for msg in conversations:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")
            
            html += f"""
    <div class="message {role}">
        <div class="timestamp">{timestamp}</div>
        <div class="role">{role.upper()}</div>
        <div class="content">{content.replace(chr(10), '<br>')}</div>
    </div>
"""
        
        html += """
</body>
</html>"""
        
        return html
    
    @staticmethod
    async def export_to_pdf(conversations: List[Dict[str, Any]], session_id: str, filename: str) -> str:
        """Export to PDF format"""
        doc = SimpleDocTemplate(filename, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#667eea'),
            spaceAfter=30
        )
        story.append(Paragraph(f"JARVIS Conversation Export - {session_id}", title_style))
        story.append(Spacer(1, 12))
        
        # Metadata
        meta_style = ParagraphStyle(
            'Metadata',
            parent=styles['Normal'],
            fontSize=10,
            textColor=colors.grey
        )
        story.append(Paragraph(f"Export Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", meta_style))
        story.append(Paragraph(f"Total Messages: {len(conversations)}", meta_style))
        story.append(Spacer(1, 20))
        
        # Messages
        for msg in conversations:
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            timestamp = msg.get("timestamp", "")
            
            # Role header
            role_style = ParagraphStyle(
                'Role',
                parent=styles['Heading4'],
                textColor=colors.HexColor('#764ba2') if role == "ASSISTANT" else colors.HexColor('#2196f3')
            )
            story.append(Paragraph(f"{role}:", role_style))
            
            # Timestamp
            story.append(Paragraph(f"<i>{timestamp}</i>", meta_style))
            
            # Content
            story.append(Paragraph(content, styles['Normal']))
            story.append(Spacer(1, 12))
        
        doc.build(story)
        return filename