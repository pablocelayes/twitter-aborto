from twitter_api import API_HANDLER as TW

def agregar_conexiones(g):
    """
        Dado un grafo incompleto de usuarios
        agrega relaciones de seguir entre sus nodos
    """
    g = g.copy()
    uids_g = list(g.nodes())

    for uid in uids_g:
        print uid
        seguidos = TW.traer_seguidos(user_id=uid)
        g.add_edges_from([(uid, sid) for sid in seguidos if sid in uids_g])

    return g