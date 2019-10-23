import xml.etree.ElementTree as ET
tree = ET.parse('tabParsing.xml')
root = tree.getroot()

fita = ['BIN', 'VAR', '~', 'NUM', '.', 'SE', 'VAR', 'MENOR', 'NUM', '{', 'VAR', '~', 'NUM', '.', '}', 'EOF']
symbols = []
symbols_indexes = {}
productions = []
lalr_table = []


# criação do vetor "symbols", cada posição é um
# dicionário que representa um símbolo e contém
# nome e tipo, nomeclatura seguindo o xml
xml_symbols = root.iter('Symbol')
for symbol in xml_symbols:
    symbols.append({
        'Name': symbol.attrib['Name'],
        'Type': symbol.attrib['Type']
    })


# dicionário pra descobrir rapidamente qual é
# o índice na tabela de um determinado estado
for index, symbol in enumerate(symbols):
    symbols_indexes[symbol['Name']] = str(index)


# criação do vetor "productions", cada posição é um
# dicionário que representa uma produção e contém
# índice do NT, quantidade de simbolos e a
# string da prod (por enquanto não utilizada)
xml_productions = root.iter('Production')
for production in xml_productions:
    productions.append({
        'NonTerminalIndex': production.attrib['NonTerminalIndex'],
        'SymbolCount': int(production.attrib['SymbolCount']),
        'String': symbols[int(production.attrib['NonTerminalIndex'])]['Name'] + ' ::='
    })
    for prod_symbol in production:
        productions[len(productions)-1]['String'] += ' ' + symbols[int(prod_symbol.attrib['SymbolIndex'])]['Name']


# vetor mapeamento da tabela lalr em ações
# o índice mais externo representa o estado
# cada estado possui um dicionário que possui um
# conjunto de ações, identificadas pelo símbolo da transição
# ex.: se estou no estado 0 (zero) e leio um '7' da fita
# ação = tabela[0]['7']
# obs.: o '7' é o "SymbolIndex" do elemento lido
lalr_states = root.iter('LALRState')
for state in lalr_states:
    lalr_table.append({})
    for action in state:
        lalr_table[int(state.attrib['Index'])][str(action.attrib['SymbolIndex'])] = {
                'Action': action.attrib['Action'],
                'Value': action.attrib['Value']
            }


print(symbols)
print(symbols_indexes)
print(productions)
print(lalr_table)

state = ['0']
i = 0                   #utilizado para testar

while True:
    i += 1
    ultimo_fita = fita[0]
    action = lalr_table[int(state[0])][symbols_indexes[ultimo_fita]]

    if action['Action'] == '1':
        state.insert(0, fita.pop(0))
        state.insert(0, action['Value'])
    elif action['Action'] == '2':
        size = productions[int(action['Value'])]['SymbolCount'] * 2
        while size:
            state.pop(0)
            size -= 1
        # salto
        state.insert(0, symbols[int(productions[int(action['Value'])]['NonTerminalIndex'])]['Name'])
        state.insert(0, lalr_table[int(state[1])][symbols_indexes[state[0]]]['Value'])
    elif action['Action'] == '3':
        print('salto')
    elif action['Action'] == '4':
        print('Código aceito')
        break

    # if i == 0: #utilizado para testar
    #     break

print(action)
print(state)
print(fita)



#eoq teste