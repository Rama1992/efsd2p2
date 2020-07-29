from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from .models import *
from .forms import *
from django.shortcuts import render, get_object_or_404
from django.shortcuts import redirect
from django.db.models import Sum
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import CustomerSerializer
from django.contrib.auth import get_user_model
from django.template.loader import get_template
from .utils import render_to_pdf
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm

now = timezone.now()


def home(request):
    return render(request, 'portfolio/home.html',
                  {'portfolio': home})


@login_required
def customer_list(request):
    customer = Customer.objects.filter(created_date__lte=timezone.now())
    return render(request, 'portfolio/customer_list.html',
                  {'customers': customer})


@login_required
def customer_edit(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    if request.method == "POST":
        # update
        form = CustomerForm(request.POST, instance=customer)
        if form.is_valid():
            customer = form.save(commit=False)
            customer.updated_date = timezone.now()
            customer.save()
            customer = Customer.objects.filter(created_date__lte=timezone.now())
            return render(request, 'portfolio/customer_list.html',
                          {'customers': customer})
    else:
        # edit
        form = CustomerForm(instance=customer)
    return render(request, 'portfolio/customer_edit.html', {'form': form})


@login_required
def customer_delete(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customer.delete()
    return redirect('portfolio:customer_list')


@login_required
def stock_list(request):
    stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
    return render(request, 'portfolio/stock_list.html', {'stocks': stocks})


@login_required
def stock_new(request):
    if request.method == "POST":
        form = StockForm(request.POST)
        if form.is_valid():
            stock = form.save(commit=False)
            stock.created_date = timezone.now()
            stock.save()
            stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
            return render(request, 'portfolio/stock_list.html',
                          {'stocks': stocks})
    else:
        form = StockForm()
        # print("Else")
    return render(request, 'portfolio/stock_new.html', {'form': form})


@login_required
def stock_edit(request, pk):
    stock = get_object_or_404(Stock, pk=pk)
    if request.method == "POST":
        form = StockForm(request.POST, instance=stock)
        if form.is_valid():
            stock = form.save()
            # stock.customer = stock.id
            stock.updated_date = timezone.now()
            stock.save()
            stocks = Stock.objects.filter(purchase_date__lte=timezone.now())
            return render(request, 'portfolio/stock_list.html', {'stocks': stocks})
    else:
        # print("else")
        form = StockForm(instance=stock)
    return render(request, 'portfolio/stock_edit.html', {'form': form})


@login_required
def stock_delete(request, pk):
    stock = get_object_or_404(Customer, pk=pk)
    stock.delete()
    return redirect('portfolio:stock_list')


@login_required
def investment_list(request):
    investments = Investment.objects.filter(acquired_date__lte=timezone.now())
    return render(request, 'portfolio/investment_list.html', {'investments': investments})


@login_required
def investment_new(request):
    if request.method == "POST":
        form = InvestmentForm(request.POST)
        if form.is_valid():
            investment = form.save(commit=False)
            investment.acquired_date = timezone.now()
            investment.save()
            investment = Investment.objects.filter(acquired_date__lte=timezone.now())
            return render(request, 'portfolio/investment_list.html',
                          {'investments': investment})
    else:
        form = InvestmentForm()
        # print("Else")
    return render(request, 'portfolio/investment_new.html', {'form': form})


@login_required
def investment_edit(request, pk):
    investment = get_object_or_404(Investment, pk=pk)
    if request.method == "POST":
        form = InvestmentForm(request.POST, instance=investment)
        if form.is_valid():
            investment = form.save()
            # stock.customer = stock.id
            investment.updated_date = timezone.now()
            investment.save()
            investment = Investment.objects.filter(acquired_date__lte=timezone.now())
            return render(request, 'portfolio/investment_list.html', {'investments': investment})
    else:
        # print("else")
        form = InvestmentForm(instance=investment)
    return render(request, 'portfolio/investment_edit.html', {'form': form})


@login_required
def investment_delete(request, pk):
    investment = get_object_or_404(Customer, pk=pk)
    investment.delete()
    return redirect('portfolio:investment_list')


@login_required
def portfolio(request,pk):
   customer = get_object_or_404(Customer, pk=pk)
   #customers = Customer.objects.filter(created_date__lte=timezone.now())
   investments =Investment.objects.filter(customer=pk)
   stocks = Stock.objects.filter(customer=pk)


   sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value'))
   sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value'))
   print(sum_acquired_value)
   acquired_total= sum_acquired_value['acquired_value__sum']
   recent_total = sum_recent_value['recent_value__sum']

   overall_investment_results = recent_total-acquired_total
   print(overall_investment_results)

   # Initialize the value of the stocks
   sum_current_stocks_value = 0
   sum_of_initial_stock_value = 0


   # Loop through each stock and add the value to the total
   for stock in stocks:
        sum_current_stocks_value += stock.current_stock_value()
        sum_of_initial_stock_value += stock.initial_stock_value()

   sumofinitialprice = float(sum_of_initial_stock_value)
   results = sum_current_stocks_value-sumofinitialprice
   print(results)


   return render(request, 'portfolio/portfolio.html', {'customer': customer,
                                                       'investments': investments,
                                                       'stocks': stocks,
                                                       'sum_acquired_value': sum_acquired_value,
                                                       'sum_recent_value': sum_recent_value,

                                                       'acquired_total':acquired_total,
                                                       'recent_total':recent_total,
                                                       'results':results,

                                                        'overall_investment_results':overall_investment_results,
                                                        'sum_current_stocks_value': sum_current_stocks_value,
                                                        'sum_of_initial_stock_value': sum_of_initial_stock_value,})

def portfolio_summary_pdf(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customers = Customer.objects.filter(created_date__lte=timezone.now())
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)

    sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value'))
    sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value'))
    print(sum_acquired_value)
    acquired_total = sum_acquired_value['acquired_value__sum']
    recent_total = sum_recent_value['recent_value__sum']

    overall_investment_results = recent_total - acquired_total
    print(overall_investment_results)

    # Initialize the value of the stocks

    sum_current_stocks_value = 0
    sum_of_initial_stock_value = 0

    # Loop through each stock and add the value to the total
    for stock in stocks:
        sum_current_stocks_value += stock.current_stock_value()
        sum_of_initial_stock_value += stock.initial_stock_value()

    sumofinitialprice = float(sum_of_initial_stock_value)
    results = sum_current_stocks_value - sumofinitialprice



    context = {'customers': customers,
                                                        'investments': investments,
                                                        'stocks': stocks,
                                                        'sum_acquired_value': sum_acquired_value,
                                                        'sum_recent_value': sum_recent_value,

                                                        'acquired_total': acquired_total,
                                                        'recent_total': recent_total,
                                                        'results': results,

                                                        'overall_investment_results': overall_investment_results,
                                                        'sum_current_stocks_value': sum_current_stocks_value,
                                                        'sum_of_initial_stock_value': sum_of_initial_stock_value,}
    template = get_template('portfolio/portfolio_summary_pdf.html')
    html = template.render(context)
    pdf = render_to_pdf('portfolio/portfolio_summary_pdf.html', context)
    return pdf

def customer_summary_pdf(request, pk):
    customer = get_object_or_404(Customer, pk=pk)
    customers = Customer.objects.filter(created_date__lte=timezone.now())
    investments = Investment.objects.filter(customer=pk)
    stocks = Stock.objects.filter(customer=pk)

    sum_recent_value = Investment.objects.filter(customer=pk).aggregate(Sum('recent_value'))
    sum_acquired_value = Investment.objects.filter(customer=pk).aggregate(Sum('acquired_value'))
    print(sum_acquired_value)
    acquired_total = sum_acquired_value['acquired_value__sum']
    recent_total = sum_recent_value['recent_value__sum']

    overall_investment_results = recent_total - acquired_total
    print(overall_investment_results)

    # Initialize the value of the stocks

    sum_current_stocks_value = 0
    sum_of_initial_stock_value = 0

    # Loop through each stock and add the value to the total
    for stock in stocks:
        sum_current_stocks_value += stock.current_stock_value()
        sum_of_initial_stock_value += stock.initial_stock_value()

    sumofinitialprice = float(sum_of_initial_stock_value)
    results = sum_current_stocks_value - sumofinitialprice
    print(type(customers))



    context = {'customer': customer,
                                                        'investments': investments,
                                                        'stocks': stocks,
                                                        'sum_acquired_value': sum_acquired_value,
                                                        'sum_recent_value': sum_recent_value,

                                                        'acquired_total': acquired_total,
                                                        'recent_total': recent_total,
                                                        'results': results,

                                                        'overall_investment_results': overall_investment_results,
                                                        'sum_current_stocks_value': sum_current_stocks_value,
                                                        'sum_of_initial_stock_value': sum_of_initial_stock_value,}
    template = get_template('portfolio/customer_summary_pdf.html')
    html = template.render(context)
    pdf = render_to_pdf('portfolio/customer_summary_pdf.html', context)
    return pdf

# List at the end of the views.py
# Lists all customers
class CustomerList(APIView):

    def get(self, request):
        customers_json = Customer.objects.all()
        serializer = CustomerSerializer(customers_json, many=True)
        return Response(serializer.data)

@login_required
def mutualfunds_list(request):
   mutualfunds = MutualFund.objects.filter(acquired_date__lte=timezone.now())
   return render(request, 'portfolio/mutualfunds_list.html', {'mutualfunds': mutualfunds})

@login_required
def mutualfunds_new(request):
   if request.method == "POST":
       form = MutualFundForm(request.POST)
       if form.is_valid():
           mutualfunds = form.save(commit=False)
           mutualfunds.created_date = timezone.now()
           mutualfunds.save()
           mutualfunds = MutualFund.objects.filter(acquired_date__lte=timezone.now())
           return render(request, 'portfolio/mutualfunds_list.html',
                         {'mutualfunds': mutualfunds})
   else:
       form = MutualFundForm()
       # print("Else")
   return render(request, 'portfolio/mutualfunds_new.html', {'form': form})

@login_required
def mutualfunds_edit(request, pk):
   mutualfunds = get_object_or_404(MutualFund, pk=pk)
   if request.method == "POST":
       form = MutualFundForm(request.POST, instance=mutualfunds)
       if form.is_valid():
           mutualfunds = form.save()
           # stock.customer = stock.id
           mutualfunds.updated_date = timezone.now()
           mutualfunds.save()
           mutualfunds = MutualFund.objects.filter(acquired_date__lte=timezone.now())
           return render(request, 'portfolio/mutualfunds_list.html', {'mutualfunds': mutualfunds})
   else:
       # print("else")
       form = MutualFundForm(instance=mutualfunds)
   return render(request, 'portfolio/mutualfunds_edit.html', {'form': form})

@login_required
def mutualfunds_delete(request, pk):
    mutualfunds = get_object_or_404(MutualFund, pk=pk)
    mutualfunds.delete()
    return redirect('portfolio:mutualfunds_list')

def signup_view(request):
    form = UserCreationForm(request.POST)
    if form.is_valid():
        form.save()
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password1')
        user = authenticate(username=username, password=password)
        login(request, user)
        return redirect('portfolio:home')
    return render(request, 'registration/signup.html', {'form': form})