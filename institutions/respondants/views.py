from django.shortcuts import render, get_object_or_404
from django.http import HttpResponseRedirect

from respondants.forms import InstitutionSearchForm
from respondants.models import Institution

def respondant(request, respondant_id):
    respondant = get_object_or_404(Institution, pk=respondant_id)

    parents = [respondant]

    p = respondant.parent
    while p:
        parents.append(p)
        p = p.parent

    last = parents[-1]
    if last.non_reporting_parent:
        parents.append(last.non_reporting_parent)

    parents = parents[1:]
    parents = reversed(parents)

    return render(
        request, 
        'respondants/respondant.html',
        {'parents': parents, 'respondant':respondant}
    )
    
def index(request):
    """  The main view. Display the institution search box here. """

    if request.method == 'POST':
        form = InstitutionSearchForm(request.POST)
        if form.is_valid():
            name_contains = form.cleaned_data['name_contains']
            return HttpResponseRedirect(
                '/institutions/search/?q=%s' % name_contains)
    else:
        form = InstitutionSearchForm()
        
    return render(
        request,
        'respondants/index.html',
        {'search_form': form}
    )
    
def search(request):
    institution_name = request.GET.get('q', '')
    results = {}
    if institution_name:
        institution_name = institution_name.upper()
        respondant_results = Institution.objects.filter(
            name__contains=institution_name)
        print(len(respondant_results))
        if len(respondant_results) > 0:
            results['respondants'] = respondant_results

    return render(
        request, 
        'respondants/search_results.html', 
        {'results': results}
    )
