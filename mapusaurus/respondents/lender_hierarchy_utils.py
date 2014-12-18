from respondents.models import LenderHierarchy

def get_organization_id(institution_id):
    return LenderHierarchy.objects.filter(institution_id=institution_id).values('organization_id')

def get_lender_hierarchy(organization_id):
    return LenderHierarchy.objects.filter(organization_id=organization_id).values_list('institution', flat=True)

def get_related_lenders(lender_id):
    organization_id = get_organization_id(lender_id)
    return get_lender_hierarchy(organization_id)
    
