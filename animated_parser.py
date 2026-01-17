"""
animated_parser.py
"""

import streamlit as st
import time
import math
import graphviz

def create_stack_visualization(stack, symbols):
    """Create animated stack visualization"""
    states = stack.split()
    syms = symbols.split()
    
    html = '<div style="display: flex; flex-direction: column-reverse; gap: 5px; align-items: center;">'
    
    for i, (state, sym) in enumerate(zip(states, syms)):
        color = "#3b82f6" if i == len(states) - 1 else "#94a3b8"
        border = '3px solid #fff' if i == len(states) - 1 else '2px solid transparent'
        
        html += f'''
<div style="background: linear-gradient(135deg, {color}, {color}dd); color: white; padding: 12px 20px; border-radius: 8px; min-width: 80px; text-align: center; font-weight: bold; box-shadow: 0 2px 8px rgba(0,0,0,0.1); border: {border};">
    <div style="font-size: 0.8rem; opacity: 0.8;">State {state}</div>
    <div style="font-size: 1.1rem; margin-top: 4px;">{sym}</div>
</div>
'''
    
    html += "</div>"
    return html


def create_input_visualization(input_str):
    """Create animated input buffer visualization"""
    tokens = input_str.split()
    
    html = '<div style="display: flex; gap: 8px; flex-wrap: wrap; justify-content: center;">'
    
    for i, token in enumerate(tokens):
        bg_color = "#fef08a" if i == 0 else "#f1f5f9"
        border_color = "#eab308" if i == 0 else "#cbd5e1"
        border_width = "3px" if i == 0 else "2px"
        
        html += f'''
<div style="background-color: {bg_color}; color: #1e293b; padding: 10px 16px; border-radius: 6px; border: {border_width} solid {border_color}; font-weight: 600; font-family: 'Courier New', monospace; box-shadow: 0 2px 4px rgba(0,0,0,0.05);">
    {token}
</div>
'''
    
    html += "</div>"
    return html


def create_action_visualization(action):
    """Create animated action display"""
    if "Shift" in action:
        color = "#10b981"
        icon = "➡️"
        bg = "#d1fae5"
    elif "Reduce" in action:
        color = "#f59e0b"
        icon = "🔄"
        bg = "#fef3c7"
    elif "ACCEPT" in action:
        color = "#3b82f6"
        icon = "✅"
        bg = "#dbeafe"
    else:
        color = "#ef4444"
        icon = "❌"
        bg = "#fee2e2"
    
    html = f'''
<div style="background-color: {bg}; color: {color}; padding: 16px; border-radius: 8px; border: 2px solid {color}; text-align: center; font-weight: bold; font-size: 1.1rem; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    <div style="font-size: 2rem; margin-bottom: 8px;">{icon}</div>
    <div>{action}</div>
</div>
'''
    
    return html


