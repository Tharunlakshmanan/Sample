from django.shortcuts import render, redirect
from .models import Product, Orders, OrderUpdate, Contact
from math import ceil
from django.contrib import messages
import ast
# for running dashboard function only specific user
from django.contrib.auth.decorators import permission_required, login_required
from django.core.mail import EmailMessage
from django.conf import settings
# here I'm importing product from models
# Create your views here.


def index(request):
    # just calling all the product and
    # allprods=Product.objects.all()
    allprods = []
    # getting products based on category with id
    catprods = Product.objects.values('category', 'id')
    # based on the category item will coming over here
    cats = {item['category'] for item in catprods}
    print(cats)
    # now iterating all the items from specific cats, filtering product with category
    for cat in cats:
        prod = Product.objects.filter(category=cat)
        n = len(prod)
        nSlides = n//4 + ceil((n//4)-(n//4))
        print(nSlides)
        allprods.append([prod, range(1, nSlides), nSlides])
    print(allprods)
    # i'm passing those products to html page
    params = {"allprods": allprods}
    # print(allprods)
    return render(request, 'index.html', params)


def about(request):
    return render(request, 'about.html')


def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        desc = request.POST.get('desc')
        pnumber = request.POST.get('pnumber')
        myquery = Contact(name=name, email=email,
                          desc=desc, phonenumber=pnumber)
        # print(pnumber)
        myquery.save()
        messages.info(request, "We will get to you soon...Please be patient")
        return render(request, "contact.html")
    return render(request, 'contact.html')


def checkout(request):
    # check the user is logged in or not
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try again")
        return redirect('/auth/login')
    if request.method == "POST":

        items_json = request.POST.get('itemsJson', '')
        name = request.POST.get('name', '')
        amount = request.POST.get('amt')
        email = request.POST.get('email', '')
        address1 = request.POST.get('address1', '')
        address2 = request.POST.get('address2', '')
        city = request.POST.get('city', '')
        state = request.POST.get('state', '')
        zip_code = request.POST.get('zip_code', '')
        phone = request.POST.get('phone', '')

        #  login for stocks and profit details
        #  logic to update stock and profit  amount in database table order
        profit = []
        dataitems = ast.literal_eval(items_json)

        for i in dataitems.values():
            # print(i[0],i[1],i[2]), stock, productname,amount
            getProductname = Product.objects.get(product_name=i[1])
            profitamount = int(i[2]*int(i[0])) - \
                int(getProductname.actual_price)*int(i[0])
            profit.append(profitamount)
            getProductname.stock = getProductname.stock-int(i[0])
            getProductname.save()

            # ordering the final items

        profit = sum(profit)
        Order = Orders(items_json=items_json, name=name, amount=amount, email=email, address1=address1,
                       address2=address2, city=city, state=state, zipcode=zip_code, phone=phone, profit=profit)
        Order.save()
        update = OrderUpdate(order_id=Order.order_id,
                             update_des="the order has been placed")
        update.save()

        # update the order id payment status in database order tables
        id = Order.order_id
        oid = str(id)
        filter1 = Orders.objects.filter(order_id=oid)
        for post1 in filter1:
            post1.oid = oid
            post1.payment_status = "UN PAID"
            post1.amount_paid = "CASH ON DELIVERY"
            post1.save()
        # email_subject = "Order Placed By TMART"
        # message = f' Hello {name}\n Your Order is Placed with order id {oid}\n\n\n Ordered Items are \n {items_json}\n\nTotal Amount to be Paid {amount}\n We will soon deliver your ordered on below address \n\nAddress:\n{address1}\n{address2}\n{city}\n{state}\n{zip_code}\n{phone}\n\nYou can track your orders at http://127.0.0.1:8000/profile'
        # email_message=EmailMessage(email_subject,message,settings.EMAIL_HOST_USER,[email])
        # email_message.send()
        messages.success(request, "Order is placed...")
        return redirect('/profile')
    return render(request, 'checkout.html')


