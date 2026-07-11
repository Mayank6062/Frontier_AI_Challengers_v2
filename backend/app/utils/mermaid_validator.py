"""
Mermaid Diagram Validation Utility
 
Validates Mermaid syntax to ensure diagrams render correctly.
Checks for common syntax errors that cause rendering failures.
"""
 
import re
from typing import List, Tuple, Optional
 
 
class MermaidValidationError(Exception):
    """Raised when Mermaid diagram validation fails"""
    pass
 
 
def validate_mermaid_diagram(mermaid_code: str) -> Tuple[bool, List[str]]:
    """
    Validate Mermaid diagram syntax comprehensively for enterprise rendering.
   
    Checks for:
    - Duplicate node IDs
    - Missing node IDs referenced in edges
    - Invalid arrow syntax
    - Unsupported syntax
    - Invalid classDef
    - Invalid styles
    - Nested subgraphs (causes rendering failures)
    - Missing END statements
    - Unmatched brackets/quotes
    - Invalid node names (reserved keywords, special chars)
    - Reserved keywords misuse
    - Unsupported HTML/Markdown/Unicode
    - Node/edge count limits
   
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    warnings = []
   
    if not mermaid_code or not mermaid_code.strip():
        errors.append("CRITICAL: Empty Mermaid diagram")
        return False, errors
   
    lines = mermaid_code.strip().split('\n')
   
    # 1. Check for valid diagram type
    first_line = lines[0].strip().lower()
    valid_diagram_types = [
        'graph', 'flowchart', 'sequencediagram', 'classdiagram',
        'statediagram', 'erdiagram', 'journey', 'gantt', 'pie',
        'gitgraph', 'c4context', 'mindmap', 'timeline', 'quadrantchart'
    ]
   
    has_valid_type = any(first_line.startswith(t) for t in valid_diagram_types)
    if not has_valid_type:
        errors.append(f"CRITICAL: Invalid or missing diagram type. Found: '{first_line[:60]}'")
        return False, errors
   
    # 2. Extract node IDs and check for duplicates and validity
    node_ids = set()
    node_pattern = r'\b([A-Za-z0-9_]+)[\[\(\{]'
    reserved_keywords = {'subgraph', 'end', 'class', 'style', 'classDef', 'graph', 'flowchart'}
   
    for line_num, line in enumerate(lines[1:], start=2):
        # Skip comments, style definitions, and class definitions
        stripped = line.strip()
        if stripped.startswith('%%') or stripped.startswith('classDef') or stripped.startswith('style '):
            continue
           
        # Find node definitions
        matches = re.findall(node_pattern, line)
        for node_id in matches:
            # Check for reserved keywords
            if node_id.lower() in reserved_keywords:
                errors.append(f"CRITICAL: Reserved keyword '{node_id}' used as node ID on line {line_num}")
           
            # Check for invalid characters (must be alphanumeric + underscore only)
            if not re.match(r'^[A-Za-z][A-Za-z0-9_]*$', node_id):
                errors.append(f"CRITICAL: Invalid node ID '{node_id}' on line {line_num} (must start with letter, contain only alphanumeric and underscore)")
           
            # Check for duplicates
            if node_id in node_ids:
                errors.append(f"CRITICAL: Duplicate node ID '{node_id}' on line {line_num}")
            node_ids.add(node_id)
   
    if len(node_ids) == 0:
        errors.append("CRITICAL: No nodes found in diagram")
        return False, errors
   
    # 3. Check for unmatched brackets and quotes
    bracket_checks = [
        (r'\[', r'\]', 'square brackets'),
        (r'\(', r'\)', 'parentheses'),
        (r'\{', r'\}', 'curly braces'),
    ]
   
    for open_char, close_char, name in bracket_checks:
        # Count while excluding escaped ones
        open_count = len([m for m in re.finditer(open_char, mermaid_code) if mermaid_code[max(0, m.start()-1):m.start()] != '\\'])
        close_count = len([m for m in re.finditer(close_char, mermaid_code) if mermaid_code[max(0, m.start()-1):m.start()] != '\\'])
        if open_count != close_count:
            errors.append(f"CRITICAL: Mismatched {name}: {open_count} opening, {close_count} closing")
   
    # Check for unmatched quotes
    single_quotes = len(re.findall(r"(?<!\\)'", mermaid_code)) % 2
    double_quotes = len(re.findall(r'(?<!\\)"', mermaid_code)) % 2
    if single_quotes != 0:
        errors.append("CRITICAL: Unmatched single quotes detected")
    if double_quotes != 0:
        errors.append("CRITICAL: Unmatched double quotes detected")
   
    # 4. Check for unclosed subgraphs and detect nested subgraphs
    subgraph_count = len(re.findall(r'\bsubgraph\b', mermaid_code, re.IGNORECASE))
    end_count = len(re.findall(r'\bend\b', mermaid_code, re.IGNORECASE))
   
    if subgraph_count > 4:
        errors.append(f"CRITICAL: Too many subgraphs ({subgraph_count}). Maximum: 4. Use subgraphs only for major architectural layers.")
   
    if subgraph_count > end_count:
        errors.append(f"CRITICAL: Unclosed subgraph: {subgraph_count} subgraphs, {end_count} ends")
    elif subgraph_count < end_count:
        errors.append(f"CRITICAL: Too many 'end' statements: {subgraph_count} subgraphs, {end_count} ends")
   
    # Check for nested subgraphs (subgraph inside subgraph) - VERY problematic
    subgraph_depth = 0
    max_depth = 0
    for line in lines:
        if re.search(r'\bsubgraph\b', line, re.IGNORECASE):
            subgraph_depth += 1
            max_depth = max(max_depth, subgraph_depth)
        if re.search(r'\bend\b', line, re.IGNORECASE):
            subgraph_depth -= 1
   
    if max_depth > 1:
        errors.append(f"CRITICAL: Nested subgraphs detected (depth={max_depth}). Subgraphs MUST be flat (no nesting). This WILL cause rendering failures.")
   
    # 5. Check for invalid arrow syntax
    # We standardize on --> and allow --- for undirected, but reject complex arrows
    problematic_arrows = [
        (r'--->', 'arrow ---> should be -->'),
        (r'<---', 'arrow <--- should be <--'),
        (r'====>', 'thick arrow ====> should be -->'),
        (r'<====', 'thick arrow <==== should be <--'),
        (r'\.\.\.>', 'dotted arrow ...> should be -.->'),
        (r'<\.\.\.', 'dotted arrow <... should be <-.'),
        (r'~~>', 'wavy arrow ~~> not supported, use -->'),
        (r'<~~', 'wavy arrow <~~ not supported, use <--'),
    ]
   
    for pattern, msg in problematic_arrows:
        matches = re.findall(pattern, mermaid_code)
        if matches:
            errors.append(f"CRITICAL: Invalid arrow syntax '{matches[0]}' - {msg}")
   
    # 6. Check for HTML tags inside node labels (causes rendering issues)
    html_pattern = r'[\[\(\{][^\]\)\}]*<[a-zA-Z/][^>]*>[^\]\)\}]*[\]\)\}]'
    if re.search(html_pattern, mermaid_code):
        errors.append("CRITICAL: HTML tags detected inside node labels (e.g., <div>, <br>, <span>). Remove all HTML.")
   
    # 7. Check for Markdown syntax in labels (can cause issues)
    markdown_patterns = [
        (r'\*\*[^\*]+\*\*', 'bold **text**'),
        (r'\*[^\*]+\*', 'italic *text*'),
        (r'~~[^~]+~~', 'strikethrough ~~text~~'),
        (r'`[^`]+`', 'code `text`'),
    ]
    for pattern, syntax in markdown_patterns:
        if re.search(pattern, mermaid_code):
            warnings.append(f"WARNING: Markdown {syntax} detected in labels. May cause rendering issues.")
   
    # 8. Check for problematic Unicode characters
    try:
        mermaid_code.encode('ascii')
    except UnicodeEncodeError:
        non_ascii = [c for c in mermaid_code if ord(c) > 127]
        unique_non_ascii = list(set(non_ascii))
        if len(unique_non_ascii) > 10:
            warnings.append(f"WARNING: {len(unique_non_ascii)} unique non-ASCII characters detected. May cause rendering issues in some environments.")
        # Check specifically for emoji
        emoji_pattern = re.compile("["
            u"\U0001F600-\U0001F64F"  # emoticons
            u"\U0001F300-\U0001F5FF"  # symbols & pictographs
            u"\U0001F680-\U0001F6FF"  # transport & map
            u"\U0001F1E0-\U0001F1FF"  # flags
            u"\U00002702-\U000027B0"
            u"\U000024C2-\U0001F251"
            "]+", flags=re.UNICODE)
        if emoji_pattern.search(mermaid_code):
            errors.append("CRITICAL: Emoji detected in diagram. Remove all emoji characters.")
   
    # 9. Check for invalid characters in node IDs (detailed check)
    invalid_id_pattern = r'\b([^\s\[\(\{:\-\.\>]+[\s\[\(\{])'
    for line_num, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith('%%') or stripped.startswith('classDef') or stripped.startswith('style '):
            continue
        # Look for node IDs with invalid chars
        if re.search(r'[A-Za-z0-9_]+[^A-Za-z0-9_\s\[\(\{:\-\.\>]+[A-Za-z0-9_]*\s*[\[\(\{]', line):
            warnings.append(f"WARNING: Suspicious characters in node ID on line {line_num}: '{line.strip()[:60]}'")
   
    # 10. Validate classDef syntax and usage
    class_pattern = r'classDef\s+(\w+)\s+([^;\n]+)'
    defined_classes = {}
    for line_num, line in enumerate(lines, start=1):
        matches = re.findall(class_pattern, line)
        for cls_name, cls_def in matches:
            # Check for required styling properties
            if not any(prop in cls_def for prop in ['fill', 'stroke', 'color']):
                warnings.append(f"WARNING: classDef '{cls_name}' on line {line_num} missing styling properties (fill, stroke, color)")
            defined_classes[cls_name] = line_num
   
    # 11. Check for class assignments without definitions
    class_assignments = re.findall(r':::(\w+)', mermaid_code)
    undefined_classes = set()
    for cls in class_assignments:
        if cls not in defined_classes:
            undefined_classes.add(cls)
   
    if undefined_classes:
        errors.append(f"CRITICAL: Classes used but not defined: {', '.join(sorted(undefined_classes))}")
   
    # 12. Check for node/edge count (CRITICAL for enterprise readability and minimum complexity)
    node_count = len(node_ids)
    edge_pattern = r'[A-Za-z0-9_]+\s*(?:-->|<--|---|->|<-|\-\.\->|<\.-|\.\->|<\.-!>|o--o|<\.\.>|\|.*?\||==|==>|<==|x--x)\s*[A-Za-z0-9_]+'
    edge_count = len(re.findall(edge_pattern, mermaid_code))
   
    # ENFORCE MINIMUM COMPLEXITY (Enterprise requirement)
    if node_count < 8:
        errors.append(f"CRITICAL: Too few nodes ({node_count}). Enterprise diagrams require MINIMUM 8 nodes. Add more detail.")
    elif node_count < 10:
        warnings.append(f"WARNING: Low node count ({node_count}). Recommended: 10-14 for optimal enterprise communication.")
   
    if edge_count < 7:
        errors.append(f"CRITICAL: Too few edges ({node_count}). Enterprise diagrams require MINIMUM 7 edges showing relationships.")
   
    # ENFORCE MAXIMUM LIMITS
    if node_count > 18:
        errors.append(f"CRITICAL: Too many nodes ({node_count}). Maximum: 18. MUST split into multiple diagrams.")
    elif node_count > 14:
        warnings.append(f"WARNING: High node count ({node_count}). Recommended: 10-14 for optimal readability.")
   
    if edge_count > 30:
        errors.append(f"CRITICAL: Too many edges ({edge_count}). Maximum: 30. MUST simplify or split diagram.")
    elif edge_count > 20:
        warnings.append(f"WARNING: High edge count ({edge_count}). Recommended: 15-20 for optimal clarity.")
   
    # 12a. Check for business-friendly labels (Azure services should have purposes)
    # Look for labels without <br/> - these might be abbreviations or generic names
    label_without_purpose_pattern = r'[\[\(\{]"([A-Za-z0-9\s]{3,30})"[\]\)\}]'
    labels_needing_purpose = []
    for line_num, line in enumerate(lines, start=1):
        if line.strip().startswith('%%') or line.strip().startswith('classDef'):
            continue
        matches = re.findall(label_without_purpose_pattern, line)
        for label in matches:
            # Check if it looks like an Azure service or common abbreviation
            if any(keyword in label.lower() for keyword in ['azure', 'service', 'api', 'database', 'storage', 'monitor']):
                if '<br/>' not in line:
                    labels_needing_purpose.append((line_num, label))
   
    if labels_needing_purpose:
        for line_num, label in labels_needing_purpose[:3]:  # Show first 3
            warnings.append(f"WARNING: Node '{label}' on line {line_num} should include business purpose. Use: '{label}<br/>(Purpose)'")
   
    # 12b. Check for common abbreviations that should be spelled out
    common_abbreviations = {
        'ADF': 'Azure Data Factory',
        'APIM': 'Azure API Management',
        'AuthSvc': 'Authentication Service',
        'API GW': 'API Gateway',
        'DB': 'Database',
        'DW': 'Data Warehouse',
    }
    for abbrev, full_name in common_abbreviations.items():
        # Look for abbreviation in node labels
        abbrev_pattern = rf'[\[\(\{{]"?{re.escape(abbrev)}"?[\]\)\}}]'
        if re.search(abbrev_pattern, mermaid_code):
            warnings.append(f"WARNING: Abbreviation '{abbrev}' detected. Use full name: '{full_name}' with business purpose.")
   
   
    # 13. Check for edge references to undefined nodes (CRITICAL)
    edge_ref_pattern = r'([A-Za-z0-9_]+)\s*(?:-->|<--|---|->|<-|\-\.\->|<\.-)\s*([A-Za-z0-9_]+)'
    for line_num, line in enumerate(lines, start=1):
        if line.strip().startswith('%%') or line.strip().startswith('classDef') or line.strip().startswith('style '):
            continue
       
        edges = re.findall(edge_ref_pattern, line)
        for source, target in edges:
            if source not in node_ids and source.lower() not in reserved_keywords:
                errors.append(f"CRITICAL: Edge on line {line_num} references undefined source node '{source}'")
            if target not in node_ids and target.lower() not in reserved_keywords:
                errors.append(f"CRITICAL: Edge on line {line_num} references undefined target node '{target}'")
   
    # 14. Check for long node labels (readability issue)
    label_pattern = r'[\[\(\{]([^\]\)\}]{40,})[\]\)\}]'
    long_labels = re.findall(label_pattern, mermaid_code)
    if long_labels:
        warnings.append(f"WARNING: {len(long_labels)} node(s) with labels longer than 40 characters. Keep labels concise (3-20 chars ideal).")
   
    # 15. Check for empty node labels
    empty_label_pattern = r'[A-Za-z0-9_]+\s*[\[\(\{]\s*[\]\)\}]'
    if re.search(empty_label_pattern, mermaid_code):
        warnings.append("WARNING: Empty node labels detected. All nodes should have meaningful labels.")
   
    # Combine errors and warnings
    all_issues = errors + warnings
    is_valid = len(errors) == 0  # Valid if no critical errors
   
    return is_valid, all_issues
 
 
def validate_drawio_xml(xml_content: str) -> Tuple[bool, List[str]]:
    """
    Validate Draw.io XML structure.
   
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
   
    if not xml_content or not xml_content.strip():
        errors.append("Empty Draw.io XML")
        return False, errors
   
    # Check for required elements
    required_elements = ['mxGraphModel', 'root', 'mxCell']
    for element in required_elements:
        if element not in xml_content:
            errors.append(f"Missing required XML element: {element}")
   
    # Check for balanced tags
    open_tags = re.findall(r'<(\w+)(?:\s|>)', xml_content)
    close_tags = re.findall(r'</(\w+)>', xml_content)
   
    for tag in set(open_tags):
        if tag in ['mxGraphModel', 'root', 'mxCell', 'diagram']:
            open_count = open_tags.count(tag)
            close_count = close_tags.count(tag)
            # Account for self-closing tags
            self_closing = len(re.findall(f'<{tag}[^>]*/>', xml_content))
            if open_count != close_count + self_closing:
                errors.append(f"Mismatched XML tags for '{tag}': {open_count} open, {close_count} close")
   
    # Check for valid mxGraphModel structure
    if 'mxGraphModel' in xml_content:
        if '<root>' not in xml_content:
            errors.append("mxGraphModel missing <root> element")
       
        # Check for required mxCell id="0" and id="1"
        if 'mxCell id="0"' not in xml_content:
            errors.append("Missing root mxCell with id='0'")
        if 'mxCell id="1"' not in xml_content:
            errors.append("Missing default parent mxCell with id='1'")
   
    # Check for invalid characters
    if re.search(r'[^\x00-\x7F\u0080-\uFFFF]', xml_content):
        errors.append("Invalid characters detected in XML")
   
    is_valid = len(errors) == 0
    return is_valid, errors
 
 