def create_graphviz_dfa(parser):
    """Create a complete DFA-style graph using Graphviz - shows ALL items"""
 
    # Create a new directed graph
    dot = graphviz.Digraph(comment='LR(1) Automaton')
    dot.attr(rankdir='TB')  # Top to bottom for better readability
    dot.attr('node', shape='rectangle', style='rounded,filled', fillcolor='lightblue', 
             fontname='Courier', fontsize='9')
    dot.attr('edge', fontname='Courier', fontsize='8', color='#3b82f6')
    
    # Get items and tables
    items_dict = parser.get_items_as_dict()
    table_data = parser.get_parsing_table_as_dict()
    
    # Add nodes (states) - SHOW ALL ITEMS, NO TRUNCATION
    for state_name, items in sorted(items_dict.items(), key=lambda x: int(x[0][1:])):
        # Create label with ALL items (no limit)
        label = f"<<B>{state_name}</B>"
        
        # DEBUG: Print what we're processing
        print(f"\nProcessing {state_name}: {len(items)} items")
        
        # Show ALL items in this state
        for item in items:
            lhs = item['lhs']
            rhs = item['rhs']
            lookahead = item['lookahead']
            
            # DEBUG: Print each item
            print(f"  Item: {lhs} → {rhs}, {lookahead}")
            
            # Replace bullet with middle dot for better compatibility
            rhs = rhs.replace('•', '·')
            
            # Escape special characters for graphviz
            lhs = lhs.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
            rhs = rhs.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
            lookahead = lookahead.replace('<', '&lt;').replace('>', '&gt;').replace('&', '&amp;')
            
            label += f"<BR ALIGN='LEFT'/>{lhs} → {rhs}, {lookahead}"
        
        label += ">"
        
        # Different colors for special states
        if state_name == "I0":
            dot.node(state_name, label, fillcolor='#d1fae5', penwidth='3')
        else:
            # Check if this is an accepting state
            has_accept = False
            for item in items:
                if item['rhs'].endswith('•') and "'" in item['lhs']:
                    has_accept = True
                    break
            
            if has_accept:
                dot.node(state_name, label, fillcolor='#fef3c7', penwidth='2')
            else:
                dot.node(state_name, label, fillcolor='#dbeafe')
    
    # Add edges (transitions)
    added_edges = set()
    
    # Shift transitions (from ACTION table)
    for state_num, actions in table_data['action'].items():
        state_name = f"I{state_num}"
        
        for symbol, action in actions.items():
            if action and action.startswith('s'):
                target_state = f"I{action[1:]}"
                edge_key = (state_name, target_state, symbol)
                
                if edge_key not in added_edges:
                    # Escape symbol for graphviz
                    symbol_escaped = symbol.replace('<', '&lt;').replace('>', '&gt;')
                    dot.edge(state_name, target_state, label=symbol_escaped, color='#3b82f6')
                    added_edges.add(edge_key)
    
    # GOTO transitions (from GOTO table)
    for state_num, gotos in table_data['goto'].items():
        state_name = f"I{state_num}"
        
        for symbol, target in gotos.items():
            if target != '':
                target_state = f"I{target}"
                edge_key = (state_name, target_state, symbol)
                
                if edge_key not in added_edges:
                    # Escape symbol for graphviz
                    symbol_escaped = symbol.replace('<', '&lt;').replace('>', '&gt;')
                    dot.edge(state_name, target_state, label=symbol_escaped, 
                            color='#10b981', style='dashed')
                    added_edges.add(edge_key)
    
    return dot


def create_networkx_dfa(parser):
    """Create a DFA visualization using networkx - shows state numbers only"""
    try:
        import networkx as nx
        import matplotlib.pyplot as plt
        import io
        
        # Get data
        items_dict = parser.get_items_as_dict()
        table_data = parser.get_parsing_table_as_dict()
        
        # Create graph
        G = nx.DiGraph()
        
        # Add nodes
        for state_name in items_dict.keys():
            G.add_node(state_name)
        
        # Add edges with labels
        edge_labels = {}
        
        for state_num, actions in table_data['action'].items():
            state_name = f"I{state_num}"
            for symbol, action in actions.items():
                if action and action.startswith('s'):
                    target_state = f"I{action[1:]}"
                    G.add_edge(state_name, target_state)
                    if (state_name, target_state) in edge_labels:
                        edge_labels[(state_name, target_state)] += f", {symbol}"
                    else:
                        edge_labels[(state_name, target_state)] = symbol
        
        for state_num, gotos in table_data['goto'].items():
            state_name = f"I{state_num}"
            for symbol, target in gotos.items():
                if target != '':
                    target_state = f"I{target}"
                    if (state_name, target_state) in edge_labels:
                        edge_labels[(state_name, target_state)] += f", {symbol}"
                    else:
                        G.add_edge(state_name, target_state)
                        edge_labels[(state_name, target_state)] = symbol
        
        # Create figure
        fig, ax = plt.subplots(figsize=(18, 14))
        
        # Layout
        if len(G.nodes()) <= 10:
            pos = nx.circular_layout(G, scale=3)
        else:
            pos = nx.spring_layout(G, k=3, iterations=100, seed=42)
        
        # Draw nodes
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', 
                               node_size=2500, node_shape='o', ax=ax,
                               edgecolors='#3b82f6', linewidths=2.5)
        
        # Highlight initial state
        nx.draw_networkx_nodes(G, pos, nodelist=['I0'], node_color='#d1fae5',
                               node_size=2500, node_shape='o', ax=ax,
                               edgecolors='#10b981', linewidths=3.5)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='#3b82f6', 
                               arrows=True, arrowsize=25, 
                               arrowstyle='->', ax=ax, width=2.5,
                               connectionstyle='arc3,rad=0.15')
        
        # Draw labels
        nx.draw_networkx_labels(G, pos, font_size=11, 
                                font_weight='bold', ax=ax)
        
        # Draw edge labels
        nx.draw_networkx_edge_labels(G, pos, edge_labels, 
                                      font_size=9, font_color='#92400e',
                                      bbox=dict(boxstyle='round,pad=0.4', 
                                               facecolor='#fef3c7', 
                                               edgecolor='#f59e0b', linewidth=2))
        
        ax.set_title("LR(1) Automaton - State Transition Diagram\n(Use 'Detailed List' view to see all items in each state)", 
                    fontsize=16, fontweight='bold', pad=20)
        ax.axis('off')
        plt.tight_layout()
        
        # Convert to bytes
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=150, bbox_inches='tight', 
                   facecolor='white')
        buf.seek(0)
        plt.close()
        
        return buf
        
    except ImportError:
        return None


