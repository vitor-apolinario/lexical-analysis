import csv
arquivo = list(open('tokens.txt'))

simbolos = []
estados = []
alcan = []
mortos = []
gramatica = {}
tabela = {}
finais = []
epTransicao = {}
repeticao = 0


def eliminar_incal():
    loop = {}
    loop.update(tabela)
    for regra in loop:
        if regra not in alcan:
            del tabela[regra]
                

def buscar_alcan(estado):
    if estado not in alcan:         
        alcan.append(estado)
        for tran in tabela[estado]:
            if str(tabela[estado][tran])[2:-2] != '' and str(tabela[estado][tran])[2:-2] != 'X':
                buscar_alcan(str(tabela[estado][tran])[2:-2])


def encontrar_eps_set(e_transicoes):
    for x in e_transicoes:
        for y in tabela[x]['*']:
            if y not in e_transicoes:
                e_transicoes.append(y)
    return e_transicoes


def eliminar_et():
    for regra in tabela:
        et_set = encontrar_eps_set(tabela[regra]['*'])
        for estado in et_set:
            if estado in finais:
                finais.append(regra)
            for simbolo in tabela[estado]:
                for transicao in tabela[estado][simbolo]:
                    if transicao not in tabela[regra][simbolo]:
                        tabela[regra][simbolo].append(transicao)
        tabela[regra]['*'] = []


def criar_novos(nstates):
    for x in nstates:
        tabela[x] = {}
        estados.append(x)
        for y in simbolos:
            tabela[x][y] = []
        tabela[x]['*'] = []

    for state in nstates:
        estadosjuntar = sorted(state.split(':'))
        for x in estadosjuntar:
            if x in finais and state not in finais:
                finais.append(state)
            if x == 'X':
                continue
            for simbolo in simbolos:
                for transition in tabela[x][simbolo]:
                    if not tabela[state][simbolo].__contains__(transition):
                        tabela[state][simbolo].append(transition)
    determizinar()


def determizinar():
    novosestados = []
    for regra in tabela:
        for producao in tabela[regra]:
            if len(tabela[regra][producao]) > 1:
                novo = []
                for estado in tabela[regra][producao]:
                    if ':' in estado:
                        for aux in estado.split(':'):
                            if aux not in novo:
                                novo.append(aux)
                    else:
                        if estado not in novo:
                            novo.append(estado)

                if novo:
                    novo = sorted(novo)
                    novo = ':'.join(novo)

                if novo and novo not in novosestados and novo not in list(tabela.keys()):
                    novosestados.append(novo)
                tabela[regra][producao] = novo.split()
    if novosestados:
        criar_novos(novosestados)
    

def criar_af():
    for x in gramatica:
        tabela[x] = {}
        estados.append(x)
        for y in simbolos:
            tabela[x][y] = []
        tabela[x]['*'] = []

    for regra in gramatica:
        for producao in gramatica[regra]:
            if len(producao) == 1 and producao.islower():
                tabela[regra][producao].append('X')
            elif producao[0] == '<':
                tabela[regra]['*'].append(producao.split('<')[1][:-1])
            elif producao != '*':
                tabela[regra][producao[0]].append(producao.split('<')[1][:-1])
            elif producao == '*' and regra not in finais:
                finais.append(regra)


def criar_sn(s):
    global repeticao
    if 'S' + str(repeticao) in gramatica:
        return
    gramatica['S' + str(repeticao)] = s.replace('\n', '').split(' ::= ')[1].replace('>', str(repeticao) + '>').split(' | ')


def tratar_estado_ini(sentenca, op, proxregra):
    global repeticao
    repeticao += 1
    sentenca = sentenca.replace('\n', '')
    if 'S' in gramatica and op == 'G':
        gramatica['S'] += sentenca.split(' ::= ')[1].replace('>',str(repeticao)+'>').split(' | ')
    elif 'S' not in gramatica and op == 'G':
        gramatica['S'] = sentenca.split(' ::= ')[1].replace('>',str(repeticao)+'>').split(' | ')
    elif 'S' in gramatica and op == 'T':
        gramatica['S'] += str(sentenca + proxregra).split()
    elif 'S' not in gramatica and op == 'T':
        gramatica['S'] = str(sentenca + proxregra).split()


