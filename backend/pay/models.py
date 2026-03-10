from django.db import models

from therapist.models import Meet


class Pay(models.Model):
  STATUS_CHOICES = [
      ("P", "Pendiente"),
      ("D", "Hecho"),
      ("C", "Cancelado"),
      ("R", "Reembolsado"),
  ]

  meet = models.ForeignKey(Meet, on_delete=models.SET_NULL, null=True, blank=True)
  amount = models.DecimalField(default=0, max_digits=10, decimal_places=2)
  transaction_code = models.CharField(max_length=255, blank=True, default="")
  status = models.CharField(max_length=1, choices=STATUS_CHOICES, default="P")
  timestamp = models.DateTimeField(auto_now_add=True)

  class Meta:
      verbose_name = "Pago"
      verbose_name_plural = "Pagos"

  def __str__(self):
      return self.code()

  def code(self) -> str:
      init_number = 1000
      if not self.id:
          return "QP?????"
      return f"QP{self.id + init_number:09d}"

  def confirm(self):
      self.status = "D"
      self.save()

