from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.db import models

class OrderedModel(models.Model):
    """
    An abstract model that allows objects to be ordered relative to each other.
    Provides an ``order_index`` field.
    """
    
    order_index = models.PositiveIntegerField(editable=False)
    
    class Meta:
        abstract = True
        ordering = ('order_index',)
    
    def save(self, *args, **kwargs):
        if not self.id:
            qs = self.__class__.objects.order_by('-order_index')
            try:
                self.order_index = qs[0].order + 1
            except IndexError:
                self.order_index = 0
        super(OrderedModel, self).save(*args, **kwargs)
    
    def _move(self, up):
        qs = self.__class__._default_manager
        if up:
            qs = qs.order_by('-order_index').filter(order__lt=self.order_index)
        else:
            qs = qs.filter(order__gt=self.order_index)
        try:
            replacement = qs[0]
        except IndexError:
            # already first/last
            return
        self.order_index, replacement.order = replacement.order, self.order_index
        self.save()
        replacement.save()
    
    def move_down(self):
        """
        Move this object down one position.
        """
        return self._move(up=False)
    
    def move_up(self):
        """
        Move this object up one position.
        """
        return self._move(up=True)