def tratar_gramatica(gram, s):
    for x in gram.split(' ::= ')[1].replace('\n', '').split(' | '):
        if x[0] not in simbolos and x[0].islower():
            simbolos.append(x[0])
    regra = gram.split(' ::= ')[0].replace('>', str(repeticao)).replace('<', '')

    if '<S> ::=' in gram:
        tratar_estado_ini(gram, 'G', 'not used')
        if '<S>' in gram.replace('\n', '').split(' ::= ')[1]:
            criar_sn(s)
    else:
        if '<S>' in gram.replace('\n', '').split(' ::= ')[1]:
            criar_sn(s)
        gramatica[regra] = gram.replace('\n', '').split(' ::= ')[1].replace('>', str(repeticao)+'>').split(' | ')


def tratar_token(token):
    cop = token.replace('\n', '')
    token = list(token)
    if '\n' in token:
        token.remove('\n')
    for x in range(len(token)):
        if token[x] not in simbolos and token[x].islower():
            simbolos.append(token[x])
            
        if x == 0:
            regra = cop.upper() + '1'
        else:
            regra = cop.upper() + str(x)

        # é possível um token onde |token| = 1? se sim, falta tratar
        if x == 0 and x != len(token)-1:
            tratar_estado_ini(token[x], 'T', '<' + regra + '>')
        elif x == len(token)-1:
            gramatica[regra] = str(token[x] + '<' + cop.upper() + '>').split()
            gramatica[cop.upper()] = []
        else:
            gramatica[regra] = str(token[x]+ '<' + cop.upper() + str(x+1) + '>').split()


def criar_csv():
    with open('afnd.csv', 'w', newline='') as f:
        w = csv.writer(f)
        copydict = {}
        copydict.update(tabela)
        w.writerow(list(copydict['S'].keys()) + ['regra'])
        for x in copydict:
            if x in finais:
                copydict[x]['nomeregra'] = x + '*'
            else:
                copydict[x]['nomeregra'] = x
            w.writerow(copydict[x].values())


def estado_erro():
    tabela['€'] = {}
    for y in simbolos:
        tabela['€'][y] = []
    tabela['€']['*'] = []
    for regra in tabela:
        for simbolo in tabela[regra]:
            if not tabela[regra][simbolo] and (regra[-1].isnumeric() or regra in ['S', '€']):
                tabela[regra][simbolo] = ['€']
            elif not (regra[-1].isnumeric() or regra in ['S', '€']):
                tabela[regra][simbolo] = ['-']


def main():
    estadoinicial = ''
    for x in arquivo:
        if '<S> ::=' in x:
            estadoinicial = x
        if '::=' in x:
            tratar_gramatica(x, estadoinicial)
        else:
            tratar_token(x)
    criar_af()
    eliminar_et()
    determizinar()
    buscar_alcan('S')
    eliminar_incal()
    estado_erro()
    criar_csv()


main()


# gramatica exemplo
# if
# <S> ::= a<A> | b<B>
# <A> ::= x
# <B> ::= z
# else

# se
# entao
# senao
# <S> ::= a<A> | e<A> | i<A> | o<A> | u<A>
# <A> ::= a<A> | e<A> | i<A> | o<A> | u<A> | *

# se
# entao
# senao
# <S> ::= a<A> | e<A> | i<A> | o<A> | u<A> | <A>
# <A> ::= a<A> | e<A> | i<A> | o<A> | u<A> | *

# <S> ::= a<S> | <A>
# <A> ::= b<A> | <B>
# <B> ::= c<B> | *

# if
# <S> ::= a<A> | b<B> | b | c<S> | c | *
# <A> ::= a<S> | a | b<C> | c<A>
# <B> ::= a<A> | c<B> | c<S> | c
# <C> ::= a<S> | a | c<A> | c<C>
# else

# <S> ::= a<A> | a | b | c<C> | b<D>
# <A> ::= a<B> | b<A> | c<B> | *
# <B> ::= a<A> | b<B> | c<A> | a | c
# <C> ::= a<C> | b<D> | c<C> | b
# <D> ::= a<D> | b<C> | c<C> | * | c | a
# <E> ::= a<C> | b<F> | a
# <F> ::= b<E> | c<B> | b
