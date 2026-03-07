from django.contrib import admin
from .models import Therapist, GridAvailability, RangeAvailability, Freeday, ScheduleConfig, Meet

admin.site.register(ScheduleConfig)


@admin.register(Therapist)
class TherapistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "timezone_verbose", "verbose_name_display")
    list_filter = ("user__is_active",)
    search_fields = ("user__username", "user__first_name", "user__last_name", "user__email")
    raw_id_fields = ("user",)

    def verbose_name_display(self, obj):
        return obj.verbose_name_display()

    verbose_name_display.short_description = "Nombre"


admin.site.register(GridAvailability)
admin.site.register(RangeAvailability)
admin.site.register(Freeday)
admin.site.register(Meet)
