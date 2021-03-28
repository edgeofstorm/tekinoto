from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic import CreateView, ListView, UpdateView, DeleteView, DetailView, TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.utils.html import escape
from django.urls import reverse_lazy
from django.http import HttpResponse, HttpResponseRedirect
from django.db.models import Sum

# from django.template.loader import render_to_string
# from weasyprint import HTML
# import tempfile
# from django.db.models import Sum

import datetime
import csv

from django_datatables_view.base_datatable_view import BaseDatatableView

from .models import Ledger, Item, Person, Order, OrderItem
from .forms import OrderItemForm, LedgerForm, ItemForm, PersonForm, OrderUpdateForm  # OrderForm

from django.shortcuts import render
from django.template import RequestContext


def handler404(request, exception, template_name="main/404.html"):
    response = render(request,template_name)
    response.status_code = 404
    return response


@method_decorator(login_required, name='dispatch')
class LedgerListJson(BaseDatatableView):
    # The model we're going to show
    model = Ledger

    columns = ['person', 'total', 'last_modified']
    order_columns = ['person', 'total', 'last_modified']
    max_display_length = 500

    def get_initial_queryset(self):
        # .filter(orders__is_paid=False)
        return Ledger.objects.annotate(total=Sum('orders__total')-Sum('orders__paid_amount'))

    def filter_queryset(self, qs):
        # use request parameters to filter queryset
        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(person__fullname__icontains=search)
        return qs

    # def filter_queryset(self, qs):
    #     search = self.request.GET.get('search[value]', None)
    #     print(self.request)
    #     if search:
    #         qs = qs.filter(person__icontains=search)
    #     return qs

    def render_column(self, row, column):
        # We want to render user as a custom column
        if column == 'total':
            # debt = sum([order.total-order.paid_amount for order in row.orders.all()
            #            if not order.is_paid])
            if row.total is not None:
                return escape(f'{ row.total} TL')
            return escape('-')
        if column == 'last_modified':
            return escape(f'{ row.last_modified}')
        else:
            return super(LedgerListJson, self).render_column(row, column)


@method_decorator(login_required, name='dispatch')
class ItemListJson(BaseDatatableView):
    # The model we're going to show
    model = Item

    columns = ['name', 'price', 'stock', 'image']
    order_columns = ['name', 'price', 'stock', '']
    max_display_length = 500

    def render_column(self, row, column):
        # i recommend change 'flat_house.house_block.block_name' to 'address'
        modal = """<div class="modal fade" id="exampleModal{0}" tabindex="-1" aria-labelledby="exampleModalLabel" aria-hidden="true">
                        <div class="modal-dialog">
                            <div class="modal-content">
                                <div class="modal-header">
                                    <h5 class="modal-title" id="exampleModalLabel">{1}</h5>
                                    <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                                </div>
                                <div class="modal-body">
                                    <div class="row">
                                        <div class="col">
                                            <img src="{2}" alt="Resim yok" style="max-width: 100%; max-height: 100%;">
                                        </div>
                                    </div>
                                </div>
                                <div class="modal-footer">
                                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Kapat</button>
                                </div>
                            </div>
                        </div>
                    </div>""".format(row.id,row.name,row.image.url)
        if column == 'name':
            return '<a href="{0}">{1}</a>'.format(reverse('main:item_update', kwargs={'pk': row.id}), row.name)
        elif column == 'price':
            return escape(f'{row.price} TL')
        elif column == 'stock':
            if row.stock:
                return escape(f'{row.stock}')
            return escape('-')
        elif column == 'image':
            return '<button type="anchor" class="btn btn-outline-primary btn-sm" data-bs-toggle="modal" data-bs-target="#exampleModal{0}">Resim</button> {1}'.format(row.id, modal)
            # return '<a href="{0}" data-toggle="modal" data-target="#exampleModal{1}">resim</a>'.format(reverse('main:image_modal', kwargs={'pk': row.id}),row.id)
        else:
            return super(ItemListJson, self).render_column(row, column)


