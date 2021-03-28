from django import forms
from .models import Ledger, Item, Person, Order, OrderItem
from searchableselect.widgets import SearchableSelect

class LedgerForm(forms.ModelForm):
    model = Ledger

    class Meta:
        model = Ledger
        fields = ("orders",)
        widgets = {'orders': forms.widgets.HiddenInput}


class ItemForm(forms.ModelForm):
    model = Item
    def __init__(self, *args, **kwargs):
        super(ItemForm, self).__init__(*args, **kwargs)
        self.fields['name'].label = "Parca ismi"
        self.fields['price'].label = "Fiyat"
        self.fields['stock'].label = "Stok (Zorunlu değil)"
        self.fields['image'].label = "Resim (Zorunlu değil)"
        self.fields['image'].widget.clear_checkbox_label = 'temizle'
        self.fields['image'].widget.initial_text = "Mevcut resim"
        self.fields['image'].widget.input_text = "değiştir"
    class Meta:
        model = Item
        fields = ("name","price","stock","image",)
    

class OrderUpdateForm(forms.ModelForm):
    model=Order

    class Meta:
        model=Order
        fields=('is_paid', 'paid_amount',)
    
    def clean(self):
        data = self.cleaned_data
        if data['paid_amount'] > self.instance.total:
            raise forms.ValidationError("Girdiğiniz miktar toplam fiyattan yüksek, lütfen [0 - {0}] aralığında bir fiyat giriniz.".format(self.instance.total))
        return data

class PersonForm(forms.ModelForm):
    model = Person

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     self.fields['fullname'].error_messages={'invalid':"Bu isme sahip şahıs zaten mevcut"}

    class Meta:
        model = Person
        fields = ("fullname","phone_number")


class OrderItemForm(forms.ModelForm):
    model = OrderItem

    class Meta:
        model = OrderItem
        fields=("item","amount",)
        widgets = { 
            'item': forms.Select(attrs={'label': 'blabla'})#forms.Textarea(attrs={'placeholder': u'Bla bla'}),
        }   
        # widgets = {
        #     'item':# SearchableSelect(model='main.Item', search_field='name', many=False,limit=10)
        # }  

# class OrderForm(forms.ModelForm):
#     model = Order

#     class Meta:
#         model = Order
#         fields = ("amount","item")