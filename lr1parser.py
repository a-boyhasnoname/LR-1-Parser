# lr1parser.py
from items import LR1Item, ItemSet

class Production:
    """Simple production class to wrap production rules."""
    def __init__(self, lhs, rhs):
        self.lhs = lhs
        self.rhs = list(rhs) if rhs else []
    
    def __repr__(self):
        rhs_str = ' '.join(self.rhs) if self.rhs else 'ε'
        return f"{self.lhs} → {rhs_str}"
    
    def __eq__(self, other):
        return isinstance(other, Production) and \
               self.lhs == other.lhs and \
               tuple(self.rhs) == tuple(other.rhs)
    
    def __hash__(self):
        return hash((self.lhs, tuple(self.rhs)))


class LR1Parser:
    """Implements a Canonical LR(1) parser."""
    
    def __init__(self):
        self.grammar = {}  # Dict: non_terminal -> list of productions
        self.start_symbol = None
        self.terminals = set()
        self.non_terminals = set()
        self.productions = []  # List of Production objects
        self.first_sets = {}
        self.items = {}  # Dict: state_name -> list of items
        self.action_table = {}  # (state, terminal) -> action
        self.goto_table = {}  # (state, non_terminal) -> state
        self.states = []  # List of ItemSet objects
        self.state_map = {}  # Map from ItemSet to state number
        self.parsing_steps = []
    
    def parse_grammar(self, grammar_str):
        """Parse grammar from string format."""
        lines = [line.strip() for line in grammar_str.strip().split('\n') if line.strip()]
        
        for line in lines:
            # Replace → with ->
            line = line.replace('→', '->')
            
            if '->' not in line:
                continue
            
            lhs, rhs = line.split('->', 1)
            lhs = lhs.strip()
            
            # Set start symbol as the first non-terminal
            if self.start_symbol is None:
                self.start_symbol = lhs
            
            self.non_terminals.add(lhs)
            
            if lhs not in self.grammar:
                self.grammar[lhs] = []
            
            # Handle multiple productions separated by |
            alternatives = [alt.strip() for alt in rhs.split('|')]
            
            for alt in alternatives:
                if alt in ['ε', 'epsilon', '']:
                    # Empty production
                    prod = tuple()
                else:
                    # Split by whitespace
                    prod = tuple(alt.split())
                
                self.grammar[lhs].append(prod)
        
        # Identify terminals (symbols that are not non-terminals)
        for lhs, productions in self.grammar.items():
            for prod in productions:
                for symbol in prod:
                    if symbol not in self.non_terminals:
                        self.terminals.add(symbol)
        
        print(f"Parsed Grammar:")
        print(f"  Start Symbol: {self.start_symbol}")
        print(f"  Non-terminals: {self.non_terminals}")
        print(f"  Terminals: {self.terminals}")
        print(f"  Productions:")
        for lhs, prods in self.grammar.items():
            for prod in prods:
                prod_str = ' '.join(prod) if prod else 'ε'
                print(f"    {lhs} → {prod_str}")
    
    def augment_grammar(self):
        """Augment the grammar with S' -> S production."""
        new_start = self.start_symbol + "'"
        self.grammar[new_start] = [(self.start_symbol,)]
        self.non_terminals.add(new_start)
        old_start = self.start_symbol
        self.start_symbol = new_start
        return old_start
    
    def build_production_list(self):
        """Build a numbered list of productions."""
        self.productions = []
        
        # Start with augmented production (Production 0)
        for prod in self.grammar[self.start_symbol]:
            self.productions.append(Production(self.start_symbol, prod))
        
        # Add other productions in order
        for lhs in sorted(self.grammar.keys()):
            if lhs == self.start_symbol:
                continue
            for prod in self.grammar[lhs]:
                self.productions.append(Production(lhs, prod))
        
        print(f"\nNumbered Productions:")
        for i, prod in enumerate(self.productions):
            print(f"  {i}. {prod}")
    
    def get_production_list(self):
        """Get formatted production list."""
        result = []
        for i, prod in enumerate(self.productions):
            if i == 0:  # Skip augmented production
                continue
            rhs_str = ' '.join(prod.rhs) if prod.rhs else 'ε'
            result.append(f"{i}. {prod.lhs} → {rhs_str}")
        return result
    
    def compute_first(self):
        """Compute FIRST sets for all symbols."""
        self.first_sets = {symbol: set() for symbol in self.non_terminals | self.terminals}
        
        # FIRST of terminals
        for terminal in self.terminals:
            self.first_sets[terminal].add(terminal)
        
        # Special symbols
        self.first_sets['ε'] = {'ε'}
        self.first_sets['epsilon'] = {'epsilon'}
        self.first_sets['$'] = {'$'}
        
        # Iterate until no changes
        changed = True
        iterations = 0
        while changed:
            changed = False
            iterations += 1
            
            for lhs, productions in self.grammar.items():
                for prod in productions:
                    if not prod:  # Empty production
                        if 'ε' not in self.first_sets[lhs]:
                            self.first_sets[lhs].add('ε')
                            changed = True
                    else:
                        # Add FIRST of production to FIRST of lhs
                        all_nullable = True
                        for symbol in prod:
                            before = len(self.first_sets[lhs])
                            
                            # Add FIRST(symbol) - {ε} to FIRST(lhs)
                            if symbol in self.first_sets:
                                self.first_sets[lhs].update(self.first_sets[symbol] - {'ε', 'epsilon'})
                            else:
                                self.first_sets[lhs].add(symbol)
                            
                            if len(self.first_sets[lhs]) > before:
                                changed = True
                            
                            # If symbol is not nullable, stop
                            if symbol not in self.first_sets or 'ε' not in self.first_sets[symbol]:
                                all_nullable = False
                                break
                        
                        # If all symbols are nullable, add ε to FIRST(lhs)
                        if all_nullable and 'ε' not in self.first_sets[lhs]:
                            self.first_sets[lhs].add('ε')
                            changed = True
        
        print(f"\nFIRST Sets (computed in {iterations} iterations):")
        for symbol in sorted(self.first_sets.keys()):
            print(f"  FIRST({symbol}) = {self.first_sets[symbol]}")
    
    def compute_first_of_string(self, symbols):
        """Compute FIRST set of a string of symbols."""
        result = set()
        
        if not symbols:
            result.add('ε')
            return result
        
        for symbol in symbols:
            if symbol not in self.first_sets:
                # Unknown symbol, treat as terminal
                result.add(symbol)
                break
            
            # Add FIRST(symbol) - {ε}
            result.update(self.first_sets[symbol] - {'ε', 'epsilon'})
            
            # If symbol is not nullable, stop
            if 'ε' not in self.first_sets[symbol]:
                break
        else:
            # All symbols are nullable
            result.add('ε')
        
        return result
    
    def closure(self, items):
        """Compute closure of a set of LR(1) items."""
        closure_set = ItemSet(items)
        
        changed = True
        while changed:
            changed = False
            new_items = set()
            
            for item in closure_set:
                next_sym = item.next_symbol()
                
                # If next symbol is a non-terminal, add closure items
                if next_sym and next_sym in self.non_terminals:
                    # Compute FIRST(β a) where β is the rest of rhs and a is lookahead
                    beta = list(item.rhs[item.dot_pos + 1:]) + [item.lookahead]
                    first_beta = self.compute_first_of_string(beta)
                    
                    # Remove epsilon
                    first_beta = first_beta - {'ε', 'epsilon'}
                    
                    # For each production of next_sym
                    for prod in self.grammar[next_sym]:
                        # Find the Production object
                        prod_obj = None
                        for p in self.productions:
                            if p.lhs == next_sym and tuple(p.rhs) == prod:
                                prod_obj = p
                                break
                        
                        if prod_obj is None:
                            # Create temporary production object
                            prod_obj = Production(next_sym, prod)
                        
                        # For each lookahead in FIRST(β a)
                        for lookahead in first_beta:
                            new_item = LR1Item(prod_obj, 0, lookahead)
                            
                            if new_item not in closure_set.items:
                                new_items.add(new_item)
                                changed = True
            
            for item in new_items:
                closure_set.add(item)
        
        return closure_set
    
    def goto(self, items, symbol):
        """Compute GOTO(I, X) for a set of items and a symbol."""
        goto_items = set()
        
        for item in items:
            if item.next_symbol() == symbol:
                goto_items.add(item.advance())
        
        if not goto_items:
            return None
        
        return self.closure(goto_items)
    
    def compute_lr1_items(self):
        """Build the canonical collection of LR(1) item sets."""
        print("\n=== Building LR(1) Item Sets ===")
        
        # Create initial item [S' -> · S, $]
        start_prod = self.productions[0]
        start_item = LR1Item(start_prod, 0, '$')
        
        initial_state = self.closure([start_item])
        
        self.states = [initial_state]
        self.state_map[initial_state] = 0
        
        print(f"\nI0 (Initial State):")
        for item in initial_state:
            print(f"  {item}")
        
        # Process states
        i = 0
        while i < len(self.states):
            current_state = self.states[i]
            
            # Find all symbols that can be shifted
            symbols = set()
            for item in current_state:
                next_sym = item.next_symbol()
                if next_sym:
                    symbols.add(next_sym)
            
            # Compute GOTO for each symbol
            for symbol in sorted(symbols):
                goto_state = self.goto(current_state, symbol)
                
                if goto_state:
                    if goto_state not in self.state_map:
                        state_num = len(self.states)
                        self.states.append(goto_state)
                        self.state_map[goto_state] = state_num
                        
                        print(f"\nI{state_num} (from I{i} on '{symbol}'):")
                        for item in goto_state:
                            print(f"  {item}")
            
            i += 1
        
        print(f"\n=== Total States: {len(self.states)} ===")
        
        # Convert to dict format for display
        self.items = {}
        for i, state in enumerate(self.states):
            state_name = f"I{i}"
            self.items[state_name] = []
            
            for item in state:
                rhs_before = ' '.join(item.rhs[:item.dot_pos])
                rhs_after = ' '.join(item.rhs[item.dot_pos:])
                
                if not item.rhs:
                    rhs_str = "•"
                elif rhs_before and rhs_after:
                    rhs_str = f"{rhs_before} • {rhs_after}"
                elif rhs_before:
                    rhs_str = f"{rhs_before} •"
                else:
                    rhs_str = f"• {rhs_after}"
                
                self.items[state_name].append({
                    'lhs': item.lhs,
                    'rhs': rhs_str,
                    'lookahead': item.lookahead
                })
    
    def build_parsing_table(self):
        """Build the LR(1) parsing table."""
        print("\n=== Building Parsing Table ===")
        conflicts = []
        
        for state_num, state in enumerate(self.states):
            for item in state:
                if not item.is_complete():
                    # Shift or goto
                    next_sym = item.next_symbol()
                    
                    if next_sym in self.terminals:
                        # Shift action
                        goto_state = self.goto(state, next_sym)
                        if goto_state:
                            goto_state_num = self.state_map[goto_state]
                            action = f"s{goto_state_num}"
                            
                            key = (state_num, next_sym)
                            if key in self.action_table and self.action_table[key] != action:
                                conflict = f"Shift-Reduce conflict at state {state_num} on '{next_sym}': {self.action_table[key]} vs {action}"
                                conflicts.append(conflict)
                                print(f"  ⚠️  {conflict}")
                            else:
                                self.action_table[key] = action
                    
                    elif next_sym in self.non_terminals:
                        # Goto action
                        goto_state = self.goto(state, next_sym)
                        if goto_state:
                            goto_state_num = self.state_map[goto_state]
                            self.goto_table[(state_num, next_sym)] = goto_state_num
                
                else:
                    # Reduce or accept
                    if item.lhs == self.start_symbol and item.lookahead == '$':
                        # Accept action
                        self.action_table[(state_num, '$')] = 'acc'
                    else:
                        # Reduce action - find production number
                        prod_num = None
                        for idx, prod in enumerate(self.productions):
                            if prod.lhs == item.lhs and prod.rhs == item.rhs:
                                prod_num = idx
                                break
                        
                        if prod_num is None:
                            print(f"  ⚠️  WARNING: Could not find production for {item.lhs} → {' '.join(item.rhs)}")
                            continue
                        
                        action = f"r{prod_num}"
                        key = (state_num, item.lookahead)
                        
                        if key in self.action_table and self.action_table[key] != action:
                            conflict = f"Reduce-Reduce conflict at state {state_num} on '{item.lookahead}': {self.action_table[key]} vs {action}"
                            conflicts.append(conflict)
                            print(f"  ⚠️  {conflict}")
                        else:
                            self.action_table[key] = action
        
        print(f"=== Parsing Table Complete ===")
        print(f"  ACTION entries: {len(self.action_table)}")
        print(f"  GOTO entries: {len(self.goto_table)}")
        print(f"  Conflicts: {len(conflicts)}")
        
        return conflicts
    
    def get_items_as_dict(self):
        """Return items in dict format."""
        return self.items
    
    def get_parsing_table_as_dict(self):
        """Return parsing tables in dict format."""
        action_dict = {}
        goto_dict = {}
        
        terminals = sorted(self.terminals) + ['$']
        non_terminals = sorted(self.non_terminals - {self.start_symbol})
        
        for i in range(len(self.states)):
            action_dict[i] = {}
            goto_dict[i] = {}
            
            for terminal in terminals:
                action_dict[i][terminal] = self.action_table.get((i, terminal), '')
            
            for nt in non_terminals:
                goto_dict[i][nt] = self.goto_table.get((i, nt), '')
        
        return {'action': action_dict, 'goto': goto_dict}
    
    def parse_string(self, input_string):
        """Parse an input string using the LR(1) parsing table."""
        tokens = input_string.split() + ['$']
        
        stack = [0]
        symbol_stack = ['$']
        input_buffer = tokens[:]
        
        self.parsing_steps = []
        derivation = []
        step = 0
        
        while True:
            state = stack[-1]
            symbol = input_buffer[0]
            
            action = self.action_table.get((state, symbol))
            
            if action is None:
                self.parsing_steps.append({
                    'step': step,
                    'stack': ' '.join(map(str, stack)),
                    'symbols': ' '.join(symbol_stack),
                    'input': ' '.join(input_buffer),
                    'action': 'ERROR: No action defined',
                    'goto': ''
                })
                return None
            
            if action == 'acc':
                self.parsing_steps.append({
                    'step': step,
                    'stack': ' '.join(map(str, stack)),
                    'symbols': ' '.join(symbol_stack),
                    'input': ' '.join(input_buffer),
                    'action': 'ACCEPT',
                    'goto': ''
                })
                return derivation
            
            elif action.startswith('s'):
                # Shift action
                next_state = int(action[1:])
                stack.append(next_state)
                symbol_stack.append(symbol)
                input_buffer.pop(0)
                
                self.parsing_steps.append({
                    'step': step,
                    'stack': ' '.join(map(str, stack)),
                    'symbols': ' '.join(symbol_stack),
                    'input': ' '.join(input_buffer),
                    'action': f"Shift {next_state}",
                    'goto': f"→ {next_state}"
                })
                step += 1
            
            elif action.startswith('r'):
                # Reduce action
                prod_num = int(action[1:])
                prod = self.productions[prod_num]
                lhs = prod.lhs
                rhs = prod.rhs
                
                derivation.append((lhs, tuple(rhs), prod_num))
                
                # Pop |rhs| items from stack
                if rhs:
                    for _ in range(len(rhs)):
                        stack.pop()
                        symbol_stack.pop()
                
                # Get new state from GOTO table
                state = stack[-1]
                goto_state = self.goto_table.get((state, lhs))
                
                if goto_state is None:
                    self.parsing_steps.append({
                        'step': step,
                        'stack': ' '.join(map(str, stack)),
                        'symbols': ' '.join(symbol_stack),
                        'input': ' '.join(input_buffer),
                        'action': f"ERROR: No GOTO({state}, {lhs})",
                        'goto': ''
                    })
                    return None
                
                stack.append(goto_state)
                symbol_stack.append(lhs)
                
                rhs_str = ' '.join(rhs) if rhs else 'ε'
                self.parsing_steps.append({
                    'step': step,
                    'stack': ' '.join(map(str, stack)),
                    'symbols': ' '.join(symbol_stack),
                    'input': ' '.join(input_buffer),
                    'action': f"Reduce {prod_num}: {lhs} → {rhs_str}",
                    'goto': f"→ {goto_state}"
                })
                step += 1