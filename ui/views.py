import json

from formtools.wizard.views import SessionWizardView

from django.conf import settings
from django.core.urlresolvers import reverse_lazy
from django.template.response import TemplateResponse
from django.shortcuts import render, redirect
from django.utils.cache import patch_response_headers
from django.views.generic import TemplateView, FormView
from django.views.generic.base import View

from alice.helpers import rabbit
from ui import forms
from ui.clients.directory_api import api_client


class CacheMixin(object):
    def render_to_response(self, context, **response_kwargs):
        # Get response from parent TemplateView class
        response = super().render_to_response(
            context, **response_kwargs
        )

        # Add Cache-Control and Expires headers
        patch_response_headers(response, cache_timeout=60 * 30)

        # Return response
        return response


class CachableTemplateView(CacheMixin, TemplateView):
    pass


class IndexView(CacheMixin, FormView):
    template_name = "index.html"
    form_class = forms.ContactForm
    success_url = reverse_lazy("thanks")

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        json_data = {'data': json.dumps(form.cleaned_data)}
        response = rabbit.post(
            settings.DATA_SERVER + '/form/',
            data=json_data,
            request=self.request,
        )

        if not response.ok:
            return redirect("problem")

        return super().form_valid(form)


class RegistrationView(SessionWizardView):
    form_list = (
        forms.CompanyForm,
        forms.PasswordForm,
    )

    def get_template_names(self):
        return ['step1.html', 'step2.html']

    def done(self, form_list, form_dict):
        return render(self.request, 'registered.html')


class EmailConfirmationView(View):
    success_template = 'confirm-email-success.html'
    failure_template = 'confirm-email-error.html'

    def get(self, request):
        confirmation_code = request.GET.get('confirmation_code')
        if confirmation_code and api_client.confirm_email(confirmation_code):
            template = self.success_template
        else:
            template = self.failure_template
        return TemplateResponse(request, template)
