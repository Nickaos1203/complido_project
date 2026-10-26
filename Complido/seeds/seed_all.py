"""
Seed de tous les référentiels JSON de Complido dans PostgreSQL.

Fichiers attendus dans le même dossier que ce script :
    data_categories.json
    data_subject_categories.json
    legal_bases.json
    operation_types.json
    recipients.json
    security_measures.json
    subprocessors.json

Tables PostgreSQL :
    personal_data_processing_datacategory
    personal_data_processing_datasubjectcategory
    personal_data_processing_legalbasis
    personal_data_processing_operationtype
    personal_data_processing_recipient
    personal_data_processing_securitymeasure
    personal_data_processing_subprocessor

Dépendance :
    pip install psycopg2-binary

Variables d'environnement :
    DB_NAME
    DB_USER
    DB_PASSWORD
    DB_HOST (défaut : localhost)
    DB_PORT (défaut : 5432)

Exécution :
    python seed_all.py
"""

import json
import os
from pathlib import Path

import psycopg2
from psycopg2 import sql

from dotenv import load_dotenv


# Chargement des variable du fichier .env
load_dotenv()


BASE_DIR = Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Configuration des seeds
# ---------------------------------------------------------------------------
SEEDS = [
    {
        "file": "data_categories.json",
        "table": "personal_data_processing_datacategory",
        "fields": ("name", "description"),
    },
    {
        "file": "data_subject_categories.json",
        "table": "personal_data_processing_datasubjectcategory",
        "fields": ("name", "description"),
    },
    {
        "file": "legal_bases.json",
        "table": "personal_data_processing_legalbasis",
        "fields": ("name", "description"),
    },
    {
        "file": "operation_types.json",
        "table": "personal_data_processing_operationtype",
        "fields": ("name", "description"),
    },
    {
        "file": "recipients.json",
        "table": "personal_data_processing_recipient",
        "fields": ("name", "type", "description"),
    },
    {
        "file": "security_measures.json",
        "table": "personal_data_processing_securitymeasure",
        "fields": ("name", "description", "category"),
    },
    {
        "file": "subprocessors.json",
        "table": "personal_data_processing_subprocessor",
        "fields": ("name", "description", "contact"),
    },
]


def get_connection():
    """Ouvre une connexion PostgreSQL."""
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
    )


def load_json(filename):
    """Charge un fichier JSON et vérifie sa structure."""
    path = BASE_DIR / filename

    if not path.exists():
        raise FileNotFoundError(f"Fichier introuvable : {path}")

    with path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError(
            f"{filename} doit contenir une liste JSON."
        )

    return data


def validate_data(filename, data, fields):
    """Vérifie que toutes les propriétés nécessaires sont présentes."""
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict):
            raise ValueError(
                f"{filename} : l'entrée #{index} doit être un objet JSON."
            )

        missing = [field for field in fields if field not in item]

        if missing:
            raise ValueError(
                f"{filename} : entrée #{index} : "
                f"champs manquants : {', '.join(missing)}"
            )

        if not item["name"]:
            raise ValueError(
                f"{filename} : entrée #{index} : "
                "le champ 'name' ne peut pas être vide."
            )


def table_exists(cursor, table_name):
    """Vérifie l'existence d'une table dans le schéma public."""
    cursor.execute(
        """
        SELECT EXISTS (
            SELECT 1
            FROM information_schema.tables
            WHERE table_schema = 'public'
              AND table_name = %s
        );
        """,
        (table_name,),
    )

    return cursor.fetchone()[0]


def seed_table(cursor, filename, table_name, fields):
    """
    Insère ou met à jour les données d'un référentiel.

    Le nom sert de clé fonctionnelle afin d'éviter les doublons.
    L'id PostgreSQL/Django est laissé à la base.
    """
    data = load_json(filename)
    validate_data(filename, data, fields)

    if not table_exists(cursor, table_name):
        raise RuntimeError(
            f"La table '{table_name}' n'existe pas dans PostgreSQL."
        )

    inserted = 0
    updated = 0

    quoted_table = sql.Identifier(table_name)

    for item in data:
        name = item["name"]

        # Recherche de l'enregistrement existant.
        cursor.execute(
            sql.SQL(
                """
                SELECT id
                FROM {}
                WHERE name = %s
                LIMIT 1;
                """
            ).format(quoted_table),
            (name,),
        )

        existing = cursor.fetchone()

        if existing:
            # Mise à jour des champs du référentiel.
            update_fields = [field for field in fields if field != "name"]

            if update_fields:
                set_clause = sql.SQL(", ").join(
                    sql.SQL("{} = %s").format(sql.Identifier(field))
                    for field in update_fields
                )

                values = [
                    item[field]
                    for field in update_fields
                ]
                values.append(existing[0])

                cursor.execute(
                    sql.SQL(
                        """
                        UPDATE {}
                        SET {}
                        WHERE id = %s;
                        """
                    ).format(quoted_table, set_clause),
                    values,
                )

            updated += 1
            print(f"  ↻ Mise à jour : {name}")

        else:
            columns = sql.SQL(", ").join(
                sql.Identifier(field)
                for field in fields
            )

            placeholders = sql.SQL(", ").join(
                sql.Placeholder()
                for _ in fields
            )

            values = [item[field] for field in fields]

            cursor.execute(
                sql.SQL(
                    """
                    INSERT INTO {} ({})
                    VALUES ({});
                    """
                ).format(
                    quoted_table,
                    columns,
                    placeholders,
                ),
                values,
            )

            inserted += 1
            print(f"  ✓ Insertion : {name}")

    return inserted, updated


def seed_all():
    """Exécute tous les seeds dans une seule transaction."""
    connection = get_connection()

    total_inserted = 0
    total_updated = 0

    try:
        with connection.cursor() as cursor:

            print("=" * 60)
            print("SEED DES RÉFÉRENTIELS COMPLIDO")
            print("=" * 60)

            for seed in SEEDS:
                print(
                    f"\n[{seed['file']}]"
                    f"\nTable : {seed['table']}"
                )

                inserted, updated = seed_table(
                    cursor=cursor,
                    filename=seed["file"],
                    table_name=seed["table"],
                    fields=seed["fields"],
                )

                total_inserted += inserted
                total_updated += updated

        connection.commit()

        print("\n" + "=" * 60)
        print("✓ INJECTION TERMINÉE AVEC SUCCÈS")
        print("=" * 60)
        print(f"Enregistrements insérés : {total_inserted}")
        print(f"Enregistrements mis à jour : {total_updated}")
        print(f"Total traité             : {total_inserted + total_updated}")
        print("=" * 60)

    except Exception as error:
        connection.rollback()

        print("\n" + "=" * 60)
        print("✗ ERREUR : TRANSACTION ANNULÉE")
        print("=" * 60)
        print(str(error))
        print("=" * 60)

        raise

    finally:
        connection.close()


if __name__ == "__main__":
    seed_all()
