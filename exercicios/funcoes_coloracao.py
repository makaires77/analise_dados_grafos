
def random_colors(n):
    import random
    random.seed()
    saida = []
    for i in range(n):
        r = random.randint(0, 255)
        g = random.randint(0, 255)
        b = random.randint(0, 255)
        saida.append((r, g, b))

    return saida


def colorir_grafo_greedy(matriz_adjacencia, ponto_partida):
    import numpy as np
    import random
    random.seed()
    lista_cores_utilizadas = np.zeros_like(range(matriz_adjacencia.shape[0]))

    def colorir(ponto_partida):

        vizinhos = np.where(matriz_adjacencia[ponto_partida, :] == 1)[0]
        cores_vizinhos = sorted(lista_cores_utilizadas[vizinhos])
        cor_selecionada = lista_cores_utilizadas[ponto_partida]
        for cor in range(1, max(cores_vizinhos)+1):
            if cor not in cores_vizinhos:
                cor_selecionada = cor
                break

        if cor_selecionada == 0:
            cor_selecionada = max(cores_vizinhos)+1

        lista_cores_utilizadas[ponto_partida] = cor_selecionada

        vizinhos = [viz for viz in vizinhos if lista_cores_utilizadas[viz] == 0]

        if len(vizinhos) > 0:
            random.shuffle(vizinhos)
            for viz in vizinhos:
                colorir(viz)

    colorir(ponto_partida)

    return lista_cores_utilizadas


def graph_to_png(matriz_adjacencia, nome_arquivo, lista_labels=[], ponto_partida = -1):
    import random
    random.seed()
    import networkx as nx
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    grafo = nx.from_numpy_array(matriz_adjacencia)
    labels = list(range(matriz_adjacencia.shape[0]))
    if ponto_partida == -1:
        ponto_partida = random.choice(labels)
    cores_atribuidas = colorir_grafo_greedy(matriz_adjacencia, ponto_partida)
    cores = random_colors(max(cores_atribuidas))

    if len(lista_labels) == len(labels):
        labels = [lista_labels[l] for l in labels]
    # dict_cores = dict([(l, cores[cores_atribuidas[i]-1])
    #                    for i, l in enumerate(labels)])

    f = plt.figure()
    dict_ind_label = dict([(indice, letra)
                           for indice, letra in enumerate(labels)])
    # pos = nx.spring_layout(grafo)
    pos = nx.circular_layout(grafo)
    nx.draw(grafo,
            pos,
            ax=f.add_subplot(111),
            labels=dict_ind_label,
            node_color=cores_atribuidas,
            font_color='white',
            with_labels=True)
    f.savefig(nome_arquivo)



def animar_matriz_media_cumulativa(matriz,titulo,segundos,labels,matriz_simulacoes):
    from matplotlib import pyplot as plt
    from matplotlib.colors import get_named_colors_mapping
    from celluloid import Camera
    import numpy as np
    import random
    num_quadros = matriz.shape[1]
    fps = num_quadros // segundos
    # plt.figure(figsize=(16,10))
    fig, ax = plt.subplots()
    maximo = np.max(matriz_simulacoes)
    minimo = np.min(matriz_simulacoes)
    
    ax.set_ylim(minimo* 0.8, maximo * 1.2)
    ax.set_xlim(0,num_quadros)
    
    camera = Camera(fig)

    cor = random.choices(list(get_named_colors_mapping().keys()),k=len(labels))
    max_sim = [] 
    min_sim = []
    for i in range(matriz.shape[1]):
        
        # plt.legend()
        s = matriz[:,i]
        max_sim.append(np.max(s))
        min_sim.append(np.min(s))
        eixo_x = list(range(i+1))
        # ax.axhline(np.max(s),c='green',ls="--")
        # ax.axhline(np.min(s), c='blue',ls="--")    
          
        for j,linha in enumerate(matriz[:,:i+1]):
            label = labels[j]
            
            ax.plot(eixo_x,linha, label=label,c=cor[j], linewidth=1)
        if matriz.shape[0] > 1:    
            ax.plot(eixo_x,max_sim,label='Valor máximo local',c='black',ls="--")
            ax.plot(eixo_x,min_sim, label='Valor mínimo local',c='black',ls="--")
        if maximo > minimo:
            ax.axhline(maximo, label='Valor máximo', c='red',ls=":")
            ax.axhline(minimo, label='Valor mínimo', c='red',ls=":")
        camera.snap()

    animation = camera.animate()
    animation.save(titulo, fps=fps)

def simular(matriz_adjacencia, i, label):
    num_cores = max(colorir_grafo_greedy(matriz_adjacencia, i))
    return {label:num_cores}


def realizar_n_simulacoes(matriz_adjacencia, i, label,num_simulacoes):
    import multiprocessing as mp
    from multiprocessing import Pool
    args = [(matriz_adjacencia, i, label) for _ in range(num_simulacoes)]
    n_cores = mp.cpu_count()
    pool = Pool(n_cores)
    resultado = pool.starmap_async(simular, args)
    pool.close()
    pool.join()
    lista = [valor[label] for valor in resultado]
    return {label:lista}
    

def gerar_dicionarios(matriz_adjacencia,num_simulacoes, labels):
    import numpy as np
    import multiprocessing as mp
    import pandas as pd
    from multiprocessing import Pool

    args = [(matriz_adjacencia,i,label) for i,label in enumerate(labels)]
    
    n_cores = mp.cpu_count()
    
    pool = Pool(n_cores)
    resultados = dict()
    for i in range(num_simulacoes):
        resultados[i] = pool.starmap(simular, args)

    pool.close()
    pool.join()
    saida = []

    for resultado in resultados.values():
        dict_agregado = {}
        for r in resultado:
            dict_agregado = {**dict_agregado,**r}
        saida.append(dict_agregado)
    dict_resultados_final = dict([(label,[]) for label in labels])
    for s in saida:
        for label in labels:
            dict_resultados_final[label].append(s[label])

    # saida = dict([(label,[]) for label in labels])
    # for _ in range(num_simulacoes):
    #     for i,label in enumerate(labels):
    #         num_cores = max(colorir_grafo_greedy(matriz_adjacencia, i))
    #         saida[label].append(num_cores)
    # matriz_media_acumulativa = 
    # dict_max = dict([(label, np.max(lista)) for label, lista in dict_resultados_final.items()])
    # dict_min = dict([(label, np.min(lista)) for label, lista in dict_resultados_final.items()])
    # dict_media = dict([(label, np.mean(lista)) for label, lista in dict_resultados_final.items()])
    dict_media_acumulativa = dict([(label, [np.mean(lista[:i+1]) for i,_ in enumerate(lista)]) for label, lista in dict_resultados_final.items()])
    matriz_simulacoes = np.stack(list(dict_resultados_final.values()))
    # matriz_media_acumulativa = np.stack([])
    matriz_media_acumulativa = np.stack(list(dict_media_acumulativa.values()))
 

    return matriz_simulacoes, matriz_media_acumulativa



