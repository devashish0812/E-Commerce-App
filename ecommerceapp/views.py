from django.shortcuts import render,redirect
from django.contrib import messages
from math import ceil
from django.conf import settings
import json
from ecommerceapp.models import Contact,Product,Orders,OrderUpdate
import razorpay
# Create your views here
def index(request):
    allProds = []
    catprods = Product.objects.values('category','id')
    cats = {item['category'] for item in catprods}
    for cat in cats:
        prod= Product.objects.filter(category=cat)
        n=len(prod)
        nSlides = n // 4 + ceil((n / 4) - (n // 4))
        allProds.append([prod, range(1, nSlides), nSlides])

    params= {'allProds':allProds}

    return render(request,"index.html",params)


def contact(request):
    if request.method=="POST":
        name=request.POST.get("name")
        email=request.POST.get("email")
        desc=request.POST.get("desc")
        pnumber=request.POST.get("pnumber")
        myquery=Contact(name=name,email=email ,desc=desc,phonenumber=pnumber)
        myquery.save()
        messages.info(request,"We will get back to you shortly")
        return render(request,"contact.html")
    return render(request,"contact.html")

def about(request):
    return render(request,"about.html")

def checkout(request):
    thank=False
    print("****THAK*****")
    print(thank)
    print("****THAK*****")
    if not request.user.is_authenticated:
        messages.warning(request,"Login & Try Again")
        return redirect('/auth/login')
    
    if request.method=="POST":
        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        # amount = request.POST.get('amt','')
        amount = float(request.POST.get('amt', '' )) 
        print(amount)
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2','')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')
        Order = Orders(items_json=items_json,name=name,amount=amount, email=email, address1=address1,address2=address2,city=city,state=state,zip_code=zip_code,phone=phone)
        print(amount)
        Order.save()
        update = OrderUpdate(order_id=Order.order_id,update_desc="the order has been placed")
        update.save()
        thank=True
# # PAYMENT INTEGRATION
      
        client=razorpay.Client(auth=(settings.KEY,settings.SECRET))
        payment=client.order.create({'amount':str(int(amount * 100)), 'currency':'INR','payment_capture':'1'})
        Order.razor_pay_order_id=payment['id']
        Order.save()   
        print("A")  
        print(amount)
        print("B")
        context={'cart':Order,'payment':payment,'thank':thank}
        print(payment['amount'])
        print(context['thank'])
        return render(request,'checkout.html',context)
    
    return render(request, 'checkout.html',{'thank': thank})