def profile(request):
    #  check logged in id
    if not request.user.is_authenticated:
        messages.warning(request, "Login & Try again")
        return redirect('/auth/login')
    current_user = request.user.username
    print(current_user)
    # filtering items of current user
    items = Orders.objects.filter(email=current_user)
    rid = ""
    for i in items:
        myid = i.oid
        rid = myid

    try:
        # if the things are matched I stored as dictionary in profile page
        status = OrderUpdate.objects.filter(order_id=int(rid))
        context = {"items": items, "status": status}
        return render(request, "profile.html", context)
    except:
        pass

    return render(request, "profile.html")


def search(request):
    query = request.GET['search']

    if len(query) > 78:
        allprods = Product.objects.get.none()
    else:
        allprodsTitle = Product.objects.filter(product_name_icontains=query)
        allprodscontent1 = Product.objects.filter(category_icontains=query)
        allprodscontent2 = Product.objects.filter(desc_icontains=query)
        allprods = allprodsTitle.union(
            allprodscontent1).union(allprodscontent2)

    if allprods.count() == 0:
        messages.warning(request, "No result found")

    # print("allprods")
    params = {'allprods': allprods, 'query': query}
    return render(request, "search.html", params)


def cancelorder(request, id):
    d = Orders.objects.get(order_id=id)
    u = OrderUpdate.objects.get(order_id=id)
    d.delete()
    u.delete()
    messages.error(request, "Order Cancelled Successfuly")
    return redirect("/profile")


@login_required
@permission_required('ekartapp.read_product', raise_exception=True)
def dashboard(request):
    prods = Product.objects.all()
    totalProducts = len(prods)
    context = {"prods": prods, "totalProducts": totalProducts}
    return render(request, "dashboard.html", context)


@login_required
@permission_required('ekartapp.add_Product', raise_exception=True)
def addProduct(request):
    if request.method == "POST":
        pname = request.POST.get('pname')
        pimage = request.FILES['pimage']
        pcategory = request.POST.get('pcategory')
        pscategory = request.POST.get('pscategory')
        pdesc = request.POST.get('pdesc')
        pprice = request.POST.get('pprice')
        pstock = request.POST.get('pstock')
        papprice = request.POST.get('paprice')
        query = Product(product_name=pname, category=pcategory, subcategory=pscategory,
                        price=pprice, desc=pdesc, image=pimage, stock=pstock, actual_price=papprice)
        query.save()
        messages.info(request, "Successfully your product was added")
        return redirect("/dashboard")
    return render(request, "addProduct.html")


@login_required
@permission_required('ekartapp.delete_Product', raise_exception=True)
def deleteProduct(request, id):
    p = Product.objects.get(id=id)
    p.delete()
    messages.warning(request, "Product Deleted Successfully")
    return redirect('/dashboard')


@login_required
@permission_required('ekartapp.edit_Product', raise_exception=True)
def editProduct(request, id):
    d = Product.objects.get(id=id)
    context = {"d": d}
    if request.method == "POST":
        try:
            pname = request.POST.get('pname')
            pimage = request.FILES['pimage']
            pcategory = request.POST.get('pcategory')
            pscategory = request.POST.get('pscategory')
            pdesc = request.POST.get('pdesc')
            pprice = request.POST.get('pprice')
            papprice = request.POST.get('paprice')
            pstock = request.POST.get('pstock')
            edit = Product.objects.get(id=id)
            edit.product_name = pname
            edit.category = pcategory
            edit.subcategory = pscategory
            edit.desc = pdesc
            edit.price = pprice
            edit.image = pimage
            edit.stock = pstock
            edit.actual_price = papprice
            edit.save()
        except:
            pname = request.POST.get('pname')
            pcategory = request.POST.get('pcategory')
            pscategory = request.POST.get('pscategory')
            pdesc = request.POST.get('pdesc')
            pprice = request.POST.get('pprice')
            papprice = request.POST.get('paprice')
            pstock = request.POST.get('pstock')
            edit = Product.objects.get(id=id)
            edit.product_name = pname
            edit.category = pcategory
            edit.subcategory = pscategory
            edit.desc = pdesc
            edit.price = pprice
            edit.stock = pstock
            edit.actual_price = papprice
            edit.save()
            messages.info(request, "Product Updated Successfully....")
        return redirect("/dashboard")
    return render(request, "editProduct.html", context)
