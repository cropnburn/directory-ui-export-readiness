from django import forms
from django.utils.safestring import mark_safe

from directory_validators import enrolment as shared_validators
from directory_validators.constants import choices
from directory_constants.constants import urls

from enrolment import fields, helpers, validators


class IndentedInvalidFieldsMixin:
    error_css_class = 'input-field-container has-error'


class AutoFocusFieldMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        first_field = self.visible_fields()[0]
        self.fields[first_field.name].widget.attrs['autofocus'] = 'autofocus'


class CompanyForm(
    AutoFocusFieldMixin,
    IndentedInvalidFieldsMixin,
    forms.Form
):
    company_name = forms.CharField(
        label='Company name:',
        help_text=(
            "If this is not your company then click back in your browser "
            "and re-enter your company."
        ),
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )
    company_number = fields.PaddedCharField(
        label='Company number:',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
        max_length=8,
        fillchar='0',
    )
    company_address = forms.CharField(
        label='Company registered office address:',
        widget=forms.TextInput(attrs={'readonly': 'readonly'}),
    )


class CompanyExportStatusForm(
    AutoFocusFieldMixin, IndentedInvalidFieldsMixin, forms.Form
):
    export_status = forms.ChoiceField(
        label=(
            'Has your company sold products or services to overseas customers?'
        ),
        choices=choices.EXPORT_STATUSES,
        validators=[shared_validators.export_status_intention]
    )
    terms_agreed = forms.BooleanField(
        label=mark_safe(
            'Tick this box to accept the '
            '<a href="{url}" target="_blank">terms and '
            'conditions</a> of the Find a Buyer service.'.format(
                url=urls.TERMS_AND_CONDITIONS_URL)
        )
    )


class InternationalBuyerForm(IndentedInvalidFieldsMixin, forms.Form):
    PLEASE_SELECT_LABEL = 'Please select a sector'
    TERMS_CONDITIONS_MESSAGE = ('Tick the box to confirm you agree to '
                                'the terms and conditions.')

    full_name = forms.CharField(label='Your name')
    email_address = forms.EmailField(label='Your email address')
    sector = forms.ChoiceField(
        label='Sector',
        choices=(
            [['', PLEASE_SELECT_LABEL]] + list(choices.COMPANY_CLASSIFICATIONS)
        )
    )
    terms = forms.BooleanField(
        label=mark_safe(
            'I agree to the <a target="_self" '
            'href="{url}">terms and conditions</a> of the website.'.format(
                url=urls.TERMS_AND_CONDITIONS_URL)
        ),
        error_messages={'required': TERMS_CONDITIONS_MESSAGE}
    )


class CompaniesHouseSearchForm(forms.Form):
    term = forms.CharField()


class CompanyNumberForm(IndentedInvalidFieldsMixin, forms.Form):
    company_number = fields.PaddedCharField(
        validators=helpers.halt_validation_on_failure(
            shared_validators.company_number,
            validators.company_unique,
            validators.company_number_present_and_active,
        ),
        max_length=8,
        fillchar='0',
    )


def serialize_enrolment_forms(cleaned_data):
    """
    Return the shape directory-api-client expects for enrolment.

    @param {dict} cleaned_data - All the fields in
        `CompanyForm`,
        `CompanyExportStatusForm`
    @returns dict

    """

    return {
        'export_status': cleaned_data['export_status'],
    }


def serialize_international_buyer_forms(cleaned_data):
    """
    Return the shape directory-api-client expects for saving international
    buyers.

    @param {dict} cleaned_data - All the fields in `InternationalBuyerForm`
    @returns dict

    """

    return {
        'name': cleaned_data['full_name'],
        'email': cleaned_data['email_address'],
        'sector': cleaned_data['sector'],
    }


def format_registered_office_address(address):
    fields = [
        'address_line_1',
        'address_line_2',
        'care_of',
        'country',
        'locality',
        'po_box',
        'postal_code',
        'premises',
        'region'
    ]

    return ", ".join(
        address[field] for field in fields if address.get(field)
    )


def get_company_form_initial_data(data):
    """
    Returns the shape of initial data that CompanyForm expects.

    @param {str} name
    @returns dict

    """

    return {
        'company_name': data['company_name'],
        'company_number': data['company_number'],
        'company_address': format_registered_office_address(
            data['registered_office_address']
        )
    }
