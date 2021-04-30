from django.shortcuts import render, redirect
from betatrader.models import Order,  Voucher, Plan, Partner
from betatrader.forms import PreviewForm, RegisterForm, LoginForm
from django.core.mail import EmailMessage
from django.template.loader import get_template
from django.utils.datastructures import MultiValueDictKeyError


def home(request):
    # We check if the user has reached the site using an affiliate link
    if request.session.get("ref"):
        r = request.session.get("ref", None)
        # in that case the affiliate name is stored in the variable below
        return render(request, 'home.html', {"r": r})
    # If not the page is rendered normally
    else:
        return render(request, "home.html")


def preview(request):
    # The  function below is used as form action when sending order to be previewed
    if request.method == "POST":
        form = PreviewForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # check if entered coupon ceode is stored "inside database"; for this purpose I am going to use inside
            inside = Voucher.objects.filter(
                name=form.cleaned_data.get("coupon")).exists()
            # create a database object to store  the newly created order; We use try - except in case any queryset is returned
            try:
                referredBy = Partner.objects.get(
                    username=request.POST.get("ref"))
            except Partner.DoesNotExist:
                referredBy = None
            p = Order.objects.create(
                name=form.cleaned_data['name'], email=form.cleaned_data[
                    'email'], plan=form.cleaned_data['plan'], pmethod=form.cleaned_data['pmethod'],
                coupon=form.cleaned_data.get("coupon", False), affiliate=referredBy)
            # retrieve the plan from the db list
            plan = Plan.objects.get(name=form.cleaned_data["plan"])
            # Below you get  actions to do if a coupon code instance is found in the database
            if inside:
                c = True
                amountToReduce = plan.price
                v = form.cleaned_data.get("coupon", None)
                vouch = Voucher.objects.get(name=v)
                ex = vouch.expireDate
                exp = ex.strftime(" %Y/%m/%d ")
                disc = Voucher.objects.get(
                    name=form.cleaned_data["coupon"])
                reduction = disc.discount
                amount = amountToReduce * ((100 - reduction)/100)
            #  And then the action to perform when it is not
            else:
                v = None
                exp = None
                c = False
                amount = (plan.price)-1
            # In both case, do following
            p.amount = amount
            p.save()
            # In case you wonder below lines purpose is to retrieve payment option and redirect to correspondig page
            # There is a preview page for each payment method extending the main oreview page(see templates)
            if form.cleaned_data["pmethod"] == "Perfect Money":
                request.session["user"] = p.id
                request.session["amount"] = p.amount
                user = Order.objects.get(id=request.session["user"])
                r_amount = (p.amount)*10
                return render(request, "preview1.html", {"amount": amount, "user": user, "c": c, "r_amount": r_amount, "v": v, "exp": exp})
            elif form.cleaned_data["pmethod"] == "Payeer":
                request.session["user"] = p.id
                request.session["amount"] = p.amount
                user = Order.objects.get(id=request.session["user"])
                r_amount = (p.amount)*10
                return render(request, "preview2.html", {"amount": amount, "user": user, "c": c, "r_amount": r_amount, "v": v, "exp": exp})
            elif form.cleaned_data["pmethod"] == "Cryptocurrencies":
                request.session["user"] = p.id
                request.session["amount"] = p.amount
                user = Order.objects.get(id=request.session["user"])
                r_amount = (p.amount)*10
                currency2 = request.POST["currency2"]
                return render(request, "preview2.html", {"amount": amount, "user": user, "c": c, "r_amount": r_amount, "v": v, "exp": exp, "currency2": currency2})
            else:
                notification = "Invalid forrm.  Please check again."
                return render(request, "home.html", {"notification": notification})
        else:
            notification = "Invalid forrm.  Please check again."
            # Those last lines are to send  error message if it is found
            return render(request, "home.html", {"notification": notification})
    else:
        return render(request, "home.html")


def status(request):
    # This is what happens when a paymment is performed successfully
    if request.method == "POST":
        user = Order.objects.get(id=request.session["user"])
        # Here we get the affiliate which eventually has referred the customer and we update his data
        try:
            affiliate = Partner.objects.get(
                name=request.session.get("ref", False))
            affiliate.totalSales += 1
            affiliate.totalEarned += request.session.get("amount")
            affiliate.balance += request.session.get("amount")
        except Partner.DoesNotExist:
            pass
        # Then here we send the order to  the customer; he get what he asked for; see sendmail  function to know how the line works
        sendmail(user)


def success(request):
    # This function redirects customer to a success page if payment has been successful
    return render(request, 'success.html')


def fail(request):
    # This one is for unsuccessful payments
    return render(request, 'fail.html')


def sendmail(user):
    # Oh so here it is the function we talked about earlier. It is the one which send the order. It's the most expensive function right here ;)
    mail = user.email
    name = user.name
    # Below are the lines user will click to download his order, you'll have to pay either $150, $300 or even $500 to get any  of them
    if user.plan == "Basic":
        link = "https://drive.google.com/drive/folders/1ky-qWYx8ov42FzbPShb6aTc9X6H6WfFk?usp=sharing"
    elif user.plan == "Business":
        link = "https://drive.google.com/drive/folders/12AkhfCbWVe61PV0SuaCXB0sOd1hXN1ri?usp=sharing"
    else:
        link = "https://drive.google.com/drive/folders/1ky-qWYx8ov42FzbPShb6aTc9X6H6WfFk?usp=sharing"
    ctx = {'mail': mail, 'name': name, "link": link}
    message = get_template('mail.html').render(ctx)
    msg = EmailMessage(
        'Your trading bot order',
        message,
        'BetaTrader trading bot',
        [mail],
    )
    msg.content_subtype = "html"  # Main content is now text/html
    msg.send()


