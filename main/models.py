from django.db import models
# from django.contrib.auth.models import User
from django.urls import reverse, reverse_lazy
# from django.db.models.signals import pre_save, post_save
# from django.dispatch import receiver
from PIL import Image


class LedgerQuerySet(models.QuerySet):

    def delete(self, *args, **kwargs):
        for obj in self:
            obj.img.delete()
        super(LedgerQuerySet, self).delete(*args, **kwargs)

class Item(models.Model):
    name  = models.CharField(max_length=255,verbose_name= ('Parça İsmi'), unique=True) # make it unique
    price = models.DecimalField(max_digits=7,decimal_places=2,verbose_name= ('Fiyat'))
    stock = models.SmallIntegerField(null=True, blank=True,verbose_name= ('Stok (Zorunlu değil)'))
    image = models.ImageField(default='default.png',upload_to='item_pics',verbose_name= ('Resim (Zorunlu değil)'))

    def __str__(self):
        return f'{self.name} - {self.price} TL'
    
    def get_absolute_url(self,*args,**kwargs):
        return reverse("main:item_detail", kwargs={"pk": self.pk})
    
    def save(self,*args,**kwargs):
        super().save()

        img = Image.open(self.image.path)

        if img.height > 300 or img.width > 300:
            output_size = (300, 300)
            img.thumbnail(output_size)
            img.save(self.image.path)
        
    class Meta:
        verbose_name = 'Parça'
        verbose_name_plural = 'Parçalar'
        ordering = ['name']


class OrderItem(models.Model):
    item   = models.ForeignKey('main.Item',on_delete=models.CASCADE, verbose_name=('Parca'))  # related_name='order'
    person = models.ForeignKey('main.Person', on_delete=models.CASCADE)
    amount = models.SmallIntegerField(default=1, verbose_name=('Adet'))
    
    def __str__(self):
        return f'{self.person} - {self.item} TL - {self.amount} adet'


class Order(models.Model):
    person          = models.ForeignKey('main.Person',related_name='orders' ,on_delete=models.CASCADE)
    items           = models.ForeignKey(OrderItem, on_delete=models.CASCADE)
    timestamp       = models.DateField(auto_now_add=True)
    item_sale_price = models.SmallIntegerField(null=True,blank=True)
    total           = models.SmallIntegerField(null=True,blank=True) # make it decimalfield ?
    paid_amount     = models.SmallIntegerField(default=0,blank=True,verbose_name= ('Ödenen miktar'))
    is_paid         = models.BooleanField(default=False,verbose_name= ('Ödendi mi ?'))
    #ledger many to many ?

    def save(self, *args, **kwargs):
        self.total = self.items.amount*self.items.item.price
        self.item_sale_price = self.items.item.price
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.person} - {self.items} - {self.timestamp}'
     

class Ledger(models.Model):
    objects       = LedgerQuerySet.as_manager()
    person        = models.OneToOneField("main.Person", related_name="ledger", on_delete=models.CASCADE)
    orders        = models.ManyToManyField(Order)  # models.ForeignKey('main.Order', related_name='ledger', on_delete=models.CASCADE)
    last_modified = models.DateField(auto_now=True)
    timestamp     = models.DateField(auto_now_add=True)

    # class Meta:
    #     sort by last modified
    
    def __str__(self):
        return f'{self.person}' # - {self.total}
    
    def get_absolute_url(self):
        return reverse("main:ledger_detail", kwargs={"pk": self.pk})
    
    def delete(self):
        if self.orders:
            for order in self.orders.all():
                order.items.delete()
                order.delete()
        super(Ledger,self).delete()
        
        


class Person(models.Model):
    fullname      = models.CharField(max_length=100, unique=True,verbose_name= ('Ad Soyad'))
    phone_number  = models.CharField(max_length=11,null=True, blank=True, unique=True,verbose_name= ('Telefon (Zorunlu Değil)'))
    # phone_number  = models.PhoneNumberField(null=True, blank=True, unique=True)

    def __str__(self):
        return f'{self.fullname}'

    def get_absolute_url(self,*args,**kwargs):
        return reverse("main:person_detail", kwargs={"pk": self.pk})

