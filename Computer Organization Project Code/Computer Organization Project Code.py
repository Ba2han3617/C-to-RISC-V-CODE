# c_to_riscV_with_python

import tkinter as tk
from tkinter import messagebox

# ─── YARDIMCI BRANCH YAPISI ────────────────────────────────
def _make_branch(op, rL, rR, lbl):
    if   op == '<':  return f"bge {rL}, {rR}, {lbl}"
    elif op == '>':  return f"ble {rL}, {rR}, {lbl}"
    elif op == '<=': return f"bgt {rL}, {rR}, {lbl}"
    elif op == '>=': return f"blt {rL}, {rR}, {lbl}"
    elif op == '==': return f"bne {rL}, {rR}, {lbl}"
    elif op == '!=': return f"beq {rL}, {rR}, {lbl}"
    else:            return f"# unsupported op {op}"

label_counter = 0
register_map = {}
next_register = 5
riscv_code = []

def generate_label():
    global label_counter
    label = f"L{label_counter}"
    label_counter += 1
    return label

def get_register(var):
    global next_register
    if var not in register_map:
        register_map[var] = f"x{next_register}"
        next_register += 1
    return register_map[var]

def parse_condition(cond):
    ops = ['<=', '>=', '==', '!=', '<', '>']
    for op in ops:
        if op in cond:
            left, right = cond.split(op)
            return left.strip(), op, right.strip()
    return None, None, None

def compile_assignment(line):
    var, value = line.split('=')
    var = var.strip()
    value = value.strip().rstrip(';')
    reg_var = get_register(var)

    if '+' in value:
        lhs, rhs = value.split('+')
        riscv_code.append(f"add {reg_var}, {get_register(lhs.strip())}, {get_register(rhs.strip())}")
    elif '-' in value:
        lhs, rhs = value.split('-')
        riscv_code.append(f"sub {reg_var}, {get_register(lhs.strip())}, {get_register(rhs.strip())}")
    elif '*' in value:
        lhs, rhs = value.split('*')
        riscv_code.append(f"mul {reg_var}, {get_register(lhs.strip())}, {get_register(rhs.strip())}")
    elif '/' in value:
        lhs, rhs = value.split('/')
        riscv_code.append(f"div {reg_var}, {get_register(lhs.strip())}, {get_register(rhs.strip())}")
    elif value.isdigit():
        riscv_code.append(f"li {reg_var}, {value}")
    else:
        reg_val = get_register(value)
        riscv_code.append(f"mv {reg_var}, {reg_val}")

def compile_block(block_lines):
    for line in block_lines:
        if '=' in line:
            compile_assignment(line.strip())

# ─── IF–ELSE IF–ELSE ZİNCİR DERLEYİCİ ───────────────────────
def compile_if_chain(cond0, block0, elifs, else_block):
    # Etiketleri oluştur
    labels_else = [generate_label() for _ in range(len(elifs) + 1)]
    label_end  = generate_label()

    # 1) İlk if
    rl0, op0, rr0 = parse_condition(cond0)
    rL0, rR0 = get_register(rl0), get_register(rr0)
    riscv_code.append(_make_branch(op0, rL0, rR0, labels_else[0]))
    compile_block(block0)
    riscv_code.append(f"j {label_end}")

    # 2) Her bir else if
    for idx, (cond_i, block_i) in enumerate(elifs):
        riscv_code.append(f"{labels_else[idx]}:")
        rli, opi, rri = parse_condition(cond_i)
        rLi, rRi = get_register(rli), get_register(rri)
        riscv_code.append(_make_branch(opi, rLi, rRi, labels_else[idx+1]))
        compile_block(block_i)
        riscv_code.append(f"j {label_end}")

    # 3) En son else (opsiyonel)
    riscv_code.append(f"{labels_else[-1]}:")
    if else_block:
        compile_block(else_block)

    # 4) Tüm zincir sonu
    riscv_code.append(f"{label_end}:")


def extract_block(lines, start_index):
    block = []
    i = start_index
    brace_count = 0
    if '{' in lines[i]:
        brace_count += 1
        i += 1
        while i < len(lines) and brace_count > 0:
            line = lines[i]
            if '{' in line:
                brace_count += 1
            if '}' in line:
                brace_count -= 1
            if brace_count > 0:
                block.append(line)
            i += 1
    else:
        block.append(lines[i])
        i += 1
    return block, i

def compile_code(c_code):
    global label_counter, register_map, next_register, riscv_code
    label_counter = 0
    register_map = {}
    next_register = 5
    riscv_code = []

    # Süslü parantezleri ayırmak istersen:
    pre = c_code.replace("{", "\n{\n").replace("}", "\n}\n")
    lines = [l.strip() for l in pre.splitlines() if l.strip()]

    i = 0
    while i < len(lines):
        line = lines[i]
        if line.startswith("if"):
    # 1. if
            cond0 = line[line.find('(')+1 : line.find(')')]
            block0, i = extract_block(lines, i+1)

    # 2. tüm else if’leri topla
            elifs = []
            while i < len(lines) and lines[i].startswith("else if"):
                cond_i = lines[i][lines[i].find('(')+1 : lines[i].find(')')]
                block_i, i = extract_block(lines, i+1)
                elifs.append((cond_i, block_i))

    # 3. son else
            else_block = None
            if i < len(lines) and lines[i].startswith("else"):
                else_block, i = extract_block(lines, i+1)

    # 4. zinciri derle
            compile_if_chain(cond0, block0, elifs, else_block)

        elif '=' in line:
            compile_assignment(line)
            i += 1
        else:
            i += 1

    return "\n".join(riscv_code)

