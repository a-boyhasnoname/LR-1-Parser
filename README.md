
# LR(1) Parser Generator with Visualization

This project implements a **Canonical LR(1) Parser** with **interactive visualizations**. It parses context-free grammars, computes FIRST sets, builds LR(1) item sets, constructs the parsing table, and simulates the parsing process. The project includes step-by-step **animations** to visualize the parsing actions and state transitions.

## Features
- **Grammar Parsing**: Input context-free grammar in a readable format.
- **LR(1) Item Sets**: Constructs the canonical collection of LR(1) item sets (states in the LR(1) automaton).
- **Parsing Table Generation**: Builds the **ACTION** and **GOTO** tables used during parsing.
- **Shift-Reduce Parsing Simulation**: Step-by-step parsing of input strings using the LR(1) algorithm.
- **Visualization**: Animated visualizations of:
  - **Stack state** (shift actions)
  - **Input buffer** (remaining symbols to be parsed)
  - **Action** (shift, reduce, accept, error)
  - **DFA Automaton** (graphical representation of the states and transitions)
  - **Derivation tree** (production rules applied during parsing)
- **Interactive UI** using **Streamlit** for a smooth user experience.

## Installation

### Prerequisites
- Python 3.x
- Required Python packages: `streamlit`, `pandas`, `graphviz`, `matplotlib`, `networkx`

### Installation Steps
1. Clone the repository:
   ```bash
   git clone https://github.com/a-boyhasnoname/LR-1-Parser
   cd LR-1-Parser
   ```

2. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. To run the project:
   ```bash
   streamlit run app_animated.py
   ```

## Usage

### Input Grammar
1. **Enter the grammar** in the provided format (one production per line).
   - Example:
     ```
     S → A B
     A → a
     B → b
     ```

2. **Enter the string** to parse, using space-separated tokens that match the terminals in your grammar (e.g., `a b`).

3. Click **"Generate & Parse"** to:
   - Parse the grammar
   - Augment the grammar with `S' → S`
   - Compute **FIRST sets**
   - Build the **LR(1) item sets**
   - Create **parsing tables** (ACTION and GOTO)
   - Perform the **shift-reduce parsing simulation**

### Visualizations
- **State Transitions**: Displays the LR(1) automaton as a **DFA graph** (using Graphviz or NetworkX).
- **Step-by-Step Animation**: Allows users to step through each **shift**, **reduce**, or **accept** action and view the stack, input buffer, and action at each step.
- **Derivation**: Displays the sequence of production rules applied during parsing.

### Optional Settings
- Enable or disable **animations**.
- Adjust the **animation speed** using a slider.

## Files Structure
- `lr1parser.py`: Contains the core LR(1) parsing logic, including the computation of **FIRST sets**, **LR(1) items**, and **parsing tables**.
- `items.py`: Defines the `LR1Item` and `ItemSet` classes, which represent the individual items and states in the LR(1) parsing automaton.
- `animated_parser.py`: Contains utilities for **visualizing** the parsing process, including stack and input visualizations, and generating DFA diagrams using **Graphviz** or **NetworkX**.
- `app_animated.py`: A **Streamlit-based web app** that allows users to input grammars and strings, and interact with the parser through visualizations and animations.

## Example
### Grammar:
```
S → A B
A → a
B → b
```

### Input String:
```
a b
```

### Visualization:
1. **Stack**: Shows the parser’s state stack during parsing.
2. **Input Buffer**: Displays the tokens yet to be parsed.
3. **Action**: Indicates whether the parser is shifting, reducing, or accepting.
4. **DFA Automaton**: A graphical representation of the LR(1) automaton with states and transitions.
5. **Derivation**: Shows the steps taken to derive the input string using the grammar.