def sanitize_mermaid_code(mermaid_code: str) -> str:
    """
    Aggressively auto-fix common Mermaid syntax issues for enterprise rendering.
   
    Fixes:
    - Arrow syntax normalization
    - HTML tag removal
    - Subgraph removal (they cause rendering failures)
    - Excessive whitespace
    - Long node labels (truncate)
    - Reserved keyword conflicts
   
    Returns:
        Cleaned and fixed Mermaid code
    """
    if not mermaid_code or not mermaid_code.strip():
        return mermaid_code
   
    # Remove markdown fences if present
    mermaid_code = re.sub(r'```mermaid\s*\n', '', mermaid_code, flags=re.IGNORECASE)
    mermaid_code = re.sub(r'```\s*$', '', mermaid_code, flags=re.MULTILINE)
   
    # Remove multiple consecutive blank lines
    mermaid_code = re.sub(r'\n\s*\n\s*\n+', '\n\n', mermaid_code)
   
    # Fix common arrow mistakes - normalize to --> and --- only
    arrow_replacements = [
        ('--->', '-->'),
        ('<---', '<--'),
        ('====>', '-->'),
        ('<====', '<--'),
        ('===>', '-->'),
        ('<===', '<--'),
        ('...>', '-->'),
        ('<...', '<--'),
        ('..>', '-->'),
        ('<..', '<--'),
        ('~~>', '-->'),
        ('<~~', '<--'),
        ('~>', '-->'),
        ('<~', '<--'),
        ('==>', '-->'),
        ('<==', '<--'),
        ('=>', '-->'),
        ('<=', '<--'),
    ]
    for old, new in arrow_replacements:
        mermaid_code = mermaid_code.replace(old, new)
   
    # Remove HTML tags from labels (preserve text content)
    mermaid_code = re.sub(r'<br\s*/?\s*>', ' ', mermaid_code, flags=re.IGNORECASE)
    mermaid_code = re.sub(r'<[^>]+>', '', mermaid_code)
   
    # Remove Markdown bold/italic from labels
    mermaid_code = re.sub(r'\*\*([^\*]+)\*\*', r'\1', mermaid_code)  # **bold**
    mermaid_code = re.sub(r'\*([^\*]+)\*', r'\1', mermaid_code)      # *italic*
    mermaid_code = re.sub(r'~~([^~]+)~~', r'\1', mermaid_code)        # ~~strikethrough~~
   
    # Remove emoji and problematic Unicode
    emoji_pattern = re.compile("["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map
        u"\U0001F1E0-\U0001F1FF"  # flags
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        "]+", flags=re.UNICODE)
    mermaid_code = emoji_pattern.sub('', mermaid_code)
   
    # Fix nested subgraphs (keep subgraphs but flatten nesting)
    # Strategy: Keep only top-level subgraphs, remove nested ones
    lines = mermaid_code.split('\n')
    filtered_lines = []
    subgraph_depth = 0
    subgraph_labels = {}
   
    for line in lines:
        stripped = line.strip().lower()
       
        # Track subgraph entry
        if stripped.startswith('subgraph'):
            if subgraph_depth == 0:
                # Top-level subgraph - keep it
                filtered_lines.append(line)
                match = re.search(r'subgraph\s+(.+)', line, re.IGNORECASE)
                if match:
                    subgraph_labels[subgraph_depth] = match.group(1).strip()
            else:
                # Nested subgraph - remove it but keep a comment
                match = re.search(r'subgraph\s+(.+)', line, re.IGNORECASE)
                nested_label = match.group(1).strip() if match else 'unnamed'
                filtered_lines.append(f'%% Nested subgraph removed: {nested_label}')
            subgraph_depth += 1
            continue
       
        # Track subgraph exit
        if stripped == 'end':
            subgraph_depth -= 1
            if subgraph_depth >= 0:
                # Only keep 'end' for top-level subgraphs
                filtered_lines.append(line)
            continue
       
        # Keep all other lines
        filtered_lines.append(line)
   
    mermaid_code = '\n'.join(filtered_lines)
   
    # Limit subgraph count to 4 (enterprise architecture best practice)
    subgraph_count = len(re.findall(r'\bsubgraph\b', mermaid_code, re.IGNORECASE))
    if subgraph_count > 4:
        # Remove excess subgraphs, keeping first 4
        lines = mermaid_code.split('\n')
        filtered_lines = []
        current_subgraph_count = 0
        in_excess_subgraph = False
       
        for line in lines:
            stripped = line.strip().lower()
           
            if stripped.startswith('subgraph'):
                current_subgraph_count += 1
                if current_subgraph_count <= 4:
                    filtered_lines.append(line)
                    in_excess_subgraph = False
                else:
                    in_excess_subgraph = True
                    match = re.search(r'subgraph\s+(.+)', line, re.IGNORECASE)
                    label = match.group(1).strip() if match else 'unnamed'
                    filtered_lines.append(f'%% Excess subgraph removed (max 4): {label}')
                continue
           
            if stripped == 'end' and in_excess_subgraph:
                in_excess_subgraph = False
                continue
           
            if not in_excess_subgraph:
                filtered_lines.append(line)
       
        mermaid_code = '\n'.join(filtered_lines)
   
    # Ensure proper spacing around arrows for readability
    mermaid_code = re.sub(r'([A-Za-z0-9_\]\)\}])(-->|<--|---)', r'\1 \2', mermaid_code)
    mermaid_code = re.sub(r'(-->|<--|---)([A-Za-z0-9_\[\(\{])', r'\1 \2', mermaid_code)
   
    # Truncate excessively long node labels (keep first 35 chars)
    def truncate_label(match):
        full_match = match.group(0)
        opening = match.group(1)
        label = match.group(2)
        closing = match.group(3)
        if len(label) > 40:
            truncated = label[:35] + '...'
            return f'{opening}{truncated}{closing}'
        return full_match
   
    mermaid_code = re.sub(r'([\[\(\{])([^\]\)\}]{40,})([\]\)\}])', truncate_label, mermaid_code)
   
    # Fix node IDs that might be reserved keywords by appending '1'
    reserved = ['subgraph', 'end', 'class', 'style', 'classDef', 'graph', 'flowchart']
    for keyword in reserved:
        # Replace keyword when used as node ID (followed by bracket)
        pattern = rf'\b{keyword}\s*([\[\(\{{])'
        mermaid_code = re.sub(pattern, rf'{keyword}1 \1', mermaid_code, flags=re.IGNORECASE)
   
    # Ensure diagram starts with valid type
    lines = mermaid_code.strip().split('\n')
    if lines:
        first = lines[0].strip().lower()
        valid_starts = ['graph', 'flowchart', 'sequencediagram', 'classdiagram', 'statediagram']
        if not any(first.startswith(t) for t in valid_starts):
            # Prepend default flowchart if missing
            lines.insert(0, 'flowchart LR')
            mermaid_code = '\n'.join(lines)
   
    # Remove excessive whitespace while preserving structure
    mermaid_code = re.sub(r'[ \t]+', ' ', mermaid_code)  # Multiple spaces to single
    mermaid_code = re.sub(r' \n', '\n', mermaid_code)    # Trailing spaces
    mermaid_code = re.sub(r'\n\n\n+', '\n\n', mermaid_code)  # Max 2 newlines
   
    return mermaid_code.strip()
 
 
