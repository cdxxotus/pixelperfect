common_words_lemonde = [
    "France", "président", "gouvernement", "politique", "économie", "santé", "environnement",
    "Europe", "Paris", "Covid-19", "vaccin", "élection", "éducation", "sécurité", "culture",
    "écologie", "transition", "numérique", "technologie", "emploi", "chômage", "réforme", "justice",
    "social", "international", "migrant", "réfugié", "crise", "confinement", "société", "démocratie",
    "terrorisme", "législation", "Brexit", "Union européenne", "Climat", "chauffage", "mobilité",
    "agriculture", "urbanisme", "logement", "famille", "égalité", "discrimination", "religion",
    "laïcité", "droits humains", "liberté", "presse", "médias", "journalisme", "fake news",
    "désinformation", "réseaux sociaux", "Facebook", "Twitter", "Instagram", "Google", "Amazon",
    "Microsoft", "Apple", "Tesla", "blockchain", "cryptomonnaie", "bitcoin", "finance", "bourse",
    "banque", "prêt", "hypothèque", "fiscalité", "impôt", "taxe", "budget", "dépense", "déficit",
    "dette", "PIB", "inflation", "récession", "croissance", "commerce", "exportation", "importation",
    "investissement", "start-up", "innovation", "entrepreneuriat", "cybersécurité", "intelligence artificielle",
    "robotique", "Big Data", "cloud computing", "IoT", "5G", "smart city", "énergie", "nucléaire",
    "énergies renouvelables", "solaire", "éolien", "hydroélectrique", "biomasse", "automobile", "transport",
    "train", "avion", "voiture électrique", "vélo", "scooter", "bus", "taxi", "Uber", "logistique",
    "supply chain", "distribution", "commerce en ligne", "livraison", "Amazon Prime", "e-commerce",
    "alimentation", "bio", "OGM", "pesticides", "viande", "végétarien", "végan", "supermarché", "marché",
    "restaurant", "café", "bar", "brasserie", "boisson", "vin", "bière", "champagne", "cocktail",
    "cuisine", "recette", "gastronomie", "chef", "Michelin", "mode", "vêtement", "chaussure", "accessoire",
    "marque", "luxe", "bijoux", "montre", "parfum", "beauté", "cosmétique", "maquillage", "soin",
    "fitness", "yoga", "gym", "musculation", "sport", "football", "basketball", "tennis", "rugby",
    "athlétisme", "olympique", "compétition", "tournoi", "championnat", "équipe", "joueur", "entraîneur",
    "arbitre", "stade", "match", "résultat", "classement", "statistique", "médaille", "dopage", "record",
    "spectacle", "cinéma", "film", "série", "documentaire", "animation", "dessin animé", "comédie",
    "drame", "thriller", "action", "science-fiction", "fantastique", "horreur", "romance", "acteur",
    "actrice", "réalisateur", "producteur", "scénariste", "filmographie", "Oscar", "César", "Festival",
    "Cannes", "Berlin", "Venise", "Hollywood", "Bollywood", "Netflix", "Amazon Prime Video", "HBO",
    "Disney+", "Apple TV+", "YouTube", "TikTok", "Snapchat", "influenceur", "abonné", "abonnement",
    "streaming", "podcast", "webinaire", "visioconférence", "télétravail", "bureau", "open space",
    "coworking", "start-up", "incubateur", "accélérateur", "mentor", "investisseur", "capital-risque",
    "financement", "levée de fonds", "business plan", "stratégie", "marketing", "communication",
    "publicité", "SEO", "SEA", "référencement", "audience", "trafic", "conversion", "ROI", "KPI",
    "analytics", "CRM", "e-mailing", "newsletter", "content marketing", "brand content", "community management",
    "social media", "inbound marketing", "outbound marketing", "lead generation", "lead nurturing",
    "marketing automation", "influence marketing", "branding", "image de marque", "positionnement",
    "cible", "personas", "segmentation", "campagne", "création de contenu", "rédaction", "copywriting",
    "storytelling", "infographie", "vidéo", "motion design", "webdesign", "UX/UI", "ergonomie",
    "accessibilité", "responsive design", "mobile first", "e-commerce", "m-commerce", "omnicanal",
    "click and collect", "drive", "marketplace", "dropshipping", "logistique", "supply chain",
    "entrepôt", "livraison", "last mile delivery", "transport", "fret", "logistique urbaine",
    "logistique verte", "logistique durable", "mobilité", "transport en commun", "transports doux",
    "covoiturage", "autopartage", "voiture autonome", "mobilité urbaine", "mobilité intelligente",
    "smart city", "ville connectée", "ville intelligente", "urbanisme", "aménagement urbain",
    "infrastructure", "voirie", "réseau", "fibre optique", "réseau mobile", "antennes", "5G",
    "internet des objets", "IoT", "smart home", "domotique", "objets connectés", "sécurité",
    "cybersécurité", "protection des données", "RGPD", "privacy", "identité numérique", "blockchain",
    "cryptomonnaie", "bitcoin", "ethereum", "NFT", "smart contract", "DeFi", "fintech", "banque digitale",
    "néobanque", "assurtech", "insurtech", "proptech", "legaltech", "healthtech", "biotech", "medtech",
    "edtech", "cleantech", "greentech", "deeptech", "space tech", "agritech", "foodtech", "retailtech",
    "martech", "adtech", "HR tech", "recrutement", "ressources humaines", "management", "leadership",
    "gestion de projet", "méthode agile", "scrum", "kanban", "devops", "transformation digitale",
    "digital workplace", "outils collaboratifs", "visioconférence", "télétravail", "coworking", "open space",
    "flex office", "bureau virtuel", "cloud computing", "SaaS", "PaaS", "IaaS", "serveur", "hébergement",
    "datacenter", "infrastructure IT", "sécurité informatique", "cybersécurité", "protection des données",
    "RGPD", "privacy", "identité numérique", "blockchain", "cryptomonnaie", "bitcoin", "ethereum",
    "NFT", "smart contract", "DeFi", "fintech", "banque digitale", "néobanque", "assurtech", "insurtech",
    "proptech", "legaltech", "healthtech", "biotech", "medtech", "edtech", "cleantech", "greentech",
    "deeptech", "space tech", "agritech", "foodtech", "retailtech", "martech", "adtech", "HR tech"
]



# Load the file content
file_path = 'pointers/@'
with open(file_path, 'r', encoding='utf-8') as file:
    lines = file.readlines()

# Track words that have already been inserted
inserted_words = set()

# Insert common words into the file starting from line 42
start_line = 2734  # line index starts from 0, so 42nd line is index 41
current_line = start_line

for word in common_words_lemonde:
    # Check if the word is already in the file or has been inserted
    if word not in inserted_words and all(word not in line for line in lines):
        lines[current_line] = lines[current_line].strip() + word + "\n"
        inserted_words.add(word)
        current_line += 1

# Save the modified content back to the file
with open(file_path, 'w', encoding='utf-8') as file:
    file.writelines(lines)

print(f"Inserted {len(common_words_lemonde)} common words into the file starting from line 2735.")
