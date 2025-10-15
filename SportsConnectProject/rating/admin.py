from django.contrib import admin
from .models import Rating, FacilityRatingStats


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ['user', 'facility', 'stars', 'created_at', 'has_comment']
    list_filter = ['stars', 'created_at', 'facility']
    search_fields = ['user__email', 'facility__name', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    def has_comment(self, obj):
        return bool(obj.comment)
    has_comment.boolean = True
    has_comment.short_description = 'Comentario'


@admin.register(FacilityRatingStats)
class FacilityRatingStatsAdmin(admin.ModelAdmin):
    list_display = ['facility', 'average_rating', 'total_ratings', 'last_updated']
    readonly_fields = ['facility', 'average_rating', 'total_ratings', 'last_updated']
    
    def has_add_permission(self, request):
        # Las estadísticas se crean automáticamente via signals
        return False
    
    def has_delete_permission(self, request, obj=None):
        return False
