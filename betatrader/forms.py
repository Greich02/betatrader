from django import forms


class PreviewForm(forms.Form):
    email = forms.EmailField()
    name = forms.CharField(max_length=50)
    plan = forms.CharField(max_length=50)
    pmethod = forms.CharField(max_length=50)
    coupon = forms.CharField(max_length=50, required=False)


class LoginForm(forms.Form):
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))


class RegisterForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(
        attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))
    confirm = forms.CharField(widget=forms.PasswordInput(
        attrs={'class': 'form-control'}))
    name = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'form-control'}))

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(RegisterForm, self).__init__(*args, **kwargs)
