import json

from django.core.urlresolvers import reverse
from django.contrib.gis.geos import MultiPolygon, Polygon
from django.test import TestCase
from mock import Mock, patch

from geo.management.commands.load_geos_from import Command as LoadGeos
from geo.management.commands.set_tract_csa_cbsa import Command as SetTractCBSA
from geo.models import Geo
from geo.utils import check_bounds
from censusdata.models import Census2010Sex

class ViewTest(TestCase):
    fixtures = ['many_tracts', 'test_counties']


    @patch('geo.views.SearchQuerySet')
    def test_search_name(self, SQS):
        SQS = SQS.return_value.models.return_value.load_all.return_value
        result = Mock()
        result.object.geoid = '11111'
        result.object.geo_type = 1
        result.object.name = 'MSA 1'
        result.object.centlat = 45
        result.object.centlon = 52
        result.object.year = 2013
        SQS.filter.return_value.filter.return_value = [result]
        resp = self.client.get(reverse('geo:search'), {'q': 'Chicago', 'year': '2013'})
        self.assertTrue('Chicago' in str(SQS.filter.call_args))
        self.assertTrue('content' in str(SQS.filter.call_args))
        self.assertFalse('text_auto' in str(SQS.filter.call_args))
        resp = json.loads(resp.content)
        self.assertEqual(1, len(resp['geos']))
        geo = resp['geos'][0]
        self.assertEqual('11111', geo['geoid'])
        self.assertEqual('MSA 1', geo['name'])
        self.assertEqual(1, geo['geo_type'])
        self.assertEqual(45, geo['centlat'])
        self.assertEqual(52, geo['centlon'])

    @patch('geo.views.SearchQuerySet')
    def test_search_autocomplete(self, SQS):
        SQS = SQS.return_value.models.return_value.load_all.return_value
        SQS.filter.return_value.filter.return_value = [Mock()]
        self.client.get(reverse('geo:search'), {'q': 'Chicago', 'auto': '1', 'year': '2013'})
        self.assertTrue('Chicago' in str(SQS.filter.call_args))
        self.assertFalse('content' in str(SQS.filter.call_args))
        self.assertTrue('text_auto' in str(SQS.filter.call_args))
        self.assertTrue('year' in str(SQS.filter.return_value.filter.call_args))

class UtilsTest(TestCase):
    def test_check_bounds(self):
        self.assertIsNone(check_bounds('100', '100', '100', ''))
        self.assertIsNone(check_bounds('-100', '100', '200', 'asdf'))
        expected_bounds = (float('10.0'), float('40.1234'), float('20.20'), float('-10.123456'))
        actual_bounds = check_bounds('10.0', '-10.123456', '20.20', '40.1234')
        self.assertEqual(expected_bounds, actual_bounds)


class SetTractCBSATest(TestCase):
    def setUp(self):
        generic_geo = {
            'minlat': -1, 'maxlat': 1, 'minlon': -1, 'maxlon': 1, 'centlat': 0,
            'centlon': 0, 'name': 'Generic Geo', 'geom': MultiPolygon(
                Polygon(((0, 0), (0, 2), (-1, 2), (0, 0))),
                Polygon(((-4, -2), (-6, -1), (-2, -2), (-4, -2))))
        }
        self.county1 = Geo.objects.create(
            geoid='11222', geo_type=Geo.COUNTY_TYPE, state='11', county='222',
            csa='987', year='2012', **generic_geo)
        self.county2 = Geo.objects.create(
            geoid='11223', geo_type=Geo.COUNTY_TYPE, state='11', county='223',
            cbsa='88776', year='2012', **generic_geo)
        self.metro = Geo.objects.create(
            geoid='88776', geo_type=Geo.METRO_TYPE, cbsa='88776', year='2012',
            **generic_geo)
        self.tract1 = Geo.objects.create(
            geoid='1122233333', geo_type=Geo.TRACT_TYPE, state='11', year='2012',
            county='222', tract='33333', **generic_geo)
        self.tract2 = Geo.objects.create(
            geoid='1122333333', geo_type=Geo.TRACT_TYPE, state='11', year='2012',
            county='223', tract='33333', **generic_geo)

    def tearDown(self):
        self.county1.delete()
        self.county2.delete()
        self.tract1.delete()
        self.tract2.delete()
        self.metro.delete()

    def test_set_fields(self):
        SetTractCBSA().handle()
        tract1 = Geo.objects.filter(geoid='1122233333').get()
        tract2 = Geo.objects.filter(geoid='1122333333').get()
        self.assertEqual('987', tract1.csa)
        self.assertEqual(None, tract1.cbsa)
        self.assertEqual(None, tract2.csa)
        self.assertEqual('88776', tract2.cbsa)