@method_decorator(login_required, name='dispatch')
class PersonListJson(BaseDatatableView):
    # The model we're going to show
    model = Person
    # datatable_options = {
    #         'columns': [
    #             'fullname',
    #             'phone_number',
    #         ],
    #     }

    # def get_total(self, instance, *args, **kwargs):
    #     orders = Order.objects.filter(person_id = self.model.id).filter(is_paid=False)
    #     return ", ".join(sum([order.total for order in orders]))
    
    columns = ['fullname', 'total', 'phone_number']
    order_columns = ['fullname', 'total', '']
    max_display_length = 500

    # datatable_options = {
    #         'columns': [
    #             'fullname',
    #             ("timestamp",'ledger__timestamp'),
    #             'phone_number',
    #         ],
    #         'unsortable_columns':['timestamp','phone_number']
    #     }

    def get_initial_queryset(self):
        # .filter(orders__is_paid=False)
        return Person.objects.annotate(total=Sum('orders__total')-Sum('orders__paid_amount'))

    def render_column(self, row, column):
        # i recommend change 'flat_house.house_block.block_name' to 'address'
        if column == 'fullname':
            return '<a href="{0}">{1}</a>'.format(f'{row.id}/update', row.fullname)
        elif column == 'phone_number':
            if row.phone_number:
                return escape(f'{row.phone_number}')
            return escape('Yok')
        if column == 'total':
            # link = 'l/{0}'.format(row.id)
            # link = ''
            # debts = [order.total for order in Ledger.objects.filter(
            #     person=row).first().orders.all() if order.total is not None]
            if row.total is not None:
                return escape(f'{ row.total} TL')
            return escape('-')
            # return '<a href="{0}">{1}</a>'.format(link, sum(debts))
        else:
            return super(PersonListJson, self).render_column(row, column)


