"""Target schema of the NocoDB base, V1.

V1 is the smallest schema that lets us import the SMA history and iterate. Rule: get right now what
is expensive to change later (how tables link to each other); postpone what is cheap to add (a field,
a table, a list value).

Conventions
- Table titles are snake_case French, as in the POC.
- Field titles are what the people entering cases see (French, accents); `column` is the physical column name
  (snake_case, ASCII) that developers see. Links are virtual and have no column.
- `computed` fields (lookups, formulas) are created after the links they read. A link cannot be a
  display value in NocoDB, a formula can: a formula over a lookup shows a linked record's label.
- Link types (NocoDB): "mo" = this record points to one record of `to`; "mm" = many on both sides.
  NocoDB creates the reverse field on the other table automatically; `reverse` on a table is the
  title of the reverse fields its links create (e.g. "Auteurs" on cas, echelon, type_auteur...);
  a link can override it with its own `reverse` when one title does not read right on every table.
- Reference values follow the vocabulary of the SMA spreadsheet so the import maps them 1:1; `famille` groups political orientations for the site filters.
"""


def text(title, column):
    return {"title": title, "column": column, "type": "SingleLineText"}


def long_text(title, column):
    return {"title": title, "column": column, "type": "LongText"}


def number(title, column):
    return {"title": title, "column": column, "type": "Number"}


def date(title, column):
    return {"title": title, "column": column, "type": "Date"}


def checkbox(title, column):
    return {"title": title, "column": column, "type": "Checkbox"}


def url(title, column):
    return {"title": title, "column": column, "type": "URL"}


def decimal(title, column):
    return {"title": title, "column": column, "type": "Decimal"}


def select(title, column, options):
    return {"title": title, "column": column, "type": "SingleSelect", "options": options}


def link(title, to, type_, reverse=None):
    spec = {"title": title, "to": to, "type": type_}
    if reverse:
        spec["reverse"] = reverse
    return spec


def lookup(title, via, field):
    """Read-only copy of `field` from the record that the link `via` points to."""
    return {"title": title, "type": "Lookup", "via": via, "field": field}


def formula(title, expression):
    return {"title": title, "type": "Formula", "formula": expression}


def reference(title, values, extra_fields=()):
    """A closed list: one `libelle` field, plus optional extra fields, seeded with values."""
    return {"title": title, "display": "libelle",
            "fields": [text("libelle", "libelle"), *extra_fields], "links": [], "seeds": values}


MOIS = ["Janvier", "Février", "Mars", "Avril", "Mai", "Juin", "Juillet", "Août",
        "Septembre", "Octobre", "Novembre", "Décembre"]

# Decided on 2026-10-25: "Validé" means published on the site; the SMA history is imported as "À valider".
STATUTS = ["Brouillon", "À valider", "Validé", "Archivé"]

FAMILLES = ["Extrême droite", "Droite", "Centre", "Gauche", "Écologiste", "Autre", "Inconnue"]