class LoadGeosFromTest(TestCase):
    def test_census_tract(self):
        year = "2013"
        row = ('1122233333', 'Tract 33333', '11', '222', '33333', '-45',
               '45', Polygon(((0, 0), (0, 2), (-1, 2), (0, 0))))
        field_names = ('GEOID', 'NAME', 'STATEFP', 'COUNTYFP', 'TRACTCE',
                       'INTPTLAT', 'INTPTLON')
        command = LoadGeos()
        geo = command.process_row(year, row, field_names)

        self.assertEqual('20131122233333', geo['geoid'])
        self.assertEqual(Geo.TRACT_TYPE, geo['geo_type'])
        self.assertEqual('Tract 33333', geo['name'])
        self.assertEqual('11', geo['state'])
        self.assertEqual('222', geo['county'])
        self.assertEqual('33333', geo['tract'])
        self.assertEqual(None, geo['csa'])
        self.assertEqual(None, geo['cbsa'])
        self.assertEqual((-1, 0), (geo['minlon'], geo['maxlon']))
        self.assertEqual((0, 2), (geo['minlat'], geo['maxlat']))
        self.assertEqual(-45, geo['centlat'])
        self.assertEqual(45, geo['centlon'])
        self.assertEqual("2013", geo['year'])

    def test_county(self):
        year = "2010"
        poly1 = Polygon(((0, 0), (0, 2), (-1, 2), (0, 0)))
        poly2 = Polygon(((-4, -2), (-6, -1), (-2, -2), (-4, -2)))
        row = ('11222', 'Some County', '11', '222', '-45', '45',
               MultiPolygon(poly1, poly2))
        field_names = ('GEOID', 'NAME', 'STATEFP', 'COUNTYFP', 'INTPTLAT',
                       'INTPTLON')
        command = LoadGeos()
        geo = command.process_row(year, row, field_names)

        self.assertEqual('201011222', geo['geoid'])
        self.assertEqual(Geo.COUNTY_TYPE, geo['geo_type'])
        self.assertEqual('Some County', geo['name'])
        self.assertEqual('11', geo['state'])
        self.assertEqual('222', geo['county'])
        self.assertEqual(None, geo['tract'])
        self.assertEqual(None, geo['csa'])
        self.assertEqual(None, geo['cbsa'])
        self.assertEqual((-6, 0), (geo['minlon'], geo['maxlon']))
        self.assertEqual((-2, 2), (geo['minlat'], geo['maxlat']))
        self.assertEqual(-45, geo['centlat'])
        self.assertEqual(45, geo['centlon'])
        self.assertEqual("2010", geo['year'])

    def test_metro(self):
        year = "2010"
        row = ('12345', 'Big City', '090', '12345', 'M1', '-45', '45',
               Polygon(((0, 0), (0, 2), (-1, 2), (0, 0))))
        field_names = ('GEOID', 'NAME', 'CSAFP', 'CBSAFP', 'LSAD', 'INTPTLAT',
                       'INTPTLON')
        command = LoadGeos()
        geo = command.process_row(year, row, field_names)

        self.assertEqual('201012345', geo['geoid'])
        self.assertEqual(Geo.METRO_TYPE, geo['geo_type'])
        self.assertEqual('Big City', geo['name'])
        self.assertEqual(None, geo['state'])
        self.assertEqual(None, geo['county'])
        self.assertEqual(None, geo['tract'])
        self.assertEqual('090', geo['csa'])
        self.assertEqual('12345', geo['cbsa'])
        self.assertEqual("2010", geo['year'])

    def test_micro(self):
        year = '1900'
        row = ('12345', 'Small Town', '', '12345', 'M2', '-45', '45',
               Polygon(((0, 0), (0, 2), (-1, 2), (0, 0))))
        field_names = ('GEOID', 'NAME', 'CSAFP', 'CBSAFP', 'LSAD', 'INTPTLAT',
                       'INTPTLON')
        command = LoadGeos()
        geo = command.process_row(year, row, field_names)

        self.assertEqual('190012345', geo['geoid'])
        self.assertEqual(Geo.MICRO_TYPE, geo['geo_type'])
        self.assertEqual('Small Town', geo['name'])
        self.assertEqual(None, geo['state'])
        self.assertEqual(None, geo['county'])
        self.assertEqual(None, geo['tract'])
        self.assertEqual(None, geo['csa'])
        self.assertEqual('12345', geo['cbsa'])
        self.assertEqual('1900', geo['year'])

    def test_replacing(self):
        command = LoadGeos()
        old_geo = {
            'geoid': '1111111111', 'geo_type': Geo.TRACT_TYPE,
            'name': 'Geo in 1990', 'year': '1990', 'state': '11', 'county': '111',
            'tract': '11111', 'minlat': -1, 'maxlat': 1, 'minlon': -1,
            'maxlon': 1, 'centlat': 0, 'centlon': 0,
            'geom': MultiPolygon(
                Polygon(((0, 0), (0, 2), (-1, 2), (0, 0))),
                Polygon(((-4, -2), (-6, -1), (-2, -2), (-4, -2))))
        }
        command.save_batch([old_geo])
        # Geo save worked
        self.assertEqual(1, Geo.objects.filter(geoid='1111111111').count())

        census = Census2010Sex(total_pop=100, male=45, female=55)
        census.geoid_id = '1111111111'
        census.save()
        # Census data worked
        self.assertEqual(1, Census2010Sex.objects.all().count())

        new_geo = old_geo.copy()
        new_geo['name'] = 'Geo in 2000'
        command.save_batch([new_geo])
        # check that both models still exist
        query = Geo.objects.filter(geoid='1111111111')
        self.assertEqual(1, query.count())
        self.assertEqual('Geo in 2000', query.get().name)
        self.assertEqual(1, Census2010Sex.objects.all().count())

        Geo.objects.all().delete()
        Census2010Sex.objects.all().delete()
