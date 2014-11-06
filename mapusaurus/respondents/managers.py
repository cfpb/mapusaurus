from django.db import models

class AgencyManager(models.Manager):
    def get_all_by_code(self):
        agencies = self.all()

        agency_map = {}
        for agency in agencies:
            agency_map[agency.pk] = agency
        return agency_map