@method_decorator(login_required, name='dispatch')
class OrderListJson(BaseDatatableView):
    # The model we're going to show
    model = Order

    columns       = ['name', 'price', 'sale_price', 'amount','total','paid_amount', 'remaining', 'timestamp', 'is_paid']
    order_columns = ['', '', '', '','total', '', '', 'timestamp', 'is_paid']
    max_display_length = 500


    def get_initial_queryset(self):
        orders = get_object_or_404(Ledger, person_id=self.kwargs.get('pk')).orders.all()
        return orders

    def filter_queryset(self, qs):
        # use request parameters to filter queryset
        # simple example:
        search = self.request.GET.get('search[value]', None)
        if search:
            qs = qs.filter(items__item__name__icontains=search)
        return qs
    #     # more advanced example
    #     # filter_customer = self.request.GET.get('customer', None)

    #     # if filter_customer:
    #     #     customer_parts = filter_customer.split(' ')
    #     #     qs_params = None
    #     #     for part in customer_parts:
    #     #         q = Q(customer_firstname__istartswith=part)|Q(customer_lastname__istartswith=part)
    #     #         qs_params = qs_params | q if qs_params else q
    #     #     qs = qs.filter(qs_params)
       

    def prepare_results(self, qs):
        # prepare list with output column data
        # queryset is already paginated here
        json_data = []
        for order in qs:
            if order.is_paid:
                json_data.append([
                    '<s><a href="{0}">{1}</s> (Ödendi)</a>'.format(reverse('main:ledger_order_update', kwargs={"pk": order.id}),order.items.item.name),  # escape HTML for security reasons
                    "<s>{0}</s>".format(f'{order.items.item.price} TL'),  # escape HTML for security reasons
                    "<s>{0}</s>".format(f'{order.item_sale_price} TL'),
                    "<s>{0}</s>".format(order.items.amount),
                    "<s>{0}</s>".format(f'{order.total} TL'),
                    "<s>{0}</s>".format(f'{order.paid_amount} TL'),
                    "<s>{0}</s>".format(f'{order.total - order.paid_amount} TL' if not order.is_paid else '0 TL'),
                    "<s>{0}</s>".format(order.timestamp),
                    "{0}".format('Evet' if order.is_paid else 'Hayır'),
                ])
            else:
                json_data.append([
                    '<a href="{0}">{1}</a>'.format(reverse('main:ledger_order_update', kwargs={"pk": order.id}),order.items.item.name),  # escape HTML for security reasons
                    escape("{0}".format(f'{order.items.item.price} TL')),  # escape HTML for security reasons
                    escape("{0}".format(f'{order.item_sale_price} TL')),
                    escape("{0}".format(order.items.amount)),
                    escape("{0}".format(f'{order.total} TL')),
                    escape("{0}".format(f'{order.paid_amount} TL')),
                    escape("{0}".format(f'{order.total - order.paid_amount} TL' if not order.is_paid else '0 TL')),
                    escape("{0}".format(order.timestamp)),
                    escape("{0}".format('Evet' if order.is_paid else 'Hayır')),
                ])
        return json_data

    # def render_column(self, row, column):
    #     # We want to render user as a custom column
    #     if column == 'name':
    #         return '<a href="{0}">{1}</a>'.format(reverse('main:ledger_order_update', kwargs={"pk": row.pk}),row.items.item.name)  #  
    #     elif column == 'price':
    #         return escape(f'{row.items.item.price}')
    #     elif column == 'sale_price':
    #         return escape(f'{row.item_sale_price}')
    #     elif column == 'amount':
    #         return escape(f'{row.items.amount}')
    #     elif column == 'timestamp':
    #         return escape(f'{row.timestamp}')
    #     elif column == 'total':
    #         return escape(f'{row.total}')
    #     elif column == 'paid':
    #         if row.is_paid:
    #             return escape('Evet')
    #         return escape('Hayir')
    #     elif column == 'paid_amount':
    #         if row.is_paid:
    #             return escape(f'{row.total}')
    #         return escape(f'{row.paid_amount}')
    #     elif column == 'remaining':
    #         if row.is_paid:
    #             return escape('0')
    #         return escape(f'{row.total - row.paid_amount}')
    #     elif column == 'image':
    #         return escape(f'{row.items.item.image}')
    #     else:
    #         return super(OrderListJson, self).render_column(row, column)


@method_decorator(login_required, name='dispatch')
class LedgerListView(ListView):
    model = Ledger
    template_name = 'main/home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["total"] = self.all_debts()
        return context

    def all_debts(self):
        ledgers = Ledger.objects.all()
        try:
            sum = 0.0
            for ledger in ledgers:
                for order in ledger.orders.all():
                    if not order.is_paid:
                        sum += order.total-order.paid_amount
            return sum
        except:
            return -1

class OrderItemCreateView(CreateView):
    model = OrderItem
    form_class = OrderItemForm
    template_name_suffix='_create'

    def get_success_url(self):
        #   id=self.kwargs['pk']
          ledger_id = OrderItem.objects.filter(
            id=self.kwargs['pk']).first().person.ledger.id
          return reverse_lazy('main:ledger_detail', kwargs={'pk': ledger_id})
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["person"] = Person.objects.get(id=self.kwargs.get('pk'))
        return context
    
    def form_valid(self, form):
        order_item = form.save(commit=False)
        p = Person.objects.get(id=self.kwargs.get('pk'))
        order_item.person = p
        order_item.save()
        order = Order.objects.create(person=p,items=order_item)
        order.save()
        ledger = Ledger.objects.filter(person=p).first()
        ledger.orders.add(order)
        ledger.save()
        return redirect(reverse('main:ledger_detail',kwargs={'pk':ledger.id}))



@method_decorator(login_required, name='dispatch')
class LedgerDetailView(DetailView):
    model = Ledger

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        orders = Ledger.objects.filter(
            id=self.kwargs['pk']).first().orders.all()
        context["total"] = sum(
            [order.total-order.paid_amount for order in orders if not order.is_paid])
        return context