def wrap_drawio_xml(xml_content: str) -> str:
    """
    Wrap Draw.io XML in proper mxfile structure if not already wrapped.
   
    Returns:
        Properly wrapped Draw.io XML
    """
    if not xml_content or not xml_content.strip():
        return xml_content
   
    # Already wrapped
    if '<mxfile' in xml_content:
        return xml_content
   
    # Ensure mxGraphModel has required attributes
    if '<mxGraphModel' in xml_content:
        # Extract the mxGraphModel content
        import re
        match = re.search(r'<mxGraphModel[^>]*>(.*)</mxGraphModel>', xml_content, re.DOTALL)
        if match:
            inner_content = match.group(1)
            # Rebuild with proper attributes
            xml_content = f'''<mxGraphModel dx="1422" dy="794" grid="1" gridSize="10" guides="1" tooltips="1" connect="1" arrows="1" fold="1" page="1" pageScale="1" pageWidth="827" pageHeight="1169" math="0" shadow="0">
{inner_content}
</mxGraphModel>'''
   
    # Wrap in mxfile structure
    wrapped = f'''<mxfile host="app.diagrams.net" modified="{__import__('datetime').datetime.now().isoformat()}Z" agent="AI Architecture Assistant" version="22.1.11" type="device">
  <diagram name="Architecture" id="architecture-diagram">
{xml_content.strip()}
  </diagram>
</mxfile>'''
   
    return wrapped
 