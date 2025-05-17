import polyline

# La polyline fournie
polyline_str = "_ttxA~_tiBEeCLCtAP\?LDLI@OKIM@s@@sAMaAUsBaAoMuHgAc@oAUoAKeA@k@DuCd@{A^eAb@qAx@o@n@i@v@Wh@uA`E}ArFyAxEi@zAgAfDc@t@aIpK}CrDQ\Un@k@`CSj@QXMHALa@j@iFpEsArAkBzB_CfDaAdAmA~@cAj@MBEJSTwBbB_Al@iA\{@LeA@iAAs@Hg@Pc@VyAnAcAf@mAZw@JiG^gAPaAZs@^g@`@q@n@UNQBGL@NBBm@dCe@pEG^KL@NJHh@z@PLj@t@^p@j@lBnAxEFj@@`AEh@Ib@iCfG]`@k@`@q@Tw@Hw@EkFw@w@Cy@B[Dy@Vw@`@aJlGuAt@eC_Q^On@a@f@Ij@B~Ab@LH\?XKRU?EDMEIMCGDEc@KUSSa@O"

try:
    # Tenter de décoder la polyline
    coords = polyline.decode(polyline_str)
    print(f"Décodage réussi! Nombre de points: {len(coords)}")
    
    # Afficher les premiers et derniers points
    if coords:
        print(f"Premier point: {coords[0]}")
        print(f"Dernier point: {coords[-1]}")
    
    # Vérifier si les coordonnées sont valides
    valid = all(len(point) == 2 and isinstance(point[0], float) and isinstance(point[1], float) for point in coords)
    print(f"Toutes les coordonnées sont valides: {valid}")
    
    # Si les coordonnées ne sont pas valides, trouver les points problématiques
    if not valid:
        for i, point in enumerate(coords):
            if len(point) != 2 or not isinstance(point[0], float) or not isinstance(point[1], float):
                print(f"Point invalide à l'indice {i}: {point}")
except Exception as e:
    print(f"Erreur lors du décodage: {e}")