@method_decorator(login_required, name='dispatch')
class LedgerUpdateView(UpdateView):
    model = Ledger
    # fields=['',]


@method_decorator(login_required, name='dispatch')
class PersonUpdateView(UpdateView):
    model = Person
    template_name = 'main/person_update.html'
    fields = '__all__'
    success_url=reverse_lazy('main:person_list')

    


@method_decorator(login_required, name='dispatch')
class OrderUpdateView(UpdateView):
    model = Order
    template_name = 'main/ledger_update.html'
    form_class = OrderUpdateForm

    def get_success_url(self, *args, **kwargs):
        ledger_id = Order.objects.filter(
            id=self.kwargs['pk']).first().person.ledger.id
        return reverse_lazy('main:ledger_detail', kwargs={'pk': ledger_id})
    
    def form_valid(self, form):
        if form.instance.is_paid:
            form.instance.paid_amount=form.instance.total
        self.object = form.save()
        return HttpResponseRedirect(self.get_success_url())


@method_decorator(login_required, name='dispatch')
class PersonDetailView(DetailView):
    model = Person

    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context["total"] = total(self.object)
    #     return context


@method_decorator(login_required, name='dispatch')
class ItemListView(ListView):
    model = Item


@method_decorator(login_required, name='dispatch')
class LedgerDeleteView(DeleteView):
    model = Ledger


@method_decorator(login_required, name='dispatch')
class ItemDetailView(DetailView):
    model = Item


@method_decorator(login_required, name='dispatch')
class ItemUpdateView(UpdateView):
    model = Item
    fields = '__all__'
    template_name_suffix = '_update'
    success_url=reverse_lazy('main:item_list')


@method_decorator(login_required, name='dispatch')
class ItemCreateView(CreateView):
    model = Item
    form_class=ItemForm
    template_name_suffix = '_create_form'

    def get_success_url(self):
        return reverse('main:item_list')


@method_decorator(login_required, name='dispatch')
class LedgerDeleteView(DeleteView):
    pass


@method_decorator(login_required, name='dispatch')
class ItemDeleteView(DeleteView):
    pass


@method_decorator(login_required, name='dispatch')
class PersonListView(ListView):
    model = Person


# @method_decorator(login_required, name='dispatch')
# class ImageModalTemplateView(TemplateView):
#     template_name='main/snippets/img.html'

#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         context["object"] = Item.objects.filter(id=self.kwargs['pk']).first()
#         return context
    


def ledger_create(request, *args, **kwargs):
    if request.method == "POST":
        person_form = PersonForm(request.POST)
        order_item_form = OrderItemForm(request.POST)
        ledger_form = LedgerForm(request.POST)

        if person_form.is_valid():
            person = person_form.save()
            order_item = order_item_form.save(False)
            order_item.person = person
            order_item.save()
            order = Order.objects.create(person=person, items=order_item)
            # category.articles.set(category.articles.all() | article)
            # order.items.set(order.items.all() | order_item)
            # order.items.add(order_item)
            order.save()
            ledger = Ledger.objects.create(person=person)
            ledger.orders.add(order)
            # ledger.orders.set(ledger.orders.all() | order)
            # ledger = ledger_form.save(False)
            # ledger.order = order
            # ledger.person = person
            ledger.save()

            return redirect(reverse('main:ledger_detail',kwargs={'pk':ledger.id}))
        # reverse('main:homepage')
    else:
        person_form = PersonForm()
        order_item_form = OrderItemForm()
        ledger_form = LedgerForm()

    context = {
        'person_form': person_form,
        'order_form': order_item_form,
        'ledger_form': ledger_form
    }
    return render(request, "main/ledger_create_form.html", context)


