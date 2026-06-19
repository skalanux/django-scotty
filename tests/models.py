from django.db import models


class DummyItem(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, default="")
    active = models.BooleanField(default=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        app_label = "tests"
        ordering = ["pk"]

    def __str__(self):
        return self.name