# === GUI Logic ===

def convert_code():
    c_code = text_input.get("1.0", tk.END)
    try:
        output = compile_code(c_code)
        text_output.delete("1.0", tk.END)
        text_output.insert(tk.END, output)
    except Exception as e:
        messagebox.showerror("Hata", str(e))

def clear_text():
    text_input.delete("1.0", tk.END)
    text_output.delete("1.0", tk.END)

def copy_output():
    root.clipboard_clear()
    root.clipboard_append(text_output.get("1.0", tk.END))
    root.update()

def toggle_theme():
    is_dark[0] = not is_dark[0]
    bg_main = "#1e1e2f" if is_dark[0] else "white"
    bg_text = "#263238" if is_dark[0] else "white"
    fg_text = "#cfd8dc" if is_dark[0] else "black"
    fg_label = "#4fc3f7" if is_dark[0] else "black"

    root.configure(bg=bg_main)
    frame.configure(bg=bg_main)
    button_frame.configure(bg=bg_main)
    text_input.configure(bg=bg_text, fg=fg_text, insertbackground=fg_text)
    text_output.configure(bg=bg_text, fg=fg_text, insertbackground=fg_text)

    for widget in frame.winfo_children():
        if isinstance(widget, tk.Label):
            widget.configure(bg=bg_main, fg=fg_label)

def highlight_syntax(event=None):
    text_input.tag_remove("keyword", "1.0", tk.END)
    text_input.tag_remove("number", "1.0", tk.END)

    keywords = ["if", "else", "while", "for", "return", "int", "float", "char", "double", "==", "!=", "<=", ">=", "<", ">", "="]
    for keyword in keywords:
        start = "1.0"
        while True:
            pos = text_input.search(rf"\b{keyword}\b", start, stopindex=tk.END, regexp=True)
            if not pos:
                break
            end = f"{pos}+{len(keyword)}c"
            text_input.tag_add("keyword", pos, end)
            start = end
    text_input.tag_config("keyword", foreground="blue", font=("Courier", 10, "bold"))

    start = "1.0"
    while True:
        pos = text_input.search(r"\b\d+\b", start, stopindex=tk.END, regexp=True)
        if not pos:
            break
        end = f"{pos}+{len(text_input.get(pos, pos + ' wordend'))}c"
        text_input.tag_add("number", pos, end)
        start = end
    text_input.tag_config("number", foreground="darkorange")

# === GUI Setup ===

examples = [
    "a = 10;\nb = 5;\nc = a + b;",
    "if (a > b) {\n    c = a;\n} else {\n    c = b;\n}",
    "if (a == b) {\n    x = 1;\n} else {\n    x = 0;\n}",
    "if (a != b) {\n    y = a * b;\n} else {\n    y = 1;\n}",
    "a = b - c;\nd = a + 2;\n"
    "if (a < b) {\n    c = b;\n} else {\n    c = a;\n}",
    "if (a != b) {\n    y = a * b;\n} else {\n    y = 1;\n}",
    "if (a > b) {\n    x = 1;\n} else if (a == b) {\n    x = 2;\n} else {\n    x = 3;\n}",
]
current_example = [0]

is_dark = [True]

def insert_example():
    index = current_example[0]
    text_input.delete("1.0", tk.END)
    text_input.insert(tk.END, examples[index])
    current_example[0] = (index + 1) % len(examples)

root = tk.Tk()
root.title("C -> RISC-V Convert")
root.configure(bg="#1e1e2f")

title = tk.Label(root, text="C to RISC-V Converter", font=("Courier", 14, "bold"), bg="#1e1e2f", fg="#4fc3f7")
title.pack(pady=(10, 0))

frame = tk.Frame(root, bg="#1e1e2f")
frame.pack(padx=10, pady=10)

tk.Label(frame, text="C Kodu:", bg="#1e1e2f", fg="#4fc3f7", font=("Courier", 10, "bold")).grid(row=0, column=0, pady=5)
text_input = tk.Text(frame, height=10, width=50, wrap=tk.WORD, bg="#263238", fg="white", font=("Courier", 10), insertbackground="white")
text_input.grid(row=1, column=0, columnspan=4, padx=5, pady=5)

tk.Label(frame, text="RISC-V Çıktısı:", bg="#1e1e2f", fg="#4fc3f7", font=("Courier", 10, "bold")).grid(row=2, column=0, pady=5)
text_output = tk.Text(frame, height=10, width=50, wrap=tk.WORD, bg="#263238", fg="white", font=("Courier", 10), insertbackground="white")
text_output.grid(row=3, column=0, columnspan=4, padx=5, pady=5)

button_frame = tk.Frame(root, bg="#1e1e2f")
button_frame.pack(padx=10, pady=(0, 10))

tk.Button(button_frame, text="CONVERT", command=convert_code, width=15, height=2, bg="#4caf50", fg="white", font=("Courier", 10, "bold")).grid(row=0, column=0, padx=5, pady=5)
tk.Button(button_frame, text="CLEAR", command=clear_text, width=15, height=2, bg="#f44336", fg="white", font=("Courier", 10, "bold")).grid(row=0, column=1, padx=5, pady=5)
tk.Button(button_frame, text="COPY", command=copy_output, width=15, height=2, bg="#2196f3", fg="white", font=("Courier", 10, "bold")).grid(row=0, column=2, padx=5, pady=5)
tk.Button(button_frame, text="EXAMPLES", command=insert_example, width=15, height=2, bg="#9c27b0", fg="white", font=("Courier", 10, "bold")).grid(row=0, column=3, padx=5, pady=5)

root.mainloop()
