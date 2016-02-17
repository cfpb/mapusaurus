from django.core.management.base import BaseCommand, CommandError
from hmda.models import Year


class Command(BaseCommand):
    args = "<hmda_year> <census_year> <geo_year>"
    help = """Record year time-stamps for data."""

    def handle(self, *args, **options):
        if len(args) < 3:
            raise CommandError("Need three arguments for year record" + Command.args)
        yobj = Year(hmda_year = int(args[0]),census_year = int(args[1]), geo_year = int(args[2]))
        yobj.save()