# Order matters: a table must exist before another table links to it.
TABLES = [
    reference("region", [
        "Auvergne-Rhône-Alpes", "Bourgogne-Franche-Comté", "Bretagne", "Centre-Val de Loire", "Corse",
        "Grand Est", "Hauts-de-France", "Île-de-France", "Normandie", "Nouvelle-Aquitaine", "Occitanie",
        "Pays de la Loire", "Provence-Alpes-Côte d'Azur", "Guadeloupe", "Martinique", "Guyane",
        "La Réunion", "Mayotte",
    ]),
    reference("type_entrave", [
        # Labels of the 2026-10-08 data model doc (singular)
        "Financière et matérielle", "Juridique et réglementaire",
        "Symbolique et disqualification", "Policière et physique",
    ]),
    reference("motif", [
        "Contenu ou esthétique de l'oeuvre", "Engagement politique", "Contexte géopolitique",
        "Trouble à l'ordre public/non-respect du CER ou du principe de neutralité", "Religion",
        "Genre et sexualités", "Origines, racisme", "Contraintes budgétaires ou matérielles",
    ]),
    reference("consequence", [
        "Annulation d'événement", "Retrait de subvention ou de rémunération",
        "Sabotage/trouble de l'événement", "Diffamation et menaces",
        "Déplacement d'événement (date/lieu)", "Déploiement de système de police renforcé",
        "Retrait de locaux",
    ]),
    reference("secteur", [
        "Musique", "Théâtre", "Danse", "Arts visuels", "Cinéma", "Livre", "Humour",
        "Arts de la rue", "Médias",
    ]),
    reference("type_cible", [
        # Values of the SMA spreadsheet
        "Organisateur-ice", "Artiste",
    ]),
    reference("type_auteur", [
        "Elu-e", "Parti politique", "Groupuscule/collectif", "Individu isolé-e",
        "Entreprises ou associations tierces", "Etat : préfecture, ministère, police, etc",
        "Autorité religieuse",  # neutral label, to confirm with the SMA
    ]),
    # Detail kept in the base under the "Élu·e" category, as agreed with the SMA (2026-10-08).
    reference("echelon", ["Mairie", "Conseil départemental", "Conseil régional", "Elu-e d'opposition"]),
    reference("orientation_politique", [
        {"libelle": "Rassemblement national", "famille": "Extrême droite"},
        {"libelle": "Reconquête", "famille": "Extrême droite"},
        {"libelle": "UDR", "famille": "Extrême droite"},
        {"libelle": "Identité-Libertés", "famille": "Extrême droite"},
        {"libelle": "LR", "famille": "Droite"},
        {"libelle": "Divers droite", "famille": "Droite"},
        {"libelle": "Nouvelle Énergie", "famille": "Droite"},
        {"libelle": "Horizons", "famille": "Centre"},
        {"libelle": "Renaissance", "famille": "Centre"},
        {"libelle": "UDI", "famille": "Centre"},
        {"libelle": "Divers centre", "famille": "Centre"},
        {"libelle": "PS", "famille": "Gauche"},
        {"libelle": "PCF", "famille": "Gauche"},
        {"libelle": "LFI", "famille": "Gauche"},
        {"libelle": "Divers gauche", "famille": "Gauche"},
        {"libelle": "EELV", "famille": "Écologiste"},
        {"libelle": "Sans étiquette", "famille": "Autre"},
    ], extra_fields=[select("famille", "famille", FAMILLES)]),
    reference("organisation", ["SMA", "OLA"]),
    {
        "title": "commune", "display": "Nom",
        "fields": [
            text("Nom", "nom"),
            text("Code INSEE", "code_insee"),
            text("Département", "departement"),
            decimal("latitude", "latitude"),
            decimal("longitude", "longitude"),
        ],
        "links": [link("Région", "region", "mo")], "reverse": "Communes",
    },
    {
        "title": "source", "display": "titre",
        "fields": [
            text("titre", "titre"),
            url("url", "url"),
            text("Média", "media"),
            date("Date de publication", "date_publication"),
            select("type", "type", [
                "Presse", "Communiqué", "Compte rendu de conseil", "Décision de justice", "Témoignage",
            ]),
        ],
        "links": [],
    },
    {
        "title": "structure", "display": "Nom",
        "fields": [text("Nom", "Nom"), checkbox("est_association", "est_association")],
        # No Cible: the target is entered once, on the case (cas.Cibles).
        "links": [link("Commune", "commune", "mo")], "reverse": "Structures",
    },
    {
        "title": "cas", "display": "Titre",
        "fields": [
            text("Titre", "titre"),
            long_text("Description", "description"),
            number("Année", "annee"),
            select("Mois", "mois", MOIS),
            number("Jour", "jour"),  # optional, filled when known
            select("Statut", "statut", STATUTS),
            checkbox("Médiatisé", "mediatise"),
        ],
        "links": [
            link("Commune", "commune", "mo"),
            link("Région", "region", "mo"),  # for regional cases without a commune
            link("Structures", "structure", "mm"),
            link("Sources", "source", "mm"),
            link("Types d'entrave", "type_entrave", "mm"),
            link("Motifs", "motif", "mm"),
            link("Conséquences", "consequence", "mm"),
            link("Secteurs", "secteur", "mm"),
            link("Cibles", "type_cible", "mm"),
            link("Couleur de la mairie", "orientation_politique", "mo"),  # kept pending a team decision on political labels
        ],
        "reverse": "Cas",
    },
    {
        # One row per perpetrator of a case: the `case_perpetrator` of the 2026-10-08 data model doc,
        # named cas_auteur (schema in French). The obstruction type stays on the case: the sources
        # never say which actor did which type. `Type d'auteur` is the category shown in the site
        # filter; `Détail de l'auteur` is the precise perpetrator shown in the case page
        # ("Préfecture de l'Isère", "CRIF"), until named perpetrators get their own table.
        "title": "cas_auteur", "display": "Détail de l'auteur",
        "fields": [
            text("Détail de l'auteur", "detail_auteur"),
            select("Rôle", "role", ["Décision", "Pression", "Exécution"]),
        ],
        "links": [
            link("Cas", "cas", "mo"),
            link("Type d'auteur", "type_auteur", "mo"),
            link("Échelon", "echelon", "mo"),
            link("Orientation politique", "orientation_politique", "mo"),
        ],
        "reverse": "Auteurs",
    },
    {
        # Who reported the case. No external reference (OLA record number, SMA file number) in V1.
        # Display value = the organisation's name, so a case shows "Recensé par: SMA, OLA".
        "title": "cas_organisation", "display": "Libellé",
        # The date when the organisation entered the case; a Date they can correct, not a
        # creation timestamp. For the imported history it is the import date, as the 2026-10-08 data model doc planned.
        "fields": [date("Date de recensement", "date_recensement")],
        "computed": [lookup("Nom de l'organisation", "Organisation", "libelle"),
                     formula("Libellé", "{Nom de l'organisation}")],
        # Not "Signalements": that reads like the public reporting sent to the OLA.
        "links": [link("Cas", "cas", "mo"), link("Organisation", "organisation", "mo", reverse="Cas recensés")],
        "reverse": "Recensé par",
    },
]
