import json

from django.http import HttpResponse, Http404

from hmda.models import HMDARecord


def loan_originations(request):
    """Get loan originations for a given lender, county combination. This
    ignores year for the moment."""

    state_fips = request.GET.get('state_fips', '')
    county_fips = request.GET.get('county_fips', '')
    lender = request.GET.get('lender', '')

    if state_fips and county_fips and lender:
        records = HMDARecord.objects.filter(action_taken__lte=6,
                                            lender=lender)
        lender_avg = records.

        return HttpResponse(json.dumps(1), content_type='application/json')
    else:
        raise Http404