def export_csv_items(request):
    # tr={'Ledger':'Hesap Defteri','Item':'Parcalar','Person':'Kisiler'}
    response = HttpResponse(content_type='text/csv')
    # if clsname in tr:
    response['Content-Disposition'] = 'attachment; filename=Parcalar - ' + \
        str(datetime.date.today().day)+'-'+str(datetime.date.today().month) + \
        '-'+str(datetime.date.today().year)+'.csv'

    writer = csv.writer(response, delimiter=',')

    writer.writerow(['Parca Ismi', 'Fiyat', 'Stok'])

    items = Item.objects.all()

    for item in items:
        writer.writerow([item.name, item.price, item.stock])

    return response


def export_csv_ledgers(request):
    # tr={'Ledger':'Hesap Defteri','Item':'Parcalar','Person':'Kisiler'}
    response = HttpResponse(content_type='text/csv')
    # if clsname in tr:
    response['Content-Disposition'] = 'attachment; filename=Hesap Defteri - ' + \
        str(datetime.date.today().day)+'-'+str(datetime.date.today().month) + \
        '-'+str(datetime.date.today().year)+'.csv'

    writer = csv.writer(response, delimiter=',')

    writer.writerow(['Ad Soyad', 'Toplam Borc', 'Telefon'])

    ledgers = Ledger.objects.all()

    for ledger in ledgers:
        total = sum([order.total for order in ledger.orders.all()
                    if order.total is not None])
        name = Person.objects.get(id=ledger.person.id).fullname
        phone = Person.objects.get(id=ledger.person.id).phone_number
        writer.writerow([name, total, phone])

    return response


def export_csv_persons(request):
    # tr={'Ledger':'Hesap Defteri','Item':'Parcalar','Person':'Kisiler'}
    response = HttpResponse(content_type='text/csv')
    # if clsname in tr:
    response['Content-Disposition'] = 'attachment; filename=Kisiler - ' + \
        str(datetime.date.today().day)+'-'+str(datetime.date.today().month) + \
        '-'+str(datetime.date.today().year)+'.csv'

    writer = csv.writer(response, delimiter=',')

    writer.writerow(['Ad Soyad', 'Toplam Borc', 'Telefon'])

    ledgers = Ledger.objects.all()

    for ledger in ledgers:
        total = sum([order.total for order in ledger.orders.all()
                    if order.total is not None])
        name = Person.objects.get(id=ledger.person.id).fullname
        phone = Person.objects.get(id=ledger.person.id).phone_number
        writer.writerow([name, total, phone])

    return response


def export_csv_person_ledger(request, pk):
    response = HttpResponse(content_type='text/csv')
    # if clsname in tr:
    response['Content-Disposition'] = f'attachment; filename={Person.objects.get(id=pk).fullname} - Hesap Defteri - ' + \
        str(datetime.date.today().day)+'-'+str(datetime.date.today().month) + \
        '-'+str(datetime.date.today().year)+'.csv'

    writer = csv.writer(response, delimiter=',')

    writer.writerow(['Parca Ismi', 'Satis fiyati', 'Adet', 'Toplam fiyat',
                    'Odendi mi?','Odenen miktar', 'Kalan Borc', 'Siparis Tarihi'])

    ledger = Ledger.objects.filter(person=Person.objects.get(id=pk)).first()
    orders = ledger.orders.all()

    for order in orders:
        name = order.items.item.name
        sale_price = order.item_sale_price
        amount = order.items.amount
        total = order.total
        is_paid = 'Evet' if order.is_paid else 'Hayir'
        if order.is_paid:
            paid_amount = order.total
            remaining = '0'
        else:
            paid_amount = order.paid_amount
            remaining = order.total - order.paid_amount
        timestamp = order.timestamp
        writer.writerow([name, sale_price, amount, total,
                        is_paid, paid_amount, remaining, timestamp])

    return response
    # response['Content-Transfer-Encoding'] = 'binary'

    # html_string=render_to_string('main/pdf_output.html',{'items':{},'total':0})

    # html = HTML(string=html_string)

    # result = html.write_pdf()

    # with tempfile.NamedTemporaryFile(delete=True) as output:
    #     output.write(result)
    #     output.flush()
    #     output=open(output.name,'rb')
    #     response.write(output.read())

    # return response