def create_item_set_animation(items_dict):
    """Create animated item set transitions with ALL items shown"""
    
    html = """
    <style>
    @keyframes fadeInUp {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .state-card {
        animation: fadeInUp 0.5s ease-out forwards;
        background: white;
        border: 2px solid #e2e8f0;
        border-radius: 12px;
        padding: 20px;
        margin: 15px 0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.08);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .state-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 24px rgba(59, 130, 246, 0.2);
        border-color: #3b82f6;
    }
    
    .state-header {
        background: linear-gradient(135deg, #3b82f6, #2563eb);
        color: white;
        padding: 12px 16px;
        border-radius: 8px;
        font-weight: bold;
        font-size: 1.2rem;
        margin-bottom: 15px;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    .item-row {
        padding: 10px 14px;
        margin: 8px 0;
        background: #f8fafc;
        border-radius: 6px;
        border-left: 3px solid #3b82f6;
        font-family: 'Courier New', monospace;
        font-size: 0.95rem;
        transition: background 0.2s ease;
    }
    
    .item-row:hover {
        background: #e0f2fe;
    }
    
    .dot {
        color: #ef4444;
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    .lookahead {
        background: #fef08a;
        padding: 3px 10px;
        border-radius: 4px;
        color: #854d0e;
        font-weight: bold;
        margin-left: 10px;
    }
    </style>
    
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 20px;">
    """
    
    for idx, (state_name, items) in enumerate(sorted(items_dict.items(), key=lambda x: int(x[0][1:]))):
        delay = idx * 0.05
        
        html += f"""
        <div class="state-card" style="animation-delay: {delay}s;">
            <div class="state-header">
                <span>🎯</span>
                <span>{state_name}</span>
                <span style="font-size: 0.9rem; opacity: 0.8;">({len(items)} items)</span>
            </div>
        """
        
        # Show ALL items (no truncation)
        for item in items:
            lhs = item['lhs']
            rhs = item['rhs'].replace('•', '<span class="dot">•</span>')
            lookahead = item['lookahead']
            
            html += f"""
            <div class="item-row">
                {lhs} → {rhs}
                <span class="lookahead">{lookahead}</span>
            </div>
            """
        
        html += "</div>"
    
    html += "</div>"
    return html


# CSS Animations to add to app
ANIMATION_CSS = """
<style>
@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes pulse {
    0%, 100% {
        transform: scale(1);
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    50% {
        transform: scale(1.05);
        box-shadow: 0 4px 12px rgba(234, 179, 8, 0.3);
    }
}

@keyframes bounceIn {
    0% {
        opacity: 0;
        transform: scale(0.3);
    }
    50% {
        transform: scale(1.05);
    }
    70% {
        transform: scale(0.9);
    }
    100% {
        opacity: 1;
        transform: scale(1);
    }
}

@keyframes fadeInScale {
    from {
        opacity: 0;
        transform: scale(0.9);
    }
    to {
        opacity: 1;
        transform: scale(1);
    }
}

@keyframes slideInRight {
    from {
        opacity: 0;
        transform: translateX(50px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}

@keyframes growBranch {
    from {
        opacity: 0;
        transform: translateY(-20px) scale(0.8);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}
</style>
"""