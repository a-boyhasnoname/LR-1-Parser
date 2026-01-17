"""
app_animated.py
"""

import streamlit as st
import pandas as pd
import time
from lr1parser import LR1Parser
from animated_parser import (
    ANIMATION_CSS,
    create_stack_visualization,
    create_input_visualization,
    create_action_visualization,
    create_graphviz_dfa,
    create_networkx_dfa
)

# Page configuration
st.set_page_config(
    page_title="LR(1) Parser Generator",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add animation CSS
st.markdown(ANIMATION_CSS, unsafe_allow_html=True)

# Custom CSS
st.markdown("""
<style>
    body {
        background-color: #ffffff !important;
    }

    .main {
        background-color: #ffffff !important;
    }

    [data-testid="stAppViewContainer"] {
        background-color: #ffffff !important;
    }

    header {
        background-color: #1e3a8a !important;
        color: #ffffff;
    }

    .main-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1e3a8a;
        text-align: center;
        padding: 1.5rem;
        margin-bottom: 1rem;
        background-color: #dbeafe;
        border-radius: 12px;
        border: 2px solid #3b82f6;
        animation: fadeInScale 0.8s ease-out;
    }
    
    .subtitle {
        text-align: center;
        color: #374151;
        font-size: 1.1rem;
        margin-bottom: 2rem;
        font-weight: 500;
        animation: slideInRight 0.8s ease-out;
    }
    
    [data-testid="stSidebar"] {
        background-color: #f8fafc;
    }

    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        border: none;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
    }
    
    .stButton>button[kind="primary"] {
        background-color: #3b82f6;
        color: white;
    }
    
    .stButton>button[kind="primary"]:hover {
        background-color: #2563eb;
    }
    
    .production-item {
        padding: 0.8rem;
        margin: 0.4rem 0;
        background-color: #ffffff;
        border-left: 4px solid #3b82f6;
        border: 1px solid #e5e7eb;
        border-left: 4px solid #3b82f6;
        border-radius: 6px;
        color: #111827;
        font-family: 'Courier New', monospace;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        animation: fadeInScale 0.5s ease-out;
    }
    
    .parsing-step {
        animation: slideInRight 0.5s ease-out;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'parser' not in st.session_state:
    st.session_state.parser = None
if 'parsed' not in st.session_state:
    st.session_state.parsed = False
if 'animate' not in st.session_state:
    st.session_state.animate = True
if 'animation_speed' not in st.session_state:
    st.session_state.animation_speed = 0.5
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0

# Header
st.markdown('<h1 class="main-title">⚙️ LR(1) Parser Generator</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Compiler Design Project - Canonical LR(1) Parser</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/?size=100&id=pjDTF9QKKKQr&format=png&color=1e3a8a", width=150)
    st.markdown("# 📚 User Guide")
    
    # Animation settings
    st.markdown("### 🎬 Animation Settings")
    st.session_state.animate = st.checkbox("Enable Animations", value=True, help="Toggle parsing animations on/off")
    
    if st.session_state.animate:
        st.session_state.animation_speed = st.slider(
            "Animation Speed",
            min_value=0.1,
            max_value=2.0,
            value=0.5,
            step=0.1,
            help="Control how fast the parsing animation plays"
        )
    
    st.markdown("---")
    
    with st.expander("📖 Grammar Format", expanded=True):
        st.markdown("""
        **Rules:**
        - One production per line
        - Format: A → B C | d or A -> B C | d
        - Use ε for epsilon
        - Use | for alternatives
        
Example:
```
E → E + T | T
T → T * F | F
F → ( E ) | id
```
        """)
    
    with st.expander("📤 Input String Format"):
        st.markdown("""
        **Rules:**
        - Space-separated tokens
        - Use terminal symbols from grammar
        
        **Examples:**
        - id + id * id
        - ( id + id ) * id
        """)
    
    st.markdown("---")
    st.markdown("### 🎨 Example Grammars")
    
    if st.button("📝 Expression Grammar", use_container_width=True):
        st.session_state.example_grammar = """E -> E + T | T
T -> T * F | F
F -> ( E ) | id"""
        st.session_state.example_string = "id + id * id"
        st.rerun()
    
    if st.button("🔢 Simple Grammar", use_container_width=True):
        st.session_state.example_grammar = """S -> A B
A -> a
B -> b"""
        st.session_state.example_string = "a b"
        st.rerun()

    if st.button("🔄 Balanced Parentheses", use_container_width=True):
        st.session_state.example_grammar = """S -> ( S ) S | ε"""
        st.session_state.example_string = "( ( ) )"
        st.rerun()

# Main content
st.markdown("### 📝 Input Section")

col1, col2 = st.columns([1.2, 1], gap="large")

with col1:
    st.markdown("#### 📋 Context-Free Grammar")
    default_grammar = st.session_state.get('example_grammar', """E -> E + T | T
T -> T * F | F
F -> ( E ) | id""")
    
    grammar_input = st.text_area(
        "Enter your grammar:",
        value=default_grammar,
        height=250,
        help="Enter one production per line. Use → or -> for production rules."
    )

with col2:
    st.markdown("#### 📤 Input String to Parse")
    default_string = st.session_state.get('example_string', "id + id * id")
    
    input_string = st.text_input(
        "Enter the string to parse:",
        value=default_string,
        help="Enter space-separated tokens"
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Action buttons
    col_btn1, col_btn2 = st.columns(2)
    with col_btn1:
        parse_button = st.button("🚀 Generate & Parse", type="primary", use_container_width=True)
    with col_btn2:
        if st.button("🔄 Clear All", use_container_width=True):
            st.session_state.parser = None
            st.session_state.parsed = False
            st.session_state.current_step = 0
            if 'example_grammar' in st.session_state:
                del st.session_state.example_grammar
            if 'example_string' in st.session_state:
                del st.session_state.example_string
            st.rerun()

# Processing
if parse_button:
    if not grammar_input.strip():
        st.error("❌ Please enter a grammar!")
    elif not input_string.strip():
        st.error("❌ Please enter an input string!")
    else:
        try:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("🔄 Parsing grammar...")
            parser = LR1Parser()
            parser.parse_grammar(grammar_input)
            progress_bar.progress(20)
            time.sleep(0.2)
            
            status_text.text("➕ Augmenting grammar...")
            parser.augment_grammar()
            progress_bar.progress(40)
            time.sleep(0.2)
            
            status_text.text("📝 Building productions...")
            parser.build_production_list()
            progress_bar.progress(60)
            time.sleep(0.2)
            
            status_text.text("🔢 Computing FIRST sets...")
            parser.compute_first()
            progress_bar.progress(70)
            time.sleep(0.2)
            
            status_text.text("📷 Computing LR(1) items...")
            parser.compute_lr1_items()
            progress_bar.progress(85)
            time.sleep(0.2)
            
            status_text.text("📊 Building parsing table...")
            conflicts = parser.build_parsing_table()
            progress_bar.progress(100)
            time.sleep(0.2)
            
            progress_bar.empty()
            status_text.empty()
            
            st.session_state.parser = parser
            st.session_state.parsed = True
            st.session_state.current_step = 0
            
            if conflicts:
                st.warning("⚠️ **Warning:** Grammar has conflicts!\n\n" + "\n".join(f"- {c}" for c in conflicts))
            else:
                st.success("✅ **Success!** LR(1) parser generated without conflicts!")
        except Exception as e:
            st.error(f"❌ **Error:** {str(e)}")
            st.session_state.parsed = False

# Display results
if st.session_state.parsed and st.session_state.parser:
    parser = st.session_state.parser
    
    st.markdown("---")
    st.markdown("### 📊 Parser Analysis & Results")
    
    # Tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📜 Productions",
        "📷 LR(1) Item Sets", 
        "📋 Parsing Tables", 
        "▶️ Parse Simulation",
        "🔄 Derivation"
    ])
    
    with tab1:
        st.markdown("#### Grammar Productions")
        st.info("💡 Numbered productions used for reductions in parsing")
        
        col_orig, col_aug = st.columns(2)
        
        with col_orig:
            st.markdown("##### 📝 Original Grammar")
            production_list = parser.get_production_list()
            for prod in production_list:
                st.markdown(f"<div class='production-item'>{prod}</div>", unsafe_allow_html=True)
        
        with col_aug:
            st.markdown("##### ➕ Augmented Grammar")
            st.markdown(f"<div class='production-item'>0. {parser.start_symbol} → {list(parser.grammar[parser.start_symbol][0])[0]}</div>", unsafe_allow_html=True)
            for prod in production_list:
                st.markdown(f"<div class='production-item'>{prod}</div>", unsafe_allow_html=True)

    # Replace tab2 section in app_animated.py with this:

    with tab2:
        st.markdown("#### Canonical Collection of LR(1) Items")
        st.info("💡 Each item shows the current parsing position (•) and lookahead symbol")
        
        # Add visualization style selector
        viz_style = st.radio(
            "Visualization Style:",
            ["DFA Graph", "Detailed List"],
            horizontal=True,
            help="Choose how to display the LR(1) item sets"
        )
        
        items_dict = parser.get_items_as_dict()
        
        if viz_style == "DFA Graph":
            st.markdown("##### 🔄 LR(1) Automaton - State Transition Diagram")
            
            try:
                # Try Graphviz first (best quality)
                import graphviz
                dfa_graph = create_graphviz_dfa(parser)
                st.graphviz_chart(dfa_graph, use_container_width=True)
                
                st.markdown("---")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("🟦 **Blue nodes** = States (Item Sets)")
                with col2:
                    st.markdown("➡️ **Solid arrows** = Terminal transitions")
                with col3:
                    st.markdown("➡️ **Dashed arrows** = Non-terminal transitions")
            
            except ImportError:
                st.warning("⚠️ Graphviz not installed. Showing alternative visualization...")
                
                # Try networkx as fallback
                try:
                    import matplotlib
                    dfa_image = create_networkx_dfa(parser)
                    if dfa_image:
                        st.image(dfa_image, use_column_width=True)
                        st.caption("DFA visualization using NetworkX")
                    else:
                        raise ImportError
                
                except ImportError:
                    st.error("📦 Install graphviz to see the DFA diagram: `pip install graphviz`")
                    st.info("Alternatively, install networkx and matplotlib: `pip install networkx matplotlib`")
                    
                    # Fallback to simple list
                    st.markdown("##### 📋 Item Sets (Install graphviz for DFA view)")
                    for state_name, items in sorted(items_dict.items(), key=lambda x: int(x[0][1:])):
                        with st.expander(f"**{state_name}**"):
                            for item in items:
                                st.code(f"{item['lhs']} → {item['rhs']}, {item['lookahead']}")
        
        else:
            # Detailed list view
            st.markdown("##### 📋 Detailed Item Sets")
            
            num_states = len(items_dict)
            if num_states <= 4:
                cols_per_row = num_states
            elif num_states <= 12:
                cols_per_row = 3
            else:
                cols_per_row = 4
            
            state_items = list(items_dict.items())
            for row_start in range(0, len(state_items), cols_per_row):
                cols = st.columns(cols_per_row)
                
                for col_idx, (state_name, items) in enumerate(state_items[row_start:row_start + cols_per_row]):
                    if col_idx < len(cols):
                        with cols[col_idx]:
                            st.markdown(f"""
                            <div style="background: linear-gradient(135deg, #3b82f6, #2563eb); 
                                        color: white; padding: 12px 16px; border-radius: 8px; 
                                        font-weight: bold; font-size: 1.1rem; margin-bottom: 10px;
                                        text-align: center;">
                                🎯 {state_name}
                            </div>
                            """, unsafe_allow_html=True)
                            
                            for item in items:
                                lhs = item['lhs']
                                rhs = item['rhs']
                                lookahead = item['lookahead']
                                
                                st.markdown(f"""
                                <div style="padding: 8px 12px; margin: 6px 0; background: #f8fafc; 
                                            border-radius: 6px; border-left: 3px solid #3b82f6; 
                                            font-family: 'Courier New', monospace; font-size: 0.9rem;">
                                    {lhs} → {rhs}
                                    <span style="background: #fef08a; padding: 2px 8px; 
                                                border-radius: 4px; color: #854d0e; 
                                                font-weight: bold; margin-left: 8px; 
                                                font-size: 0.85rem;">
                                        {lookahead}
                                    </span>
                                </div>
                                """, unsafe_allow_html=True)

    with tab3:
        st.markdown("#### LR(1) Parsing Tables")
        st.info("💡 **ACTION**: s=shift, r=reduce, acc=accept | **GOTO**: state transitions")
        
        table_data = parser.get_parsing_table_as_dict()
        
        col_action, col_goto = st.columns(2, gap="large")
        
        with col_action:
            st.markdown("##### 🎯 ACTION Table")
            action_df = pd.DataFrame.from_dict(table_data['action'], orient='index')
            action_df.index.name = 'State'
            
            def highlight_actions(val):
                if isinstance(val, str):
                    if val.startswith('s'):
                        return 'background-color: #d1fae5; color: #065f46; font-weight: 600'
                    elif val.startswith('r'):
                        return 'background-color: #fef3c7; color: #92400e; font-weight: 600'
                    elif val == 'acc':
                        return 'background-color: #dbeafe; color: #1e40af; font-weight: bold'
                return ''
            
            styled_action = action_df.style.applymap(highlight_actions)
            st.dataframe(styled_action, use_container_width=True, height=400)
        
        with col_goto:
            st.markdown("##### ➡️ GOTO Table")
            goto_df = pd.DataFrame.from_dict(table_data['goto'], orient='index')
            goto_df.index.name = 'State'
            st.dataframe(goto_df, use_container_width=True, height=400)
    
    with tab4:
        st.markdown("#### 🎬 Step-by-Step Parse Simulation")
        
        # Parse the string
        derivation = parser.parse_string(input_string)
        
        if derivation is not None:
            st.success(f"✅ **ACCEPTED** - String `{input_string}` belongs to the grammar!")
            
            # Animation section
            if st.session_state.animate:
                st.markdown("### 🎥 Live Parsing Animation")
                
                # Control buttons
                col_play, col_step, col_reset = st.columns(3)
                
                with col_play:
                    play_animation = st.button("▶️ Play Animation", use_container_width=True, key="play_btn")
                
                with col_step:
                    step_mode = st.checkbox("⏯️ Step Mode", help="Manual step-by-step", key="step_mode_cb")
                
                with col_reset:
                    if st.button("🔄 Reset", use_container_width=True, key="reset_btn"):
                        st.session_state.current_step = 0
                        st.rerun()
                
                st.markdown("---")
                
                # Create containers
                stack_col, input_col, action_col = st.columns([2, 2, 1])
                
                with stack_col:
                    st.markdown("#### 📚 Stack State")
                    stack_container = st.empty()
                
                with input_col:
                    st.markdown("#### 📥 Input Buffer")
                    input_container = st.empty()
                
                with action_col:
                    st.markdown("#### ⚡ Action")
                    action_container = st.empty()
                
                # Animation logic
                if play_animation and not step_mode:
                    # Auto-play
                    for i, step in enumerate(parser.parsing_steps):
                        stack_html = create_stack_visualization(step['stack'], step['symbols'])
                        stack_container.markdown(stack_html, unsafe_allow_html=True)
                        
                        input_html = create_input_visualization(step['input'])
                        input_container.markdown(input_html, unsafe_allow_html=True)
                        
                        action_html = create_action_visualization(step['action'])
                        action_container.markdown(action_html, unsafe_allow_html=True)
                        
                        time.sleep(st.session_state.animation_speed)
                
                elif step_mode:
                    # Step mode
                    current = st.session_state.current_step
                    
                    if current < len(parser.parsing_steps):
                        step = parser.parsing_steps[current]
                        
                        stack_html = create_stack_visualization(step['stack'], step['symbols'])
                        stack_container.markdown(stack_html, unsafe_allow_html=True)
                        
                        input_html = create_input_visualization(step['input'])
                        input_container.markdown(input_html, unsafe_allow_html=True)
                        
                        action_html = create_action_visualization(step['action'])
                        action_container.markdown(action_html, unsafe_allow_html=True)
                        
                        # Progress
                        st.progress((current + 1) / len(parser.parsing_steps))
                        st.caption(f"Step {current + 1} of {len(parser.parsing_steps)}")
                        
                        # Navigation
                        col_prev, col_next = st.columns(2)
                        with col_prev:
                            if st.button("⬅️ Previous", disabled=(current == 0), use_container_width=True, key="prev_btn"):
                                st.session_state.current_step = max(0, current - 1)
                                st.rerun()
                        
                        with col_next:
                            if st.button("➡️ Next", disabled=(current >= len(parser.parsing_steps) - 1), use_container_width=True, key="next_btn"):
                                st.session_state.current_step = min(len(parser.parsing_steps) - 1, current + 1)
                                st.rerun()
                    else:
                        st.info("✅ Animation complete!")
                
                else:
                    # Show initial state
                    if parser.parsing_steps:
                        step = parser.parsing_steps[0]
                        
                        stack_html = create_stack_visualization(step['stack'], step['symbols'])
                        stack_container.markdown(stack_html, unsafe_allow_html=True)
                        
                        input_html = create_input_visualization(step['input'])
                        input_container.markdown(input_html, unsafe_allow_html=True)
                        
                        action_container.info("Click **Play** or enable **Step Mode**")
                
                st.markdown("---")
            
            # Detailed table
            st.markdown("##### 📊 Detailed Parsing Trace")
            steps_df = pd.DataFrame(parser.parsing_steps)
            
            column_order = ['step', 'stack', 'symbols', 'input', 'action', 'goto']
            steps_df = steps_df[column_order]
            steps_df.columns = ['Step', 'State Stack', 'Symbol Stack', 'Input', 'Action', 'State Transition']
            
            def highlight_step(row):
                action_str = str(row['Action'])
                if 'Shift' in action_str:
                    return ['background-color: #d1fae5; color: #065f46'] * len(row)
                elif 'Reduce' in action_str:
                    return ['background-color: #fef3c7; color: #92400e'] * len(row)
                elif 'ACCEPT' in action_str:
                    return ['background-color: #dbeafe; color: #1e40af; font-weight: bold'] * len(row)
                elif 'ERROR' in action_str:
                    return ['background-color: #fecaca; color: #991b1b'] * len(row)
                return ['color: #111827'] * len(row)
            
            styled_steps = steps_df.style.apply(highlight_step, axis=1)
            st.dataframe(styled_steps, use_container_width=True, height=400)
        
        else:
            st.error(f"❌ **REJECTED** - String `{input_string}` does not belong to the grammar!")
            
            if parser.parsing_steps:
                st.markdown("##### ⚠️ Parsing Trace (until error)")
                steps_df = pd.DataFrame(parser.parsing_steps)
                column_order = ['step', 'stack', 'symbols', 'input', 'action', 'goto']
                steps_df = steps_df[column_order]
                steps_df.columns = ['Step', 'State Stack', 'Symbol Stack', 'Input', 'Action', 'State Transition']
                st.dataframe(steps_df, use_container_width=True)
    
    # In app_animated.py, replace the ENTIRE tab5 section with this code:

    with tab5:
        st.markdown("#### 🔄 Derivation Sequence")
    
        if derivation is not None:
            # Animated derivation tree
            if st.session_state.animate:
                st.markdown("##### 🎬 Animated Derivation Tree")
                
                # Display each derivation step with animation
                for idx, (lhs, rhs, prod_num) in enumerate(reversed(derivation)):
                    delay = idx * 0.1
                    rhs_str = ' '.join(rhs) if rhs else 'ε'
                    
                    st.markdown(f"""
                    <div style="animation: growBranch 0.6s ease-out forwards;
                                animation-delay: {delay}s;
                                opacity: 0;
                                margin: 10px 0;
                                padding: 15px;
                                background: linear-gradient(135deg, #f0f9ff, #e0f2fe);
                                border-left: 4px solid #3b82f6;
                                border-radius: 8px;
                                font-family: 'Courier New', monospace;
                                font-size: 1.05rem;
                                box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                        <span style="color: #64748b; font-weight: 600;">Step {idx + 1}:</span>
                        <span style="color: #3b82f6; font-weight: bold; margin: 0 10px;">⇒</span>
                        Apply production 
                        <span style="background-color: #fef08a;
                                    padding: 3px 8px;
                                    border-radius: 4px;
                                    font-weight: bold;
                                    color: #854d0e;">
                            [{prod_num}] {lhs} → {rhs_str}
                        </span>
                    </div>
                    
                    <style>
                    @keyframes growBranch {{
                        from {{
                            opacity: 0;
                            transform: translateY(-20px) scale(0.8);
                        }}
                        to {{
                            opacity: 1;
                            transform: translateY(0) scale(1);
                        }}
                    }}
                    </style>
                    """, unsafe_allow_html=True)
                
                st.markdown("---")
            
            # Two-column layout for derivations
            col_der1, col_der2 = st.columns(2, gap="large")
            
            with col_der1:
                st.markdown("##### 🔼 Reverse Rightmost Derivation")
                st.info("Production sequence applied during parsing (bottom-up)")
                
                for idx, (lhs, rhs, prod_num) in enumerate(derivation, 1):
                    rhs_str = ' '.join(rhs) if rhs else 'ε'
                    st.markdown(f"**Step {idx}:** Production {prod_num}: `{lhs} → {rhs_str}`")
            
            with col_der2:
                st.markdown("##### 🔽 Rightmost Derivation")
                st.info("Derivation sequence from start symbol (top-down)")
                
                for idx, (lhs, rhs, prod_num) in enumerate(reversed(derivation), 1):
                    rhs_str = ' '.join(rhs) if rhs else 'ε'
                    st.markdown(f"**Step {idx}:** `{lhs} → {rhs_str}`")
        
        else:
            st.warning("⚠️ Parse the string successfully first to see the derivation!")

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 1.5rem 0;'>
    <p style='color: #6b7280; font-size: 0.9rem;'>
        🎓 <strong>LR(1) Parser Generator</strong> | Compiler Design Project<br>
        Built by KU-DoCSE CS-22 Students | © 2026
    </p>
</div>
""", unsafe_allow_html=True)