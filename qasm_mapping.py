from re import match, findall

def format(input_line, layout_map) -> str:
    """
    Returns new qasm line with physical qubit numbering.

    Args:
        input_line (str): Original qasm string.

        layout_map (dict): Logical to physical mapping.
    
    Returns:
        qasm_str (str): Newly mapped qasm string.

    Note:
        Assumes there is a single register named 'q', replaces that name with 
        'physical'.
    """
    # Find all instances of qubit reference
    if match('qreg', input_line):
        return input_line.replace('q[', 'physical[')

    qasm_str = input_line

    log_qubits = list(findall('q\[\d+\]', input_line))
    for lq in log_qubits:
        log_number = int(findall('\d+', lq)[0])
        replacement = 'physical[' + str(layout_map[log_number]) + ']'
        qasm_str = qasm_str.replace(lq, replacement)
        
    return qasm_str.replace('physical[', 'q[')

if __name__ == '__main__':
    str1 = "cx q[0], q[1];"
    str2 = "u3(0,0,-pi/4)  q[100];"
    str3 = ""

    mapping = {0:'a', 1:'b', 100:'c'}

    print(format(str1, mapping))
    print(format(str2, mapping))