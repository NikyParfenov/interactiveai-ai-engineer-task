LLM_PHRASES = {
    'en': [
        "delve into", "dive into", "embark on", "navigate", 
        "in conclusion", "it's worth noting", "it is worth noting",
        "in today's", "in todays", "leverage", "robust", 
        "utilize", "optimize", "furthermore", "moreover", 
        "nonetheless", "ergo", "thus", "unlock", "harness",
        "boasts", "nestled", "showcase", "unparalleled",
        "exceptional", "magnificent", "stunning"
    ],
    'pt': [
        "mergulhar em", "embarcar em", "navegar", "em conclusão",
        "vale a pena notar", "nos dias de hoje", "alavancar",
        "robusto", "utilizar", "otimizar", "além disso",
        "no entanto", "portanto", "assim", "desbloquear",
        "aproveitar", "ostenta", "situado", "exibir",
        "incomparável", "excepcional", "magnífico", "deslumbrante"
    ],
    'es': [
        "sumergirse en", "embarcarse en", "navegar", "en conclusión",
        "vale la pena señalar", "en los días de hoy", "aprovechar",
        "robusto", "utilizar", "optimizar", "además",
        "sin embargo", "por lo tanto", "así", "desbloquear",
        "presume", "situado", "exhibir", "incomparable",
        "excepcional", "magnífico", "impresionante"
    ],
    'fr': [
        "plonger dans", "se lancer dans", "naviguer", "en conclusion",
        "il convient de noter", "de nos jours", "tirer parti",
        "robuste", "utiliser", "optimiser", "en outre",
        "néanmoins", "donc", "ainsi", "déverrouiller",
        "se vante", "niché", "présenter", "inégalé",
        "exceptionnel", "magnifique", "époustouflant"
    ],
    'de': [
        "eintauchen in", "sich einlassen auf", "navigieren", "zusammenfassend",
        "es ist erwähnenswert", "heutzutage", "nutzen",
        "robust", "verwenden", "optimieren", "darüber hinaus",
        "dennoch", "daher", "somit", "freischalten",
        "prahlt", "eingebettet", "präsentieren", "unvergleichlich",
        "außergewöhnlich", "prächtig", "atemberaubend"
    ],
    'it': [
        "immergersi in", "intraprendere", "navigare", "in conclusione",
        "vale la pena notare", "al giorno d'oggi", "sfruttare",
        "robusto", "utilizzare", "ottimizzare", "inoltre",
        "tuttavia", "pertanto", "così", "sbloccare",
        "vanta", "situato", "mostrare", "impareggiabile",
        "eccezionale", "magnifico", "mozzafiato"
    ],
    'nl': [
        "duiken in", "beginnen aan", "navigeren", "concluderend",
        "het is vermeldenswaard", "tegenwoordig", "benutten",
        "robuust", "gebruiken", "optimaliseren", "bovendien",
        "desondanks", "daarom", "dus", "ontgrendelen",
        "pronkt", "gelegen", "tonen", "ongeëvenaard",
        "uitzonderlijk", "prachtig", "adembenemend"
    ]
}


CTA_PATTERNS = {
    'en': [
        r'contact', r'schedule', r'visit', r'call', r'book',
        r"don't miss", r"dont miss", r'opportunity', r'inquire', 
        r'request', r'learn more', r'find out', r'discover', 
        r'explore', r'get in touch', r'reach out', r'arrange',
        r'reserve', r'view', r'tour', r'see', r'check out'
    ],
    'pt': [
        r'contacte', r'contactar', r'agende', r'visite', r'ligue',
        r'reserve', r'não perca', r'nao perca', r'oportunidade',
        r'solicite', r'peça', r'saiba mais', r'descubra',
        r'explore', r'entre em contato', r'marque', r'visitar',
        r'conheça', r'conheca', r'veja', r'confira'
    ],
    'es': [
        r'contacte', r'contactar', r'programe', r'agende', r'visite',
        r'llame', r'reserve', r'no pierda', r'oportunidad',
        r'solicite', r'pida', r'aprenda más', r'descubra',
        r'explore', r'póngase en contacto', r'comuníquese',
        r'concierte', r'conozca', r'vea', r'consulte'
    ],
    'fr': [
        r'contactez', r'contacter', r'planifiez', r'visitez',
        r'appelez', r'réservez', r'ne manquez pas', r'opportunité',
        r'demandez', r'renseignez', r'en savoir plus', r'découvrez',
        r'explorez', r'prenez contact', r'organisez', r'rencontrez',
        r'connaissez', r'voyez', r'consultez'
    ],
    'de': [
        r'kontaktieren', r'kontakt', r'planen', r'vereinbaren',
        r'besuchen', r'anrufen', r'buchen', r'verpassen sie nicht',
        r'gelegenheit', r'anfragen', r'erfahren sie mehr',
        r'entdecken', r'erkunden', r'besichtigen', r'besichtigung',
        r'sehen', r'prüfen'
    ],
    'it': [
        r'contattare', r'contatto', r'programmare', r'visitare',
        r'chiamare', r'prenotare', r'non perdere', r'opportunità',
        r'richiedere', r'chiedere', r'scopri di più', r'scoprire',
        r'esplorare', r'mettersi in contatto', r'organizzare',
        r'vedere', r'consultare'
    ]
}


PROPERTY_TYPES = {
    'en': [
        r'apartment', r'flat', r'house', r'villa', r'studio',
        r'penthouse', r'duplex', r'townhouse', r'condo', r'loft',
        r'property', r'residence', r'home', r'dwelling',
        r't0', r't1', r't2', r't3', r't4', r't5'
    ],
    'pt': [
        r'apartamento', r'moradia', r'vivenda', r'casa',
        r'estúdio', r'studio', r'cobertura', r'duplex',
        r'triplex', r'loft', r'propriedade', r'residência',
        r'habitação', r'imóvel',
        r't0', r't1', r't2', r't3', r't4', r't5'
    ],
    'es': [
        r'apartamento', r'piso', r'casa', r'chalet', r'villa',
        r'estudio', r'ático', r'dúplex', r'duplex', r'loft',
        r'propiedad', r'residencia', r'vivienda', r'inmueble'
    ],
    'fr': [
        r'appartement', r'maison', r'villa', r'studio',
        r'penthouse', r'duplex', r'loft', r'propriété',
        r'résidence', r'habitation', r'logement', r'immeuble'
    ],
    'de': [
        r'wohnung', r'haus', r'villa', r'studio',
        r'penthouse', r'maisonette', r'loft', r'immobilie',
        r'residenz', r'eigenheim', r'apartment'
    ],
    'it': [
        r'appartamento', r'casa', r'villa', r'monolocale',
        r'attico', r'duplex', r'loft', r'proprietà',
        r'residenza', r'abitazione', r'immobile'
    ]
}