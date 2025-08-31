from metadata_db import MetadataDB

class MetadataLogic:
    @staticmethod
    def get_all_metadata():
        rows = MetadataDB.get_all_metadata()
        # Convert tuples to dicts for UI
        return [
            {
                "ID": r[0],
                "Name": r[1],
                "Description": r[2],
                "Unit": r[3],
            }
            for r in rows
        ]

    @staticmethod
    def add_metadata(name, description, unit):
        MetadataDB.add_metadata(name, description, unit)

    @staticmethod
    def update_metadata(metadata_id, name, description, unit):
        MetadataDB.update_metadata(metadata_id, name, description, unit)

    @staticmethod
    def delete_metadata(metadata_id):
        MetadataDB.delete_metadata(metadata_id)