def test(request):
    # This  was a simple test I made to ensure everything was fine with the sendmail function, ("Jamais trop prudent :p ")
    t = Order.objects.create(
        name="Ulrich", email="ugbongboui@gmail.com", plan="Business", pmethod="Payeer", amount="30", coupon="PROMODEAL")
    sendmail(t)
    return render(request, "test.html")


# Below functions are mainly for affiliate section, keep  reading

# Dashboard views

def dashboard(request):
    # First check if user is logged  in and reidrect him in login page if not
    loggedUser = getLoggedUser(request)
    if loggedUser == None:
        return redirect('login')
    else:
        # If logged in display his personal data on dashboard; they will be re used in templates
        order = Order.objects.filter(
            affiliate=request.session.get("loggedUserId", None))
        totalSales = order.count()
        user = Partner.objects.get(
            id=request.session.get("loggedUserId", None))
        totalEarned = user.totalEarned
        totalWithdraw = user.totalWithdraw
        balance = user.balance
        totalSales = user.totalSales
        context = {"order": order, "totalEarned": totalEarned,
                   "totalWithdraw": totalWithdraw, "balance": balance, "user": user, "totalSales": totalSales}
        return render(request, 'dashboard/dashboard.html', context)


def coupons(request):
    # This function renders all available coupons code created on admin daashboard
    loggedUser = getLoggedUser(request)
    if loggedUser == None:
        return redirect('login')
    else:
        coupons = Voucher.objects.all()
        return render(request, 'dashboard/coupons.html', {"coupons": coupons})


def withdraw(request):
    # This returns withdraw page with corresponding form
    loggedUser = getLoggedUser(request)
    if loggedUser == None:
        return redirect('login')
    else:
        return render(request, 'dashboard/withdraw.html')


def getLoggedUser(request):
    # check if logged in function; maybe I should have put it on top
    if 'loggedUserId' in request.session:
        loggedUserId = request.session['loggedUserId']
        if len(Partner.objects.filter(id=loggedUserId)) == 1:
            return Partner.objects.get(id=loggedUserId)
        else:
            return None
    else:
        return None


def register(request):
    # Registration function; you probably know how it works so let's move on
    loggedUser = getLoggedUser(request)
    if loggedUser:
        return redirect('dashboard')
    else:
        if request.method == 'POST':
            # create a form instance and populate it with data from the request:
            # check whether it's valid:
            try:
                if Partner.objects.filter(username=request.POST['username']).exists():
                    return render(request, 'dashboard/register.html', {
                        'error_message': 'This username is already taken. Please choose another one'
                    })
                elif Partner.objects.filter(email=request.POST['email']).exists():
                    return render(request, 'dashboard/register.html', {
                        'error_message': 'This Email is already registered.'
                    })
                elif request.POST['password'] != request.POST['confirm']:
                    return render(request, 'dashboard/register.html', {
                        'error_message': 'Passwords do not match.'
                    })
                else:
                    # Create the user:
                    Partner.objects.create(
                        name=request.POST['name'],
                        email=request.POST['email'],
                        username=request.POST['username'],
                        password=request.POST['password'],
                    )
                    return redirect('login')
            except MultiValueDictKeyError:
                return render(request, "dashboard/register.html", {"error_message": "An error occured, try again"})
        else:
            return render(request, 'dashboard/register.html')


def login(request):
    # login form; same thing as the function above: un vieux classic
    loggedUser = getLoggedUser(request)
    if loggedUser:
        return redirect('dashboard')
    else:
        if request.method == "POST":
            form = LoginForm(request.POST)
            if form.is_valid():
                if Partner.objects.filter(email=request.POST['email'], password=request.POST['password']).exists():
                    loggedUser = Partner.objects.get(
                        email=request.POST['email'], password=request.POST['password'])
                    request.session["loggedUserId"] = loggedUser.id
                    # request.session.set_expiry(10)
                    # it shows home page
                    return render(request, "dashboard/dashboard.html", {"loggedUser": loggedUser})
                elif Partner.objects.filter(email=request.POST['email']).exists():
                    return render(request, 'dashboard/login.html', {
                        'form': form,
                        'error_message': 'Password does not match.'
                    })
                else:
                    return render(request, 'dashboard/login.html', {
                        'form': form,
                        'error_message': 'User not found.'})
        # it shows again login page
        form = LoginForm()
        return render(request, "dashboard/login.html", {'form': form})


def logout(request):
    # Basic logout function
    del request.session["loggedUserId"]
    return redirect('login')


def reflink(request, ref):
    # We use this fubbction to  track affiliate links
    if len(ref) == 0:
        return render("home")
    else:
        request.session["ref"] = ref
        return redirect("home")


def withdraw_request(request):
    # The form action function used to process withdraw requet for affiliates
    if request.method == "POST":
        user = Partner.objects.get(
            id=request.session.get("loggedUserId", False))
        mail = user.email
        name = user.name
        amount = request.POST["amount"]
        method = request.POST["method"]
        ctx = {'mail': mail, 'name': name, "amount": amount, "method": method}
        message = get_template('withdraw_request.html').render(ctx)
        msg = EmailMessage(
            'New withdraw request',
            message,
            'BetaTrader trading bot',
            [mail],
        )
        msg.content_subtype = "html"  # Main content is now text/html
        msg.send()
        return render(request, "dashboard/withdraw.html", {"success": "Your request has been sent to approval."})
