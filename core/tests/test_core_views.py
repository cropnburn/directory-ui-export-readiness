from django.core.urlresolvers import reverse

from core import views
from casestudy import casestudies


def test_landing_page(client):
    url = reverse('landing-page')

    response = client.get(url)

    assert response.status_code == 200
    assert response.template_name == [views.LandingPagelView.template_name]
    assert response.context_data['casestudies'] == [
        casestudies.MARKETPLACE,
        casestudies.HELLO_BABY,
        casestudies.YORK,
    ]
